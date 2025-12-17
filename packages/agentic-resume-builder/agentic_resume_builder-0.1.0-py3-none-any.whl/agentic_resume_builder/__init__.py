"""
Agentic Resume Builder

A Python library that helps users create professional, impact-oriented resumes
through an AI-guided interactive process using Strands Agents SDK and Ollama.
"""

__version__ = "0.1.0"

from agentic_resume_builder.config import OllamaConfig, PDFStyle, ResumeConfig
from agentic_resume_builder.exceptions import (
    ResumeBuilderError,
    ResumeFileNotFoundError,
    OllamaConnectionError,
    MarkdownSyntaxError,
    PDFGenerationError,
    PDFConversionError,
    SessionNotFoundError,
    SessionCorruptedError,
    SessionLoadError,
)
from agentic_resume_builder.models import (
    PersonalInfo,
    Achievement,
    Experience,
    Education,
    Section,
    ResumeDocument,
    Resume,
    Question,
    Interaction,
    InteractiveSession,
)
from agentic_resume_builder.markdown_processor import (
    MarkdownProcessor,
    ValidationResult,
)
from agentic_resume_builder.document_converter import DocumentConverter
from agentic_resume_builder.pdf_generator import PDFGenerator
from agentic_resume_builder.resume_manager import ResumeManager
from agentic_resume_builder.templates import ResumeTemplates
from agentic_resume_builder.ollama_client import OllamaConnectionManager
from agentic_resume_builder.agent_tools import ResumeAgentTools
from agentic_resume_builder.resume_agent import ResumeAgent
from agentic_resume_builder.session_manager import SessionManager
from agentic_resume_builder import cli
from agentic_resume_builder import api

__all__ = [
    "__version__",
    # Config
    "OllamaConfig",
    "PDFStyle",
    "ResumeConfig",
    # Exceptions
    "ResumeBuilderError",
    "ResumeFileNotFoundError",
    "OllamaConnectionError",
    "MarkdownSyntaxError",
    "PDFGenerationError",
    "PDFConversionError",
    "SessionNotFoundError",
    "SessionCorruptedError",
    "SessionLoadError",
    # Models
    "PersonalInfo",
    "Achievement",
    "Experience",
    "Education",
    "Section",
    "ResumeDocument",
    "Resume",
    "Question",
    "Interaction",
    "InteractiveSession",
    # Markdown Processing
    "MarkdownProcessor",
    "ValidationResult",
    # Document Conversion
    "DocumentConverter",
    # PDF Generation
    "PDFGenerator",
    # Resume Management
    "ResumeManager",
    "ResumeTemplates",
    # Ollama Integration
    "OllamaConnectionManager",
    # Agent Tools
    "ResumeAgentTools",
    # Agent
    "ResumeAgent",
    # Session Management
    "SessionManager",
    # CLI
    "cli",
    # High-level API
    "api",
]
