"""
Configuration models for the Agentic Resume Builder.

This module defines configuration structures for Ollama, PDF styling,
and overall resume builder settings.
"""

from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field, field_validator

from agentic_resume_builder.exceptions import InvalidPathError, InvalidStyleError


class OllamaConfig(BaseModel):
    """Configuration for Ollama connection and model."""

    base_url: str = Field(
        default="http://localhost:11434", description="Ollama server base URL"
    )
    model: str = Field(default="llama3.2:3b", description="Model name to use")
    temperature: float = Field(
        default=0.7, ge=0.0, le=2.0, description="Temperature for generation"
    )
    timeout: int = Field(default=30, gt=0, description="Request timeout in seconds")


class PDFStyle(BaseModel):
    """Configuration for PDF styling."""

    font_family: str = Field(default="Helvetica", description="Font family name")
    font_size: int = Field(default=11, gt=0, description="Base font size")
    heading_font_size: int = Field(default=14, gt=0, description="Heading font size")
    line_spacing: float = Field(default=1.2, gt=0.0, description="Line spacing multiplier")
    margin_top: float = Field(default=2.0, ge=0.0, description="Top margin in cm")
    margin_bottom: float = Field(default=2.0, ge=0.0, description="Bottom margin in cm")
    margin_left: float = Field(default=2.0, ge=0.0, description="Left margin in cm")
    margin_right: float = Field(default=2.0, ge=0.0, description="Right margin in cm")
    color_primary: str = Field(default="#000000", description="Primary color (hex)")
    color_secondary: str = Field(default="#666666", description="Secondary color (hex)")
    color_accent: str = Field(default="#0066cc", description="Accent color (hex)")


class ResumeConfig(BaseModel):
    """Overall configuration for the resume builder."""

    ollama: OllamaConfig = Field(default_factory=OllamaConfig, description="Ollama configuration")
    pdf_style: PDFStyle = Field(default_factory=PDFStyle, description="PDF style configuration")
    template_dir: str = Field(default="./templates", description="Template directory path")
    session_dir: str = Field(default="./sessions", description="Session directory path")
    auto_save: bool = Field(default=True, description="Enable auto-save")
    save_interval: int = Field(default=60, gt=0, description="Auto-save interval in seconds")

    @classmethod
    def from_yaml(cls, yaml_path: str) -> "ResumeConfig":
        """Load configuration from a YAML file.

        Args:
            yaml_path: Path to the YAML configuration file

        Returns:
            ResumeConfig instance with loaded settings

        Raises:
            InvalidPathError: If the file doesn't exist
            InvalidStyleError: If configuration is invalid
        """
        path = Path(yaml_path)
        if not path.exists():
            raise InvalidPathError(yaml_path, "File does not exist")

        with open(path, "r") as f:
            data = yaml.safe_load(f) or {}

        # Parse Ollama config
        ollama_data = data.get("ollama", {})
        ollama_config = OllamaConfig(
            base_url=ollama_data.get("base_url", "http://localhost:11434"),
            model=ollama_data.get("model", "llama3.2:3b"),
            temperature=ollama_data.get("temperature", 0.7),
            timeout=ollama_data.get("timeout", 30),
        )

        # Parse PDF style config
        style_data = data.get("pdf_style", {})
        margins = style_data.get("margins", {})
        colors = style_data.get("colors", {})

        pdf_style = PDFStyle(
            font_family=style_data.get("font_family", "Helvetica"),
            font_size=style_data.get("font_size", 11),
            heading_font_size=style_data.get("heading_font_size", 14),
            line_spacing=style_data.get("line_spacing", 1.2),
            margin_top=margins.get("top", 2.0),
            margin_bottom=margins.get("bottom", 2.0),
            margin_left=margins.get("left", 2.0),
            margin_right=margins.get("right", 2.0),
            color_primary=colors.get("primary", "#000000"),
            color_secondary=colors.get("secondary", "#666666"),
            color_accent=colors.get("accent", "#0066cc"),
        )

        # Parse general settings
        templates = data.get("templates", {})
        sessions = data.get("sessions", {})

        return cls(
            ollama=ollama_config,
            pdf_style=pdf_style,
            template_dir=templates.get("directory", "./templates"),
            session_dir=sessions.get("directory", "./sessions"),
            auto_save=sessions.get("auto_save", True),
            save_interval=sessions.get("save_interval", 60),
        )

    def to_yaml(self, yaml_path: str) -> None:
        """Save configuration to a YAML file.

        Args:
            yaml_path: Path where to save the YAML configuration
        """
        data = {
            "ollama": {
                "base_url": self.ollama.base_url,
                "model": self.ollama.model,
                "temperature": self.ollama.temperature,
                "timeout": self.ollama.timeout,
            },
            "pdf_style": {
                "font_family": self.pdf_style.font_family,
                "font_size": self.pdf_style.font_size,
                "heading_font_size": self.pdf_style.heading_font_size,
                "line_spacing": self.pdf_style.line_spacing,
                "margins": {
                    "top": self.pdf_style.margin_top,
                    "bottom": self.pdf_style.margin_bottom,
                    "left": self.pdf_style.margin_left,
                    "right": self.pdf_style.margin_right,
                },
                "colors": {
                    "primary": self.pdf_style.color_primary,
                    "secondary": self.pdf_style.color_secondary,
                    "accent": self.pdf_style.color_accent,
                },
            },
            "templates": {
                "directory": self.template_dir,
            },
            "sessions": {
                "directory": self.session_dir,
                "auto_save": self.auto_save,
                "save_interval": self.save_interval,
            },
        }

        path = Path(yaml_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    @classmethod
    def from_yaml(cls, yaml_path: str) -> "ResumeConfig":
        """Load configuration from a YAML file.

        Args:
            yaml_path: Path to the YAML configuration file

        Returns:
            ResumeConfig instance with loaded settings

        Raises:
            InvalidPathError: If the file doesn't exist
            InvalidStyleError: If configuration is invalid
        """
        path = Path(yaml_path)
        if not path.exists():
            raise InvalidPathError(yaml_path, "File does not exist")

        with open(path, "r") as f:
            data = yaml.safe_load(f)

        # Parse Ollama config
        ollama_data = data.get("ollama", {})
        ollama_config = OllamaConfig(
            base_url=ollama_data.get("base_url", "http://localhost:11434"),
            model=ollama_data.get("model", "llama3.2:3b"),
            temperature=ollama_data.get("temperature", 0.7),
            timeout=ollama_data.get("timeout", 30),
        )

        # Parse PDF style config
        style_data = data.get("pdf_style", {})
        margins = style_data.get("margins", {})
        colors = style_data.get("colors", {})

        pdf_style = PDFStyle(
            font_family=style_data.get("font_family", "Helvetica"),
            font_size=style_data.get("font_size", 11),
            heading_font_size=style_data.get("heading_font_size", 14),
            line_spacing=style_data.get("line_spacing", 1.2),
            margin_top=margins.get("top", 2.0),
            margin_bottom=margins.get("bottom", 2.0),
            margin_left=margins.get("left", 2.0),
            margin_right=margins.get("right", 2.0),
            color_primary=colors.get("primary", "#000000"),
            color_secondary=colors.get("secondary", "#666666"),
            color_accent=colors.get("accent", "#0066cc"),
        )

        # Parse general settings
        templates = data.get("templates", {})
        sessions = data.get("sessions", {})

        return cls(
            ollama=ollama_config,
            pdf_style=pdf_style,
            template_dir=templates.get("directory", "./templates"),
            session_dir=sessions.get("directory", "./sessions"),
            auto_save=sessions.get("auto_save", True),
            save_interval=sessions.get("save_interval", 60),
        )

    def to_yaml(self, yaml_path: str) -> None:
        """Save configuration to a YAML file.

        Args:
            yaml_path: Path where to save the YAML configuration
        """
        data = {
            "ollama": {
                "base_url": self.ollama.base_url,
                "model": self.ollama.model,
                "temperature": self.ollama.temperature,
                "timeout": self.ollama.timeout,
            },
            "pdf_style": {
                "font_family": self.pdf_style.font_family,
                "font_size": self.pdf_style.font_size,
                "heading_font_size": self.pdf_style.heading_font_size,
                "line_spacing": self.pdf_style.line_spacing,
                "margins": {
                    "top": self.pdf_style.margin_top,
                    "bottom": self.pdf_style.margin_bottom,
                    "left": self.pdf_style.margin_left,
                    "right": self.pdf_style.margin_right,
                },
                "colors": {
                    "primary": self.pdf_style.color_primary,
                    "secondary": self.pdf_style.color_secondary,
                    "accent": self.pdf_style.color_accent,
                },
            },
            "templates": {
                "directory": self.template_dir,
            },
            "sessions": {
                "directory": self.session_dir,
                "auto_save": self.auto_save,
                "save_interval": self.save_interval,
            },
        }

        path = Path(yaml_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
