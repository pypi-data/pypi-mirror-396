"""
PDF Generator for the Agentic Resume Builder.

This module handles conversion of Markdown resumes to professional PDF documents
with customizable styling.
"""

import logging
import warnings
from pathlib import Path
from typing import Optional

import markdown
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

from agentic_resume_builder.config import PDFStyle
from agentic_resume_builder.exceptions import (
    PDFGenerationError,
    InvalidPathError,
    InvalidStyleError,
)

logger = logging.getLogger(__name__)


class PDFGenerator:
    """Generates professional PDF documents from Markdown resumes."""

    def __init__(self, default_style: Optional[PDFStyle] = None):
        """Initialize PDF generator with default style.

        Args:
            default_style: Default PDF style configuration. If None, uses PDFStyle defaults.
        """
        self.default_style = default_style or PDFStyle()
        self.font_config = FontConfiguration()
        logger.info("PDFGenerator initialized with default style")

    def markdown_to_html(self, markdown_text: str, style: Optional[PDFStyle] = None) -> str:
        """Convert Markdown text to styled HTML.

        Args:
            markdown_text: Markdown content to convert
            style: PDF style configuration. If None, uses default style.

        Returns:
            HTML string with embedded CSS styling

        Raises:
            PDFGenerationError: If conversion fails
        """
        try:
            # Use provided style or default
            pdf_style = style or self.default_style

            # Convert Markdown to HTML
            html_content = markdown.markdown(
                markdown_text,
                extensions=[
                    'extra',  # Tables, fenced code blocks, etc.
                    'nl2br',  # Newline to <br>
                    'sane_lists',  # Better list handling
                ]
            )

            # Generate CSS from style configuration
            css = self._generate_css(pdf_style)

            # Wrap in complete HTML document
            html_document = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        {css}
    </style>
</head>
<body>
    {html_content}
</body>
</html>"""

            logger.debug("Successfully converted Markdown to HTML")
            return html_document

        except Exception as e:
            logger.error(f"Failed to convert Markdown to HTML: {e}")
            raise PDFGenerationError(f"Markdown to HTML conversion failed: {e}")

    def _generate_css(self, style: PDFStyle) -> str:
        """Generate CSS from PDFStyle configuration.

        Args:
            style: PDF style configuration

        Returns:
            CSS string
        """
        css = f"""
        @page {{
            margin: {style.margin_top}cm {style.margin_right}cm {style.margin_bottom}cm {style.margin_left}cm;
            size: A4;
        }}

        body {{
            font-family: {style.font_family}, Arial, sans-serif;
            font-size: {style.font_size}pt;
            line-height: {style.line_spacing};
            color: {style.color_primary};
            margin: 0;
            padding: 0;
        }}

        h1 {{
            font-size: {style.heading_font_size + 6}pt;
            color: {style.color_primary};
            margin-top: 0;
            margin-bottom: 0.5em;
            font-weight: bold;
            page-break-after: avoid;
        }}

        h2 {{
            font-size: {style.heading_font_size + 2}pt;
            color: {style.color_primary};
            margin-top: 1em;
            margin-bottom: 0.5em;
            font-weight: bold;
            border-bottom: 2px solid {style.color_accent};
            padding-bottom: 0.2em;
            page-break-after: avoid;
        }}

        h3 {{
            font-size: {style.heading_font_size}pt;
            color: {style.color_secondary};
            margin-top: 0.8em;
            margin-bottom: 0.4em;
            font-weight: bold;
            page-break-after: avoid;
        }}

        h4, h5, h6 {{
            font-size: {style.font_size + 1}pt;
            color: {style.color_secondary};
            margin-top: 0.6em;
            margin-bottom: 0.3em;
            font-weight: bold;
            page-break-after: avoid;
        }}

        p {{
            margin-top: 0.3em;
            margin-bottom: 0.3em;
            orphans: 2;
            widows: 2;
        }}

        ul, ol {{
            margin-top: 0.3em;
            margin-bottom: 0.3em;
            padding-left: 1.5em;
        }}

        li {{
            margin-bottom: 0.2em;
        }}

        strong, b {{
            font-weight: bold;
            color: {style.color_primary};
        }}

        em, i {{
            font-style: italic;
        }}

        a {{
            color: {style.color_accent};
            text-decoration: none;
        }}

        a:hover {{
            text-decoration: underline;
        }}

        code {{
            font-family: 'Courier New', monospace;
            background-color: #f4f4f4;
            padding: 0.1em 0.3em;
            border-radius: 3px;
            font-size: {style.font_size - 1}pt;
        }}

        pre {{
            background-color: #f4f4f4;
            padding: 0.5em;
            border-radius: 3px;
            overflow-x: auto;
            page-break-inside: avoid;
        }}

        pre code {{
            background-color: transparent;
            padding: 0;
        }}

        table {{
            border-collapse: collapse;
            width: 100%;
            margin-top: 0.5em;
            margin-bottom: 0.5em;
            page-break-inside: avoid;
        }}

        th, td {{
            border: 1px solid {style.color_secondary};
            padding: 0.3em 0.5em;
            text-align: left;
        }}

        th {{
            background-color: #f4f4f4;
            font-weight: bold;
        }}

        blockquote {{
            margin-left: 1em;
            padding-left: 1em;
            border-left: 3px solid {style.color_accent};
            color: {style.color_secondary};
        }}

        hr {{
            border: none;
            border-top: 1px solid {style.color_secondary};
            margin: 1em 0;
        }}

        /* Prevent page breaks inside important elements */
        h1, h2, h3, h4, h5, h6 {{
            page-break-inside: avoid;
        }}

        /* Keep headings with following content */
        h1, h2, h3, h4, h5, h6 {{
            page-break-after: avoid;
        }}
        """

        return css


    def generate(
        self,
        markdown_text: str,
        output_path: str,
        style: Optional[PDFStyle] = None
    ) -> None:
        """Generate PDF from Markdown text.

        Args:
            markdown_text: Markdown content to convert
            output_path: Path where to save the PDF file
            style: PDF style configuration. If None, uses default style.

        Raises:
            InvalidPathError: If output path is invalid
            PDFGenerationError: If PDF generation fails
        """
        # Validate output path
        self._validate_output_path(output_path)

        # Use provided style or default
        pdf_style = style or self.default_style

        # Validate style configuration
        validated_style = self._validate_style(pdf_style)

        try:
            # Convert Markdown to HTML
            html_content = self.markdown_to_html(markdown_text, validated_style)

            # Generate PDF from HTML
            logger.info(f"Generating PDF at: {output_path}")
            
            # Create HTML object
            html_obj = HTML(string=html_content)
            
            # Generate CSS
            css_string = self._generate_css(validated_style)
            css_obj = CSS(string=css_string, font_config=self.font_config)
            
            # Write PDF to file
            html_obj.write_pdf(
                output_path,
                stylesheets=[css_obj],
                font_config=self.font_config
            )

            logger.info(f"Successfully generated PDF: {output_path}")

        except InvalidPathError:
            raise
        except PDFGenerationError:
            raise
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            raise PDFGenerationError(f"Failed to generate PDF: {e}")

    def _validate_output_path(self, output_path: str) -> None:
        """Validate output path before generation.

        Args:
            output_path: Path to validate

        Raises:
            InvalidPathError: If path is invalid
        """
        if not output_path or not output_path.strip():
            raise InvalidPathError(output_path, "Output path cannot be empty")

        path = Path(output_path)

        # Check if parent directory exists or can be created
        parent_dir = path.parent
        if not parent_dir.exists():
            try:
                parent_dir.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Created parent directory: {parent_dir}")
            except Exception as e:
                raise InvalidPathError(
                    output_path,
                    f"Cannot create parent directory: {e}"
                )

        # Check if we can write to the location
        if path.exists() and not path.is_file():
            raise InvalidPathError(
                output_path,
                "Path exists but is not a file"
            )

        # Ensure .pdf extension
        if not output_path.lower().endswith('.pdf'):
            logger.warning(f"Output path does not have .pdf extension: {output_path}")

    def _validate_style(self, style: PDFStyle) -> PDFStyle:
        """Validate PDFStyle configuration and apply fallbacks.

        Args:
            style: PDF style configuration to validate

        Returns:
            Validated PDFStyle with fallbacks applied

        Raises:
            InvalidStyleError: If style has critical validation errors
        """
        validated_style = style.model_copy()
        warnings_list = []

        # Validate font size
        if style.font_size <= 0 or style.font_size > 72:
            warnings_list.append(
                f"Invalid font_size {style.font_size}, using default {self.default_style.font_size}"
            )
            validated_style.font_size = self.default_style.font_size

        # Validate heading font size
        if style.heading_font_size <= 0 or style.heading_font_size > 72:
            warnings_list.append(
                f"Invalid heading_font_size {style.heading_font_size}, "
                f"using default {self.default_style.heading_font_size}"
            )
            validated_style.heading_font_size = self.default_style.heading_font_size

        # Validate line spacing
        if style.line_spacing <= 0 or style.line_spacing > 5:
            warnings_list.append(
                f"Invalid line_spacing {style.line_spacing}, "
                f"using default {self.default_style.line_spacing}"
            )
            validated_style.line_spacing = self.default_style.line_spacing

        # Validate margins
        for margin_name in ['margin_top', 'margin_bottom', 'margin_left', 'margin_right']:
            margin_value = getattr(style, margin_name)
            if margin_value < 0 or margin_value > 10:
                default_value = getattr(self.default_style, margin_name)
                warnings_list.append(
                    f"Invalid {margin_name} {margin_value}, using default {default_value}"
                )
                setattr(validated_style, margin_name, default_value)

        # Validate color format (hex colors)
        for color_name in ['color_primary', 'color_secondary', 'color_accent']:
            color_value = getattr(style, color_name)
            if not self._is_valid_hex_color(color_value):
                default_value = getattr(self.default_style, color_name)
                warnings_list.append(
                    f"Invalid {color_name} '{color_value}', using default '{default_value}'"
                )
                setattr(validated_style, color_name, default_value)

        # Log all warnings
        for warning_msg in warnings_list:
            logger.warning(warning_msg)
            warnings.warn(warning_msg, UserWarning)

        return validated_style

    def _is_valid_hex_color(self, color: str) -> bool:
        """Check if a string is a valid hex color.

        Args:
            color: Color string to validate

        Returns:
            True if valid hex color, False otherwise
        """
        if not color or not isinstance(color, str):
            return False
        
        # Remove leading # if present
        color = color.lstrip('#')
        
        # Check if it's a valid hex color (3 or 6 characters)
        if len(color) not in [3, 6]:
            return False
        
        try:
            int(color, 16)
            return True
        except ValueError:
            return False

    def load_style(self, style_path: str) -> PDFStyle:
        """Load style configuration from YAML file.

        Args:
            style_path: Path to YAML style configuration file

        Returns:
            PDFStyle configuration loaded from file

        Raises:
            InvalidPathError: If file doesn't exist
            InvalidStyleError: If configuration is invalid
        """
        path = Path(style_path)
        if not path.exists():
            raise InvalidPathError(style_path, "Style file does not exist")

        try:
            import yaml
            
            with open(path, 'r') as f:
                data = yaml.safe_load(f) or {}

            # Extract PDF style data
            style_data = data.get('pdf_style', data)
            
            # Handle nested margins and colors
            margins = style_data.get('margins', {})
            colors = style_data.get('colors', {})

            # Create PDFStyle with loaded data
            pdf_style = PDFStyle(
                font_family=style_data.get('font_family', self.default_style.font_family),
                font_size=style_data.get('font_size', self.default_style.font_size),
                heading_font_size=style_data.get('heading_font_size', self.default_style.heading_font_size),
                line_spacing=style_data.get('line_spacing', self.default_style.line_spacing),
                margin_top=margins.get('top', self.default_style.margin_top),
                margin_bottom=margins.get('bottom', self.default_style.margin_bottom),
                margin_left=margins.get('left', self.default_style.margin_left),
                margin_right=margins.get('right', self.default_style.margin_right),
                color_primary=colors.get('primary', self.default_style.color_primary),
                color_secondary=colors.get('secondary', self.default_style.color_secondary),
                color_accent=colors.get('accent', self.default_style.color_accent),
            )

            logger.info(f"Loaded style configuration from: {style_path}")
            return pdf_style

        except yaml.YAMLError as e:
            raise InvalidStyleError(f"Invalid YAML in style file: {e}")
        except Exception as e:
            raise InvalidStyleError(f"Failed to load style configuration: {e}")

    def validate_style(self, style: PDFStyle) -> dict:
        """Validate style configuration and return validation result.

        Args:
            style: PDF style configuration to validate

        Returns:
            Dictionary with validation results:
                - 'valid': bool indicating if style is valid
                - 'warnings': list of warning messages
                - 'errors': list of error messages
        """
        result = {
            'valid': True,
            'warnings': [],
            'errors': []
        }

        # Check font sizes
        if style.font_size <= 0 or style.font_size > 72:
            result['warnings'].append(
                f"Font size {style.font_size} is outside recommended range (1-72)"
            )

        if style.heading_font_size <= 0 or style.heading_font_size > 72:
            result['warnings'].append(
                f"Heading font size {style.heading_font_size} is outside recommended range (1-72)"
            )

        # Check line spacing
        if style.line_spacing <= 0:
            result['errors'].append("Line spacing must be positive")
            result['valid'] = False
        elif style.line_spacing > 5:
            result['warnings'].append(
                f"Line spacing {style.line_spacing} is unusually large"
            )

        # Check margins
        for margin_name in ['margin_top', 'margin_bottom', 'margin_left', 'margin_right']:
            margin_value = getattr(style, margin_name)
            if margin_value < 0:
                result['errors'].append(f"{margin_name} cannot be negative")
                result['valid'] = False
            elif margin_value > 10:
                result['warnings'].append(
                    f"{margin_name} {margin_value}cm is unusually large"
                )

        # Check colors
        for color_name in ['color_primary', 'color_secondary', 'color_accent']:
            color_value = getattr(style, color_name)
            if not self._is_valid_hex_color(color_value):
                result['errors'].append(
                    f"{color_name} '{color_value}' is not a valid hex color"
                )
                result['valid'] = False

        return result
