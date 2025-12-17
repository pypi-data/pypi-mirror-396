"""
High-level API functions for the Agentic Resume Builder.

This module provides convenient functions for common workflows, supporting
both interactive and batch modes.
"""

import logging
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from agentic_resume_builder.config import OllamaConfig, PDFStyle, ResumeConfig
from agentic_resume_builder.models import InteractiveSession, Question, Resume
from agentic_resume_builder.pdf_generator import PDFGenerator
from agentic_resume_builder.resume_manager import ResumeManager

logger = logging.getLogger(__name__)


def create_resume(
    output_path: str,
    template: str = "professional",
    config: Optional[ResumeConfig] = None,
) -> Resume:
    """
    Create a new resume from a template.

    This is a convenience function that initializes a ResumeManager and creates
    a new resume file from the specified template.

    Args:
        output_path: Path where the resume Markdown file will be created
        template: Template type to use (professional, academic, technical)
        config: Optional configuration. If None, uses defaults.

    Returns:
        Resume: Newly created resume object

    Raises:
        InvalidPathError: If the path is invalid
        FileExistsError: If file exists at output_path
        ValueError: If template type is unknown

    Example:
        >>> from agentic_resume_builder.api import create_resume
        >>> resume = create_resume("my_resume.md", template="professional")
        >>> print(f"Created resume at {resume.file_path}")

    Requirements: 11.1, 11.4
    """
    logger.info(f"API: Creating new resume at {output_path}")
    manager = ResumeManager(config)
    return manager.create_new(output_path, template)


def load_resume(
    markdown_path: str,
    config: Optional[ResumeConfig] = None,
) -> Resume:
    """
    Load an existing Markdown resume file.

    This is a convenience function that initializes a ResumeManager and loads
    an existing resume from a Markdown file.

    Args:
        markdown_path: Path to the Markdown resume file
        config: Optional configuration. If None, uses defaults.

    Returns:
        Resume: Loaded resume object

    Raises:
        ResumeFileNotFoundError: If the file doesn't exist
        InvalidPathError: If the path is invalid
        MarkdownParseError: If the Markdown cannot be parsed

    Example:
        >>> from agentic_resume_builder.api import load_resume
        >>> resume = load_resume("existing_resume.md")
        >>> print(f"Loaded resume with {len(resume.document.experiences)} experiences")

    Requirements: 11.1, 11.4
    """
    logger.info(f"API: Loading resume from {markdown_path}")
    manager = ResumeManager(config)
    return manager.load_markdown(markdown_path)


def import_resume_from_pdf(
    pdf_path: str,
    output_path: str,
    config: Optional[ResumeConfig] = None,
) -> Resume:
    """
    Import a resume from PDF, convert to Markdown, and load.

    This is a convenience function that converts a PDF resume to Markdown format
    and loads it as a Resume object.

    Args:
        pdf_path: Path to the PDF file to import
        output_path: Path where the converted Markdown will be saved
        config: Optional configuration. If None, uses defaults.

    Returns:
        Resume: Loaded resume object from converted Markdown

    Raises:
        ResumeFileNotFoundError: If the PDF file doesn't exist
        PDFConversionError: If PDF conversion fails
        InvalidPathError: If paths are invalid
        FileExistsError: If output_path already exists

    Example:
        >>> from agentic_resume_builder.api import import_resume_from_pdf
        >>> resume = import_resume_from_pdf("old_resume.pdf", "converted_resume.md")
        >>> print(f"Imported resume from PDF")

    Requirements: 11.1, 11.4
    """
    logger.info(f"API: Importing resume from PDF {pdf_path} to {output_path}")
    manager = ResumeManager(config)
    return manager.import_from_pdf(pdf_path, output_path)


def save_resume(
    resume: Resume,
    create_backup: bool = True,
    config: Optional[ResumeConfig] = None,
) -> None:
    """
    Save a resume to its file path.

    This is a convenience function that saves the resume with atomic writes
    and optional backup.

    Args:
        resume: Resume object to save
        create_backup: Whether to create a backup of the existing file
        config: Optional configuration. If None, uses defaults.

    Raises:
        InvalidPathError: If the file path is invalid
        PermissionError: If write permission is denied

    Example:
        >>> from agentic_resume_builder.api import load_resume, save_resume
        >>> resume = load_resume("my_resume.md")
        >>> # Make modifications...
        >>> save_resume(resume)

    Requirements: 11.1, 11.4
    """
    logger.info(f"API: Saving resume to {resume.file_path}")
    manager = ResumeManager(config)
    manager.save(resume, create_backup)


def generate_pdf(
    resume: Resume,
    output_path: str,
    style: Optional[PDFStyle] = None,
    config: Optional[ResumeConfig] = None,
) -> None:
    """
    Generate a PDF from a resume.

    This is a convenience function that converts the resume Markdown to a
    professional PDF document.

    Args:
        resume: Resume object to convert
        output_path: Path where the PDF will be saved
        style: Optional PDF style configuration. If None, uses defaults.
        config: Optional configuration. If None, uses defaults.

    Raises:
        PDFGenerationError: If PDF generation fails
        InvalidPathError: If output path is invalid

    Example:
        >>> from agentic_resume_builder.api import load_resume, generate_pdf
        >>> resume = load_resume("my_resume.md")
        >>> generate_pdf(resume, "my_resume.pdf")

    Requirements: 11.1, 11.4
    """
    logger.info(f"API: Generating PDF at {output_path}")
    
    # Get style from config if not provided
    if style is None and config is not None:
        style = config.pdf_style
    
    # Initialize PDF generator
    pdf_gen = PDFGenerator(default_style=style or PDFStyle())
    
    # Render resume to markdown
    manager = ResumeManager(config)
    markdown_text = manager.markdown_processor.render(resume.document)
    
    # Generate PDF
    pdf_gen.generate(markdown_text, output_path, style)
    logger.info(f"PDF generated successfully at {output_path}")


def start_interactive_session(
    resume: Resume,
    config: Optional[ResumeConfig] = None,
    session_id: Optional[str] = None,
) -> InteractiveSession:
    """
    Start an interactive session with the AI agent.

    This function starts or resumes an interactive session where the AI agent
    guides the user through improving their resume.

    Args:
        resume: Resume to work with
        config: Optional configuration. If None, uses defaults.
        session_id: Optional session ID to resume an existing session

    Returns:
        InteractiveSession: The active session

    Raises:
        SessionNotFoundError: If session_id is provided but not found
        OllamaConnectionError: If Ollama is not available

    Example:
        >>> from agentic_resume_builder.api import load_resume, start_interactive_session
        >>> resume = load_resume("my_resume.md")
        >>> session = start_interactive_session(resume)
        >>> print(f"Session started: {session.session_id}")

    Requirements: 11.1, 11.4
    """
    logger.info("API: Starting interactive session")
    manager = ResumeManager(config)
    return manager.start_interactive_session(resume, session_id)


def process_response(
    session: InteractiveSession,
    resume: Resume,
    question: Question,
    response: str,
    config: Optional[ResumeConfig] = None,
) -> Dict[str, Any]:
    """
    Process a user response during an interactive session.

    This function handles the user's answer to a question, extracts information,
    and generates follow-up questions.

    Args:
        session: The active interactive session
        resume: The resume being worked on
        question: The question that was asked
        response: The user's response
        config: Optional configuration. If None, uses defaults.

    Returns:
        Dictionary containing:
            - next_question: Next question to ask (or None if done)
            - modifications: List of proposed modifications
            - session_complete: Whether the session is complete
            - extracted_info: Information extracted from the response

    Example:
        >>> result = process_response(session, resume, question, "I worked at...")
        >>> if result["next_question"]:
        >>>     print(result["next_question"].text)

    Requirements: 11.1, 11.4
    """
    logger.info("API: Processing user response")
    manager = ResumeManager(config)
    return manager.process_user_response(session, resume, question, response)


def pause_session(
    session: InteractiveSession,
    config: Optional[ResumeConfig] = None,
) -> None:
    """
    Pause an interactive session and save its state.

    Args:
        session: The session to pause
        config: Optional configuration. If None, uses defaults.

    Example:
        >>> from agentic_resume_builder.api import pause_session
        >>> pause_session(session)
        >>> print("Session paused. You can resume it later.")

    Requirements: 11.1, 11.4
    """
    logger.info("API: Pausing session")
    manager = ResumeManager(config)
    manager.pause_session(session)


def resume_session(
    session_id: str,
    resume: Resume,
    config: Optional[ResumeConfig] = None,
) -> InteractiveSession:
    """
    Resume a previously paused session.

    Args:
        session_id: ID of the session to resume
        resume: Resume to work with
        config: Optional configuration. If None, uses defaults.

    Returns:
        InteractiveSession: The resumed session

    Raises:
        SessionNotFoundError: If session not found

    Example:
        >>> from agentic_resume_builder.api import resume_session, load_resume
        >>> resume = load_resume("my_resume.md")
        >>> session = resume_session("session-id-123", resume)
        >>> print(f"Resumed session with {len(session.conversation_history)} interactions")

    Requirements: 11.1, 11.4
    """
    logger.info(f"API: Resuming session {session_id}")
    manager = ResumeManager(config)
    return manager.resume_session(session_id, resume)


def batch_update_resume(
    resume: Resume,
    updates: List[Dict[str, str]],
    config: Optional[ResumeConfig] = None,
) -> Resume:
    """
    Apply multiple updates to a resume in batch mode.

    This function allows programmatic updates to multiple sections of a resume
    without interactive prompts. Useful for automated workflows.

    Args:
        resume: Resume to update
        updates: List of update dictionaries, each containing:
            - section_name: Name of the section to update
            - content: New content for the section
        config: Optional configuration. If None, uses defaults.

    Returns:
        Resume: Updated resume object

    Example:
        >>> from agentic_resume_builder.api import load_resume, batch_update_resume
        >>> resume = load_resume("my_resume.md")
        >>> updates = [
        >>>     {"section_name": "Summary", "content": "Experienced developer..."},
        >>>     {"section_name": "Skills", "content": "Python, JavaScript, Go"},
        >>> ]
        >>> resume = batch_update_resume(resume, updates)

    Requirements: 11.1, 11.4
    """
    logger.info(f"API: Applying {len(updates)} batch updates")
    manager = ResumeManager(config)
    
    for update in updates:
        section_name = update.get("section_name")
        content = update.get("content")
        
        if not section_name or content is None:
            logger.warning(f"Skipping invalid update: {update}")
            continue
        
        try:
            # Update the section
            updated_document = manager.markdown_processor.update_section(
                resume.document,
                section_name,
                content,
            )
            resume.document = updated_document
            logger.info(f"Updated section: {section_name}")
        except Exception as e:
            logger.error(f"Error updating section {section_name}: {e}")
            # Continue with other updates
    
    # Save the resume
    manager.save(resume)
    logger.info("Batch updates complete")
    
    return resume


def complete_workflow(
    input_path: str,
    output_pdf_path: str,
    template: str = "professional",
    config: Optional[ResumeConfig] = None,
    interactive_callback: Optional[Callable[[Question], str]] = None,
) -> Resume:
    """
    Complete end-to-end workflow: create/load resume, optionally run interactive
    session, and generate PDF.

    This is a high-level convenience function that orchestrates the entire
    resume building process.

    Args:
        input_path: Path to existing resume (Markdown or PDF) or path for new resume
        output_pdf_path: Path where the final PDF will be saved
        template: Template to use if creating new resume
        config: Optional configuration. If None, uses defaults.
        interactive_callback: Optional callback function that receives a Question
            and returns the user's response. If None, skips interactive session.

    Returns:
        Resume: Final resume object

    Example:
        >>> from agentic_resume_builder.api import complete_workflow
        >>> 
        >>> def my_callback(question):
        >>>     print(question.text)
        >>>     return input("Your answer: ")
        >>> 
        >>> resume = complete_workflow(
        >>>     input_path="my_resume.md",
        >>>     output_pdf_path="my_resume.pdf",
        >>>     interactive_callback=my_callback
        >>> )

    Requirements: 11.1, 11.4
    """
    logger.info(f"API: Starting complete workflow from {input_path} to {output_pdf_path}")
    
    manager = ResumeManager(config)
    input_file = Path(input_path)
    
    # Determine how to load/create the resume
    if input_file.exists():
        if input_file.suffix.lower() == ".pdf":
            # Import from PDF
            temp_md = input_file.with_suffix(".md")
            resume = manager.import_from_pdf(str(input_file), str(temp_md))
        else:
            # Load existing Markdown
            resume = manager.load_markdown(str(input_file))
    else:
        # Create new resume
        resume = manager.create_new(str(input_file), template)
    
    logger.info(f"Resume loaded/created: {resume.file_path}")
    
    # Run interactive session if callback provided
    if interactive_callback:
        logger.info("Starting interactive session")
        session = manager.start_interactive_session(resume)
        
        # Get initial question
        current_question = getattr(session, "_pending_question", None)
        
        while current_question:
            # Get user response via callback
            user_response = interactive_callback(current_question)
            
            # Process the response
            result = manager.process_user_response(
                session, resume, current_question, user_response
            )
            
            # Check if session is complete
            if result.get("session_complete"):
                logger.info("Interactive session complete")
                break
            
            # Get next question
            current_question = result.get("next_question")
        
        # Save the session
        manager.pause_session(session)
    
    # Generate PDF
    generate_pdf(resume, output_pdf_path, config=config)
    logger.info(f"Workflow complete. PDF saved to {output_pdf_path}")
    
    return resume


def validate_resume(
    resume: Resume,
    config: Optional[ResumeConfig] = None,
) -> Dict[str, Any]:
    """
    Validate a resume and return validation results.

    This function checks the resume structure and content for completeness
    and correctness.

    Args:
        resume: Resume to validate
        config: Optional configuration. If None, uses defaults.

    Returns:
        Dictionary containing:
            - is_valid: Whether the resume is valid
            - errors: List of error messages
            - warnings: List of warning messages
            - suggestions: List of improvement suggestions

    Example:
        >>> from agentic_resume_builder.api import load_resume, validate_resume
        >>> resume = load_resume("my_resume.md")
        >>> result = validate_resume(resume)
        >>> if not result["is_valid"]:
        >>>     print("Errors:", result["errors"])

    Requirements: 11.1, 11.4
    """
    logger.info("API: Validating resume")
    manager = ResumeManager(config)
    validation_result = manager.markdown_processor.validate(resume.document)
    
    return {
        "is_valid": validation_result.is_valid,
        "errors": validation_result.errors,
        "warnings": validation_result.warnings,
        "suggestions": getattr(validation_result, "suggestions", []),
    }


def get_resume_statistics(resume: Resume) -> Dict[str, Any]:
    """
    Get statistics about a resume.

    This function analyzes the resume and returns useful statistics about
    its content.

    Args:
        resume: Resume to analyze

    Returns:
        Dictionary containing statistics:
            - num_experiences: Number of work experiences
            - num_education: Number of education entries
            - num_sections: Number of custom sections
            - total_achievements: Total number of achievements
            - has_metrics: Whether achievements contain metrics
            - completeness_score: Score from 0-100 indicating completeness

    Example:
        >>> from agentic_resume_builder.api import load_resume, get_resume_statistics
        >>> resume = load_resume("my_resume.md")
        >>> stats = get_resume_statistics(resume)
        >>> print(f"Completeness: {stats['completeness_score']}%")

    Requirements: 11.1, 11.4
    """
    logger.info("API: Calculating resume statistics")
    
    doc = resume.document
    
    # Count basic elements
    num_experiences = len(doc.experiences)
    num_education = len(doc.education)
    num_sections = len(doc.sections)
    
    # Count achievements
    total_achievements = sum(len(exp.achievements) for exp in doc.experiences)
    
    # Check for metrics in achievements
    has_metrics = False
    if total_achievements > 0:
        for exp in doc.experiences:
            for achievement in exp.achievements:
                if achievement.metrics:
                    has_metrics = True
                    break
            if has_metrics:
                break
    
    # Calculate completeness score
    completeness_score = 0
    if doc.personal_info and doc.personal_info.name:
        completeness_score += 20
    if doc.personal_info and doc.personal_info.email:
        completeness_score += 10
    if num_experiences > 0:
        completeness_score += 30
    if num_education > 0:
        completeness_score += 15
    if total_achievements > 0:
        completeness_score += 15
    if has_metrics:
        completeness_score += 10
    
    return {
        "num_experiences": num_experiences,
        "num_education": num_education,
        "num_sections": num_sections,
        "total_achievements": total_achievements,
        "has_metrics": has_metrics,
        "completeness_score": completeness_score,
    }
