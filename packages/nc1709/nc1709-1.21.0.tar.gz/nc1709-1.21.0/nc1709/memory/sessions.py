"""
Session Manager for NC1709
Handles conversation persistence and session management
"""
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class Message:
    """Represents a single message in a conversation"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Session:
    """Represents a conversation session"""
    id: str
    name: str
    messages: List[Message] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    project_path: Optional[str] = None

    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to the session"""
        message = Message(role=role, content=content, metadata=metadata or {})
        self.messages.append(message)
        self.updated_at = datetime.now().isoformat()

    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, str]]:
        """Get message history in format suitable for LLM

        Args:
            limit: Maximum number of messages to return

        Returns:
            List of message dicts with 'role' and 'content'
        """
        messages = self.messages[-limit:] if limit else self.messages
        return [{"role": m.role, "content": m.content} for m in messages]

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "messages": [asdict(m) for m in self.messages],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
            "project_path": self.project_path
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        """Create session from dictionary"""
        messages = [Message(**m) for m in data.get("messages", [])]
        return cls(
            id=data["id"],
            name=data["name"],
            messages=messages,
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
            metadata=data.get("metadata", {}),
            project_path=data.get("project_path")
        )

    def to_markdown(self) -> str:
        """Export session as markdown

        Returns:
            Markdown formatted conversation
        """
        lines = [
            f"# Session: {self.name}",
            f"",
            f"**ID:** {self.id}",
            f"**Created:** {self.created_at}",
            f"**Updated:** {self.updated_at}",
            f"",
            "---",
            ""
        ]

        for msg in self.messages:
            if msg.role == "user":
                lines.append(f"## User ({msg.timestamp})")
            else:
                lines.append(f"## Assistant ({msg.timestamp})")

            lines.append("")
            lines.append(msg.content)
            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)


class SessionManager:
    """Manages conversation sessions"""

    def __init__(self, storage_path: Optional[str] = None):
        """Initialize session manager

        Args:
            storage_path: Path to store sessions
        """
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            self.storage_path = Path.home() / ".nc1709" / "sessions"

        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.index_file = self.storage_path / "index.json"

        # Currently active session
        self.current_session: Optional[Session] = None

        # Session index (id -> metadata)
        self._index: Dict[str, Dict[str, Any]] = {}
        self._load_index()

    def create_session(
        self,
        name: Optional[str] = None,
        project_path: Optional[str] = None
    ) -> Session:
        """Create a new session

        Args:
            name: Session name (auto-generated if None)
            project_path: Associated project path

        Returns:
            New Session instance
        """
        session_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if name is None:
            name = f"session_{timestamp}"

        session = Session(
            id=session_id,
            name=name,
            project_path=project_path
        )

        # Update index
        self._index[session_id] = {
            "id": session_id,
            "name": name,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "message_count": 0,
            "project_path": project_path
        }

        # Save session
        self._save_session(session)
        self._save_index()

        return session

    def load_session(self, session_id: str) -> Optional[Session]:
        """Load a session by ID

        Args:
            session_id: Session ID

        Returns:
            Session or None if not found
        """
        session_file = self.storage_path / f"{session_id}.json"

        if not session_file.exists():
            return None

        try:
            data = json.loads(session_file.read_text())
            return Session.from_dict(data)
        except Exception as e:
            print(f"Error loading session {session_id}: {e}")
            return None

    def save_session(self, session: Session):
        """Save a session

        Args:
            session: Session to save
        """
        self._save_session(session)

        # Update index
        self._index[session.id] = {
            "id": session.id,
            "name": session.name,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "message_count": len(session.messages),
            "project_path": session.project_path
        }
        self._save_index()

    def delete_session(self, session_id: str) -> bool:
        """Delete a session

        Args:
            session_id: Session ID

        Returns:
            True if deleted
        """
        session_file = self.storage_path / f"{session_id}.json"

        try:
            if session_file.exists():
                session_file.unlink()

            if session_id in self._index:
                del self._index[session_id]
                self._save_index()

            return True
        except Exception:
            return False

    def list_sessions(
        self,
        limit: Optional[int] = None,
        project_path: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List all sessions

        Args:
            limit: Maximum number to return
            project_path: Filter by project

        Returns:
            List of session metadata dicts
        """
        sessions = list(self._index.values())

        # Filter by project
        if project_path:
            sessions = [s for s in sessions if s.get("project_path") == project_path]

        # Sort by updated_at (newest first)
        sessions.sort(key=lambda x: x.get("updated_at", ""), reverse=True)

        # Limit
        if limit:
            sessions = sessions[:limit]

        return sessions

    def get_latest_session(self, project_path: Optional[str] = None) -> Optional[Session]:
        """Get the most recent session

        Args:
            project_path: Filter by project

        Returns:
            Most recent session or None
        """
        sessions = self.list_sessions(limit=1, project_path=project_path)

        if sessions:
            return self.load_session(sessions[0]["id"])

        return None

    def start_session(
        self,
        session_id: Optional[str] = None,
        name: Optional[str] = None,
        project_path: Optional[str] = None
    ) -> Session:
        """Start a session (load existing or create new)

        Args:
            session_id: Existing session ID to resume
            name: Name for new session
            project_path: Project path

        Returns:
            Active session
        """
        if session_id:
            session = self.load_session(session_id)
            if session:
                self.current_session = session
                return session

        # Create new session
        self.current_session = self.create_session(name=name, project_path=project_path)
        return self.current_session

    def add_message(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict] = None,
        auto_save: bool = True
    ):
        """Add a message to the current session

        Args:
            role: 'user' or 'assistant'
            content: Message content
            metadata: Additional metadata
            auto_save: Automatically save session
        """
        if self.current_session is None:
            self.current_session = self.create_session()

        self.current_session.add_message(role, content, metadata)

        if auto_save:
            self.save_session(self.current_session)

    def get_current_history(self, limit: Optional[int] = None) -> List[Dict[str, str]]:
        """Get history from current session

        Args:
            limit: Maximum messages

        Returns:
            Message history for LLM
        """
        if self.current_session is None:
            return []

        return self.current_session.get_history(limit)

    def export_session(
        self,
        session_id: str,
        output_path: str,
        format: str = "markdown"
    ) -> bool:
        """Export a session to file

        Args:
            session_id: Session ID
            output_path: Output file path
            format: Export format ('markdown' or 'json')

        Returns:
            True if successful
        """
        session = self.load_session(session_id)

        if session is None:
            return False

        output_file = Path(output_path)

        try:
            if format == "markdown":
                content = session.to_markdown()
            else:
                content = json.dumps(session.to_dict(), indent=2)

            output_file.write_text(content)
            return True
        except Exception as e:
            print(f"Error exporting session: {e}")
            return False

    def search_sessions(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search sessions by content

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of matching sessions with context
        """
        results = []
        query_lower = query.lower()

        for session_meta in self.list_sessions():
            session = self.load_session(session_meta["id"])
            if session is None:
                continue

            # Search in messages
            matches = []
            for i, msg in enumerate(session.messages):
                if query_lower in msg.content.lower():
                    matches.append({
                        "message_index": i,
                        "role": msg.role,
                        "preview": msg.content[:200]
                    })

            if matches:
                results.append({
                    "session": session_meta,
                    "matches": matches[:3]  # Limit matches per session
                })

        return results[:limit]

    def _save_session(self, session: Session):
        """Save session to disk"""
        session_file = self.storage_path / f"{session.id}.json"
        session_file.write_text(json.dumps(session.to_dict(), indent=2))

    def _load_index(self):
        """Load session index from disk"""
        if self.index_file.exists():
            try:
                self._index = json.loads(self.index_file.read_text())
            except Exception:
                self._index = {}

    def _save_index(self):
        """Save session index to disk"""
        self.index_file.write_text(json.dumps(self._index, indent=2))
