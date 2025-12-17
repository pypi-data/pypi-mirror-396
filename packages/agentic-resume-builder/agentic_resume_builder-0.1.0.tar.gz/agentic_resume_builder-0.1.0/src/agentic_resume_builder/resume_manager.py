"""
Resume Manager for the Agentic Resume Builder.

This module manages the lifecycle of resume documents including creation,
loading, saving, and PDF generation.
"""

import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from agentic_resume_builder.config import ResumeConfig
from agentic_resume_builder.document_converter import DocumentConverter
from agentic_resume_builder.exceptions import (
    InvalidPathError,
    ResumeFileNotFoundError,
)
from agentic_resume_builder.markdown_processor import MarkdownProcessor
from agentic_resume_builder.models import Resume, ResumeDocument
from agentic_resume_builder.templates import ResumeTemplates

logger = logging.getLogger(__name__)


class ResumeManager:
    """Manages resume document lifecycle and operations."""

    def __init__(self, config: Optional[ResumeConfig] = None):
        """
        Initialize the resume manager.

        Args:
            config: Configuration for the resume builder. If None, uses defaults.
        """
        self.config = config or ResumeConfig()
        self.markdown_processor = MarkdownProcessor()
        self.document_converter = DocumentConverter()
        logger.info("ResumeManager initialized")

    def create_new(self, path: str, template: str = "professional") -> Resume:
        """
        Create a new resume from a template.

        Args:
            path: Path where the resume Markdown file will be created
            template: Template type to use (professional, academic, technical)

        Returns:
            Resume: Newly created resume object

        Raises:
            InvalidPathError: If the path is invalid
            FileExistsError: If file exists and user doesn't confirm overwrite
            ValueError: If template type is unknown
        """
        logger.info(f"Creating new resume at {path} with template '{template}'")

        # Validate path
        file_path = Path(path)
        if not file_path.parent.exists():
            logger.error(f"Parent directory does not exist: {file_path.parent}")
            raise InvalidPathError(str(file_path.parent), "Parent directory does not exist")

        # Check if file already exists
        if file_path.exists():
            logger.warning(f"File already exists: {path}")
            # In a CLI context, this would prompt the user
            # For now, we raise an error that the caller can handle
            raise FileExistsError(
                f"File already exists: {path}. "
                "Please confirm if you want to overwrite it."
            )

        # Get template content
        try:
            template_content = ResumeTemplates.get_template(template)
        except ValueError as e:
            logger.error(f"Invalid template type: {template}")
            raise

        # Write template to file
        try:
            file_path.write_text(template_content, encoding="utf-8")
            logger.info(f"Template written to {path}")
        except Exception as e:
            logger.error(f"Failed to write template to {path}: {e}")
            raise InvalidPathError(path, f"Failed to write file: {str(e)}")

        # Parse the template into a Resume object
        try:
            document = self.markdown_processor.parse(template_content)
            resume = Resume(
                document=document,
                file_path=str(file_path.absolute()),
                last_modified=datetime.now(),
                version=1,
            )
            logger.info(f"Resume created successfully at {path}")
            return resume
        except Exception as e:
            logger.error(f"Failed to parse template: {e}")
            # Clean up the file if parsing failed
            if file_path.exists():
                file_path.unlink()
            raise

    def load_markdown(self, path: str) -> Resume:
        """
        Load an existing Markdown resume file.

        Args:
            path: Path to the Markdown resume file

        Returns:
            Resume: Loaded resume object

        Raises:
            ResumeFileNotFoundError: If the file doesn't exist
            InvalidPathError: If the path is invalid
            MarkdownParseError: If the Markdown cannot be parsed
        """
        logger.info(f"Loading resume from {path}")

        # Validate path
        file_path = Path(path)
        if not file_path.exists():
            logger.error(f"Resume file not found: {path}")
            raise ResumeFileNotFoundError(path)

        if not file_path.is_file():
            logger.error(f"Path is not a file: {path}")
            raise InvalidPathError(path, "Path is not a file")

        # Read file content
        try:
            markdown_text = file_path.read_text(encoding="utf-8")
            logger.info(f"Read {len(markdown_text)} characters from {path}")
        except Exception as e:
            logger.error(f"Failed to read file {path}: {e}")
            raise InvalidPathError(path, f"Failed to read file: {str(e)}")

        # Parse Markdown
        try:
            document = self.markdown_processor.parse(markdown_text)
            
            # Validate the document
            validation_result = self.markdown_processor.validate(document)
            if not validation_result.is_valid:
                logger.warning(f"Resume has validation errors: {validation_result.errors}")
            if validation_result.warnings:
                logger.info(f"Resume has warnings: {validation_result.warnings}")
            
            # Get file modification time
            last_modified = datetime.fromtimestamp(file_path.stat().st_mtime)
            
            resume = Resume(
                document=document,
                file_path=str(file_path.absolute()),
                last_modified=last_modified,
                version=1,
            )
            logger.info(f"Resume loaded successfully from {path}")
            return resume
        except Exception as e:
            logger.error(f"Failed to parse resume: {e}")
            raise

    def import_from_pdf(self, pdf_path: str, output_path: str) -> Resume:
        """
        Import a resume from PDF, convert to Markdown, and load.

        Args:
            pdf_path: Path to the PDF file to import
            output_path: Path where the converted Markdown will be saved

        Returns:
            Resume: Loaded resume object from converted Markdown

        Raises:
            ResumeFileNotFoundError: If the PDF file doesn't exist
            PDFConversionError: If PDF conversion fails
            InvalidPathError: If paths are invalid
        """
        logger.info(f"Importing resume from PDF: {pdf_path} -> {output_path}")

        # Convert PDF to Markdown
        try:
            markdown_text = self.document_converter.pdf_to_markdown(pdf_path)
            logger.info(f"PDF converted to Markdown ({len(markdown_text)} characters)")
        except Exception as e:
            logger.error(f"PDF conversion failed: {e}")
            raise

        # Normalize the Markdown
        try:
            normalized_markdown = self.document_converter.normalize_markdown(markdown_text)
            logger.info("Markdown normalized")
        except Exception as e:
            logger.error(f"Markdown normalization failed: {e}")
            # Continue with unnormalized markdown if normalization fails
            normalized_markdown = markdown_text

        # Validate output path
        output_file = Path(output_path)
        if not output_file.parent.exists():
            logger.error(f"Output directory does not exist: {output_file.parent}")
            raise InvalidPathError(str(output_file.parent), "Parent directory does not exist")

        # Check if output file already exists
        if output_file.exists():
            logger.warning(f"Output file already exists: {output_path}")
            raise FileExistsError(
                f"File already exists: {output_path}. "
                "Please confirm if you want to overwrite it."
            )

        # Save converted Markdown
        try:
            output_file.write_text(normalized_markdown, encoding="utf-8")
            logger.info(f"Converted Markdown saved to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save converted Markdown: {e}")
            raise InvalidPathError(output_path, f"Failed to write file: {str(e)}")

        # Load the converted Markdown as a Resume
        try:
            resume = self.load_markdown(output_path)
            logger.info(f"Resume imported successfully from {pdf_path}")
            return resume
        except Exception as e:
            logger.error(f"Failed to load converted resume: {e}")
            # Clean up the output file if loading failed
            if output_file.exists():
                output_file.unlink()
            raise

    def save(self, resume: Resume, create_backup: bool = True) -> None:
        """
        Save the resume to its file path with atomic writes and optional backup.

        Args:
            resume: Resume object to save
            create_backup: Whether to create a backup of the existing file

        Raises:
            InvalidPathError: If the file path is invalid
            PermissionError: If write permission is denied
        """
        logger.info(f"Saving resume to {resume.file_path}")

        file_path = Path(resume.file_path)

        # Create backup if file exists and backup is requested
        if create_backup and file_path.exists():
            backup_path = file_path.with_suffix(file_path.suffix + ".bak")
            try:
                shutil.copy2(file_path, backup_path)
                logger.info(f"Backup created at {backup_path}")
            except Exception as e:
                logger.warning(f"Failed to create backup: {e}")
                # Continue with save even if backup fails

        # Render the document to Markdown
        try:
            markdown_text = self.markdown_processor.render(resume.document)
            logger.info(f"Document rendered to Markdown ({len(markdown_text)} characters)")
        except Exception as e:
            logger.error(f"Failed to render document: {e}")
            raise

        # Write to a temporary file first (atomic write)
        temp_path = file_path.with_suffix(file_path.suffix + ".tmp")
        try:
            temp_path.write_text(markdown_text, encoding="utf-8")
            logger.info(f"Temporary file written: {temp_path}")
        except Exception as e:
            logger.error(f"Failed to write temporary file: {e}")
            raise InvalidPathError(str(temp_path), f"Failed to write file: {str(e)}")

        # Move temporary file to final location (atomic operation)
        try:
            temp_path.replace(file_path)
            logger.info(f"Resume saved successfully to {resume.file_path}")
        except Exception as e:
            logger.error(f"Failed to move temporary file: {e}")
            # Clean up temporary file
            if temp_path.exists():
                temp_path.unlink()
            raise InvalidPathError(str(file_path), f"Failed to save file: {str(e)}")

        # Update resume metadata
        resume.last_modified = datetime.now()
        resume.version += 1
        logger.info(f"Resume metadata updated (version {resume.version})")

    def start_interactive_session(
        self,
        resume: Resume,
        session_id: Optional[str] = None,
    ) -> "InteractiveSession":
        """
        Start an interactive session with the AI agent.

        This orchestrates the conversation between the user and the agent,
        coordinating between the Agent, SessionManager, and MarkdownProcessor.

        Args:
            resume: Resume to work with
            session_id: Optional session ID to resume an existing session

        Returns:
            InteractiveSession: The active session

        Raises:
            SessionNotFoundError: If session_id is provided but not found
            OllamaConnectionError: If Ollama is not available

        Requirements: 2.1, 2.2, 3.1, 3.2, 3.4, 9.2, 9.3
        """
        from agentic_resume_builder.agent_tools import ResumeAgentTools
        from agentic_resume_builder.models import InteractiveSession
        from agentic_resume_builder.resume_agent import ResumeAgent
        from agentic_resume_builder.session_manager import SessionManager

        logger.info("Starting interactive session")

        # Initialize session manager
        session_manager = SessionManager(self.config.session_dir)

        # Check if we're resuming an existing session
        if session_id:
            logger.info(f"Resuming session: {session_id}")
            session = session_manager.load_session(session_id)
            
            # Verify the resume path matches
            if session.resume_path != resume.file_path:
                logger.warning(
                    f"Session resume path mismatch: {session.resume_path} != {resume.file_path}"
                )
            
            # Update the resume reference
            session.resume_path = resume.file_path
            
            logger.info(
                f"Session resumed with {len(session.conversation_history)} previous interactions"
            )
        else:
            # Create a new session
            session_id = session_manager.generate_session_id()
            session = InteractiveSession(
                session_id=session_id,
                resume_path=resume.file_path,
                conversation_history=[],
                current_focus="general",
                started_at=datetime.now(),
                last_activity=datetime.now(),
                introductory_complete=False,
            )
            logger.info(f"Created new session: {session_id}")

        # Initialize agent tools
        agent_tools = ResumeAgentTools(self.markdown_processor)

        # Initialize the AI agent
        agent = ResumeAgent(
            ollama_config=self.config.ollama,
            agent_tools=agent_tools,
            resume=resume,
        )

        # Restore agent state from session
        agent.introductory_complete = session.introductory_complete
        agent.current_experience_index = 0

        # If this is a new session or introductory not complete, ask introductory question
        if not session.introductory_complete:
            logger.info("Asking introductory question")
            introductory_question = agent.ask_introductory_question(resume)
            
            # Store the question in the session for the caller to present
            # The actual interaction will be added when the user responds
            session.current_focus = "introductory"
            session._pending_question = introductory_question  # Store for reference
        else:
            logger.info("Introductory phase already complete")
            # Continue with experience questioning
            next_experience = agent.get_next_experience()
            if next_experience:
                session.current_focus = "experience"
                logger.info(f"Continuing with experience: {next_experience}")

        # Save the session
        if self.config.auto_save:
            session_manager.save_session(session)
            logger.info("Session saved")

        return session

    def process_user_response(
        self,
        session: "InteractiveSession",
        resume: Resume,
        question: "Question",
        response: str,
    ) -> Dict[str, Any]:
        """
        Process a user response during an interactive session.

        This handles the user's answer to a question, extracts information,
        generates follow-up questions, and updates the resume as needed.

        Args:
            session: The active interactive session
            resume: The resume being worked on
            question: The question that was asked
            response: The user's response

        Returns:
            Dictionary containing:
                - next_question: Next question to ask (or None if done)
                - modifications: List of proposed modifications
                - session_complete: Whether the session is complete

        Requirements: 3.2, 3.4
        """
        from agentic_resume_builder.agent_tools import ResumeAgentTools
        from agentic_resume_builder.models import Interaction
        from agentic_resume_builder.resume_agent import ResumeAgent
        from agentic_resume_builder.session_manager import SessionManager

        logger.info(f"Processing user response for question: {question.id}")

        # Initialize components
        session_manager = SessionManager(self.config.session_dir)
        agent_tools = ResumeAgentTools(self.markdown_processor)
        agent = ResumeAgent(
            ollama_config=self.config.ollama,
            agent_tools=agent_tools,
            resume=resume,
        )

        # Restore agent state
        agent.introductory_complete = session.introductory_complete

        # Process the response
        try:
            processing_result = agent.process_response(
                question=question,
                response=response,
                conversation_history=session.conversation_history,
            )

            # Create interaction record
            interaction = Interaction(
                question=question,
                response=response,
                timestamp=datetime.now(),
                extracted_info=processing_result.get("extracted_info", {}),
            )

            # Add to conversation history
            session.conversation_history.append(interaction)
            session.last_activity = datetime.now()

            # Handle introductory question completion
            if question.question_type == "introductory" and not session.introductory_complete:
                logger.info("Processing introductory response")
                
                # Extract experiences from the response
                experiences = agent.extract_experiences(response)
                
                # Prioritize experiences
                if experiences:
                    prioritized = agent.prioritize_experiences(experiences)
                    agent.prioritized_experiences = prioritized
                    
                    # Store in session metadata
                    interaction.extracted_info["prioritized_experiences"] = prioritized
                
                # Mark introductory as complete
                session.introductory_complete = True
                agent.introductory_complete = True

            # Determine next question
            next_question = None
            
            # Check for follow-up questions from processing
            follow_up_questions = processing_result.get("follow_up_questions", [])
            if follow_up_questions:
                next_question = follow_up_questions[0]
                logger.info(f"Generated follow-up question: {next_question.question_type}")
            
            # If no follow-up, move to next experience
            elif session.introductory_complete:
                # Get next experience to question about
                next_experience = agent.get_next_experience()
                
                if next_experience:
                    logger.info(f"Moving to next experience: {next_experience}")
                    session.current_focus = "experience"
                    
                    # Generate questions for this experience
                    questions = agent.generate_questions(
                        experience=next_experience,
                        conversation_history=session.conversation_history,
                    )
                    
                    if questions:
                        next_question = questions[0]
                else:
                    logger.info("All experiences processed, session complete")
                    session.current_focus = "complete"

            # Save session
            if self.config.auto_save:
                session_manager.save_session(session)
                logger.info("Session saved after processing response")

            return {
                "next_question": next_question,
                "modifications": [],  # Will be populated by modification approval workflow
                "session_complete": session.current_focus == "complete",
                "extracted_info": processing_result.get("extracted_info", {}),
            }

        except Exception as e:
            logger.error(f"Error processing response: {e}")
            error_message = agent.handle_error(e)
            return {
                "next_question": None,
                "modifications": [],
                "session_complete": False,
                "error": error_message,
            }

    def pause_session(self, session: "InteractiveSession") -> None:
        """
        Pause an interactive session and save its state.

        Args:
            session: The session to pause

        Requirements: 9.1
        """
        from agentic_resume_builder.session_manager import SessionManager

        logger.info(f"Pausing session: {session.session_id}")
        
        session_manager = SessionManager(self.config.session_dir)
        session.last_activity = datetime.now()
        session_manager.save_session(session)
        
        logger.info("Session paused and saved")

    def resume_session(self, session_id: str, resume: Resume) -> "InteractiveSession":
        """
        Resume a previously paused session.

        Args:
            session_id: ID of the session to resume
            resume: Resume to work with

        Returns:
            InteractiveSession: The resumed session

        Raises:
            SessionNotFoundError: If session not found

        Requirements: 9.2, 9.3
        """
        from agentic_resume_builder.session_manager import SessionManager

        logger.info(f"Resuming session: {session_id}")
        
        session_manager = SessionManager(self.config.session_dir)
        session = session_manager.load_session(session_id)
        
        # Update resume path if it changed
        session.resume_path = resume.file_path
        session.last_activity = datetime.now()
        
        logger.info(
            f"Session resumed with {len(session.conversation_history)} interactions"
        )
        
        return session

    def propose_modification(
        self,
        resume: Resume,
        section_name: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """
        Propose a modification to the resume without applying it.

        This shows the user what changes would be made before applying them.

        Args:
            resume: Current resume
            section_name: Section to modify
            new_content: Proposed new content

        Returns:
            Dictionary containing:
                - current_content: Current section content
                - proposed_content: Proposed new content
                - section_name: Name of the section

        Requirements: 4.4
        """
        logger.info(f"Proposing modification to section: {section_name}")

        # Get current section content
        current_section = self.markdown_processor.get_section(
            resume.document, section_name
        )

        current_content = ""
        if current_section:
            current_content = current_section.content

        return {
            "section_name": section_name,
            "current_content": current_content,
            "proposed_content": new_content,
        }

    def apply_modification(
        self,
        resume: Resume,
        section_name: str,
        new_content: str,
        approved: bool,
    ) -> Resume:
        """
        Apply or reject a proposed modification based on user approval.

        Args:
            resume: Current resume
            section_name: Section to modify
            new_content: New content to apply
            approved: Whether the user approved the modification

        Returns:
            Resume: Updated resume if approved, unchanged if rejected

        Requirements: 4.4, 4.5
        """
        if not approved:
            logger.info(f"Modification to {section_name} rejected by user")
            return resume

        logger.info(f"Applying approved modification to {section_name}")

        try:
            # Apply the modification
            updated_document = self.markdown_processor.update_section(
                resume.document,
                section_name,
                new_content,
            )

            # Update the resume
            resume.document = updated_document

            # Save the resume
            self.save(resume)

            logger.info(f"Modification to {section_name} applied and saved")
            return resume

        except Exception as e:
            logger.error(f"Error applying modification: {e}")
            raise

    def show_modification_diff(
        self,
        current_content: str,
        proposed_content: str,
    ) -> str:
        """
        Generate a human-readable diff of the proposed changes.

        Args:
            current_content: Current content
            proposed_content: Proposed new content

        Returns:
            Formatted diff string
        """
        if not current_content:
            return f"[NEW CONTENT]\n{proposed_content}"

        if not proposed_content:
            return f"[CONTENT WILL BE REMOVED]\n{current_content}"

        # Simple line-by-line comparison
        current_lines = current_content.split("\n")
        proposed_lines = proposed_content.split("\n")

        diff_lines = []
        diff_lines.append("=" * 60)
        diff_lines.append("CURRENT:")
        diff_lines.append("-" * 60)
        diff_lines.extend(current_lines)
        diff_lines.append("")
        diff_lines.append("=" * 60)
        diff_lines.append("PROPOSED:")
        diff_lines.append("-" * 60)
        diff_lines.extend(proposed_lines)
        diff_lines.append("=" * 60)

        return "\n".join(diff_lines)

    def batch_apply_modifications(
        self,
        resume: Resume,
        modifications: List[Dict[str, Any]],
    ) -> Resume:
        """
        Apply multiple modifications to the resume.

        Each modification should be a dict with:
            - section_name: str
            - content: str
            - approved: bool

        Args:
            resume: Current resume
            modifications: List of modification dicts

        Returns:
            Resume: Updated resume with all approved modifications

        Requirements: 4.4, 4.5
        """
        logger.info(f"Applying batch of {len(modifications)} modifications")

        for mod in modifications:
            if mod.get("approved", False):
                try:
                    resume = self.apply_modification(
                        resume=resume,
                        section_name=mod["section_name"],
                        new_content=mod["content"],
                        approved=True,
                    )
                except Exception as e:
                    logger.error(
                        f"Error applying modification to {mod['section_name']}: {e}"
                    )
                    # Continue with other modifications

        logger.info("Batch modifications complete")
        return resume
