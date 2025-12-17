"""
Resume Assistant Agent using Strands Agents SDK.

This module implements the AI agent that guides users through the interactive
resume building process, asking targeted questions and extracting information.
"""

import logging
import uuid
from typing import Any, Dict, List, Optional

from strands import Agent, tool
from strands.models.ollama import OllamaModel

from agentic_resume_builder.agent_tools import ResumeAgentTools
from agentic_resume_builder.config import OllamaConfig
from agentic_resume_builder.exceptions import AgentTimeoutError, OllamaConnectionError
from agentic_resume_builder.models import (
    Question,
    Resume,
    ResumeDocument,
    Interaction,
)
from agentic_resume_builder.ollama_client import OllamaConnectionManager

logger = logging.getLogger(__name__)


class ResumeAgent:
    """
    AI Agent for interactive resume building.
    
    This agent uses Strands Agents SDK with Ollama to guide users through
    creating impact-oriented resumes. It asks targeted questions, extracts
    information, and helps quantify achievements.
    
    Requirements: 2.1, 2.2, 3.1, 3.3, 5.1, 8.1, 8.2
    """

    def __init__(
        self,
        ollama_config: OllamaConfig,
        agent_tools: ResumeAgentTools,
        resume: Optional[Resume] = None,
    ):
        """
        Initialize the Resume Agent.
        
        Args:
            ollama_config: Configuration for Ollama connection
            agent_tools: Tools for resume manipulation
            resume: Optional resume to work with
            
        Raises:
            OllamaConnectionError: If Ollama is not available
        """
        self.config = ollama_config
        self.tools = agent_tools
        self.resume = resume
        
        # Validate Ollama connection
        self.connection_manager = OllamaConnectionManager(ollama_config)
        
        # Create Ollama model
        self.model = OllamaModel(
            host=ollama_config.base_url,
            model_id=ollama_config.model,
            temperature=ollama_config.temperature,
        )
        
        # Build system prompt
        system_prompt = self._build_system_prompt()
        
        # Create Strands Agent with tools
        self.agent = Agent(
            model=self.model,
            system_prompt=system_prompt,
            tools=self._register_tools(),
        )
        
        # Track conversation state
        self.current_experience_index = 0
        self.prioritized_experiences: List[str] = []
        self.introductory_complete = False
        
        logger.info("Resume Agent initialized successfully")
    
    def _build_system_prompt(self) -> str:
        """
        Build the system prompt for the career coach persona.
        
        The prompt focuses on:
        - Impact-oriented content
        - Quantifiable metrics
        - Action verbs
        - Comprehensive questioning
        
        Returns:
            System prompt string
        """
        return """You are an expert career coach specialized in creating impact-oriented resumes.

Your mission is to help users create resumes that demonstrate their true professional value through concrete metrics and achievements.

## Your Approach

1. **Start with an Introductory Question**
   - For new or sparse resumes: Ask a comprehensive question to understand their complete professional background
   - For existing resumes with unclear content: Ask for clarification about ambiguous experiences

2. **Extract and Prioritize Experiences**
   - Identify all key experiences from their response
   - Prioritize them for detailed questioning (most recent and important first)

3. **Ask Targeted Questions**
   - For each experience, ask about:
     * Specific projects and responsibilities
     * Results and outcomes achieved
     * Impact on the organization
   - Always request quantifiable metrics

4. **Quantify Everything**
   - When you receive generic responses, always ask:
     * How many people/users were involved?
     * What percentage improvement did you achieve?
     * How much time did you save/reduce?
     * What budget did you manage?
     * What was the team size?
   - Never accept vague terms like "many", "several", "various" - always ask for specific numbers

5. **Use Impact-Oriented Language**
   - Start achievements with strong action verbs (achieved, improved, increased, reduced, developed, led, etc.)
   - Emphasize results and impact, not just activities
   - Format metrics prominently (bold numbers, percentages)

6. **Maintain Context**
   - Remember previous responses in the conversation
   - Generate follow-up questions based on what you've learned
   - Move sequentially through experiences

## Guidelines

- Be conversational and encouraging
- Ask one focused question at a time
- Probe for specifics when responses are vague
- Celebrate achievements while pushing for quantification
- Help users remember details they might have forgotten

Your goal is to extract every achievement and quantify every result, creating a resume that truly showcases the user's professional impact."""

    def _register_tools(self) -> List:
        """
        Register tools for the agent to use.
        
        Returns:
            List of tool functions
        """
        # Create tool wrappers that work with the agent
        tools = []
        
        @tool
        def update_section(section: str, content: str, position: Optional[int] = None) -> str:
            """Update a specific section of the resume.
            
            Args:
                section: Name of the section to update
                content: New content for the section
                position: Optional position for insertion (0-based index)
            """
            if self.resume is None:
                return "Error: No resume loaded"
            
            try:
                updated_doc = self.tools.update_resume_section(
                    self.resume.document,
                    section,
                    content,
                    position
                )
                self.resume.document = updated_doc
                return f"Successfully updated section '{section}'"
            except Exception as e:
                logger.error(f"Error updating section: {e}")
                return f"Error updating section: {str(e)}"
        
        @tool
        def add_experience(
            company: str,
            role: str,
            period: str,
            achievements: List[str],
            location: Optional[str] = None,
            technologies: Optional[List[str]] = None,
        ) -> str:
            """Add a new work experience to the resume.
            
            Args:
                company: Company name
                role: Job role/title
                period: Time period (e.g., "2020-01 - 2022-06")
                achievements: List of achievement descriptions
                location: Optional work location
                technologies: Optional list of technologies used
            """
            if self.resume is None:
                return "Error: No resume loaded"
            
            try:
                updated_doc = self.tools.add_experience_item(
                    self.resume.document,
                    company,
                    role,
                    period,
                    achievements,
                    location,
                    technologies,
                )
                self.resume.document = updated_doc
                return f"Successfully added experience at {company} as {role}"
            except Exception as e:
                logger.error(f"Error adding experience: {e}")
                return f"Error adding experience: {str(e)}"
        
        @tool
        def enhance_text(text: str, metrics: Dict[str, Any]) -> str:
            """Enhance text with quantifiable metrics.
            
            Args:
                text: Original text to enhance
                metrics: Dictionary of metrics (percentage, number, currency, timeframe, team_size, custom)
            """
            try:
                enhanced = self.tools.enhance_with_metrics(text, metrics)
                return enhanced
            except Exception as e:
                logger.error(f"Error enhancing text: {e}")
                return f"Error: {str(e)}"
        
        @tool
        def analyze_impact(text: str) -> Dict[str, Any]:
            """Analyze how impact-oriented a text is.
            
            Args:
                text: Text to analyze (e.g., achievement description)
            """
            try:
                result = self.tools.analyze_impact_score(text)
                return result
            except Exception as e:
                logger.error(f"Error analyzing impact: {e}")
                return {"error": str(e)}
        
        tools.extend([update_section, add_experience, enhance_text, analyze_impact])
        
        return tools

    def ask_introductory_question(self, resume: Resume) -> Question:
        """
        Generate an introductory question based on resume state.
        
        For new/sparse resumes: asks for comprehensive background
        For existing resumes: asks for clarification on unclear content
        
        Args:
            resume: The resume to analyze
            
        Returns:
            Question object with the introductory question
            
        Requirements: 2.1, 2.2
        """
        self.resume = resume
        
        # Analyze resume to determine if it's sparse or has unclear content
        is_sparse = self._is_resume_sparse(resume)
        has_unclear_content = self._has_unclear_content(resume)
        
        if is_sparse:
            # Ask comprehensive question for new/sparse resumes
            question_text = """I'd love to help you create an impactful resume! To get started, could you tell me about your professional background?

Please share:
- All the companies or organizations you've worked for
- Your roles and responsibilities at each
- Key projects or initiatives you worked on
- Any significant results or achievements you're proud of

Don't worry about being too detailed - I'll help you organize and quantify everything!"""
            
            question_type = "introductory"
            context = "New or sparse resume - gathering comprehensive background"
            
        elif has_unclear_content:
            # Ask clarification question for unclear existing content
            unclear_sections = self._identify_unclear_sections(resume)
            question_text = f"""I see you have some experience listed, but I'd like to help make it more impactful. 

I noticed these areas could use more detail:
{chr(10).join(f'- {section}' for section in unclear_sections)}

Could you tell me more about these experiences? What were your main responsibilities and what results did you achieve?"""
            
            question_type = "clarification"
            context = f"Existing resume with unclear content in: {', '.join(unclear_sections)}"
            
        else:
            # Resume looks good, ask about specific improvements
            question_text = """Your resume has good content! Let's make it even stronger by adding more quantifiable metrics.

Which experience would you like to enhance first? I can help you add specific numbers, percentages, and impact metrics."""
            
            question_type = "open"
            context = "Existing resume - seeking to enhance with metrics"
        
        question = Question(
            id=str(uuid.uuid4()),
            text=question_text,
            context=context,
            question_type=question_type,
            related_section="general",
        )
        
        logger.info(f"Generated introductory question: {question_type}")
        return question
    
    def _is_resume_sparse(self, resume: Resume) -> bool:
        """
        Check if a resume is sparse (new or minimal content).
        
        Args:
            resume: Resume to check
            
        Returns:
            True if resume is sparse
        """
        doc = resume.document
        
        # Check if there are few or no experiences
        if len(doc.experiences) == 0:
            return True
        
        # Check if experiences lack detail
        total_achievements = sum(len(exp.achievements) for exp in doc.experiences)
        if total_achievements < 3:
            return True
        
        # Check if personal info is incomplete
        if not doc.personal_info.name or not doc.personal_info.email:
            return True
        
        return False
    
    def _has_unclear_content(self, resume: Resume) -> bool:
        """
        Check if resume has unclear or generic content.
        
        Args:
            resume: Resume to check
            
        Returns:
            True if content is unclear
        """
        doc = resume.document
        
        # Check for generic achievement descriptions
        for exp in doc.experiences:
            for achievement in exp.achievements:
                # Check impact score
                if achievement.impact_score < 0.4:
                    return True
                
                # Check for vague terms
                vague_terms = ["various", "several", "many", "some", "multiple", "numerous"]
                desc_lower = achievement.description.lower()
                if any(term in desc_lower for term in vague_terms):
                    return True
        
        return False
    
    def _identify_unclear_sections(self, resume: Resume) -> List[str]:
        """
        Identify sections with unclear or generic content.
        
        Args:
            resume: Resume to analyze
            
        Returns:
            List of section names that need clarification
        """
        unclear = []
        doc = resume.document
        
        for exp in doc.experiences:
            # Check if experience has low-impact achievements
            low_impact = sum(1 for ach in exp.achievements if ach.impact_score < 0.4)
            if low_impact > 0:
                unclear.append(f"{exp.role} at {exp.company}")
        
        return unclear
    
    def extract_experiences(self, response_text: str) -> List[str]:
        """
        Extract key experiences from an introductory response.
        
        Uses the agent to parse and identify experiences from user's text.
        
        Args:
            response_text: User's response to introductory question
            
        Returns:
            List of extracted experience descriptions
            
        Requirements: 2.3
        """
        try:
            # Use the agent to extract experiences
            extraction_prompt = f"""Based on this response, extract and list all the distinct work experiences mentioned:

{response_text}

For each experience, provide:
- Company/Organization name
- Role/Position
- Brief description

Format as a simple list."""
            
            result = self.agent(extraction_prompt)
            
            # Parse the result to extract experiences
            experiences = []
            lines = str(result).strip().split('\n')
            
            current_exp = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    if line.startswith('-') or line.startswith('*'):
                        if current_exp:
                            experiences.append(' '.join(current_exp))
                            current_exp = []
                        current_exp.append(line.lstrip('-*').strip())
                    elif current_exp:
                        current_exp.append(line)
            
            if current_exp:
                experiences.append(' '.join(current_exp))
            
            logger.info(f"Extracted {len(experiences)} experiences from response")
            return experiences
            
        except Exception as e:
            logger.error(f"Error extracting experiences: {e}")
            # Fallback: return a simple split
            return [line.strip() for line in response_text.split('\n') if line.strip()]
    
    def prioritize_experiences(self, experiences: List[str]) -> List[str]:
        """
        Prioritize experiences for detailed questioning.
        
        Considers recency, completeness, and importance.
        
        Args:
            experiences: List of experience descriptions
            
        Returns:
            Prioritized list of experiences
            
        Requirements: 2.4
        """
        # For now, use a simple heuristic:
        # 1. Experiences mentioned first are often most recent
        # 2. Longer descriptions suggest more importance
        # 3. Experiences with company names are prioritized
        
        scored_experiences = []
        
        for idx, exp in enumerate(experiences):
            score = 0
            
            # Recency score (earlier in list = more recent)
            score += (len(experiences) - idx) * 10
            
            # Length score (more detail = more important)
            score += min(len(exp.split()), 20)
            
            # Has company name (contains "at" or "for")
            if ' at ' in exp.lower() or ' for ' in exp.lower():
                score += 15
            
            # Has role indicators
            role_keywords = ['engineer', 'developer', 'manager', 'director', 'lead', 'senior', 'analyst']
            if any(keyword in exp.lower() for keyword in role_keywords):
                score += 10
            
            scored_experiences.append((score, exp))
        
        # Sort by score (descending)
        scored_experiences.sort(reverse=True, key=lambda x: x[0])
        
        prioritized = [exp for score, exp in scored_experiences]
        
        self.prioritized_experiences = prioritized
        logger.info(f"Prioritized {len(prioritized)} experiences")
        
        return prioritized

    def generate_questions(
        self,
        experience: str,
        conversation_history: List[Interaction],
    ) -> List[Question]:
        """
        Generate detailed questions for a specific experience.
        
        Covers projects, responsibilities, and results. Requests metrics
        when content lacks quantification.
        
        Args:
            experience: Experience description to ask about
            conversation_history: Previous interactions for context
            
        Returns:
            List of questions to ask
            
        Requirements: 3.1, 3.3, 5.2
        """
        questions = []
        
        # Build context from conversation history
        context_summary = self._build_context_summary(conversation_history)
        
        # Generate questions using the agent
        try:
            prompt = f"""Based on this experience: "{experience}"

And considering our conversation so far:
{context_summary}

Generate 2-3 specific questions to learn more about:
1. Specific projects or initiatives they worked on
2. Their key responsibilities and contributions
3. Measurable results and impact (numbers, percentages, metrics)

Focus on extracting quantifiable achievements. Ask for specific numbers, percentages, timeframes, team sizes, etc.

Format each question on a new line starting with "Q:"."""
            
            result = self.agent(prompt)
            
            # Parse questions from result
            lines = str(result).strip().split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('Q:'):
                    question_text = line[2:].strip()
                    if question_text:
                        question = Question(
                            id=str(uuid.uuid4()),
                            text=question_text,
                            context=f"Experience: {experience}",
                            question_type="open",
                            related_section="experience",
                        )
                        questions.append(question)
            
            # If no questions were parsed, create a default one
            if not questions:
                question = Question(
                    id=str(uuid.uuid4()),
                    text=f"Can you tell me more about your work at {experience}? What were your main achievements and what impact did you have?",
                    context=f"Experience: {experience}",
                    question_type="open",
                    related_section="experience",
                )
                questions.append(question)
            
            logger.info(f"Generated {len(questions)} questions for experience")
            return questions
            
        except Exception as e:
            logger.error(f"Error generating questions: {e}")
            # Return a default question
            return [
                Question(
                    id=str(uuid.uuid4()),
                    text=f"Tell me about your experience with {experience}. What were your key achievements?",
                    context=f"Experience: {experience}",
                    question_type="open",
                    related_section="experience",
                )
            ]
    
    def _build_context_summary(self, conversation_history: List[Interaction]) -> str:
        """
        Build a summary of conversation history for context.
        
        Args:
            conversation_history: List of previous interactions
            
        Returns:
            Summary string
        """
        if not conversation_history:
            return "This is the start of our conversation."
        
        # Summarize last few interactions
        recent = conversation_history[-3:]  # Last 3 interactions
        summary_parts = []
        
        for interaction in recent:
            summary_parts.append(f"- Asked: {interaction.question.text[:100]}...")
            summary_parts.append(f"  Response: {interaction.response[:100]}...")
        
        return '\n'.join(summary_parts)
    
    def process_response(
        self,
        question: Question,
        response: str,
        conversation_history: List[Interaction],
    ) -> Dict[str, Any]:
        """
        Process a user response and extract information.
        
        Generates follow-up questions based on previous responses and
        maintains conversation context.
        
        Args:
            question: The question that was asked
            response: User's response
            conversation_history: Previous interactions
            
        Returns:
            Dictionary with extracted info and follow-up questions
            
        Requirements: 3.2, 3.4
        """
        extracted_info = {}
        follow_up_questions = []
        
        try:
            # Analyze the response for impact
            impact_analysis = self.tools.analyze_impact_score(response)
            extracted_info['impact_analysis'] = impact_analysis
            
            # Check if response needs more quantification
            if not impact_analysis.get('has_quantification', False):
                # Generate metric request question
                metric_question = Question(
                    id=str(uuid.uuid4()),
                    text=f"That's great! Can you quantify that? For example: How many users/people were affected? What percentage improvement? How much time or money was saved?",
                    context=f"Following up on: {response[:100]}",
                    question_type="metric",
                    related_section=question.related_section,
                )
                follow_up_questions.append(metric_question)
            
            # Use agent to extract structured information
            extraction_prompt = f"""From this response, extract any specific information about:
- Company names
- Job titles/roles
- Time periods (dates, durations)
- Technologies or tools used
- Metrics (numbers, percentages, amounts)
- Team sizes
- Project names

Response: {response}

Provide the extracted information in a structured format."""
            
            extraction_result = self.agent(extraction_prompt)
            extracted_info['structured_data'] = str(extraction_result)
            
            # Generate contextual follow-up based on conversation history
            if conversation_history:
                context_summary = self._build_context_summary(conversation_history)
                
                follow_up_prompt = f"""Based on our conversation:
{context_summary}

And this latest response:
{response}

Should I ask a follow-up question to get more details? If yes, what should I ask?
If no follow-up is needed, respond with "NO_FOLLOWUP"."""
                
                follow_up_result = self.agent(follow_up_prompt)
                
                if "NO_FOLLOWUP" not in str(follow_up_result).upper():
                    # Extract the follow-up question
                    follow_up_text = str(follow_up_result).strip()
                    if follow_up_text and len(follow_up_text) > 10:
                        follow_up_question = Question(
                            id=str(uuid.uuid4()),
                            text=follow_up_text,
                            context=f"Contextual follow-up based on: {response[:100]}",
                            question_type="clarification",
                            related_section=question.related_section,
                        )
                        follow_up_questions.append(follow_up_question)
            
            logger.info(f"Processed response, generated {len(follow_up_questions)} follow-ups")
            
        except Exception as e:
            logger.error(f"Error processing response: {e}")
            extracted_info['error'] = str(e)
        
        return {
            'extracted_info': extracted_info,
            'follow_up_questions': follow_up_questions,
        }
    
    def get_next_experience(self) -> Optional[str]:
        """
        Get the next prioritized experience to question about.
        
        Tracks current experience and moves sequentially through the list.
        
        Returns:
            Next experience description, or None if all are complete
            
        Requirements: 3.5
        """
        if self.current_experience_index >= len(self.prioritized_experiences):
            logger.info("All experiences have been processed")
            return None
        
        experience = self.prioritized_experiences[self.current_experience_index]
        self.current_experience_index += 1
        
        logger.info(f"Moving to experience {self.current_experience_index}/{len(self.prioritized_experiences)}")
        return experience
    
    def handle_error(self, error: Exception) -> str:
        """
        Handle errors during agent interactions.
        
        Provides actionable feedback for different error types.
        
        Args:
            error: The exception that occurred
            
        Returns:
            User-friendly error message with actionable feedback
            
        Requirements: 8.4
        """
        if isinstance(error, OllamaConnectionError):
            return f"""I'm having trouble connecting to Ollama. Please check:

1. Is Ollama running? Try: `ollama serve`
2. Is the correct model installed? Try: `ollama pull {self.config.model}`
3. Is Ollama accessible at {self.config.base_url}?

Error details: {str(error)}"""
        
        elif isinstance(error, AgentTimeoutError):
            return f"""The request timed out after {self.config.timeout} seconds.

This might happen if:
1. The model is taking too long to respond
2. The question is too complex
3. The model needs more resources

Try:
- Simplifying your response
- Increasing the timeout in configuration
- Using a smaller/faster model

Error details: {str(error)}"""
        
        elif "timeout" in str(error).lower():
            return f"""The operation timed out. This might be due to:

1. Ollama server being slow or overloaded
2. The model taking too long to generate a response
3. Network issues

Try waiting a moment and trying again, or restart Ollama.

Error details: {str(error)}"""
        
        else:
            return f"""An unexpected error occurred: {str(error)}

Please try:
1. Checking that Ollama is running properly
2. Verifying your configuration
3. Restarting the session if the problem persists

If the error continues, please report it with these details:
{type(error).__name__}: {str(error)}"""
    
    def chat(self, message: str) -> str:
        """
        Send a message to the agent and get a response.
        
        This is a simple interface for direct interaction with the agent.
        
        Args:
            message: User message
            
        Returns:
            Agent's response
            
        Raises:
            OllamaConnectionError: If Ollama connection fails
            AgentTimeoutError: If request times out
        """
        try:
            response = self.agent(message)
            return str(response)
        except Exception as e:
            error_message = self.handle_error(e)
            logger.error(f"Chat error: {e}")
            raise OllamaConnectionError(
                self.config.base_url,
                error_message
            )
