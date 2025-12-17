"""
Markdown processor for parsing and rendering resume documents.

This module handles conversion between Markdown text and ResumeDocument structures,
maintaining formatting and structure throughout the process.
"""

import re
from typing import Dict, List, Optional, Tuple

from agentic_resume_builder.exceptions import (
    IncompleteSectionError,
    MarkdownParseError,
    MarkdownSyntaxError,
)
from agentic_resume_builder.models import (
    Achievement,
    Education,
    Experience,
    PersonalInfo,
    ResumeDocument,
    Section,
)


class ValidationResult:
    """Result of document validation."""

    def __init__(self, is_valid: bool, errors: Optional[List[str]] = None, warnings: Optional[List[str]] = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []

    def __bool__(self) -> bool:
        return self.is_valid


class MarkdownProcessor:
    """Processes Markdown resume documents."""

    # Standard section names
    STANDARD_SECTIONS = {
        "experience",
        "work experience",
        "education",
        "skills",
        "summary",
        "professional summary",
    }

    def __init__(self):
        """Initialize the Markdown processor."""
        pass

    def parse(self, markdown_text: str) -> ResumeDocument:
        """
        Parse Markdown text into a ResumeDocument structure.

        Args:
            markdown_text: The Markdown text to parse

        Returns:
            ResumeDocument: Parsed resume document

        Raises:
            MarkdownParseError: If parsing fails
            MarkdownSyntaxError: If Markdown syntax is invalid
        """
        if not markdown_text or not markdown_text.strip():
            raise MarkdownParseError("Empty Markdown text provided")

        lines = markdown_text.split("\n")
        
        # Parse personal info from the first heading
        personal_info = self._parse_personal_info(lines)
        
        # Parse sections
        sections_data = self._parse_sections(lines)
        
        # Extract structured data from sections
        summary = self._extract_summary(sections_data)
        experiences = self._extract_experiences(sections_data)
        education = self._extract_education(sections_data)
        skills = self._extract_skills(sections_data)
        
        # Create generic sections for non-standard sections
        sections = self._create_generic_sections(sections_data)
        
        return ResumeDocument(
            personal_info=personal_info,
            summary=summary,
            experiences=experiences,
            education=education,
            skills=skills,
            sections=sections,
            metadata={"source": "markdown"}
        )

    def _parse_personal_info(self, lines: List[str]) -> PersonalInfo:
        """Extract personal information from the document."""
        name = ""
        email = ""
        phone = None
        location = None
        linkedin = None
        github = None
        website = None
        
        # Look for the first level-1 heading as the name
        for i, line in enumerate(lines):
            if line.startswith("# "):
                name = line[2:].strip()
                
                # Look for contact info in the next few lines
                for j in range(i + 1, min(i + 10, len(lines))):
                    contact_line = lines[j].strip()
                    # Skip empty lines
                    if not contact_line:
                        continue
                    # Stop at next heading
                    if contact_line.startswith("#"):
                        break
                    
                    # Extract email
                    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', contact_line)
                    if email_match and not email:
                        email = email_match.group(0)
                    
                    # Extract phone
                    phone_match = re.search(r'[\+\(]?[0-9][0-9\s\-\(\)\.]{7,}[0-9]', contact_line)
                    if phone_match and not phone:
                        phone = phone_match.group(0).strip()
                    
                    # Extract LinkedIn
                    if 'linkedin.com' in contact_line.lower() and not linkedin:
                        url_match = re.search(r'https?://[^\s\|\)]+', contact_line)
                        if url_match:
                            linkedin = url_match.group(0)
                    
                    # Extract GitHub
                    if 'github.com' in contact_line.lower() and not github:
                        url_match = re.search(r'https?://github\.com[^\s\|\)]+', contact_line)
                        if url_match:
                            github = url_match.group(0)
                    
                    # Extract website (generic URL that's not LinkedIn or GitHub)
                    if not website and 'http' in contact_line:
                        if 'linkedin.com' not in contact_line.lower() and 'github.com' not in contact_line.lower():
                            url_match = re.search(r'https?://[^\s\)]+', contact_line)
                            if url_match:
                                website = url_match.group(0)
                    
                    # Extract location (look for city, state patterns)
                    if not location and not email_match and not phone_match and not 'http' in contact_line:
                        # Simple heuristic: if it contains a comma or common location words
                        if ',' in contact_line or any(word in contact_line.lower() for word in ['city', 'state', 'country']):
                            location = contact_line
                
                break
        
        if not name:
            raise MarkdownParseError("No name found (expected level-1 heading)")
        
        if not email:
            # Provide a default email to avoid validation errors
            email = "email@example.com"
        
        return PersonalInfo(
            name=name,
            email=email,
            phone=phone,
            location=location,
            linkedin=linkedin,
            github=github,
            website=website
        )

    def _parse_sections(self, lines: List[str]) -> Dict[str, Tuple[int, List[str]]]:
        """
        Parse document into sections based on heading hierarchy.
        
        Returns a dict mapping section names to (level, content_lines).
        Level-2 sections (##) contain all content including subsections (###).
        """
        sections = {}
        current_section = None
        current_level = 0
        current_content = []
        
        for i, line in enumerate(lines):
            # Check for headings
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            
            if heading_match:
                level = len(heading_match.group(1))
                section_name = heading_match.group(2).strip()
                
                # Skip level-1 headings (that's the name)
                if level == 1:
                    continue
                
                # If this is a level-2 heading, save previous section and start new one
                if level == 2:
                    # Save previous section
                    if current_section:
                        sections[current_section] = (current_level, current_content)
                    
                    current_section = section_name
                    current_level = level
                    current_content = []
                else:
                    # For level-3+ headings, add them to current section content
                    if current_section:
                        current_content.append(line)
            elif current_section:
                # Add content to current section
                current_content.append(line)
        
        # Save last section
        if current_section:
            sections[current_section] = (current_level, current_content)
        
        return sections

    def _extract_summary(self, sections_data: Dict[str, Tuple[int, List[str]]]) -> Optional[str]:
        """Extract professional summary from sections."""
        for section_name, (level, content) in sections_data.items():
            if section_name.lower() in ["summary", "professional summary", "about"]:
                return "\n".join(content).strip()
        return None

    def _extract_experiences(self, sections_data: Dict[str, Tuple[int, List[str]]]) -> List[Experience]:
        """Extract work experiences from sections."""
        experiences = []
        
        for section_name, (level, content) in sections_data.items():
            section_lower = section_name.lower()
            if section_lower in ["experience", "work experience", "professional experience"]:
                experiences.extend(self._parse_experience_section(content))
        
        return experiences

    def _parse_experience_section(self, content_lines: List[str]) -> List[Experience]:
        """Parse experience entries from content lines."""
        experiences = []
        current_exp = None
        current_achievements = []
        
        for line in content_lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for experience header (### Company Name or **Company Name**)
            if line.startswith("###") or (line.startswith("**") and line.endswith("**")):
                # Save previous experience
                if current_exp:
                    current_exp["achievements"] = current_achievements
                    try:
                        experiences.append(Experience(**current_exp))
                    except Exception:
                        pass  # Skip invalid experiences
                
                # Start new experience
                company_name = line.replace("###", "").replace("**", "").strip()
                current_exp = {
                    "company": company_name,
                    "role": "",
                    "start_date": "2020",  # Default
                    "end_date": None,
                }
                current_achievements = []
            
            # Check for role and dates (e.g., "Software Engineer | Jan 2020 - Present")
            elif current_exp and "|" in line:
                parts = line.split("|")
                if len(parts) >= 2:
                    current_exp["role"] = parts[0].strip()
                    date_part = parts[1].strip()
                    
                    # Parse dates
                    date_match = re.search(r'(\d{4}(?:-\d{2})?)\s*[-–]\s*(\d{4}(?:-\d{2})?|Present|Current)', date_part)
                    if date_match:
                        current_exp["start_date"] = date_match.group(1)
                        end_date = date_match.group(2)
                        if end_date.lower() not in ["present", "current"]:
                            current_exp["end_date"] = end_date
            
            # Check for bullet points (achievements)
            elif line.startswith("-") or line.startswith("*"):
                achievement_text = line.lstrip("-*").strip()
                if achievement_text and current_exp:
                    current_achievements.append(Achievement(description=achievement_text))
        
        # Save last experience
        if current_exp:
            current_exp["achievements"] = current_achievements
            try:
                experiences.append(Experience(**current_exp))
            except Exception:
                pass
        
        return experiences

    def _extract_education(self, sections_data: Dict[str, Tuple[int, List[str]]]) -> List[Education]:
        """Extract education entries from sections."""
        education_list = []
        
        for section_name, (level, content) in sections_data.items():
            if section_name.lower() in ["education"]:
                education_list.extend(self._parse_education_section(content))
        
        return education_list

    def _parse_education_section(self, content_lines: List[str]) -> List[Education]:
        """Parse education entries from content lines."""
        education_list = []
        current_edu = None
        
        for line in content_lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for education header
            if line.startswith("###") or (line.startswith("**") and line.endswith("**")):
                # Save previous education
                if current_edu:
                    try:
                        education_list.append(Education(**current_edu))
                    except Exception:
                        pass
                
                # Start new education
                institution = line.replace("###", "").replace("**", "").strip()
                current_edu = {
                    "institution": institution,
                    "degree": "",
                    "field": "",
                    "start_date": "2020",
                    "end_date": "2024",
                }
            
            # Check for degree and field
            elif current_edu and "|" in line:
                parts = line.split("|")
                if len(parts) >= 2:
                    current_edu["degree"] = parts[0].strip()
                    
                    # Second part might have field and dates
                    second_part = parts[1].strip()
                    date_match = re.search(r'(\d{4}(?:-\d{2})?)\s*[-–]\s*(\d{4}(?:-\d{2})?)', second_part)
                    if date_match:
                        current_edu["start_date"] = date_match.group(1)
                        current_edu["end_date"] = date_match.group(2)
                        # Field is everything before the dates
                        field = second_part[:date_match.start()].strip()
                        if field:
                            current_edu["field"] = field
                    else:
                        current_edu["field"] = second_part
        
        # Save last education
        if current_edu:
            try:
                education_list.append(Education(**current_edu))
            except Exception:
                pass
        
        return education_list

    def _extract_skills(self, sections_data: Dict[str, Tuple[int, List[str]]]) -> Dict[str, List[str]]:
        """Extract skills from sections."""
        skills = {}
        
        for section_name, (level, content) in sections_data.items():
            if section_name.lower() in ["skills", "technical skills"]:
                skills = self._parse_skills_section(content)
        
        return skills

    def _parse_skills_section(self, content_lines: List[str]) -> Dict[str, List[str]]:
        """Parse skills section into categories."""
        skills = {}
        current_category = "General"
        
        for line in content_lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for skill category (bold text or subheading)
            if line.startswith("**") and line.endswith("**"):
                current_category = line.replace("**", "").strip().rstrip(":")
                skills[current_category] = []
            elif line.startswith("-") or line.startswith("*"):
                # Skill item
                skill_text = line.lstrip("-*").strip()
                if current_category not in skills:
                    skills[current_category] = []
                
                # Split by commas if multiple skills on one line
                skill_items = [s.strip() for s in skill_text.split(",")]
                skills[current_category].extend(skill_items)
        
        return skills

    def _create_generic_sections(self, sections_data: Dict[str, Tuple[int, List[str]]]) -> List[Section]:
        """Create Section objects for non-standard sections."""
        sections = []
        
        for section_name, (level, content) in sections_data.items():
            section_lower = section_name.lower()
            # Skip standard sections that are parsed separately
            # Only include level-2 sections (##) as generic sections
            if section_lower not in self.STANDARD_SECTIONS and level == 2:
                section = Section(
                    name=section_name,
                    content="\n".join(content).strip(),
                    subsections=[],
                    metadata={"level": level}
                )
                sections.append(section)
        
        return sections


    def render(self, document: ResumeDocument) -> str:
        """
        Render a ResumeDocument back to Markdown text.

        Args:
            document: The ResumeDocument to render

        Returns:
            str: Markdown text representation

        Raises:
            MarkdownParseError: If rendering fails
        """
        lines = []
        
        # Render personal info
        lines.append(f"# {document.personal_info.name}")
        lines.append("")
        
        # Contact information
        contact_parts = []
        if document.personal_info.email:
            contact_parts.append(document.personal_info.email)
        if document.personal_info.phone:
            contact_parts.append(document.personal_info.phone)
        if document.personal_info.location:
            contact_parts.append(document.personal_info.location)
        
        if contact_parts:
            lines.append(" | ".join(contact_parts))
            lines.append("")
        
        # Links
        links = []
        if document.personal_info.linkedin:
            links.append(f"LinkedIn: {document.personal_info.linkedin}")
        if document.personal_info.github:
            links.append(f"GitHub: {document.personal_info.github}")
        if document.personal_info.website:
            links.append(f"Website: {document.personal_info.website}")
        
        if links:
            lines.append(" | ".join(links))
            lines.append("")
        
        # Render summary
        if document.summary:
            lines.append("## Summary")
            lines.append("")
            lines.append(document.summary)
            lines.append("")
        
        # Render experience
        if document.experiences:
            lines.append("## Experience")
            lines.append("")
            for exp in document.experiences:
                lines.append(f"### {exp.company}")
                
                # Role and dates
                date_str = exp.start_date
                if exp.end_date:
                    date_str += f" - {exp.end_date}"
                else:
                    date_str += " - Present"
                
                lines.append(f"{exp.role} | {date_str}")
                
                if exp.location:
                    lines.append(f"*{exp.location}*")
                
                lines.append("")
                
                # Achievements
                for achievement in exp.achievements:
                    lines.append(f"- {achievement.description}")
                
                if exp.technologies:
                    lines.append("")
                    lines.append(f"**Technologies:** {', '.join(exp.technologies)}")
                
                lines.append("")
        
        # Render education
        if document.education:
            lines.append("## Education")
            lines.append("")
            for edu in document.education:
                lines.append(f"### {edu.institution}")
                
                date_str = f"{edu.start_date} - {edu.end_date}"
                lines.append(f"{edu.degree} | {edu.field} | {date_str}")
                
                if edu.gpa:
                    lines.append(f"*GPA: {edu.gpa}*")
                
                if edu.honors:
                    lines.append("")
                    for honor in edu.honors:
                        lines.append(f"- {honor}")
                
                lines.append("")
        
        # Render skills
        if document.skills:
            lines.append("## Skills")
            lines.append("")
            for category, skill_list in document.skills.items():
                lines.append(f"**{category}:**")
                for skill in skill_list:
                    lines.append(f"- {skill}")
                lines.append("")
        
        # Render additional sections
        for section in document.sections:
            lines.append(f"## {section.name}")
            lines.append("")
            lines.append(section.content)
            lines.append("")
            
            # Render subsections
            for subsection in section.subsections:
                lines.append(f"### {subsection.name}")
                lines.append("")
                lines.append(subsection.content)
                lines.append("")
        
        return "\n".join(lines).strip() + "\n"

    def get_section(self, document: ResumeDocument, section_name: str) -> Optional[Section]:
        """
        Extract a specific section from the document.

        Args:
            document: The ResumeDocument to search
            section_name: Name of the section to find (case-insensitive)

        Returns:
            Optional[Section]: The section if found, None otherwise
        """
        section_name_lower = section_name.lower()
        
        # Check standard sections
        if section_name_lower in ["summary", "professional summary"]:
            if document.summary:
                return Section(
                    name="Summary",
                    content=document.summary,
                    subsections=[],
                    metadata={}
                )
        
        elif section_name_lower in ["experience", "work experience"]:
            # Convert experiences to section format
            content_lines = []
            for exp in document.experiences:
                content_lines.append(f"### {exp.company}")
                date_str = exp.start_date
                if exp.end_date:
                    date_str += f" - {exp.end_date}"
                else:
                    date_str += " - Present"
                content_lines.append(f"{exp.role} | {date_str}")
                if exp.location:
                    content_lines.append(f"*{exp.location}*")
                content_lines.append("")
                for achievement in exp.achievements:
                    content_lines.append(f"- {achievement.description}")
                content_lines.append("")
            
            return Section(
                name="Experience",
                content="\n".join(content_lines).strip(),
                subsections=[],
                metadata={}
            )
        
        elif section_name_lower == "education":
            content_lines = []
            for edu in document.education:
                content_lines.append(f"### {edu.institution}")
                date_str = f"{edu.start_date} - {edu.end_date}"
                content_lines.append(f"{edu.degree} | {edu.field} | {date_str}")
                if edu.gpa:
                    content_lines.append(f"*GPA: {edu.gpa}*")
                content_lines.append("")
            
            return Section(
                name="Education",
                content="\n".join(content_lines).strip(),
                subsections=[],
                metadata={}
            )
        
        elif section_name_lower == "skills":
            content_lines = []
            for category, skill_list in document.skills.items():
                content_lines.append(f"**{category}:**")
                for skill in skill_list:
                    content_lines.append(f"- {skill}")
                content_lines.append("")
            
            return Section(
                name="Skills",
                content="\n".join(content_lines).strip(),
                subsections=[],
                metadata={}
            )
        
        # Check custom sections
        for section in document.sections:
            if section.name.lower() == section_name_lower:
                return section
        
        return None

    def update_section(self, document: ResumeDocument, section_name: str, content: str) -> ResumeDocument:
        """
        Update a section while preserving document structure.

        Args:
            document: The ResumeDocument to update
            section_name: Name of the section to update (case-insensitive)
            content: New content for the section

        Returns:
            ResumeDocument: Updated document with modified section

        Raises:
            MarkdownParseError: If section update fails
        """
        section_name_lower = section_name.lower()
        
        # Create a copy of the document
        updated_doc = document.model_copy(deep=True)
        
        # Update standard sections
        if section_name_lower in ["summary", "professional summary"]:
            updated_doc.summary = content.strip()
        
        elif section_name_lower in ["experience", "work experience"]:
            # Parse the new content as experiences
            content_lines = content.split("\n")
            new_experiences = self._parse_experience_section(content_lines)
            updated_doc.experiences = new_experiences
        
        elif section_name_lower == "education":
            content_lines = content.split("\n")
            new_education = self._parse_education_section(content_lines)
            updated_doc.education = new_education
        
        elif section_name_lower == "skills":
            content_lines = content.split("\n")
            new_skills = self._parse_skills_section(content_lines)
            updated_doc.skills = new_skills
        
        else:
            # Update or add custom section
            section_found = False
            for i, section in enumerate(updated_doc.sections):
                if section.name.lower() == section_name_lower:
                    updated_doc.sections[i] = Section(
                        name=section.name,
                        content=content.strip(),
                        subsections=section.subsections,
                        metadata=section.metadata
                    )
                    section_found = True
                    break
            
            # If section doesn't exist, add it
            if not section_found:
                updated_doc.sections.append(Section(
                    name=section_name,
                    content=content.strip(),
                    subsections=[],
                    metadata={}
                ))
        
        return updated_doc

    def validate(self, document: ResumeDocument) -> ValidationResult:
        """
        Validate document structure and identify issues.

        Args:
            document: The ResumeDocument to validate

        Returns:
            ValidationResult: Validation result with errors and warnings
        """
        errors = []
        warnings = []
        
        # Check for required personal info
        if not document.personal_info.name:
            errors.append("Missing required field: name")
        
        if not document.personal_info.email or document.personal_info.email == "email@example.com":
            warnings.append("Email is missing or using default placeholder")
        
        # Check for incomplete sections
        if not document.experiences and not document.education:
            warnings.append("Resume has no experience or education sections")
        
        # Check for sparse experiences
        for i, exp in enumerate(document.experiences):
            if not exp.role:
                warnings.append(f"Experience {i+1} ({exp.company}) is missing role")
            
            if not exp.achievements:
                warnings.append(f"Experience {i+1} ({exp.company}) has no achievements listed")
            
            # Check for generic/unquantified achievements
            for j, achievement in enumerate(exp.achievements):
                if len(achievement.description) < 20:
                    warnings.append(
                        f"Experience {i+1} ({exp.company}), achievement {j+1} is very brief"
                    )
                
                # Check for metrics
                has_numbers = bool(re.search(r'\d+', achievement.description))
                if not has_numbers:
                    warnings.append(
                        f"Experience {i+1} ({exp.company}), achievement {j+1} lacks quantifiable metrics"
                    )
        
        # Check for sparse education
        for i, edu in enumerate(document.education):
            if not edu.field:
                warnings.append(f"Education {i+1} ({edu.institution}) is missing field of study")
        
        # Check for empty skills
        if not document.skills:
            warnings.append("Skills section is empty")
        
        # Check for empty summary
        if not document.summary:
            warnings.append("Professional summary is missing")
        elif len(document.summary) < 50:
            warnings.append("Professional summary is very brief")
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)
