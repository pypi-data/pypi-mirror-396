"""Claude CLI SDK Client."""

import json
import asyncio
import subprocess
import shutil
from asyncio.subprocess import Process
from typing import Optional, Callable, AsyncIterator, Any, Union
from pathlib import Path

from .config import ClaudeConfig, OutputFormat
from .models import StreamEvent, ClaudeResult
from .exceptions import (
    CLINotFoundError,
    SessionNotFoundError,
    SessionNotStartedError,
    ExecutionTimeoutError,
    ExecutionCancelledError,
)


def _verify_claude_cli(path: str) -> str:
    """Verify Claude CLI exists and is executable.

    Args:
        path: Path to Claude CLI or "claude" for PATH lookup

    Returns:
        Verified path to Claude CLI

    Raises:
        CLINotFoundError: If Claude CLI is not found or not executable
    """
    if path == "claude":
        found = shutil.which("claude")
        if found:
            return found
        raise CLINotFoundError("Claude CLI not found in PATH")

    path_obj = Path(path)
    if not path_obj.exists():
        raise CLINotFoundError(f"Claude CLI not found at: {path}")

    if not path_obj.is_file():
        raise CLINotFoundError(f"Claude CLI path is not a file: {path}")

    # Check if executable (Unix)
    import os
    if not os.access(path, os.X_OK):
        raise CLINotFoundError(f"Claude CLI is not executable: {path}")

    return path


def check_claude_cli(path: str = "claude") -> bool:
    """Check if Claude CLI is available.

    Args:
        path: Path to Claude CLI (default: "claude" for PATH lookup)

    Returns:
        True if Claude CLI is available, False otherwise

    Example:
        >>> if check_claude_cli():
        ...     print("Claude CLI is ready!")
    """
    try:
        _verify_claude_cli(path)
        return True
    except CLINotFoundError:
        return False


# Callback type definitions
OnMessageCallback = Callable[[StreamEvent], None]
OnToolUseCallback = Callable[[dict], None]
OnErrorCallback = Callable[[str], None]
OnResultCallback = Callable[[dict], None]
OnProgressCallback = Callable[[str, dict], None]  # (event_type, data)


class CancellationToken:
    """Cancellation token for cancelling operations in progress.

    Use this to cancel long-running Claude operations.

    Example:
        >>> token = CancellationToken()
        >>> task = asyncio.create_task(claude.run("Long task", cancel_token=token))
        >>> # Later, to cancel:
        >>> token.cancel()
    """

    def __init__(self):
        self._cancelled = False

    def cancel(self):
        """Request cancellation."""
        self._cancelled = True

    @property
    def is_cancelled(self) -> bool:
        """Check if cancellation has been requested."""
        return self._cancelled

    def reset(self):
        """Reset the token for reuse."""
        self._cancelled = False


class Claude:
    """Async Claude CLI SDK client.

    A Python async client that wraps Claude CLI as a subprocess.
    Supports Skills, Hooks, Slash Commands, Agents, and all CLI features.

    Example:
        >>> async with Claude() as claude:
        ...     result = await claude.run("Hello!")
        ...     print(result.text)

        >>> claude = Claude(ClaudeConfig(model="sonnet"))
        >>> result = await claude.run("Explain this code")

    Cancellation:
        >>> token = CancellationToken()
        >>> task = asyncio.create_task(claude.run("Long task", cancel_token=token))
        >>> token.cancel()  # Request cancellation

    Progress callback:
        >>> def on_progress(event_type, data):
        ...     print(f"Progress: {event_type}")
        >>> result = await claude.run("Task", on_progress=on_progress)
    """

    def __init__(self, config: Optional[ClaudeConfig] = None, verify_cli: bool = True):
        """Initialize Claude client.

        Args:
            config: Claude configuration. Uses defaults if None.
            verify_cli: Whether to verify Claude CLI exists (default: True)

        Raises:
            CLINotFoundError: If verify_cli is True and Claude CLI is not found
        """
        self.config = config or ClaudeConfig()
        self._process: Optional[Process] = None
        self._session_id: Optional[str] = None
        self._current_process: Optional[Process] = None

        # Verify CLI exists
        if verify_cli:
            _verify_claude_cli(self.config.claude_path)

        # Event handlers
        self.on_message: Optional[OnMessageCallback] = None
        self.on_tool_use: Optional[OnToolUseCallback] = None
        self.on_error: Optional[OnErrorCallback] = None
        self.on_result: Optional[OnResultCallback] = None

    async def __aenter__(self) -> "Claude":
        """Enter async context manager."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit async context manager."""
        await self.close()

    def _build_args(
        self,
        prompt: Optional[str] = None,
        resume: Optional[str] = None,
        continue_session: bool = False
    ) -> list[str]:
        """Build CLI arguments.

        Args:
            prompt: Prompt to execute
            resume: Session ID to resume
            continue_session: Whether to continue current session

        Returns:
            List of CLI arguments
        """
        args = [self.config.claude_path]

        # Prompt mode (-p)
        if prompt:
            args.extend(["-p", prompt])

        # Session resume
        if resume:
            args.extend(["--resume", resume])
        elif continue_session and self._session_id:
            args.extend(["--resume", self._session_id])

        # Model
        if self.config.model:
            args.extend(["--model", self.config.model])

        # Permission mode
        args.extend(["--permission-mode", self.config.permission_mode.value])

        # Output format
        args.extend(["--output-format", self.config.output_format.value])

        # stream-json + print mode (-p) requires --verbose
        if self.config.output_format == OutputFormat.STREAM_JSON and prompt:
            args.append("--verbose")

        # Input format (bidirectional communication)
        args.extend(["--input-format", self.config.input_format])

        # Setting sources (skills, CLAUDE.md, subagents)
        if self.config.setting_sources:
            args.extend(["--setting-sources", ",".join(self.config.setting_sources)])

        # Allowed tools
        if self.config.allowed_tools:
            args.extend(["--allowed-tools", ",".join(self.config.allowed_tools)])

        # Disallowed tools
        if self.config.disallowed_tools:
            args.extend(["--disallowed-tools", ",".join(self.config.disallowed_tools)])

        # MCP configuration
        if self.config.mcp_config:
            args.extend(["--mcp-config", self.config.mcp_config])

        # Max turns
        if self.config.max_turns:
            args.extend(["--max-turns", str(self.config.max_turns)])

        # System prompt
        if self.config.system_prompt:
            args.extend(["--system-prompt", self.config.system_prompt])

        return args

    async def start_session(self) -> None:
        """Start a session for bidirectional communication.

        Use this for persistent conversations.
        Communicate via send_message() and read_stream().
        """
        args = self._build_args()

        self._process = await asyncio.create_subprocess_exec(
            *args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.config.cwd
        )

    async def send_message(self, message: str) -> None:
        """Send a message (bidirectional communication).

        Args:
            message: Message to send

        Raises:
            SessionNotStartedError: If session has not been started
        """
        if not self._process or not self._process.stdin:
            raise SessionNotStartedError()

        # Send in stream-json format
        msg = json.dumps({
            "type": "user_message",
            "content": message
        }) + "\n"

        self._process.stdin.write(msg.encode())
        await self._process.stdin.drain()

    async def read_stream(self) -> AsyncIterator[StreamEvent]:
        """Read from the stream.

        Yields:
            StreamEvent: Received events

        Raises:
            SessionNotStartedError: If session has not been started
        """
        if not self._process or not self._process.stdout:
            raise SessionNotStartedError()

        while True:
            line = await self._process.stdout.readline()
            if not line:
                break

            try:
                data = json.loads(line.decode())
                event = StreamEvent(
                    type=data.get("type", "unknown"),
                    data=data,
                    raw=line.decode()
                )

                # Save session ID
                if event.type == "system" and "session_id" in data:
                    self._session_id = data["session_id"]

                # Call event handlers
                if self.on_message:
                    self.on_message(event)
                if self.on_tool_use and event.type == "tool_use":
                    self.on_tool_use(data)
                if self.on_result and event.type == "result":
                    self.on_result(data)

                yield event

            except json.JSONDecodeError:
                # Non-JSON output (errors, etc.)
                if self.on_error:
                    self.on_error(line.decode())

    async def run(
        self,
        prompt: str,
        *,
        cancel_token: Optional[CancellationToken] = None,
        on_progress: Optional[OnProgressCallback] = None,
        timeout: Optional[float] = None
    ) -> ClaudeResult:
        """Execute a single prompt.

        Args:
            prompt: Prompt to execute
            cancel_token: Cancellation token for cancelling the operation
            on_progress: Progress callback
            timeout: Timeout in seconds. Uses config.timeout if None

        Returns:
            ClaudeResult: Execution result

        Raises:
            asyncio.CancelledError: If cancelled
            asyncio.TimeoutError: If timeout exceeded
        """
        args = self._build_args(prompt)
        effective_timeout = timeout or self.config.timeout

        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.config.cwd
        )
        self._current_process = process

        try:
            # Monitor cancellation token
            async def check_cancel():
                while process.returncode is None:
                    if cancel_token and cancel_token.is_cancelled:
                        process.terminate()
                        raise asyncio.CancelledError("Operation cancelled by user")
                    await asyncio.sleep(0.1)

            # Handle timeout
            if effective_timeout:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=effective_timeout
                )
            else:
                # Run cancellation check in parallel
                if cancel_token:
                    cancel_task = asyncio.create_task(check_cancel())
                    try:
                        stdout, stderr = await process.communicate()
                    finally:
                        cancel_task.cancel()
                        try:
                            await cancel_task
                        except asyncio.CancelledError:
                            pass
                else:
                    stdout, stderr = await process.communicate()

        except asyncio.TimeoutError:
            process.terminate()
            await process.wait()
            return ClaudeResult(
                events=[],
                result=None,
                session_id=self._session_id,
                stderr="Timeout exceeded",
                success=False
            )
        finally:
            self._current_process = None

        # Parse stream-json
        events: list[dict] = []
        result: Optional[dict] = None

        for line in stdout.decode().strip().split("\n"):
            if line:
                try:
                    data = json.loads(line)
                    events.append(data)

                    # Progress callback
                    if on_progress:
                        on_progress(data.get("type", "unknown"), data)

                    if data.get("type") == "result":
                        result = data

                    # Save session ID
                    if data.get("type") == "system" and "session_id" in data:
                        self._session_id = data["session_id"]

                except json.JSONDecodeError:
                    pass

        return ClaudeResult(
            events=events,
            result=result,
            session_id=self._session_id,
            stderr=stderr.decode() if stderr else None,
            success=process.returncode == 0
        )

    async def run_with_files(
        self,
        prompt: str,
        files: list[Union[str, Path]],
        *,
        cancel_token: Optional[CancellationToken] = None,
        on_progress: Optional[OnProgressCallback] = None
    ) -> ClaudeResult:
        """Execute with file context.

        Args:
            prompt: Prompt to execute
            files: List of file paths to include as context
            cancel_token: Cancellation token
            on_progress: Progress callback

        Returns:
            ClaudeResult: Execution result
        """
        # Include file contents in prompt
        file_contents = []
        for file_path in files:
            path = Path(file_path)
            if path.exists():
                content = path.read_text(encoding="utf-8")
                file_contents.append(f"=== {path.name} ===\n{content}")

        if file_contents:
            full_prompt = f"{prompt}\n\n--- Files ---\n" + "\n\n".join(file_contents)
        else:
            full_prompt = prompt

        return await self.run(full_prompt, cancel_token=cancel_token, on_progress=on_progress)

    async def run_streaming(
        self,
        prompt: str,
        *,
        cancel_token: Optional[CancellationToken] = None
    ) -> AsyncIterator[StreamEvent]:
        """Streaming execution - yields events in real-time.

        Args:
            prompt: Prompt to execute
            cancel_token: Cancellation token

        Yields:
            StreamEvent: Received events
        """
        args = self._build_args(prompt)

        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.config.cwd
        )
        self._current_process = process

        try:
            while True:
                if cancel_token and cancel_token.is_cancelled:
                    process.terminate()
                    break

                line = await process.stdout.readline()
                if not line:
                    break

                try:
                    data = json.loads(line.decode())
                    event = StreamEvent(
                        type=data.get("type", "unknown"),
                        data=data,
                        raw=line.decode()
                    )

                    if event.type == "system" and "session_id" in data:
                        self._session_id = data["session_id"]

                    yield event

                except json.JSONDecodeError:
                    pass

            await process.wait()
        finally:
            self._current_process = None

    async def cancel(self) -> None:
        """Cancel the currently running operation."""
        if self._current_process:
            self._current_process.terminate()
            await self._current_process.wait()
            self._current_process = None

    async def skill(self, skill_name: str, prompt: str) -> ClaudeResult:
        """Execute using a skill.

        Args:
            skill_name: Skill name (e.g., "frontend-design")
            prompt: Prompt to pass to the skill

        Returns:
            ClaudeResult: Execution result
        """
        # Add Skill tool to allowed list
        original_tools = self.config.allowed_tools
        if self.config.allowed_tools:
            if "Skill" not in self.config.allowed_tools:
                self.config.allowed_tools = self.config.allowed_tools + ["Skill"]
        else:
            self.config.allowed_tools = ["Skill", "Read", "Write", "Edit", "Bash", "Glob", "Grep"]

        # Skill invocation prompt
        full_prompt = f'Use the "{skill_name}" skill to: {prompt}'

        try:
            result = await self.run(full_prompt)
        finally:
            # Restore original tool settings
            self.config.allowed_tools = original_tools

        return result

    async def command(self, command: str, args: str = "") -> ClaudeResult:
        """Execute a slash command.

        Args:
            command: Command name (without slash, e.g., "code-review")
            args: Command arguments

        Returns:
            ClaudeResult: Execution result
        """
        # Use SlashCommand tool
        original_tools = self.config.allowed_tools
        if self.config.allowed_tools:
            if "SlashCommand" not in self.config.allowed_tools:
                self.config.allowed_tools = self.config.allowed_tools + ["SlashCommand"]

        full_prompt = f'Execute the slash command: /{command} {args}'

        try:
            result = await self.run(full_prompt)
        finally:
            self.config.allowed_tools = original_tools

        return result

    async def agent(self, agent_type: str, task: str) -> ClaudeResult:
        """Execute using an agent (Task tool).

        Args:
            agent_type: Agent type (e.g., "Explore", "Plan")
            task: Task to pass to the agent

        Returns:
            ClaudeResult: Execution result
        """
        original_tools = self.config.allowed_tools
        if self.config.allowed_tools:
            if "Task" not in self.config.allowed_tools:
                self.config.allowed_tools = self.config.allowed_tools + ["Task"]

        full_prompt = f'Use the Task tool with subagent_type="{agent_type}" to: {task}'

        try:
            result = await self.run(full_prompt)
        finally:
            self.config.allowed_tools = original_tools

        return result

    async def continue_conversation(self, prompt: str) -> ClaudeResult:
        """Continue a previous conversation.

        Args:
            prompt: Prompt to continue with

        Returns:
            ClaudeResult: Execution result

        Raises:
            SessionNotFoundError: If there is no previous session
        """
        if not self._session_id:
            raise SessionNotFoundError()

        args = self._build_args(prompt, continue_session=True)

        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.config.cwd
        )

        stdout, stderr = await process.communicate()

        events: list[dict] = []
        result: Optional[dict] = None

        for line in stdout.decode().strip().split("\n"):
            if line:
                try:
                    data = json.loads(line)
                    events.append(data)
                    if data.get("type") == "result":
                        result = data
                except json.JSONDecodeError:
                    pass

        return ClaudeResult(
            events=events,
            result=result,
            session_id=self._session_id,
            stderr=stderr.decode() if stderr else None,
            success=process.returncode == 0
        )

    async def close(self) -> None:
        """Close the session."""
        if self._process:
            self._process.terminate()
            await self._process.wait()
            self._process = None
        if self._current_process:
            self._current_process.terminate()
            await self._current_process.wait()
            self._current_process = None

    @property
    def session_id(self) -> Optional[str]:
        """Current session ID."""
        return self._session_id

    @property
    def is_running(self) -> bool:
        """Whether an operation is currently running."""
        return self._current_process is not None


class ClaudeSync:
    """Synchronous Claude CLI SDK client.

    A synchronous version that works without asyncio.

    Example:
        >>> claude = ClaudeSync()
        >>> result = claude.run("Hello!")
        >>> print(result.text)

    With files:
        >>> result = claude.run_with_files("Analyze this", ["main.py", "utils.py"])
    """

    def __init__(self, config: Optional[ClaudeConfig] = None, verify_cli: bool = True):
        """Initialize ClaudeSync client.

        Args:
            config: Claude configuration. Uses defaults if None.
            verify_cli: Whether to verify Claude CLI exists (default: True)

        Raises:
            CLINotFoundError: If verify_cli is True and Claude CLI is not found
        """
        self.config = config or ClaudeConfig()
        self._session_id: Optional[str] = None
        self._current_process: Optional[subprocess.Popen] = None

        # Verify CLI exists
        if verify_cli:
            _verify_claude_cli(self.config.claude_path)

    def __enter__(self) -> "ClaudeSync":
        """Enter context manager."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager."""
        self.close()

    def _build_args(self, prompt: str, resume: Optional[str] = None) -> list[str]:
        """Build CLI arguments."""
        args = [self.config.claude_path, "-p", prompt]

        if resume:
            args.extend(["--resume", resume])

        if self.config.model:
            args.extend(["--model", self.config.model])

        args.extend(["--permission-mode", self.config.permission_mode.value])
        args.extend(["--output-format", self.config.output_format.value])

        # stream-json requires --verbose
        if self.config.output_format == OutputFormat.STREAM_JSON:
            args.append("--verbose")

        if self.config.setting_sources:
            args.extend(["--setting-sources", ",".join(self.config.setting_sources)])

        if self.config.allowed_tools:
            args.extend(["--allowed-tools", ",".join(self.config.allowed_tools)])

        if self.config.disallowed_tools:
            args.extend(["--disallowed-tools", ",".join(self.config.disallowed_tools)])

        if self.config.mcp_config:
            args.extend(["--mcp-config", self.config.mcp_config])

        if self.config.max_turns:
            args.extend(["--max-turns", str(self.config.max_turns)])

        if self.config.system_prompt:
            args.extend(["--system-prompt", self.config.system_prompt])

        return args

    def run(
        self,
        prompt: str,
        *,
        timeout: Optional[float] = None,
        on_progress: Optional[OnProgressCallback] = None
    ) -> ClaudeResult:
        """Synchronous execution.

        Args:
            prompt: Prompt to execute
            timeout: Timeout in seconds
            on_progress: Progress callback

        Returns:
            ClaudeResult: Execution result
        """
        args = self._build_args(prompt)
        effective_timeout = timeout or self.config.timeout

        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                cwd=self.config.cwd,
                timeout=effective_timeout
            )
        except subprocess.TimeoutExpired:
            return ClaudeResult(
                events=[],
                result=None,
                session_id=self._session_id,
                stderr="Timeout exceeded",
                success=False
            )

        events: list[dict] = []
        final_result: Optional[dict] = None

        for line in result.stdout.strip().split("\n"):
            if line:
                try:
                    data = json.loads(line)
                    events.append(data)

                    if on_progress:
                        on_progress(data.get("type", "unknown"), data)

                    if data.get("type") == "result":
                        final_result = data
                    if data.get("type") == "system" and "session_id" in data:
                        self._session_id = data["session_id"]
                except json.JSONDecodeError:
                    pass

        return ClaudeResult(
            events=events,
            result=final_result,
            session_id=self._session_id,
            stderr=result.stderr,
            success=result.returncode == 0
        )

    def run_with_files(
        self,
        prompt: str,
        files: list[Union[str, Path]],
        *,
        timeout: Optional[float] = None
    ) -> ClaudeResult:
        """Execute with file context.

        Args:
            prompt: Prompt to execute
            files: List of file paths to include as context
            timeout: Timeout in seconds

        Returns:
            ClaudeResult: Execution result
        """
        file_contents = []
        for file_path in files:
            path = Path(file_path)
            if path.exists():
                content = path.read_text(encoding="utf-8")
                file_contents.append(f"=== {path.name} ===\n{content}")

        if file_contents:
            full_prompt = f"{prompt}\n\n--- Files ---\n" + "\n\n".join(file_contents)
        else:
            full_prompt = prompt

        return self.run(full_prompt, timeout=timeout)

    def skill(self, skill_name: str, prompt: str) -> ClaudeResult:
        """Execute using a skill."""
        original_tools = self.config.allowed_tools
        if self.config.allowed_tools:
            if "Skill" not in self.config.allowed_tools:
                self.config.allowed_tools = self.config.allowed_tools + ["Skill"]
        else:
            self.config.allowed_tools = ["Skill", "Read", "Write", "Edit", "Bash", "Glob", "Grep"]

        full_prompt = f'Use the "{skill_name}" skill to: {prompt}'

        try:
            result = self.run(full_prompt)
        finally:
            self.config.allowed_tools = original_tools

        return result

    def command(self, command: str, args: str = "") -> ClaudeResult:
        """Execute a slash command."""
        original_tools = self.config.allowed_tools
        if self.config.allowed_tools:
            if "SlashCommand" not in self.config.allowed_tools:
                self.config.allowed_tools = self.config.allowed_tools + ["SlashCommand"]

        full_prompt = f'Execute the slash command: /{command} {args}'

        try:
            result = self.run(full_prompt)
        finally:
            self.config.allowed_tools = original_tools

        return result

    def agent(self, agent_type: str, task: str) -> ClaudeResult:
        """Execute using an agent (Task tool)."""
        original_tools = self.config.allowed_tools
        if self.config.allowed_tools:
            if "Task" not in self.config.allowed_tools:
                self.config.allowed_tools = self.config.allowed_tools + ["Task"]

        full_prompt = f'Use the Task tool with subagent_type="{agent_type}" to: {task}'

        try:
            result = self.run(full_prompt)
        finally:
            self.config.allowed_tools = original_tools

        return result

    def continue_conversation(self, prompt: str) -> ClaudeResult:
        """Continue a previous conversation.

        Args:
            prompt: Prompt to continue with

        Returns:
            ClaudeResult: Execution result

        Raises:
            SessionNotFoundError: If there is no previous session
        """
        if not self._session_id:
            raise SessionNotFoundError()

        args = self._build_args(prompt, resume=self._session_id)

        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            cwd=self.config.cwd,
            timeout=self.config.timeout
        )

        events: list[dict] = []
        final_result: Optional[dict] = None

        for line in result.stdout.strip().split("\n"):
            if line:
                try:
                    data = json.loads(line)
                    events.append(data)
                    if data.get("type") == "result":
                        final_result = data
                except json.JSONDecodeError:
                    pass

        return ClaudeResult(
            events=events,
            result=final_result,
            session_id=self._session_id,
            stderr=result.stderr,
            success=result.returncode == 0
        )

    def close(self) -> None:
        """Clean up resources."""
        if self._current_process:
            self._current_process.terminate()
            self._current_process = None

    @property
    def session_id(self) -> Optional[str]:
        """Current session ID."""
        return self._session_id
