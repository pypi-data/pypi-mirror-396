"""Custom exceptions for Claude CLI SDK."""


class ClaudeSDKError(Exception):
    """Base exception for Claude CLI SDK."""
    pass


class CLINotFoundError(ClaudeSDKError):
    """Raised when Claude CLI is not found or not executable."""

    def __init__(self, message: str = "Claude CLI not found"):
        self.message = message
        super().__init__(
            f"{message}. Please install Claude CLI and ensure it's in your PATH. "
            "Visit https://claude.ai/download for installation instructions."
        )


class SessionNotFoundError(ClaudeSDKError):
    """Raised when attempting to continue a non-existent session."""

    def __init__(self, message: str = "No previous session found"):
        self.message = message
        super().__init__(f"{message}. Call run() first to create a session.")


class SessionNotStartedError(ClaudeSDKError):
    """Raised when attempting to use a session that hasn't been started."""

    def __init__(self, message: str = "Session not started"):
        self.message = message
        super().__init__(f"{message}. Call start_session() first.")


class ExecutionTimeoutError(ClaudeSDKError):
    """Raised when execution exceeds the timeout limit."""

    def __init__(self, timeout: float):
        self.timeout = timeout
        super().__init__(f"Execution timed out after {timeout} seconds.")


class ExecutionCancelledError(ClaudeSDKError):
    """Raised when execution is cancelled by user."""

    def __init__(self, message: str = "Execution cancelled by user"):
        self.message = message
        super().__init__(message)


class ResourceLimitExceededError(ClaudeSDKError):
    """Raised when system resource limits are exceeded."""

    def __init__(self, resource: str, limit: float, current: float):
        self.resource = resource
        self.limit = limit
        self.current = current
        super().__init__(
            f"{resource} limit exceeded: {current:.1f}% (limit: {limit:.1f}%)"
        )


class InvalidConfigError(ClaudeSDKError):
    """Raised when configuration is invalid."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(f"Invalid configuration: {message}")
