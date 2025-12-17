"""
Document converter for converting various formats to Markdown.

This module handles conversion from PDF and other document formats to Markdown
using Microsoft's MarkItDown library, with normalization and cleaning.
"""

import logging
import re
from pathlib import Path
from typing import Optional

from markitdown import MarkItDown

from agentic_resume_builder.exceptions import (
    CorruptedFileError,
    PDFConversionError,
    ResumeFileNotFoundError,
    UnsupportedFormatError,
)

logger = logging.getLogger(__name__)


class DocumentConverter:
    """Converts documents from various formats to Markdown."""

    # Standard resume section names for normalization
    SECTION_MAPPINGS = {
        "work experience": "Experience",
        "professional experience": "Experience",
        "employment": "Experience",
        "employment history": "Experience",
        "work history": "Experience",
        "experience": "Experience",
        "education": "Education",
        "educational background": "Education",
        "academic background": "Education",
        "skills": "Skills",
        "technical skills": "Skills",
        "core competencies": "Skills",
        "competencies": "Skills",
        "summary": "Summary",
        "professional summary": "Summary",
        "profile": "Summary",
        "about": "Summary",
        "about me": "Summary",
    }

    def __init__(self):
        """Initialize the document converter with MarkItDown."""
        try:
            self.converter = MarkItDown()
            logger.info("DocumentConverter initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MarkItDown: {e}")
            raise PDFConversionError("", f"Failed to initialize converter: {str(e)}")

    def pdf_to_markdown(self, pdf_path: str) -> str:
        """
        Convert a PDF file to Markdown text.

        Args:
            pdf_path: Path to the PDF file to convert

        Returns:
            str: Markdown text extracted from the PDF

        Raises:
            ResumeFileNotFoundError: If the PDF file doesn't exist
            UnsupportedFormatError: If the file is not a PDF
            PDFConversionError: If conversion fails
            CorruptedFileError: If the PDF is corrupted or unreadable
        """
        path = Path(pdf_path)

        # Validate file exists
        if not path.exists():
            logger.error(f"PDF file not found: {pdf_path}")
            raise ResumeFileNotFoundError(pdf_path)

        # Validate file extension
        if path.suffix.lower() != ".pdf":
            logger.error(f"File is not a PDF: {pdf_path}")
            raise UnsupportedFormatError(pdf_path, path.suffix)

        # Validate file is readable
        if not path.is_file():
            logger.error(f"Path is not a file: {pdf_path}")
            raise PDFConversionError(pdf_path, "Path is not a file")

        try:
            logger.info(f"Converting PDF to Markdown: {pdf_path}")
            
            # Convert using MarkItDown
            result = self.converter.convert(str(path))
            
            if not result or not hasattr(result, 'text_content'):
                logger.error(f"Conversion returned empty or invalid result for: {pdf_path}")
                raise PDFConversionError(pdf_path, "Conversion returned empty result")
            
            markdown_text = result.text_content
            
            if not markdown_text or not markdown_text.strip():
                logger.error(f"Conversion produced empty text for: {pdf_path}")
                raise PDFConversionError(pdf_path, "Conversion produced empty text")
            
            logger.info(f"Successfully converted PDF to Markdown ({len(markdown_text)} characters)")
            return markdown_text

        except (ResumeFileNotFoundError, UnsupportedFormatError, PDFConversionError):
            # Re-raise our custom exceptions
            raise
        except PermissionError as e:
            logger.error(f"Permission denied reading PDF: {pdf_path}")
            raise PDFConversionError(pdf_path, f"Permission denied: {str(e)}")
        except Exception as e:
            # Check if it's a corrupted file error
            error_msg = str(e).lower()
            if any(keyword in error_msg for keyword in ["corrupt", "damaged", "invalid pdf", "malformed"]):
                logger.error(f"PDF file appears corrupted: {pdf_path}")
                raise CorruptedFileError(pdf_path)
            
            logger.error(f"Unexpected error converting PDF: {pdf_path} - {e}")
            raise PDFConversionError(pdf_path, str(e))

    def normalize_markdown(self, markdown_text: str) -> str:
        """
        Normalize and clean extracted Markdown text.

        This method:
        - Standardizes section headings to match resume structure
        - Removes PDF extraction artifacts
        - Cleans up formatting inconsistencies
        - Normalizes whitespace

        Args:
            markdown_text: Raw Markdown text from conversion

        Returns:
            str: Cleaned and normalized Markdown text
        """
        if not markdown_text:
            return ""

        logger.info("Normalizing Markdown text")
        
        # Start with the original text
        text = markdown_text

        # Remove common PDF artifacts
        text = self._remove_pdf_artifacts(text)

        # Standardize section headings
        text = self._standardize_section_headings(text)

        # Clean up whitespace
        text = self._normalize_whitespace(text)

        # Remove page numbers and headers/footers
        text = self._remove_page_artifacts(text)

        logger.info("Markdown normalization complete")
        return text

    def _remove_pdf_artifacts(self, text: str) -> str:
        """Remove common PDF extraction artifacts."""
        # Remove form feed characters
        text = text.replace("\f", "\n")
        
        # Remove excessive dashes/underscores (often from tables or lines)
        text = re.sub(r"[-_]{5,}", "", text)
        
        # Remove bullet point artifacts (sometimes PDFs have weird unicode bullets)
        text = re.sub(r"[•◦▪▫]", "-", text)
        
        # Remove zero-width spaces and other invisible characters
        text = re.sub(r"[\u200b\u200c\u200d\ufeff]", "", text)
        
        return text

    def _standardize_section_headings(self, text: str) -> str:
        """Standardize section headings to match resume structure."""
        lines = text.split("\n")
        normalized_lines = []

        for line in lines:
            # Check if line is a heading (starts with # or is all caps and short)
            if line.startswith("#"):
                # Extract heading text
                heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)
                if heading_match:
                    level = heading_match.group(1)
                    heading_text = heading_match.group(2).strip()
                    
                    # Normalize the heading text
                    normalized_heading = self._normalize_section_name(heading_text)
                    normalized_lines.append(f"{level} {normalized_heading}")
                else:
                    normalized_lines.append(line)
            
            # Check for all-caps headings (common in resumes)
            elif line.strip() and line.strip().isupper() and len(line.strip()) < 50:
                heading_text = line.strip()
                normalized_heading = self._normalize_section_name(heading_text)
                # Convert to level-2 heading
                normalized_lines.append(f"## {normalized_heading}")
            
            else:
                normalized_lines.append(line)

        return "\n".join(normalized_lines)

    def _normalize_section_name(self, section_name: str) -> str:
        """Normalize a section name to standard format."""
        # Convert to lowercase for matching
        section_lower = section_name.lower().strip()
        
        # Remove trailing colons
        section_lower = section_lower.rstrip(":")
        
        # Check if it matches a known section
        if section_lower in self.SECTION_MAPPINGS:
            return self.SECTION_MAPPINGS[section_lower]
        
        # If not found, return title case version
        return section_name.strip().title()

    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace in the text."""
        # Replace multiple spaces with single space
        text = re.sub(r" +", " ", text)
        
        # Replace multiple blank lines with maximum of 2
        text = re.sub(r"\n{4,}", "\n\n\n", text)
        
        # Remove trailing whitespace from lines
        lines = [line.rstrip() for line in text.split("\n")]
        text = "\n".join(lines)
        
        # Ensure file ends with single newline
        text = text.strip() + "\n"
        
        return text

    def _remove_page_artifacts(self, text: str) -> str:
        """Remove page numbers and common header/footer artifacts."""
        lines = text.split("\n")
        cleaned_lines = []

        for line in lines:
            line_stripped = line.strip()
            
            # Skip lines that look like page numbers
            if re.match(r"^Page\s+\d+$", line_stripped, re.IGNORECASE):
                continue
            if re.match(r"^\d+\s+of\s+\d+$", line_stripped, re.IGNORECASE):
                continue
            if re.match(r"^\d+$", line_stripped) and len(line_stripped) <= 3:
                # Might be a page number, but could also be a year or other number
                # Only skip if it's on its own line
                continue
            
            # Skip common header/footer patterns
            if re.match(r"^(confidential|draft|resume|curriculum vitae|cv)$", line_stripped, re.IGNORECASE):
                continue
            
            cleaned_lines.append(line)

        return "\n".join(cleaned_lines)
