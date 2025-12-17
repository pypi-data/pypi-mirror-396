"""
Session Manager for the Agentic Resume Builder.

This module manages interactive session state, including saving and loading
conversation history, tracking progress, and maintaining context across sessions.
"""

import json
import os
import stat
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from pydantic import ValidationError

from agentic_resume_builder.exceptions import (
    InvalidPathError,
    SessionCorruptedError,
    SessionLoadError,
    SessionNotFoundError,
)
from agentic_resume_builder.models import InteractiveSession, Interaction, Question


class SessionManager:
    """Manages interactive session persistence and restoration."""

    def __init__(self, session_dir: str = "./sessions"):
        """Initialize the session manager.

        Args:
            session_dir: Directory where session files will be stored
        """
        self.session_dir = Path(session_dir)
        self.session_dir.mkdir(parents=True, exist_ok=True)

    def _get_session_path(self, session_id: str) -> Path:
        """Get the file path for a session.

        Args:
            session_id: Unique session identifier

        Returns:
            Path to the session file
        """
        return self.session_dir / f"{session_id}.json"

    def _set_restrictive_permissions(self, file_path: Path) -> None:
        """Set restrictive file permissions (600) for privacy.

        Args:
            file_path: Path to the file to protect
        """
        # Set permissions to 600 (read/write for owner only)
        os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)

    def save_session(self, session: InteractiveSession) -> None:
        """Save an interactive session to a JSON file.

        Args:
            session: The interactive session to save

        Raises:
            InvalidPathError: If the session directory is invalid
        """
        session_path = self._get_session_path(session.session_id)

        # Update last activity timestamp
        session.last_activity = datetime.now()

        # Convert session to dictionary for JSON serialization
        session_data = {
            "session_id": session.session_id,
            "resume_path": session.resume_path,
            "conversation_history": [
                {
                    "question": {
                        "id": interaction.question.id,
                        "text": interaction.question.text,
                        "context": interaction.question.context,
                        "question_type": interaction.question.question_type,
                        "related_section": interaction.question.related_section,
                    },
                    "response": interaction.response,
                    "timestamp": interaction.timestamp.isoformat(),
                    "extracted_info": interaction.extracted_info,
                }
                for interaction in session.conversation_history
            ],
            "current_focus": session.current_focus,
            "started_at": session.started_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "introductory_complete": session.introductory_complete,
        }

        # Write to file with proper formatting
        try:
            with open(session_path, "w") as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)

            # Set restrictive permissions for privacy
            self._set_restrictive_permissions(session_path)

        except (IOError, OSError) as e:
            raise InvalidPathError(
                str(session_path), f"Failed to save session: {str(e)}"
            )

    def load_session(self, session_id: str) -> InteractiveSession:
        """Load an interactive session from a JSON file.

        Args:
            session_id: Unique session identifier

        Returns:
            The restored interactive session

        Raises:
            SessionNotFoundError: If the session file doesn't exist
            SessionCorruptedError: If the session data is corrupted
            SessionLoadError: If loading fails for other reasons
        """
        session_path = self._get_session_path(session_id)

        # Check if session file exists
        if not session_path.exists():
            raise SessionNotFoundError(session_id)

        try:
            # Read session data from file
            with open(session_path, "r") as f:
                session_data = json.load(f)

            # Validate required fields
            required_fields = [
                "session_id",
                "resume_path",
                "conversation_history",
                "current_focus",
                "started_at",
                "last_activity",
                "introductory_complete",
            ]
            missing_fields = [
                field for field in required_fields if field not in session_data
            ]
            if missing_fields:
                raise SessionCorruptedError(
                    session_id, f"Missing fields: {', '.join(missing_fields)}"
                )

            # Parse conversation history
            conversation_history = []
            for interaction_data in session_data["conversation_history"]:
                try:
                    question = Question(
                        id=interaction_data["question"]["id"],
                        text=interaction_data["question"]["text"],
                        context=interaction_data["question"]["context"],
                        question_type=interaction_data["question"]["question_type"],
                        related_section=interaction_data["question"]["related_section"],
                    )

                    interaction = Interaction(
                        question=question,
                        response=interaction_data["response"],
                        timestamp=datetime.fromisoformat(interaction_data["timestamp"]),
                        extracted_info=interaction_data.get("extracted_info", {}),
                    )
                    conversation_history.append(interaction)
                except (KeyError, ValueError, ValidationError) as e:
                    raise SessionCorruptedError(
                        session_id, f"Invalid interaction data: {str(e)}"
                    )

            # Create InteractiveSession object
            session = InteractiveSession(
                session_id=session_data["session_id"],
                resume_path=session_data["resume_path"],
                conversation_history=conversation_history,
                current_focus=session_data["current_focus"],
                started_at=datetime.fromisoformat(session_data["started_at"]),
                last_activity=datetime.fromisoformat(session_data["last_activity"]),
                introductory_complete=session_data["introductory_complete"],
            )

            return session

        except json.JSONDecodeError as e:
            raise SessionCorruptedError(session_id, f"Invalid JSON format: {str(e)}")
        except (IOError, OSError) as e:
            raise SessionLoadError(session_id, f"Failed to read session file: {str(e)}")

    def list_sessions(self) -> list[str]:
        """List all available session IDs.

        Returns:
            List of session IDs
        """
        if not self.session_dir.exists():
            return []

        session_files = self.session_dir.glob("*.json")
        return [f.stem for f in session_files]

    def delete_session(self, session_id: str) -> None:
        """Delete a session file.

        Args:
            session_id: Unique session identifier

        Raises:
            SessionNotFoundError: If the session file doesn't exist
        """
        session_path = self._get_session_path(session_id)

        if not session_path.exists():
            raise SessionNotFoundError(session_id)

        try:
            session_path.unlink()
        except (IOError, OSError) as e:
            raise SessionLoadError(
                session_id, f"Failed to delete session file: {str(e)}"
            )

    @staticmethod
    def generate_session_id() -> str:
        """Generate a unique session ID.

        Returns:
            A unique session ID (UUID)
        """
        return str(uuid.uuid4())
