"""
Custom exceptions for the Agentic Resume Builder.

This module defines the exception hierarchy used throughout the application
to provide clear and actionable error messages.
"""

from typing import Any, Dict, Optional


class ResumeBuilderError(Exception):
    """Base exception for all library errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


# File System Errors


class ResumeFileNotFoundError(ResumeBuilderError):
    """Raised when a resume file is not found."""

    def __init__(self, file_path: str):
        super().__init__(
            f"Resume file not found: {file_path}",
            details={"file_path": file_path},
        )


class ResumePermissionError(ResumeBuilderError):
    """Raised when permission is denied for a file operation."""

    def __init__(self, file_path: str, operation: str):
        super().__init__(
            f"Permission denied for {operation} on: {file_path}",
            details={"file_path": file_path, "operation": operation},
        )


class InvalidPathError(ResumeBuilderError):
    """Raised when a file path is invalid."""

    def __init__(self, path: str, reason: str = ""):
        super().__init__(
            f"Invalid path: {path}" + (f" - {reason}" if reason else ""),
            details={"path": path, "reason": reason},
        )


# Markdown Processing Errors


class MarkdownSyntaxError(ResumeBuilderError):
    """Raised when Markdown syntax is invalid."""

    def __init__(self, message: str, line: Optional[int] = None):
        details = {"line": line} if line is not None else {}
        super().__init__(f"Markdown syntax error: {message}", details=details)


class IncompleteSectionError(ResumeBuilderError):
    """Raised when required sections are missing or incomplete."""

    def __init__(self, missing_sections: list):
        super().__init__(
            f"Incomplete or missing sections: {', '.join(missing_sections)}",
            details={"missing_sections": missing_sections},
        )


class MarkdownParseError(ResumeBuilderError):
    """Raised when Markdown parsing fails."""

    def __init__(self, message: str, source: Optional[str] = None):
        details = {"source": source} if source else {}
        super().__init__(f"Failed to parse Markdown: {message}", details=details)


# Document Conversion Errors


class PDFConversionError(ResumeBuilderError):
    """Raised when PDF to Markdown conversion fails."""

    def __init__(self, pdf_path: str, reason: str = ""):
        super().__init__(
            f"Failed to convert PDF: {pdf_path}" + (f" - {reason}" if reason else ""),
            details={"pdf_path": pdf_path, "reason": reason},
        )


class UnsupportedFormatError(ResumeBuilderError):
    """Raised when a file format is not supported."""

    def __init__(self, file_path: str, format_type: str):
        super().__init__(
            f"Unsupported format '{format_type}' for file: {file_path}",
            details={"file_path": file_path, "format": format_type},
        )


class CorruptedFileError(ResumeBuilderError):
    """Raised when a file is corrupted or unreadable."""

    def __init__(self, file_path: str):
        super().__init__(
            f"File is corrupted or unreadable: {file_path}",
            details={"file_path": file_path},
        )


# AI Agent Errors


class OllamaConnectionError(ResumeBuilderError):
    """Raised when connection to Ollama fails."""

    def __init__(self, base_url: str, reason: str = ""):
        super().__init__(
            f"Failed to connect to Ollama at {base_url}" + (f": {reason}" if reason else ""),
            details={"base_url": base_url, "reason": reason},
        )


class ModelNotFoundError(ResumeBuilderError):
    """Raised when the specified model is not found."""

    def __init__(self, model_name: str, available_models: Optional[list] = None):
        details = {"model_name": model_name}
        if available_models:
            details["available_models"] = available_models
        super().__init__(
            f"Model not found: {model_name}",
            details=details,
        )


class AgentTimeoutError(ResumeBuilderError):
    """Raised when agent generation times out."""

    def __init__(self, timeout: int):
        super().__init__(
            f"Agent generation timed out after {timeout} seconds",
            details={"timeout": timeout},
        )


class AgentResponseError(ResumeBuilderError):
    """Raised when agent response format is invalid."""

    def __init__(self, message: str, response: Optional[str] = None):
        details = {"response": response} if response else {}
        super().__init__(f"Invalid agent response: {message}", details=details)


# PDF Generation Errors


class PDFGenerationError(ResumeBuilderError):
    """Raised when PDF generation fails."""

    def __init__(self, message: str, markdown_path: Optional[str] = None):
        details = {"markdown_path": markdown_path} if markdown_path else {}
        super().__init__(f"PDF generation failed: {message}", details=details)


class InvalidStyleError(ResumeBuilderError):
    """Raised when PDF style configuration is invalid."""

    def __init__(self, message: str, style_config: Optional[Dict[str, Any]] = None):
        details = {"style_config": style_config} if style_config else {}
        super().__init__(f"Invalid style configuration: {message}", details=details)


class FontNotFoundError(ResumeBuilderError):
    """Raised when a specified font is not available."""

    def __init__(self, font_name: str):
        super().__init__(
            f"Font not found: {font_name}",
            details={"font_name": font_name},
        )


# Session Errors


class SessionNotFoundError(ResumeBuilderError):
    """Raised when a session is not found."""

    def __init__(self, session_id: str):
        super().__init__(
            f"Session not found: {session_id}",
            details={"session_id": session_id},
        )


class SessionCorruptedError(ResumeBuilderError):
    """Raised when session data is corrupted."""

    def __init__(self, session_id: str, reason: str = ""):
        super().__init__(
            f"Session data corrupted: {session_id}" + (f" - {reason}" if reason else ""),
            details={"session_id": session_id, "reason": reason},
        )


class SessionLoadError(ResumeBuilderError):
    """Raised when session loading fails."""

    def __init__(self, session_id: str, reason: str = ""):
        super().__init__(
            f"Failed to load session: {session_id}" + (f" - {reason}" if reason else ""),
            details={"session_id": session_id, "reason": reason},
        )
