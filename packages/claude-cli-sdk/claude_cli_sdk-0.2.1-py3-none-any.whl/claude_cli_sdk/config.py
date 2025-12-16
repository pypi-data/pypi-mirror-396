"""Configuration and Enum definitions for Claude CLI SDK."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class PermissionMode(Enum):
    """Permission mode for Claude CLI.

    Attributes:
        DEFAULT: Default mode (requires user confirmation)
        ACCEPT_EDITS: Auto-approve file edits
        BYPASS_PERMISSIONS: Bypass all permissions (use with caution!)
    """
    DEFAULT = "default"
    ACCEPT_EDITS = "acceptEdits"
    BYPASS_PERMISSIONS = "bypassPermissions"


class OutputFormat(Enum):
    """Output format for Claude CLI.

    Attributes:
        TEXT: Plain text output
        JSON: JSON output
        STREAM_JSON: JSON line stream (SDK default)
    """
    TEXT = "text"
    JSON = "json"
    STREAM_JSON = "stream-json"


@dataclass
class ClaudeConfig:
    """Claude CLI configuration.

    Attributes:
        model: Model to use (e.g., "claude-3-opus", "claude-3-sonnet")
        permission_mode: Permission mode
        output_format: Output format
        setting_sources: Setting sources (for loading Skills, Hooks, CLAUDE.md)
        allowed_tools: List of allowed tools
        disallowed_tools: List of disallowed tools
        mcp_config: Path to MCP configuration file
        cwd: Working directory
        input_format: Input format (for bidirectional communication)
        max_turns: Maximum number of turns
        system_prompt: System prompt
        claude_path: Path to Claude CLI (default: "claude")
        timeout: Timeout in seconds

    Example:
        >>> config = ClaudeConfig(
        ...     model="claude-3-sonnet",
        ...     permission_mode=PermissionMode.ACCEPT_EDITS,
        ...     allowed_tools=["Bash", "Read", "Write"],
        ...     max_turns=5
        ... )
    """
    # Basic settings
    model: Optional[str] = None
    permission_mode: PermissionMode = PermissionMode.ACCEPT_EDITS
    output_format: OutputFormat = OutputFormat.STREAM_JSON

    # Setting sources (for loading skills, CLAUDE.md, subagents)
    setting_sources: list[str] = field(default_factory=lambda: ["user", "project"])

    # Tool permissions
    allowed_tools: Optional[list[str]] = None
    disallowed_tools: Optional[list[str]] = None

    # MCP configuration
    mcp_config: Optional[str] = None

    # Working directory
    cwd: Optional[str] = None

    # Bidirectional communication
    input_format: str = "stream-json"

    # Other settings
    max_turns: Optional[int] = None
    system_prompt: Optional[str] = None

    # CLI path
    claude_path: str = "claude"

    # Timeout
    timeout: Optional[float] = None
