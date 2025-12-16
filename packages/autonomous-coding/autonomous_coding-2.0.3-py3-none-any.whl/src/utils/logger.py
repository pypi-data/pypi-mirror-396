"""
Dev-Friendly Logger
===================

Provides consistent logging with timestamps across the autonomous coding system.
"""

import sys
from datetime import datetime
from enum import Enum


class LogLevel(Enum):
    """Log levels for filtering output."""

    DEBUG = 0
    INFO = 1
    WARN = 2
    ERROR = 3
    SUCCESS = 4


# ANSI color codes for terminal output
COLORS = {
    LogLevel.DEBUG: "\033[90m",  # Gray
    LogLevel.INFO: "\033[36m",  # Cyan
    LogLevel.WARN: "\033[33m",  # Yellow
    LogLevel.ERROR: "\033[31m",  # Red
    LogLevel.SUCCESS: "\033[32m",  # Green
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
}

# Emoji/symbols for log levels
SYMBOLS = {
    LogLevel.DEBUG: "🔍",
    LogLevel.INFO: "ℹ️ ",
    LogLevel.WARN: "⚠️ ",
    LogLevel.ERROR: "❌",
    LogLevel.SUCCESS: "✅",
}


class Logger:
    """Simple logger with timestamps and colored output."""

    def __init__(
        self,
        name: str = "autonomous-coding",
        min_level: LogLevel = LogLevel.INFO,
        use_colors: bool = True,
        use_emoji: bool = True,
    ):
        """
        Initialize logger.

        Args:
            name: Logger name (shown in output)
            min_level: Minimum log level to display
            use_colors: Whether to use ANSI colors
            use_emoji: Whether to use emoji symbols
        """
        self.name = name
        self.min_level = min_level
        self.use_colors = use_colors and sys.stdout.isatty()
        self.use_emoji = use_emoji

    def _format_timestamp(self) -> str:
        """Get dev-friendly timestamp: YYYY-MM-DD HH:MM:SS"""
        now = datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")

    def _colorize(self, text: str, level: LogLevel) -> str:
        """Apply color to text based on log level."""
        if not self.use_colors:
            return text
        return f"{COLORS[level]}{text}{COLORS['reset']}"

    def _format_message(
        self,
        level: LogLevel,
        message: str,
        context: str | None = None,
    ) -> str:
        """Format a log message with timestamp, level, and optional context."""
        timestamp = self._format_timestamp()

        # Level indicator
        level_str = SYMBOLS.get(level, "") if self.use_emoji else f"[{level.name}]"

        # Colorize timestamp (dim)
        if self.use_colors:
            timestamp = f"{COLORS['dim']}{timestamp}{COLORS['reset']}"

        # Build message parts
        parts = [timestamp, level_str]

        if context:
            context_str = f"[{context}]"
            if self.use_colors:
                context_str = f"{COLORS['bold']}{context_str}{COLORS['reset']}"
            parts.append(context_str)

        # Colorize the main message
        colored_message = self._colorize(message, level)
        parts.append(colored_message)

        return " ".join(parts)

    def _log(
        self,
        level: LogLevel,
        message: str,
        context: str | None = None,
    ) -> None:
        """Internal log method."""
        if level.value < self.min_level.value:
            return

        formatted = self._format_message(level, message, context)
        print(formatted, flush=True)

    def debug(self, message: str, context: str | None = None) -> None:
        """Log debug message."""
        self._log(LogLevel.DEBUG, message, context)

    def info(self, message: str, context: str | None = None) -> None:
        """Log info message."""
        self._log(LogLevel.INFO, message, context)

    def warn(self, message: str, context: str | None = None) -> None:
        """Log warning message."""
        self._log(LogLevel.WARN, message, context)

    def error(self, message: str, context: str | None = None) -> None:
        """Log error message."""
        self._log(LogLevel.ERROR, message, context)

    def success(self, message: str, context: str | None = None) -> None:
        """Log success message."""
        self._log(LogLevel.SUCCESS, message, context)

    def section(self, title: str) -> None:
        """Print a section header."""
        timestamp = self._format_timestamp()
        if self.use_colors:
            timestamp = f"{COLORS['dim']}{timestamp}{COLORS['reset']}"
            line = f"{COLORS['bold']}{'=' * 60}{COLORS['reset']}"
            title = f"{COLORS['bold']}{title}{COLORS['reset']}"
        else:
            line = "=" * 60

        print(f"\n{timestamp} {line}")
        print(f"{timestamp} {title}")
        print(f"{timestamp} {line}\n")

    def tool(self, tool_name: str, status: str = "executing") -> None:
        """Log tool execution."""
        if self.use_colors:
            tool_name = f"{COLORS['bold']}{tool_name}{COLORS['reset']}"
        self.info(f"Tool: {tool_name} ({status})", "SDK")

    def api(self, message: str) -> None:
        """Log API-related message."""
        self.info(message, "API")

    def agent(self, message: str, agent_type: str = "Agent") -> None:
        """Log agent-related message."""
        self.info(message, agent_type)


# Global logger instance
_logger: Logger | None = None


def get_logger() -> Logger:
    """Get or create the global logger instance."""
    global _logger
    if _logger is None:
        _logger = Logger()
    return _logger


def set_log_level(level: LogLevel) -> None:
    """Set the global log level."""
    get_logger().min_level = level


# Convenience functions using global logger
def log_debug(message: str, context: str | None = None) -> None:
    """Log debug message using global logger."""
    get_logger().debug(message, context)


def log_info(message: str, context: str | None = None) -> None:
    """Log info message using global logger."""
    get_logger().info(message, context)


def log_warn(message: str, context: str | None = None) -> None:
    """Log warning message using global logger."""
    get_logger().warn(message, context)


def log_error(message: str, context: str | None = None) -> None:
    """Log error message using global logger."""
    get_logger().error(message, context)


def log_success(message: str, context: str | None = None) -> None:
    """Log success message using global logger."""
    get_logger().success(message, context)


def log_section(title: str) -> None:
    """Print a section header using global logger."""
    get_logger().section(title)


def log_tool(tool_name: str, status: str = "executing") -> None:
    """Log tool execution using global logger."""
    get_logger().tool(tool_name, status)


def log_api(message: str) -> None:
    """Log API message using global logger."""
    get_logger().api(message)


def log_agent(message: str, agent_type: str = "Agent") -> None:
    """Log agent message using global logger."""
    get_logger().agent(message, agent_type)
