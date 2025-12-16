"""
Structured logging for NC1709 CLI
Provides consistent, configurable logging across all modules
"""
import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class NC1709Logger:
    """Custom logger with colored console output and file logging"""

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m"
    }

    # Emoji prefixes for different log levels
    EMOJIS = {
        "DEBUG": "🔍",
        "INFO": "✅",
        "WARNING": "⚠️",
        "ERROR": "❌",
        "CRITICAL": "🚨"
    }

    def __init__(
        self,
        name: str = "nc1709",
        level: int = logging.INFO,
        log_file: Optional[str] = None,
        use_colors: bool = True,
        use_emojis: bool = True
    ):
        """Initialize the logger

        Args:
            name: Logger name
            level: Logging level
            log_file: Optional path to log file
            use_colors: Whether to use colored output
            use_emojis: Whether to use emoji prefixes
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.handlers = []  # Clear any existing handlers

        self.use_colors = use_colors
        self.use_emojis = use_emojis

        # Console handler
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(level)
        console_handler.setFormatter(self._create_formatter(colored=use_colors))
        self.logger.addHandler(console_handler)

        # File handler (if specified)
        if log_file:
            log_path = Path(log_file).expanduser()
            log_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_path)
            file_handler.setLevel(logging.DEBUG)  # Log everything to file
            file_handler.setFormatter(self._create_formatter(colored=False))
            self.logger.addHandler(file_handler)

    def _create_formatter(self, colored: bool = False) -> logging.Formatter:
        """Create a log formatter

        Args:
            colored: Whether to include color codes

        Returns:
            Logging formatter
        """
        if colored:
            return ColoredFormatter(self.COLORS, self.EMOJIS, self.use_emojis)
        else:
            return logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )

    def debug(self, msg: str, *args, **kwargs):
        """Log debug message"""
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        """Log info message"""
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        """Log warning message"""
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        """Log error message"""
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs):
        """Log critical message"""
        self.logger.critical(msg, *args, **kwargs)

    def set_level(self, level: int):
        """Set logging level"""
        self.logger.setLevel(level)
        for handler in self.logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.setLevel(level)


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors and emojis"""

    def __init__(self, colors: dict, emojis: dict, use_emojis: bool = True):
        super().__init__()
        self.colors = colors
        self.emojis = emojis
        self.use_emojis = use_emojis

    def format(self, record: logging.LogRecord) -> str:
        level = record.levelname
        color = self.colors.get(level, "")
        reset = self.colors.get("RESET", "")
        emoji = self.emojis.get(level, "") if self.use_emojis else ""

        # Format: emoji [LEVEL] message
        if emoji:
            formatted = f"{emoji} {color}[{level}]{reset} {record.getMessage()}"
        else:
            formatted = f"{color}[{level}]{reset} {record.getMessage()}"

        return formatted


# Global logger instance
_logger: Optional[NC1709Logger] = None


def get_logger(
    name: str = "nc1709",
    level: Optional[int] = None,
    log_file: Optional[str] = None
) -> NC1709Logger:
    """Get or create the global logger instance

    Args:
        name: Logger name
        level: Logging level (default: INFO)
        log_file: Optional log file path

    Returns:
        NC1709Logger instance
    """
    global _logger

    if _logger is None:
        from .config import get_config
        config = get_config()

        # Get settings from config
        verbose = config.get("ui.verbose", False)
        use_colors = config.get("ui.color", True)
        log_dir = Path.home() / ".nc1709" / "logs"

        if level is None:
            level = logging.DEBUG if verbose else logging.INFO

        if log_file is None:
            log_file = str(log_dir / f"nc1709_{datetime.now().strftime('%Y%m%d')}.log")

        _logger = NC1709Logger(
            name=name,
            level=level,
            log_file=log_file,
            use_colors=use_colors,
            use_emojis=True
        )

    return _logger


def reset_logger():
    """Reset the global logger instance"""
    global _logger
    _logger = None
