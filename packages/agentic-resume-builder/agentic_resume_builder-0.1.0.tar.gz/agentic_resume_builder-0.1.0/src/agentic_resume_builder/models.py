"""
Data models for the Agentic Resume Builder.

This module defines the core data structures used throughout the application,
including resume documents, personal information, experiences, and configuration.
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class PersonalInfo(BaseModel):
    """Personal information section of a resume."""

    name: str = Field(..., min_length=1, description="Full name")
    email: str = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    location: Optional[str] = Field(None, description="Location")
    linkedin: Optional[str] = Field(None, description="LinkedIn profile URL")
    github: Optional[str] = Field(None, description="GitHub profile URL")
    website: Optional[str] = Field(None, description="Personal website URL")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        if not v:
            raise ValueError("Email cannot be empty")
        # Simple email validation
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, v):
            raise ValueError(f"Invalid email format: {v}")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name is not empty."""
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()


class Achievement(BaseModel):
    """A single achievement with metrics and impact score."""

    description: str = Field(..., min_length=1, description="Achievement description")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Quantifiable metrics")
    impact_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Impact score between 0 and 1"
    )

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate description is not empty."""
        if not v or not v.strip():
            raise ValueError("Achievement description cannot be empty")
        return v.strip()


class Experience(BaseModel):
    """Work experience entry."""

    company: str = Field(..., min_length=1, description="Company name")
    role: str = Field(..., min_length=1, description="Job role/title")
    start_date: str = Field(..., description="Start date (YYYY-MM format)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM format), None if current")
    location: Optional[str] = Field(None, description="Work location")
    achievements: List[Achievement] = Field(default_factory=list, description="List of achievements")
    technologies: List[str] = Field(default_factory=list, description="Technologies used")

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate date format is YYYY-MM or YYYY."""
        if v is None:
            return v
        if not v:
            raise ValueError("Date cannot be empty string")
        # Accept YYYY-MM or YYYY format
        if not re.match(r"^\d{4}(-\d{2})?$", v):
            raise ValueError(f"Date must be in YYYY-MM or YYYY format, got: {v}")
        # Validate month if present
        if "-" in v:
            year, month = v.split("-")
            month_int = int(month)
            if month_int < 1 or month_int > 12:
                raise ValueError(f"Month must be between 01 and 12, got: {month}")
        return v

    @field_validator("company", "role")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Validate field is not empty."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()

    @model_validator(mode="after")
    def validate_date_order(self) -> "Experience":
        """Validate that start_date is before end_date if both are present."""
        if self.end_date and self.start_date:
            # Simple string comparison works for YYYY-MM format
            if self.start_date > self.end_date:
                raise ValueError(f"Start date {self.start_date} must be before end date {self.end_date}")
        return self


class Education(BaseModel):
    """Education entry."""

    institution: str = Field(..., min_length=1, description="Educational institution name")
    degree: str = Field(..., min_length=1, description="Degree type")
    field: str = Field(..., min_length=1, description="Field of study")
    start_date: str = Field(..., description="Start date (YYYY-MM format)")
    end_date: str = Field(..., description="End date (YYYY-MM format)")
    gpa: Optional[str] = Field(None, description="GPA")
    honors: List[str] = Field(default_factory=list, description="Honors and awards")

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Validate date format is YYYY-MM or YYYY."""
        if not v:
            raise ValueError("Date cannot be empty")
        # Accept YYYY-MM or YYYY format
        if not re.match(r"^\d{4}(-\d{2})?$", v):
            raise ValueError(f"Date must be in YYYY-MM or YYYY format, got: {v}")
        # Validate month if present
        if "-" in v:
            year, month = v.split("-")
            month_int = int(month)
            if month_int < 1 or month_int > 12:
                raise ValueError(f"Month must be between 01 and 12, got: {month}")
        return v

    @field_validator("institution", "degree", "field")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Validate field is not empty."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()

    @model_validator(mode="after")
    def validate_date_order(self) -> "Education":
        """Validate that start_date is before end_date."""
        if self.start_date > self.end_date:
            raise ValueError(f"Start date {self.start_date} must be before end date {self.end_date}")
        return self


class Section(BaseModel):
    """A section in the resume document."""

    name: str = Field(..., min_length=1, description="Section name")
    content: str = Field(default="", description="Section content")
    subsections: List["Section"] = Field(default_factory=list, description="Nested subsections")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name is not empty."""
        if not v or not v.strip():
            raise ValueError("Section name cannot be empty")
        return v.strip()


class ResumeDocument(BaseModel):
    """Complete resume document structure."""

    personal_info: PersonalInfo = Field(..., description="Personal information")
    summary: Optional[str] = Field(None, description="Professional summary")
    experiences: List[Experience] = Field(default_factory=list, description="Work experiences")
    education: List[Education] = Field(default_factory=list, description="Education history")
    skills: Dict[str, List[str]] = Field(default_factory=dict, description="Skills by category")
    sections: List[Section] = Field(default_factory=list, description="Additional sections")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")


class Resume(BaseModel):
    """Resume with file metadata."""

    document: ResumeDocument = Field(..., description="Resume document content")
    file_path: str = Field(..., min_length=1, description="Path to resume file")
    last_modified: datetime = Field(default_factory=datetime.now, description="Last modification time")
    version: int = Field(default=1, ge=1, description="Document version number")

    @field_validator("file_path")
    @classmethod
    def validate_file_path(cls, v: str) -> str:
        """Validate file path is not empty."""
        if not v or not v.strip():
            raise ValueError("File path cannot be empty")
        return v.strip()


class Question(BaseModel):
    """A question asked during the interactive session."""

    id: str = Field(..., min_length=1, description="Question ID")
    text: str = Field(..., min_length=1, description="Question text")
    context: str = Field(default="", description="Question context")
    question_type: str = Field(
        ..., description="Question type: introductory, open, metric, or clarification"
    )
    related_section: str = Field(default="", description="Related resume section")

    @field_validator("question_type")
    @classmethod
    def validate_question_type(cls, v: str) -> str:
        """Validate question type is one of the allowed values."""
        allowed_types = {"introductory", "open", "metric", "clarification"}
        if v not in allowed_types:
            raise ValueError(
                f"Question type must be one of {allowed_types}, got: {v}"
            )
        return v


class Interaction(BaseModel):
    """A single question-response interaction."""

    question: Question = Field(..., description="The question asked")
    response: str = Field(..., description="User's response")
    timestamp: datetime = Field(default_factory=datetime.now, description="Interaction timestamp")
    extracted_info: Dict[str, Any] = Field(
        default_factory=dict, description="Information extracted from response"
    )


class InteractiveSession(BaseModel):
    """An interactive session with the AI agent."""

    session_id: str = Field(..., min_length=1, description="Unique session ID")
    resume_path: str = Field(..., min_length=1, description="Path to resume file")
    conversation_history: List[Interaction] = Field(
        default_factory=list, description="Conversation history"
    )
    current_focus: str = Field(default="", description="Current section being worked on")
    started_at: datetime = Field(default_factory=datetime.now, description="Session start time")
    last_activity: datetime = Field(default_factory=datetime.now, description="Last activity time")
    introductory_complete: bool = Field(
        default=False, description="Whether introductory questions are complete"
    )
