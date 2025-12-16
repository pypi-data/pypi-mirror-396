"""Hook management for Claude CLI SDK.

Provides programmatic hook registration and management for Claude CLI.
Hooks allow you to intercept and modify Claude's behavior at various points.

Hook Types:
    - PreToolUse: Called before a tool is executed (can block/modify)
    - PostToolUse: Called after a tool completes
    - Notification: Called on notifications
    - Stop: Called when Claude stops

Example:
    >>> from claude_cli_sdk import HookManager, Hook
    >>>
    >>> # Create a hook manager
    >>> hooks = HookManager()
    >>>
    >>> # Add a pre-tool hook for Bash commands
    >>> hooks.add_pre_tool_use(
    ...     Hook(
    ...         matcher="Bash",
    ...         command="echo 'Bash command intercepted'",
    ...         timeout=5000
    ...     )
    ... )
    >>>
    >>> # Use with Claude
    >>> config = ClaudeConfig()
    >>> hooks.apply_to_config(config)
"""

import json
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional, Union, Callable, Any


class HookType(Enum):
    """Types of hooks available in Claude CLI.

    Attributes:
        PRE_TOOL_USE: Called before tool execution
        POST_TOOL_USE: Called after tool execution
        NOTIFICATION: Called on notifications
        STOP: Called when Claude stops
    """
    PRE_TOOL_USE = "PreToolUse"
    POST_TOOL_USE = "PostToolUse"
    NOTIFICATION = "Notification"
    STOP = "Stop"


@dataclass
class Hook:
    """A single hook configuration.

    Attributes:
        matcher: Tool name pattern to match (e.g., "Bash", "Read", "Edit")
                 Use "*" for all tools. Can be a regex pattern.
        command: Shell command to execute when hook triggers
        timeout: Timeout in milliseconds (default: 60000)

    Example:
        >>> # Block all Bash commands that contain 'rm'
        >>> hook = Hook(
        ...     matcher="Bash",
        ...     command="validate_bash.sh",
        ...     timeout=5000
        ... )
    """
    matcher: str = "*"
    command: str = ""
    timeout: int = 60000


@dataclass
class HookConfig:
    """Complete hook configuration for Claude CLI.

    Attributes:
        pre_tool_use: List of pre-tool-use hooks
        post_tool_use: List of post-tool-use hooks
        notification: List of notification hooks
        stop: List of stop hooks
    """
    pre_tool_use: list[Hook] = field(default_factory=list)
    post_tool_use: list[Hook] = field(default_factory=list)
    notification: list[Hook] = field(default_factory=list)
    stop: list[Hook] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary format for settings.json."""
        result = {}

        if self.pre_tool_use:
            result["PreToolUse"] = [
                {"matcher": h.matcher, "hooks": [{"command": h.command, "timeout": h.timeout}]}
                for h in self.pre_tool_use
            ]

        if self.post_tool_use:
            result["PostToolUse"] = [
                {"matcher": h.matcher, "hooks": [{"command": h.command, "timeout": h.timeout}]}
                for h in self.post_tool_use
            ]

        if self.notification:
            result["Notification"] = [
                {"hooks": [{"command": h.command, "timeout": h.timeout}]}
                for h in self.notification
            ]

        if self.stop:
            result["Stop"] = [
                {"hooks": [{"command": h.command, "timeout": h.timeout}]}
                for h in self.stop
            ]

        return result


class HookManager:
    """Manages hooks for Claude CLI SDK.

    Provides a programmatic interface to register, manage, and apply hooks
    without manually editing settings.json files.

    Example:
        >>> manager = HookManager()
        >>>
        >>> # Add hooks programmatically
        >>> manager.add_pre_tool_use(Hook(matcher="Bash", command="validate.sh"))
        >>> manager.add_post_tool_use(Hook(matcher="*", command="log_tool.sh"))
        >>>
        >>> # Apply to project settings
        >>> manager.save_to_project()
        >>>
        >>> # Or get as dict for inline use
        >>> hooks_dict = manager.to_dict()
    """

    def __init__(self, project_dir: Optional[Union[str, Path]] = None):
        """Initialize HookManager.

        Args:
            project_dir: Project directory for .claude/settings.json
                        Defaults to current working directory.
        """
        self.project_dir = Path(project_dir) if project_dir else Path.cwd()
        self.config = HookConfig()
        self._python_hooks: dict[str, list[Callable]] = {
            "pre_tool_use": [],
            "post_tool_use": [],
            "notification": [],
            "stop": []
        }

    def add_pre_tool_use(self, hook: Hook) -> "HookManager":
        """Add a pre-tool-use hook.

        Pre-tool hooks are called before a tool executes.
        They can block execution by returning non-zero exit code.

        Args:
            hook: Hook configuration

        Returns:
            Self for chaining

        Example:
            >>> manager.add_pre_tool_use(
            ...     Hook(matcher="Bash", command="./scripts/validate_bash.sh")
            ... )
        """
        self.config.pre_tool_use.append(hook)
        return self

    def add_post_tool_use(self, hook: Hook) -> "HookManager":
        """Add a post-tool-use hook.

        Post-tool hooks are called after a tool completes.

        Args:
            hook: Hook configuration

        Returns:
            Self for chaining
        """
        self.config.post_tool_use.append(hook)
        return self

    def add_notification(self, hook: Hook) -> "HookManager":
        """Add a notification hook.

        Notification hooks are called when Claude emits notifications.

        Args:
            hook: Hook configuration

        Returns:
            Self for chaining
        """
        self.config.notification.append(hook)
        return self

    def add_stop(self, hook: Hook) -> "HookManager":
        """Add a stop hook.

        Stop hooks are called when Claude stops execution.

        Args:
            hook: Hook configuration

        Returns:
            Self for chaining
        """
        self.config.stop.append(hook)
        return self

    def clear(self) -> "HookManager":
        """Clear all hooks.

        Returns:
            Self for chaining
        """
        self.config = HookConfig()
        return self

    def to_dict(self) -> dict:
        """Convert hooks to dictionary format.

        Returns:
            Dictionary suitable for settings.json
        """
        return self.config.to_dict()

    def _get_settings_path(self, scope: str = "project") -> Path:
        """Get settings file path.

        Args:
            scope: "project" for .claude/settings.json,
                   "user" for ~/.claude/settings.json

        Returns:
            Path to settings file
        """
        if scope == "user":
            return Path.home() / ".claude" / "settings.json"
        return self.project_dir / ".claude" / "settings.json"

    def _read_settings(self, path: Path) -> dict:
        """Read existing settings file.

        Args:
            path: Path to settings file

        Returns:
            Parsed settings or empty dict
        """
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return {}
        return {}

    def _write_settings(self, path: Path, settings: dict) -> None:
        """Write settings to file.

        Args:
            path: Path to settings file
            settings: Settings dictionary to write
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(settings, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    def save_to_project(self) -> Path:
        """Save hooks to project settings (.claude/settings.json).

        Creates the .claude directory if it doesn't exist.
        Merges with existing settings.

        Returns:
            Path to the saved settings file

        Example:
            >>> manager.add_pre_tool_use(Hook(matcher="Bash", command="validate.sh"))
            >>> manager.save_to_project()
            PosixPath('.claude/settings.json')
        """
        path = self._get_settings_path("project")
        settings = self._read_settings(path)
        settings["hooks"] = self.to_dict()
        self._write_settings(path, settings)
        return path

    def save_to_user(self) -> Path:
        """Save hooks to user settings (~/.claude/settings.json).

        These hooks apply globally to all Claude CLI sessions.

        Returns:
            Path to the saved settings file
        """
        path = self._get_settings_path("user")
        settings = self._read_settings(path)
        settings["hooks"] = self.to_dict()
        self._write_settings(path, settings)
        return path

    def load_from_project(self) -> "HookManager":
        """Load hooks from project settings.

        Returns:
            Self for chaining
        """
        path = self._get_settings_path("project")
        settings = self._read_settings(path)
        self._load_from_dict(settings.get("hooks", {}))
        return self

    def load_from_user(self) -> "HookManager":
        """Load hooks from user settings.

        Returns:
            Self for chaining
        """
        path = self._get_settings_path("user")
        settings = self._read_settings(path)
        self._load_from_dict(settings.get("hooks", {}))
        return self

    def _load_from_dict(self, hooks_dict: dict) -> None:
        """Load hooks from dictionary.

        Args:
            hooks_dict: Hooks dictionary from settings
        """
        self.config = HookConfig()

        for hook_entry in hooks_dict.get("PreToolUse", []):
            matcher = hook_entry.get("matcher", "*")
            for h in hook_entry.get("hooks", []):
                self.config.pre_tool_use.append(Hook(
                    matcher=matcher,
                    command=h.get("command", ""),
                    timeout=h.get("timeout", 60000)
                ))

        for hook_entry in hooks_dict.get("PostToolUse", []):
            matcher = hook_entry.get("matcher", "*")
            for h in hook_entry.get("hooks", []):
                self.config.post_tool_use.append(Hook(
                    matcher=matcher,
                    command=h.get("command", ""),
                    timeout=h.get("timeout", 60000)
                ))

        for hook_entry in hooks_dict.get("Notification", []):
            for h in hook_entry.get("hooks", []):
                self.config.notification.append(Hook(
                    command=h.get("command", ""),
                    timeout=h.get("timeout", 60000)
                ))

        for hook_entry in hooks_dict.get("Stop", []):
            for h in hook_entry.get("hooks", []):
                self.config.stop.append(Hook(
                    command=h.get("command", ""),
                    timeout=h.get("timeout", 60000)
                ))

    def remove_from_project(self) -> None:
        """Remove hooks from project settings.

        Keeps other settings intact.
        """
        path = self._get_settings_path("project")
        settings = self._read_settings(path)
        if "hooks" in settings:
            del settings["hooks"]
            self._write_settings(path, settings)

    def remove_from_user(self) -> None:
        """Remove hooks from user settings.

        Keeps other settings intact.
        """
        path = self._get_settings_path("user")
        settings = self._read_settings(path)
        if "hooks" in settings:
            del settings["hooks"]
            self._write_settings(path, settings)


# Convenience functions

def create_bash_validator(script_path: str, timeout: int = 5000) -> Hook:
    """Create a hook that validates Bash commands.

    Args:
        script_path: Path to validation script
        timeout: Timeout in milliseconds

    Returns:
        Configured Hook

    Example:
        >>> hook = create_bash_validator("./scripts/validate_bash.sh")
        >>> manager.add_pre_tool_use(hook)
    """
    return Hook(matcher="Bash", command=script_path, timeout=timeout)


def create_file_logger(log_script: str, tools: str = "*") -> Hook:
    """Create a hook that logs tool usage.

    Args:
        log_script: Path to logging script
        tools: Tool pattern to match (default: all tools)

    Returns:
        Configured Hook
    """
    return Hook(matcher=tools, command=log_script)


def create_edit_backup(backup_script: str) -> Hook:
    """Create a hook that backs up files before editing.

    Args:
        backup_script: Path to backup script

    Returns:
        Configured Hook for Edit tool
    """
    return Hook(matcher="Edit", command=backup_script)


def quick_hook_setup(
    project_dir: Optional[Union[str, Path]] = None,
    validate_bash: Optional[str] = None,
    log_tools: Optional[str] = None,
    backup_edits: Optional[str] = None
) -> HookManager:
    """Quick setup for common hook configurations.

    Args:
        project_dir: Project directory
        validate_bash: Path to Bash validation script
        log_tools: Path to tool logging script
        backup_edits: Path to edit backup script

    Returns:
        Configured HookManager

    Example:
        >>> hooks = quick_hook_setup(
        ...     validate_bash="./scripts/validate.sh",
        ...     log_tools="./scripts/log.sh"
        ... )
        >>> hooks.save_to_project()
    """
    manager = HookManager(project_dir)

    if validate_bash:
        manager.add_pre_tool_use(create_bash_validator(validate_bash))

    if log_tools:
        manager.add_post_tool_use(create_file_logger(log_tools))

    if backup_edits:
        manager.add_pre_tool_use(create_edit_backup(backup_edits))

    return manager
