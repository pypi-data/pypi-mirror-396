"""
Command-line interface for the Agentic Resume Builder.

This module provides CLI commands for creating, loading, importing, and
managing resumes through an interactive AI-assisted process.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from agentic_resume_builder import __version__
from agentic_resume_builder.config import ResumeConfig
from agentic_resume_builder.exceptions import (
    ResumeBuilderError,
    ResumeFileNotFoundError,
    OllamaConnectionError,
    SessionNotFoundError,
)
from agentic_resume_builder.models import Resume, InteractiveSession
from agentic_resume_builder.pdf_generator import PDFGenerator
from agentic_resume_builder.resume_manager import ResumeManager
from agentic_resume_builder.session_manager import SessionManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path: Optional[str] = None, model: Optional[str] = None) -> ResumeConfig:
    """Load configuration from file or use defaults.
    
    Args:
        config_path: Optional path to configuration file
        model: Optional Ollama model name to override default
        
    Returns:
        ResumeConfig instance
    """
    if config_path:
        try:
            config = ResumeConfig.from_yaml(config_path)
        except Exception as e:
            logger.warning(f"Failed to load config from {config_path}: {e}")
            logger.info("Using default configuration")
            config = ResumeConfig()
    else:
        config = ResumeConfig()
    
    # Override model if specified
    if model:
        config.ollama.model = model
        logger.info(f"Using Ollama model: {model}")
    
    return config


def cmd_init(args: argparse.Namespace) -> int:
    """Handle the 'init' command to create a new resume from template.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        config = load_config(args.config, args.model)
        manager = ResumeManager(config)
        
        # Check if file exists
        if Path(args.output).exists() and not args.force:
            response = input(f"File '{args.output}' already exists. Overwrite? (y/N): ")
            if response.lower() != 'y':
                print("Operation cancelled.")
                return 0
        
        # Create new resume
        print(f"Creating new resume from '{args.template}' template...")
        resume = manager.create_new(args.output, template=args.template)
        
        print(f"✓ Resume created successfully at: {args.output}")
        print(f"\nNext steps:")
        print(f"  1. Edit the resume manually, or")
        print(f"  2. Start an interactive session: agentic-resume interactive {args.output}")
        
        return 0
        
    except FileExistsError as e:
        logger.error(str(e))
        return 1
    except ValueError as e:
        logger.error(f"Invalid template: {e}")
        return 1
    except ResumeBuilderError as e:
        logger.error(f"Failed to create resume: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


def cmd_load(args: argparse.Namespace) -> int:
    """Handle the 'load' command to load an existing Markdown resume.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        config = load_config(args.config, args.model)
        manager = ResumeManager(config)
        
        print(f"Loading resume from: {args.input}")
        resume = manager.load_markdown(args.input)
        
        print(f"✓ Resume loaded successfully")
        print(f"\nResume details:")
        print(f"  Path: {resume.file_path}")
        print(f"  Last modified: {resume.last_modified}")
        print(f"  Version: {resume.version}")
        
        # Show validation warnings if any
        validation = manager.markdown_processor.validate(resume.document)
        if not validation.is_valid:
            print(f"\n⚠ Validation errors:")
            for error in validation.errors:
                print(f"  - {error}")
        
        if validation.warnings:
            print(f"\n⚠ Warnings:")
            for warning in validation.warnings:
                print(f"  - {warning}")
        
        print(f"\nNext steps:")
        print(f"  1. Start an interactive session: agentic-resume interactive {args.input}")
        print(f"  2. Generate PDF: agentic-resume generate {args.input} output.pdf")
        
        return 0
        
    except ResumeFileNotFoundError as e:
        logger.error(f"Resume file not found: {e}")
        return 1
    except ResumeBuilderError as e:
        logger.error(f"Failed to load resume: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


def cmd_import(args: argparse.Namespace) -> int:
    """Handle the 'import' command to convert PDF to Markdown.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        config = load_config(args.config, args.model)
        manager = ResumeManager(config)
        
        # Check if output file exists
        if Path(args.output).exists() and not args.force:
            response = input(f"File '{args.output}' already exists. Overwrite? (y/N): ")
            if response.lower() != 'y':
                print("Operation cancelled.")
                return 0
        
        print(f"Importing resume from PDF: {args.input}")
        print("This may take a moment...")
        
        resume = manager.import_from_pdf(args.input, args.output)
        
        print(f"✓ Resume imported successfully")
        print(f"  PDF: {args.input}")
        print(f"  Markdown: {args.output}")
        
        # Show validation warnings
        validation = manager.markdown_processor.validate(resume.document)
        if validation.warnings:
            print(f"\n⚠ Note: The imported resume may need manual cleanup:")
            for warning in validation.warnings[:5]:  # Show first 5 warnings
                print(f"  - {warning}")
        
        print(f"\nNext steps:")
        print(f"  1. Review and edit: {args.output}")
        print(f"  2. Start interactive session: agentic-resume interactive {args.output}")
        
        return 0
        
    except ResumeFileNotFoundError as e:
        logger.error(f"PDF file not found: {e}")
        return 1
    except ResumeBuilderError as e:
        logger.error(f"Failed to import resume: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


def cmd_interactive(args: argparse.Namespace) -> int:
    """Handle the 'interactive' command to start AI-assisted session.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        config = load_config(args.config, args.model)
        manager = ResumeManager(config)
        
        # Load the resume
        print(f"Loading resume: {args.resume}")
        resume = manager.load_markdown(args.resume)
        
        print(f"✓ Resume loaded")
        print(f"\nStarting interactive session...")
        print(f"The AI assistant will help you create an impact-oriented resume.")
        print(f"Type 'quit' or 'exit' at any time to save and exit.\n")
        
        # Start interactive session
        session = manager.start_interactive_session(resume)
        
        # Check if there's a pending introductory question
        if hasattr(session, '_pending_question'):
            question = session._pending_question
            print(f"\n{question.text}\n")
            
            # Get user response
            response = input("Your answer: ").strip()
            
            if response.lower() in ['quit', 'exit']:
                manager.pause_session(session)
                print(f"\n✓ Session saved. Resume later with: agentic-resume resume {session.session_id}")
                return 0
            
            # Process the response
            result = manager.process_user_response(session, resume, question, response)
            
            # Continue with follow-up questions
            while result.get('next_question') and not result.get('session_complete'):
                next_q = result['next_question']
                print(f"\n{next_q.text}\n")
                
                response = input("Your answer: ").strip()
                
                if response.lower() in ['quit', 'exit']:
                    manager.pause_session(session)
                    print(f"\n✓ Session saved. Resume later with: agentic-resume resume {session.session_id}")
                    return 0
                
                result = manager.process_user_response(session, resume, next_q, response)
        
        # Session complete
        print(f"\n✓ Interactive session complete!")
        print(f"  Resume updated: {resume.file_path}")
        print(f"\nNext steps:")
        print(f"  1. Review your resume: {resume.file_path}")
        print(f"  2. Generate PDF: agentic-resume generate {resume.file_path} output.pdf")
        
        return 0
        
    except ResumeFileNotFoundError as e:
        logger.error(f"Resume file not found: {e}")
        return 1
    except OllamaConnectionError as e:
        logger.error(f"Cannot connect to Ollama: {e}")
        logger.error("Make sure Ollama is installed and running.")
        logger.error("Visit: https://ollama.ai for installation instructions")
        return 1
    except ResumeBuilderError as e:
        logger.error(f"Session error: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n\nSession interrupted. Progress has been saved.")
        return 0
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


def cmd_generate(args: argparse.Namespace) -> int:
    """Handle the 'generate' command to create PDF from Markdown.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        config = load_config(args.config, args.model)
        manager = ResumeManager(config)
        
        # Load the resume
        print(f"Loading resume: {args.input}")
        resume = manager.load_markdown(args.input)
        
        # Load custom style if provided
        style = None
        if args.style:
            print(f"Loading custom style: {args.style}")
            pdf_gen = PDFGenerator()
            style = pdf_gen.load_style(args.style)
        
        # Check if output file exists
        if Path(args.output).exists() and not args.force:
            response = input(f"File '{args.output}' already exists. Overwrite? (y/N): ")
            if response.lower() != 'y':
                print("Operation cancelled.")
                return 0
        
        # Generate PDF
        print(f"Generating PDF...")
        pdf_gen = PDFGenerator(default_style=config.pdf_style)
        
        # Render markdown to text
        markdown_text = manager.markdown_processor.render(resume.document)
        
        # Generate PDF
        pdf_gen.generate(markdown_text, args.output, style=style)
        
        print(f"✓ PDF generated successfully: {args.output}")
        
        return 0
        
    except ResumeFileNotFoundError as e:
        logger.error(f"Resume file not found: {e}")
        return 1
    except ResumeBuilderError as e:
        logger.error(f"Failed to generate PDF: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


def cmd_resume(args: argparse.Namespace) -> int:
    """Handle the 'resume' command to continue a saved session.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        config = load_config(args.config, args.model)
        manager = ResumeManager(config)
        session_manager = SessionManager(config.session_dir)
        
        # Load the session
        print(f"Loading session: {args.session_id}")
        session = session_manager.load_session(args.session_id)
        
        # Load the resume
        print(f"Loading resume: {session.resume_path}")
        resume = manager.load_markdown(session.resume_path)
        
        print(f"✓ Session resumed")
        print(f"  Started: {session.started_at}")
        print(f"  Last activity: {session.last_activity}")
        print(f"  Interactions: {len(session.conversation_history)}")
        print(f"\nContinuing where you left off...\n")
        
        # Determine what to ask next
        if not session.introductory_complete:
            # Still in introductory phase
            from agentic_resume_builder.agent_tools import ResumeAgentTools
            from agentic_resume_builder.resume_agent import ResumeAgent
            
            agent_tools = ResumeAgentTools(manager.markdown_processor)
            agent = ResumeAgent(
                ollama_config=config.ollama,
                agent_tools=agent_tools,
                resume=resume,
            )
            
            question = agent.ask_introductory_question(resume)
            print(f"{question.text}\n")
            
            response = input("Your answer: ").strip()
            
            if response.lower() in ['quit', 'exit']:
                manager.pause_session(session)
                print(f"\n✓ Session saved.")
                return 0
            
            result = manager.process_user_response(session, resume, question, response)
            
            # Continue with follow-up questions
            while result.get('next_question') and not result.get('session_complete'):
                next_q = result['next_question']
                print(f"\n{next_q.text}\n")
                
                response = input("Your answer: ").strip()
                
                if response.lower() in ['quit', 'exit']:
                    manager.pause_session(session)
                    print(f"\n✓ Session saved.")
                    return 0
                
                result = manager.process_user_response(session, resume, next_q, response)
        
        # Session complete
        print(f"\n✓ Session complete!")
        print(f"  Resume: {resume.file_path}")
        print(f"\nNext steps:")
        print(f"  1. Review your resume: {resume.file_path}")
        print(f"  2. Generate PDF: agentic-resume generate {resume.file_path} output.pdf")
        
        return 0
        
    except SessionNotFoundError as e:
        logger.error(f"Session not found: {e}")
        logger.info(f"\nAvailable sessions:")
        session_manager = SessionManager(config.session_dir)
        sessions = session_manager.list_sessions()
        if sessions:
            for sid in sessions:
                print(f"  - {sid}")
        else:
            print(f"  (no saved sessions)")
        return 1
    except ResumeFileNotFoundError as e:
        logger.error(f"Resume file not found: {e}")
        return 1
    except OllamaConnectionError as e:
        logger.error(f"Cannot connect to Ollama: {e}")
        return 1
    except ResumeBuilderError as e:
        logger.error(f"Session error: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n\nSession interrupted. Progress has been saved.")
        return 0
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog='agentic-resume',
        description='AI-powered resume builder using Ollama and Strands Agents',
        epilog='''
Quick Start:
  1. Create a new resume:     agentic-resume init my_resume.md
  2. Start interactive mode:  agentic-resume interactive my_resume.md
  3. Generate PDF:            agentic-resume generate my_resume.md output.pdf

For detailed help on any command, use:
  agentic-resume <command> --help

For more information, visit: https://github.com/yourusername/agentic-agentic-resume
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        metavar='PATH',
        help='Path to configuration file (YAML)'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        metavar='MODEL',
        help='Ollama model to use (default: llama3.2:3b). Examples: llama3.2:3b, mistral, codellama'
    )
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(
        title='commands',
        description='Available commands',
        dest='command',
        required=True
    )
    
    # Init command
    parser_init = subparsers.add_parser(
        'init',
        help='Create a new resume from template',
        description='Initialize a new resume project from a template',
        epilog='''
Examples:
  # Create a new professional resume
  agentic-resume init my_resume.md
  
  # Create an academic resume
  agentic-resume init my_resume.md --template academic
  
  # Force overwrite existing file
  agentic-resume init my_resume.md --force
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser_init.add_argument(
        'output',
        type=str,
        help='Output path for the new resume Markdown file'
    )
    parser_init.add_argument(
        '--template',
        type=str,
        default='professional',
        choices=['professional', 'academic', 'technical'],
        help='Template type to use (default: professional)'
    )
    parser_init.add_argument(
        '--force',
        action='store_true',
        help='Overwrite existing file without confirmation'
    )
    parser_init.set_defaults(func=cmd_init)
    
    # Load command
    parser_load = subparsers.add_parser(
        'load',
        help='Load an existing Markdown resume',
        description='Load and validate an existing Markdown resume file',
        epilog='''
Examples:
  # Load and validate a resume
  agentic-resume load my_resume.md
  
  # Load with custom config
  agentic-resume --config config.yaml load my_resume.md
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser_load.add_argument(
        'input',
        type=str,
        help='Path to the Markdown resume file'
    )
    parser_load.set_defaults(func=cmd_load)
    
    # Import command
    parser_import = subparsers.add_parser(
        'import',
        help='Import resume from PDF',
        description='Convert a PDF resume to Markdown format',
        epilog='''
Examples:
  # Import a PDF resume
  agentic-resume import old_resume.pdf my_resume.md
  
  # Import and force overwrite
  agentic-resume import old_resume.pdf my_resume.md --force
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser_import.add_argument(
        'input',
        type=str,
        help='Path to the PDF file to import'
    )
    parser_import.add_argument(
        'output',
        type=str,
        help='Output path for the converted Markdown file'
    )
    parser_import.add_argument(
        '--force',
        action='store_true',
        help='Overwrite existing file without confirmation'
    )
    parser_import.set_defaults(func=cmd_import)
    
    # Interactive command
    parser_interactive = subparsers.add_parser(
        'interactive',
        help='Start AI-assisted interactive session',
        description='Start an interactive session with the AI assistant to build your resume',
        epilog='''
Examples:
  # Start interactive session
  agentic-resume interactive my_resume.md
  
  # Use custom Ollama model
  agentic-resume --config config.yaml interactive my_resume.md
  
Note: Requires Ollama to be installed and running.
Visit https://ollama.ai for installation instructions.
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser_interactive.add_argument(
        'resume',
        type=str,
        help='Path to the resume Markdown file'
    )
    parser_interactive.set_defaults(func=cmd_interactive)
    
    # Generate command
    parser_generate = subparsers.add_parser(
        'generate',
        help='Generate PDF from Markdown resume',
        description='Convert a Markdown resume to a professional PDF document',
        epilog='''
Examples:
  # Generate PDF with default styling
  agentic-resume generate my_resume.md output.pdf
  
  # Generate with custom style
  agentic-resume generate my_resume.md output.pdf --style custom_style.yaml
  
  # Force overwrite existing PDF
  agentic-resume generate my_resume.md output.pdf --force
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser_generate.add_argument(
        'input',
        type=str,
        help='Path to the Markdown resume file'
    )
    parser_generate.add_argument(
        'output',
        type=str,
        help='Output path for the PDF file'
    )
    parser_generate.add_argument(
        '--style',
        type=str,
        metavar='PATH',
        help='Path to custom style configuration (YAML)'
    )
    parser_generate.add_argument(
        '--force',
        action='store_true',
        help='Overwrite existing file without confirmation'
    )
    parser_generate.set_defaults(func=cmd_generate)
    
    # Resume command
    parser_resume = subparsers.add_parser(
        'resume',
        help='Continue a saved session',
        description='Resume a previously saved interactive session',
        epilog='''
Examples:
  # Resume a saved session
  agentic-resume resume abc123-session-id
  
  # List available sessions (if session not found, they will be shown)
  agentic-resume resume invalid-id
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser_resume.add_argument(
        'session_id',
        type=str,
        help='Session ID to resume'
    )
    parser_resume.set_defaults(func=cmd_resume)
    
    return parser


def main() -> int:
    """Main entry point for the CLI.
    
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = create_parser()
    args = parser.parse_args()
    
    # Call the appropriate command function
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
