"""
Parallel Execution Module for Claude CLI SDK
=============================================

Session-based parallelization layer that respects CLI's serial execution
within sessions while enabling parallel execution across sessions.

Key Concepts:
- Within a session: Always sequential execution (CLI architecture constraint)
- Across sessions: Parallel execution via asyncio
- Result aggregation: Collected and combined in Python

Example:
    >>> from claude_cli_sdk import SessionManager, TaskSpec
    >>> manager = SessionManager(max_concurrent_sessions=4)
    >>> async with manager:
    ...     session_a = await manager.create_session("worker-a")
    ...     session_b = await manager.create_session("worker-b")
    ...     results = await manager.run_sessions_parallel({
    ...         session_a: [TaskSpec.prompt_task("Hello")],
    ...         session_b: [TaskSpec.prompt_task("World")],
    ...     })
"""

from __future__ import annotations
import asyncio
import uuid
import time
from dataclasses import dataclass, field
from typing import Optional, Literal, Any, Callable, Mapping, Dict, List, TYPE_CHECKING

from .config import ClaudeConfig
from .models import ClaudeResult

if TYPE_CHECKING:
    from .client import Claude


# =============================================================================
# Data Classes
# =============================================================================

TaskKind = Literal["prompt", "agent", "skill", "slash_command"]


@dataclass
class TaskSpec:
    """Task specification for parallel execution.

    Attributes:
        id: Unique task identifier
        kind: Task type (prompt, agent, skill, slash_command)
        prompt: The prompt text
        agent_type: Agent type for agent tasks
        skill_name: Skill name for skill tasks
        slash_command: Command name for slash command tasks
        slash_args: Arguments for slash commands
        metadata: Additional metadata
    """
    id: str
    kind: TaskKind
    prompt: str

    # Kind-specific metadata
    agent_type: Optional[str] = None
    skill_name: Optional[str] = None
    slash_command: Optional[str] = None
    slash_args: str = ""

    # Optional metadata
    metadata: dict = field(default_factory=dict)

    @classmethod
    def prompt_task(cls, prompt: str, task_id: Optional[str] = None) -> "TaskSpec":
        """Create a simple prompt task.

        Args:
            prompt: The prompt text
            task_id: Optional task ID (auto-generated if not provided)

        Returns:
            TaskSpec for the prompt
        """
        return cls(
            id=task_id or str(uuid.uuid4())[:8],
            kind="prompt",
            prompt=prompt
        )

    @classmethod
    def agent_task(
        cls, agent_type: str, prompt: str, task_id: Optional[str] = None
    ) -> "TaskSpec":
        """Create an agent task.

        Args:
            agent_type: Agent type (e.g., "Explore", "Plan")
            prompt: The task description
            task_id: Optional task ID

        Returns:
            TaskSpec for the agent task
        """
        return cls(
            id=task_id or str(uuid.uuid4())[:8],
            kind="agent",
            prompt=prompt,
            agent_type=agent_type
        )

    @classmethod
    def skill_task(
        cls, skill_name: str, prompt: str, task_id: Optional[str] = None
    ) -> "TaskSpec":
        """Create a skill task.

        Args:
            skill_name: Name of the skill
            prompt: The prompt for the skill
            task_id: Optional task ID

        Returns:
            TaskSpec for the skill task
        """
        return cls(
            id=task_id or str(uuid.uuid4())[:8],
            kind="skill",
            prompt=prompt,
            skill_name=skill_name
        )

    @classmethod
    def slash_task(
        cls, command: str, args: str = "", task_id: Optional[str] = None
    ) -> "TaskSpec":
        """Create a slash command task.

        Args:
            command: Command name (without slash)
            args: Command arguments
            task_id: Optional task ID

        Returns:
            TaskSpec for the slash command
        """
        return cls(
            id=task_id or str(uuid.uuid4())[:8],
            kind="slash_command",
            prompt="",
            slash_command=command,
            slash_args=args
        )


@dataclass
class SessionResult:
    """Result from a session task execution.

    Attributes:
        session_id: The session ID
        task_id: The task ID
        result: ClaudeResult from execution
        error: Exception if failed
        duration_ms: Execution duration in milliseconds
    """
    session_id: Optional[str]
    task_id: str
    result: Optional[ClaudeResult] = None
    error: Optional[Exception] = None
    duration_ms: Optional[float] = None

    @property
    def is_success(self) -> bool:
        """Whether the task succeeded."""
        return self.error is None and self.result is not None and self.result.success

    @property
    def text(self) -> Optional[str]:
        """Result text if available."""
        if self.result:
            return self.result.text
        return None


@dataclass
class SessionState:
    """Internal state of a session."""
    queue: asyncio.Queue = field(default_factory=asyncio.Queue)
    current_task: Optional[TaskSpec] = None
    results: List[SessionResult] = field(default_factory=list)
    cancelled: bool = False
    started: bool = False
    completed_count: int = 0


@dataclass
class CombinedResult:
    """Combined results from multiple sessions.

    Attributes:
        sessions: List of all session results
        summary: Optional summary text
        metadata: Additional metadata
    """
    sessions: List[SessionResult] = field(default_factory=list)
    summary: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def total_count(self) -> int:
        """Total number of tasks."""
        return len(self.sessions)

    @property
    def success_count(self) -> int:
        """Number of successful tasks."""
        return sum(1 for r in self.sessions if r.is_success)

    @property
    def error_count(self) -> int:
        """Number of failed tasks."""
        return sum(1 for r in self.sessions if not r.is_success)

    @property
    def all_success(self) -> bool:
        """Whether all tasks succeeded."""
        return self.error_count == 0

    def get_successful_results(self) -> List[SessionResult]:
        """Get only successful results."""
        return [r for r in self.sessions if r.is_success]

    def get_failed_results(self) -> List[SessionResult]:
        """Get only failed results."""
        return [r for r in self.sessions if not r.is_success]


# =============================================================================
# ClaudeSession
# =============================================================================

class ClaudeSession:
    """A Claude session wrapper for parallel execution.

    Tasks within a session are always executed sequentially,
    respecting CLI's architecture constraints.

    Example:
        >>> session = ClaudeSession(Claude(), name="worker-1")
        >>> await session.enqueue_task(TaskSpec.prompt_task("Hello"))
        >>> await session.run_loop()
        >>> results = session.get_results()
    """

    def __init__(
        self,
        client: "Claude",
        name: Optional[str] = None,
        session_id: Optional[str] = None,
    ):
        """Initialize a session.

        Args:
            client: Claude client instance
            name: Session name for identification
            session_id: Existing session ID to resume
        """
        self._client = client
        self._name = name or str(uuid.uuid4())[:8]
        self._session_id = session_id
        self._state = SessionState()

    @property
    def id(self) -> str:
        """Session identifier."""
        return self._session_id or self._name

    @property
    def name(self) -> str:
        """Session name."""
        return self._name

    @property
    def session_id(self) -> Optional[str]:
        """Claude session ID."""
        return self._session_id

    @property
    def client(self) -> "Claude":
        """The underlying Claude client."""
        return self._client

    def is_idle(self) -> bool:
        """Check if session is idle (no pending tasks)."""
        return (
            self._state.queue.empty() and
            self._state.current_task is None
        )

    def mark_cancelled(self) -> None:
        """Mark the session as cancelled."""
        self._state.cancelled = True

    async def enqueue_task(self, task: TaskSpec) -> None:
        """Add a task to the queue.

        Args:
            task: Task to enqueue
        """
        await self._state.queue.put(task)

    async def enqueue_tasks(self, tasks: List[TaskSpec]) -> None:
        """Add multiple tasks to the queue.

        Args:
            tasks: Tasks to enqueue
        """
        for task in tasks:
            await self._state.queue.put(task)

    async def run_next(self) -> bool:
        """Execute the next task in queue.

        Returns:
            True if a task was executed, False if queue was empty
        """
        if self._state.queue.empty():
            return False

        task = await self._state.queue.get()
        self._state.current_task = task

        try:
            result = await self._run_task(task)
            self._state.results.append(result)
            self._state.completed_count += 1
        finally:
            self._state.current_task = None
            self._state.queue.task_done()

        return True

    async def run_loop(self) -> None:
        """Run all tasks in queue until empty or cancelled.

        Tasks are executed sequentially within the session.
        """
        self._state.started = True

        while not self._state.cancelled:
            has_task = await self.run_next()
            if not has_task:
                break

    async def _run_task(self, task: TaskSpec) -> SessionResult:
        """Execute a single task.

        Args:
            task: The task to execute

        Returns:
            SessionResult with execution results
        """
        start_time = time.time()

        try:
            if task.kind == "prompt":
                result = await self._client.run(task.prompt)
            elif task.kind == "agent":
                result = await self._client.agent(task.agent_type, task.prompt)
            elif task.kind == "skill":
                result = await self._client.skill(task.skill_name, task.prompt)
            elif task.kind == "slash_command":
                result = await self._client.command(task.slash_command, task.slash_args)
            else:
                raise ValueError(f"Unknown task kind: {task.kind}")

            # Update session_id
            if result.session_id:
                self._session_id = result.session_id

            duration_ms = (time.time() - start_time) * 1000

            return SessionResult(
                session_id=self._session_id,
                task_id=task.id,
                result=result,
                duration_ms=duration_ms
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return SessionResult(
                session_id=self._session_id,
                task_id=task.id,
                result=None,
                error=e,
                duration_ms=duration_ms
            )

    def get_results(self) -> List[SessionResult]:
        """Get all results from this session."""
        return self._state.results.copy()

    def clear_results(self) -> None:
        """Clear all results."""
        self._state.results.clear()
        self._state.completed_count = 0


# =============================================================================
# SessionManager
# =============================================================================

class SessionManager:
    """Manages multiple Claude sessions for parallel execution.

    Orchestrates parallel execution across sessions while ensuring
    sequential execution within each session.

    Example:
        >>> async with SessionManager(max_concurrent_sessions=4) as manager:
        ...     session = await manager.create_session("worker")
        ...     results = await manager.run_sessions_parallel({
        ...         session: [TaskSpec.prompt_task("Hello")]
        ...     })
    """

    def __init__(
        self,
        config: Optional[ClaudeConfig] = None,
        max_concurrent_sessions: int = 4,
        min_concurrent_sessions: int = 1,
    ):
        """Initialize the session manager.

        Args:
            config: Default ClaudeConfig for new sessions
            max_concurrent_sessions: Maximum number of parallel sessions
            min_concurrent_sessions: Minimum number of parallel sessions
        """
        self._config = config
        self._max_concurrent = max_concurrent_sessions
        self._min_concurrent = min_concurrent_sessions
        self._sessions: Dict[str, ClaudeSession] = {}
        self._semaphore = asyncio.Semaphore(max_concurrent_sessions)

    async def __aenter__(self) -> "SessionManager":
        """Enter async context manager."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit async context manager."""
        await self.close()

    @property
    def max_concurrent(self) -> int:
        """Maximum concurrent sessions."""
        return self._max_concurrent

    async def create_session(
        self,
        name: Optional[str] = None,
        config: Optional[ClaudeConfig] = None,
    ) -> ClaudeSession:
        """Create a new session.

        Args:
            name: Session name (auto-generated if not provided)
            config: Override config for this session

        Returns:
            New ClaudeSession instance
        """
        from .client import Claude

        session_config = config or self._config or ClaudeConfig()
        client = Claude(session_config)
        session = ClaudeSession(client, name=name)
        self._sessions[session.name] = session
        return session

    def get_session(self, name: str) -> Optional[ClaudeSession]:
        """Get a session by name.

        Args:
            name: Session name

        Returns:
            ClaudeSession if found, None otherwise
        """
        return self._sessions.get(name)

    def list_sessions(self) -> List[ClaudeSession]:
        """List all sessions."""
        return list(self._sessions.values())

    async def close(self) -> None:
        """Close all sessions and clean up resources."""
        for session in self._sessions.values():
            await session.client.close()
        self._sessions.clear()

    async def run_sessions_parallel(
        self,
        assignments: Mapping[ClaudeSession, List[TaskSpec]],
    ) -> Dict[ClaudeSession, List[SessionResult]]:
        """Run tasks across sessions in parallel.

        Tasks assigned to the same session run sequentially.
        Different sessions run in parallel (up to max_concurrent_sessions).

        Args:
            assignments: Mapping of session -> tasks to execute

        Returns:
            Mapping of session -> results
        """
        # Enqueue tasks to each session
        for session, tasks in assignments.items():
            await session.enqueue_tasks(tasks)

        # Run sessions with semaphore limiting concurrency
        async def run_with_limit(session: ClaudeSession):
            async with self._semaphore:
                await session.run_loop()

        await asyncio.gather(*[
            run_with_limit(session)
            for session in assignments.keys()
        ])

        # Collect results
        return {
            session: session.get_results()
            for session in assignments.keys()
        }

    async def run_all_until_idle(self) -> Dict[ClaudeSession, List[SessionResult]]:
        """Run all non-idle sessions until they become idle.

        Returns:
            Mapping of session -> results for active sessions
        """
        active_sessions = [
            s for s in self._sessions.values()
            if not s.is_idle()
        ]

        if not active_sessions:
            return {}

        async def run_with_limit(session: ClaudeSession):
            async with self._semaphore:
                await session.run_loop()

        await asyncio.gather(*[
            run_with_limit(session)
            for session in active_sessions
        ])

        return {
            session: session.get_results()
            for session in active_sessions
        }

    async def cancel_session(self, session: ClaudeSession) -> None:
        """Cancel a specific session.

        Args:
            session: Session to cancel
        """
        session.mark_cancelled()

    async def cancel_all(self) -> None:
        """Cancel all sessions."""
        for session in self._sessions.values():
            session.mark_cancelled()


# =============================================================================
# Result Aggregation
# =============================================================================

def aggregate_results(
    per_session: Dict[ClaudeSession, List[SessionResult]],
) -> CombinedResult:
    """Aggregate results from multiple sessions.

    Args:
        per_session: Session -> results mapping

    Returns:
        CombinedResult with all results
    """
    all_results = []
    for session, results in per_session.items():
        all_results.extend(results)

    return CombinedResult(
        sessions=all_results,
        metadata={
            "session_count": len(per_session),
            "total_tasks": len(all_results),
            "success_tasks": sum(1 for r in all_results if r.is_success),
            "error_tasks": sum(1 for r in all_results if not r.is_success),
        }
    )


# =============================================================================
# Convenience Functions
# =============================================================================

async def run_parallel_prompts(
    prompts: List[str],
    max_concurrent: int = 4,
    config: Optional[ClaudeConfig] = None,
) -> CombinedResult:
    """Execute multiple prompts in parallel.

    Each prompt runs in a separate session.

    Args:
        prompts: List of prompts to execute
        max_concurrent: Maximum concurrent sessions
        config: ClaudeConfig for all sessions

    Returns:
        CombinedResult with all results

    Example:
        >>> results = await run_parallel_prompts([
        ...     "What is 2+2?",
        ...     "What is 3+3?",
        ... ], max_concurrent=2)
        >>> print(results.success_count)
    """
    async with SessionManager(config, max_concurrent_sessions=max_concurrent) as manager:
        assignments: Dict[ClaudeSession, List[TaskSpec]] = {}

        for i, prompt in enumerate(prompts):
            session = await manager.create_session(f"worker-{i}")
            assignments[session] = [TaskSpec.prompt_task(prompt, f"task-{i}")]

        per_session = await manager.run_sessions_parallel(assignments)
        return aggregate_results(per_session)


async def run_parallel_tasks(
    tasks: List[TaskSpec],
    max_concurrent: int = 4,
    config: Optional[ClaudeConfig] = None,
) -> CombinedResult:
    """Execute multiple tasks in parallel.

    Each task runs in a separate session.

    Args:
        tasks: List of TaskSpec to execute
        max_concurrent: Maximum concurrent sessions
        config: ClaudeConfig for all sessions

    Returns:
        CombinedResult with all results

    Example:
        >>> tasks = [
        ...     TaskSpec.prompt_task("Hello"),
        ...     TaskSpec.agent_task("Explore", "Find files"),
        ... ]
        >>> results = await run_parallel_tasks(tasks)
    """
    async with SessionManager(config, max_concurrent_sessions=max_concurrent) as manager:
        assignments: Dict[ClaudeSession, List[TaskSpec]] = {}

        for i, task in enumerate(tasks):
            session = await manager.create_session(f"worker-{i}")
            assignments[session] = [task]

        per_session = await manager.run_sessions_parallel(assignments)
        return aggregate_results(per_session)
