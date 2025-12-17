"""
Conversation Logger for NC1709
Logs all conversations per session with user tracking.
"""
import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field, asdict


@dataclass
class ConversationEntry:
    """A single entry in a conversation"""
    timestamp: str
    role: str  # 'user', 'assistant', 'tool', 'system', 'error'
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "ConversationEntry":
        return cls(**data)


@dataclass
class SessionInfo:
    """Information about a session"""
    session_id: str
    started_at: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    user_id: Optional[str] = None
    working_directory: Optional[str] = None
    mode: str = "remote"  # 'remote', 'local', 'agent'

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "SessionInfo":
        return cls(**data)


class ConversationLogger:
    """
    Logs conversations to files per session.

    Features:
    - Per-session log files
    - IP address tracking (for remote mode)
    - User agent tracking
    - Tool call logging
    - Error logging
    - JSON format for easy parsing
    """

    # Default log directory
    LOG_DIR = "logs"

    def __init__(
        self,
        base_dir: Optional[Path] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        user_id: Optional[str] = None,
        mode: str = "remote"
    ):
        """
        Initialize the conversation logger.

        Args:
            base_dir: Base directory for logs (defaults to ~/.nc1709)
            session_id: Unique session ID (auto-generated if not provided)
            ip_address: Client IP address (for remote mode)
            user_agent: Client user agent string
            user_id: Optional user identifier
            mode: Operation mode (remote, local, agent)
        """
        # Determine base directory
        if base_dir:
            self.base_dir = Path(base_dir)
        else:
            self.base_dir = Path.home() / ".nc1709"

        self.log_dir = self.base_dir / self.LOG_DIR
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Session info
        self.session_id = session_id or self._generate_session_id()
        self.session_info = SessionInfo(
            session_id=self.session_id,
            started_at=datetime.now().isoformat(),
            ip_address=ip_address,
            user_agent=user_agent,
            user_id=user_id,
            working_directory=str(Path.cwd()),
            mode=mode
        )

        # Conversation entries
        self.entries: List[ConversationEntry] = []

        # Log file path
        self.log_file = self._get_log_file_path()

        # Initialize log file with session info
        self._init_log_file()

    def _generate_session_id(self) -> str:
        """Generate a unique session ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique = uuid.uuid4().hex[:8]
        return f"{timestamp}_{unique}"

    def _get_log_file_path(self) -> Path:
        """Get the log file path for this session"""
        # Organize by date
        date_str = datetime.now().strftime("%Y-%m-%d")
        date_dir = self.log_dir / date_str
        date_dir.mkdir(exist_ok=True)

        return date_dir / f"session_{self.session_id}.json"

    def _init_log_file(self) -> None:
        """Initialize the log file with session info"""
        data = {
            "session": self.session_info.to_dict(),
            "entries": []
        }
        self._write_log(data)

    def _write_log(self, data: Dict) -> None:
        """Write data to log file"""
        try:
            self.log_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        except Exception as e:
            # Silently fail - logging shouldn't break the app
            pass

    def _append_entry(self, entry: ConversationEntry) -> None:
        """Append an entry to the log file"""
        self.entries.append(entry)

        try:
            # Read current log
            if self.log_file.exists():
                data = json.loads(self.log_file.read_text())
            else:
                data = {"session": self.session_info.to_dict(), "entries": []}

            # Append entry
            data["entries"].append(entry.to_dict())

            # Write back
            self._write_log(data)
        except Exception:
            pass

    def log_user_message(self, message: str, metadata: Optional[Dict] = None) -> None:
        """Log a user message"""
        entry = ConversationEntry(
            timestamp=datetime.now().isoformat(),
            role="user",
            content=message,
            metadata=metadata or {}
        )
        self._append_entry(entry)

    def log_assistant_message(self, message: str, metadata: Optional[Dict] = None) -> None:
        """Log an assistant response"""
        entry = ConversationEntry(
            timestamp=datetime.now().isoformat(),
            role="assistant",
            content=message,
            metadata=metadata or {}
        )
        self._append_entry(entry)

    def log_tool_call(
        self,
        tool_name: str,
        parameters: Dict,
        result: Optional[str] = None,
        success: bool = True,
        duration_ms: Optional[int] = None
    ) -> None:
        """Log a tool call"""
        entry = ConversationEntry(
            timestamp=datetime.now().isoformat(),
            role="tool",
            content=result or "",
            metadata={
                "tool_name": tool_name,
                "parameters": parameters,
                "success": success,
                "duration_ms": duration_ms
            }
        )
        self._append_entry(entry)

    def log_error(self, error: str, context: Optional[Dict] = None) -> None:
        """Log an error"""
        entry = ConversationEntry(
            timestamp=datetime.now().isoformat(),
            role="error",
            content=error,
            metadata=context or {}
        )
        self._append_entry(entry)

    def log_system(self, message: str, metadata: Optional[Dict] = None) -> None:
        """Log a system message"""
        entry = ConversationEntry(
            timestamp=datetime.now().isoformat(),
            role="system",
            content=message,
            metadata=metadata or {}
        )
        self._append_entry(entry)

    def update_session_info(self, **kwargs) -> None:
        """Update session info (e.g., when IP becomes available)"""
        for key, value in kwargs.items():
            if hasattr(self.session_info, key):
                setattr(self.session_info, key, value)

        # Update log file
        try:
            if self.log_file.exists():
                data = json.loads(self.log_file.read_text())
                data["session"] = self.session_info.to_dict()
                self._write_log(data)
        except Exception:
            pass

    def get_session_summary(self) -> Dict:
        """Get a summary of the current session"""
        user_messages = sum(1 for e in self.entries if e.role == "user")
        assistant_messages = sum(1 for e in self.entries if e.role == "assistant")
        tool_calls = sum(1 for e in self.entries if e.role == "tool")
        errors = sum(1 for e in self.entries if e.role == "error")

        return {
            "session_id": self.session_id,
            "started_at": self.session_info.started_at,
            "ip_address": self.session_info.ip_address,
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "tool_calls": tool_calls,
            "errors": errors,
            "total_entries": len(self.entries)
        }

    @classmethod
    def list_sessions(
        cls,
        base_dir: Optional[Path] = None,
        date: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict]:
        """
        List recent sessions.

        Args:
            base_dir: Base directory for logs
            date: Filter by date (YYYY-MM-DD format)
            limit: Maximum number of sessions to return

        Returns:
            List of session summaries
        """
        if base_dir:
            log_dir = Path(base_dir) / cls.LOG_DIR
        else:
            log_dir = Path.home() / ".nc1709" / cls.LOG_DIR

        if not log_dir.exists():
            return []

        sessions = []

        # Get date directories
        if date:
            date_dirs = [log_dir / date] if (log_dir / date).exists() else []
        else:
            date_dirs = sorted(log_dir.iterdir(), reverse=True)

        for date_dir in date_dirs:
            if not date_dir.is_dir():
                continue

            for log_file in sorted(date_dir.glob("session_*.json"), reverse=True):
                try:
                    data = json.loads(log_file.read_text())
                    session = data.get("session", {})
                    entries = data.get("entries", [])

                    sessions.append({
                        "session_id": session.get("session_id"),
                        "started_at": session.get("started_at"),
                        "ip_address": session.get("ip_address"),
                        "mode": session.get("mode"),
                        "entry_count": len(entries),
                        "file": str(log_file)
                    })

                    if len(sessions) >= limit:
                        return sessions
                except Exception:
                    continue

        return sessions

    @classmethod
    def load_session(cls, session_id: str, base_dir: Optional[Path] = None) -> Optional[Dict]:
        """
        Load a specific session by ID.

        Args:
            session_id: The session ID to load
            base_dir: Base directory for logs

        Returns:
            Full session data or None if not found
        """
        if base_dir:
            log_dir = Path(base_dir) / cls.LOG_DIR
        else:
            log_dir = Path.home() / ".nc1709" / cls.LOG_DIR

        if not log_dir.exists():
            return None

        # Search all date directories
        for date_dir in log_dir.iterdir():
            if not date_dir.is_dir():
                continue

            log_file = date_dir / f"session_{session_id}.json"
            if log_file.exists():
                try:
                    return json.loads(log_file.read_text())
                except Exception:
                    return None

        return None


# Global logger instance (initialized per session)
_current_logger: Optional[ConversationLogger] = None


def get_logger() -> Optional[ConversationLogger]:
    """Get the current conversation logger"""
    return _current_logger


def init_logger(
    session_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    user_id: Optional[str] = None,
    mode: str = "remote"
) -> ConversationLogger:
    """Initialize a new conversation logger for this session"""
    global _current_logger
    _current_logger = ConversationLogger(
        session_id=session_id,
        ip_address=ip_address,
        user_agent=user_agent,
        user_id=user_id,
        mode=mode
    )
    return _current_logger


def log_user(message: str, metadata: Optional[Dict] = None) -> None:
    """Convenience function to log user message"""
    if _current_logger:
        _current_logger.log_user_message(message, metadata)


def log_assistant(message: str, metadata: Optional[Dict] = None) -> None:
    """Convenience function to log assistant message"""
    if _current_logger:
        _current_logger.log_assistant_message(message, metadata)


def log_tool(
    tool_name: str,
    parameters: Dict,
    result: Optional[str] = None,
    success: bool = True,
    duration_ms: Optional[int] = None
) -> None:
    """Convenience function to log tool call"""
    if _current_logger:
        _current_logger.log_tool_call(tool_name, parameters, result, success, duration_ms)


def log_error(error: str, context: Optional[Dict] = None) -> None:
    """Convenience function to log error"""
    if _current_logger:
        _current_logger.log_error(error, context)


def log_system(message: str, metadata: Optional[Dict] = None) -> None:
    """Convenience function to log system message"""
    if _current_logger:
        _current_logger.log_system(message, metadata)
