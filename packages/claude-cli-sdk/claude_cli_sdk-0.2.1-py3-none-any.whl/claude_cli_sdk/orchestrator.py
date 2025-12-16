"""
Advanced Orchestrator for Claude CLI SDK
=========================================

Provides DAG-based task execution with dependency management,
retry policies, real-time progress monitoring, and shared context.

Based on insights from idea.md - implementing the orchestrator pattern
that CLI can achieve with bash scripts, but with elegant Python API.

Example:
    >>> from claude_cli_sdk import Orchestrator, TaskSpec, RetryPolicy
    >>>
    >>> async with Orchestrator(max_concurrent=4) as orch:
    ...     # Add tasks with dependencies
    ...     orch.add_task("frontend", TaskSpec.prompt_task("Analyze frontend"))
    ...     orch.add_task("backend", TaskSpec.prompt_task("Analyze backend"))
    ...     orch.add_task("integration",
    ...         TaskSpec.prompt_task("Integrate results"),
    ...         depends_on=["frontend", "backend"]
    ...     )
    ...     results = await orch.run()
"""

from __future__ import annotations
import asyncio
import time
from dataclasses import dataclass, field
from typing import Optional, Callable, Any, Dict, List, Set, Awaitable
from enum import Enum

from .config import ClaudeConfig
from .models import ClaudeResult, StreamEvent
from .parallel import TaskSpec, SessionResult, CombinedResult
from .exceptions import ClaudeSDKError


# =============================================================================
# Retry Policy
# =============================================================================

class RetryStrategy(Enum):
    """Retry strategy options."""
    IMMEDIATE = "immediate"
    LINEAR_BACKOFF = "linear"
    EXPONENTIAL_BACKOFF = "exponential"


@dataclass
class RetryPolicy:
    """Retry policy configuration.

    Attributes:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay between retries in seconds
        max_delay: Maximum delay between retries
        strategy: Backoff strategy
        retry_on: Exception types to retry on (default: all ClaudeSDKError)

    Example:
        >>> policy = RetryPolicy(
        ...     max_retries=3,
        ...     strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
        ...     base_delay=1.0
        ... )
    """
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    retry_on: tuple = (ClaudeSDKError, Exception)

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number."""
        if self.strategy == RetryStrategy.IMMEDIATE:
            return 0
        elif self.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = self.base_delay * attempt
        else:  # EXPONENTIAL_BACKOFF
            delay = self.base_delay * (2 ** (attempt - 1))

        return min(delay, self.max_delay)


# =============================================================================
# Task Node (DAG Node)
# =============================================================================

class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    WAITING = "waiting"  # Waiting for dependencies
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TaskNode:
    """A node in the task DAG.

    Attributes:
        id: Unique task identifier
        spec: Task specification
        depends_on: IDs of tasks this depends on
        status: Current execution status
        result: Execution result when completed
        error: Error if failed
        attempts: Number of execution attempts
        duration_ms: Total execution time
    """
    id: str
    spec: TaskSpec
    depends_on: Set[str] = field(default_factory=set)
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[SessionResult] = None
    error: Optional[Exception] = None
    attempts: int = 0
    duration_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_ready(self) -> bool:
        """Check if task is ready to run (no pending dependencies)."""
        return self.status == TaskStatus.PENDING and len(self.depends_on) == 0

    @property
    def is_done(self) -> bool:
        """Check if task is in a terminal state."""
        return self.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED)


# =============================================================================
# Progress Callback Types
# =============================================================================

ProgressCallback = Callable[[str, TaskStatus, Optional[StreamEvent]], Awaitable[None]]
"""Callback for task progress updates.

Args:
    task_id: The task that changed
    status: New status
    event: Optional stream event (for real-time updates)
"""


# =============================================================================
# Shared Context
# =============================================================================

class SharedContext:
    """Thread-safe shared context for inter-task communication.

    Allows tasks to share results and coordinate without
    explicit file-based communication.

    Example:
        >>> ctx = SharedContext()
        >>> await ctx.write("security", {"vulnerabilities": ["SQL injection"]})
        >>> findings = await ctx.read("security")
    """

    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._lock = asyncio.Lock()
        self._events: List[Dict[str, Any]] = []

    async def write(self, key: str, value: Any) -> None:
        """Write a value to shared context.

        Args:
            key: Context key
            value: Value to store
        """
        async with self._lock:
            self._data[key] = value
            self._events.append({
                "type": "write",
                "key": key,
                "timestamp": time.time()
            })

    async def read(self, key: str, default: Any = None) -> Any:
        """Read a value from shared context.

        Args:
            key: Context key
            default: Default value if key not found

        Returns:
            Stored value or default
        """
        async with self._lock:
            return self._data.get(key, default)

    async def read_all(self) -> Dict[str, Any]:
        """Read all values from shared context."""
        async with self._lock:
            return self._data.copy()

    async def append(self, key: str, value: Any) -> None:
        """Append to a list in shared context.

        Args:
            key: Context key (creates list if not exists)
            value: Value to append
        """
        async with self._lock:
            if key not in self._data:
                self._data[key] = []
            self._data[key].append(value)

    async def clear(self) -> None:
        """Clear all shared context."""
        async with self._lock:
            self._data.clear()
            self._events.clear()


# =============================================================================
# Orchestrator
# =============================================================================

class Orchestrator:
    """Advanced task orchestrator with DAG-based execution.

    Provides:
    - Dependency-based task ordering
    - Automatic retry with configurable policy
    - Real-time progress callbacks
    - Shared context between tasks
    - Concurrent execution with limits

    Example:
        >>> async with Orchestrator(max_concurrent=4) as orch:
        ...     orch.add_task("analyze", TaskSpec.prompt_task("Analyze code"))
        ...     orch.add_task("fix",
        ...         TaskSpec.prompt_task("Fix issues"),
        ...         depends_on=["analyze"]
        ...     )
        ...     results = await orch.run()
    """

    def __init__(
        self,
        config: Optional[ClaudeConfig] = None,
        max_concurrent: int = 4,
        retry_policy: Optional[RetryPolicy] = None,
        on_progress: Optional[ProgressCallback] = None,
    ):
        """Initialize orchestrator.

        Args:
            config: Default ClaudeConfig for tasks
            max_concurrent: Maximum concurrent task execution
            retry_policy: Retry policy for failed tasks
            on_progress: Callback for progress updates
        """
        self._config = config
        self._max_concurrent = max_concurrent
        self._retry_policy = retry_policy or RetryPolicy()
        self._on_progress = on_progress

        self._tasks: Dict[str, TaskNode] = {}
        self._context = SharedContext()
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._cancelled = False

    async def __aenter__(self) -> "Orchestrator":
        """Enter async context manager."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit async context manager."""
        pass

    @property
    def context(self) -> SharedContext:
        """Get shared context."""
        return self._context

    def add_task(
        self,
        task_id: str,
        spec: TaskSpec,
        depends_on: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "Orchestrator":
        """Add a task to the orchestrator.

        Args:
            task_id: Unique task identifier
            spec: Task specification
            depends_on: List of task IDs this depends on
            metadata: Optional task metadata

        Returns:
            Self for chaining

        Raises:
            ValueError: If task_id already exists or dependency not found
        """
        if task_id in self._tasks:
            raise ValueError(f"Task '{task_id}' already exists")

        deps = set(depends_on) if depends_on else set()

        # Validate dependencies exist
        for dep in deps:
            if dep not in self._tasks:
                raise ValueError(f"Dependency '{dep}' not found for task '{task_id}'")

        self._tasks[task_id] = TaskNode(
            id=task_id,
            spec=spec,
            depends_on=deps,
            metadata=metadata or {}
        )
        return self

    def add_tasks(self, tasks: Dict[str, TaskSpec]) -> "Orchestrator":
        """Add multiple independent tasks.

        Args:
            tasks: Mapping of task_id -> TaskSpec

        Returns:
            Self for chaining
        """
        for task_id, spec in tasks.items():
            self.add_task(task_id, spec)
        return self

    def get_task(self, task_id: str) -> Optional[TaskNode]:
        """Get a task by ID."""
        return self._tasks.get(task_id)

    def list_tasks(self) -> List[TaskNode]:
        """List all tasks."""
        return list(self._tasks.values())

    async def run(self) -> CombinedResult:
        """Execute all tasks respecting dependencies.

        Tasks without dependencies run first. Tasks with dependencies
        wait until all dependencies complete successfully.

        Returns:
            CombinedResult with all task results
        """
        if not self._tasks:
            return CombinedResult()

        # Track completed task IDs for dependency resolution
        completed: Set[str] = set()
        running: Set[str] = set()

        async def run_task(node: TaskNode) -> None:
            """Execute a single task with retry."""
            async with self._semaphore:
                if self._cancelled:
                    node.status = TaskStatus.CANCELLED
                    return

                node.status = TaskStatus.RUNNING
                running.add(node.id)
                await self._notify_progress(node.id, TaskStatus.RUNNING)

                start_time = time.time()
                last_error: Optional[Exception] = None

                for attempt in range(1, self._retry_policy.max_retries + 1):
                    node.attempts = attempt

                    try:
                        result = await self._execute_task(node)
                        node.result = result
                        node.status = TaskStatus.COMPLETED
                        node.duration_ms = (time.time() - start_time) * 1000

                        # Store result in shared context
                        await self._context.write(f"result:{node.id}", {
                            "text": result.text if result else None,
                            "success": result.is_success if result else False,
                        })

                        await self._notify_progress(node.id, TaskStatus.COMPLETED)
                        break

                    except Exception as e:
                        last_error = e
                        if attempt < self._retry_policy.max_retries:
                            delay = self._retry_policy.get_delay(attempt)
                            await asyncio.sleep(delay)
                        else:
                            node.error = e
                            node.status = TaskStatus.FAILED
                            node.duration_ms = (time.time() - start_time) * 1000
                            await self._notify_progress(node.id, TaskStatus.FAILED)

                running.discard(node.id)
                if node.status == TaskStatus.COMPLETED:
                    completed.add(node.id)

        # Main execution loop
        pending_tasks = list(self._tasks.values())

        while pending_tasks and not self._cancelled:
            # Find tasks ready to run
            ready_tasks = []
            still_pending = []

            for task in pending_tasks:
                if task.is_done:
                    continue

                # Check if all dependencies are completed
                unmet_deps = task.depends_on - completed

                # Check for failed dependencies
                failed_deps = [
                    d for d in unmet_deps
                    if self._tasks[d].status == TaskStatus.FAILED
                ]
                if failed_deps:
                    task.status = TaskStatus.CANCELLED
                    task.error = Exception(
                        f"Dependencies failed: {', '.join(failed_deps)}"
                    )
                    await self._notify_progress(task.id, TaskStatus.CANCELLED)
                    continue

                if not unmet_deps:
                    ready_tasks.append(task)
                else:
                    task.status = TaskStatus.WAITING
                    still_pending.append(task)

            if not ready_tasks and not running:
                # No progress possible - deadlock or all done
                break

            # Start ready tasks
            if ready_tasks:
                await asyncio.gather(*[
                    run_task(task) for task in ready_tasks
                ])

            pending_tasks = still_pending

        # Collect results
        all_results = []
        for task in self._tasks.values():
            if task.result:
                all_results.append(task.result)

        return CombinedResult(
            sessions=all_results,
            metadata={
                "total_tasks": len(self._tasks),
                "completed": sum(1 for t in self._tasks.values() if t.status == TaskStatus.COMPLETED),
                "failed": sum(1 for t in self._tasks.values() if t.status == TaskStatus.FAILED),
                "cancelled": sum(1 for t in self._tasks.values() if t.status == TaskStatus.CANCELLED),
            }
        )

    async def _execute_task(self, node: TaskNode) -> SessionResult:
        """Execute a task and return result."""
        from .client import Claude

        config = self._config or ClaudeConfig()
        async with Claude(config, verify_cli=False) as client:
            spec = node.spec
            start_time = time.time()

            if spec.kind == "prompt":
                result = await client.run(spec.prompt)
            elif spec.kind == "agent":
                result = await client.agent(spec.agent_type, spec.prompt)
            elif spec.kind == "skill":
                result = await client.skill(spec.skill_name, spec.prompt)
            elif spec.kind == "slash_command":
                result = await client.command(spec.slash_command, spec.slash_args)
            else:
                raise ValueError(f"Unknown task kind: {spec.kind}")

            duration_ms = (time.time() - start_time) * 1000

            return SessionResult(
                session_id=result.session_id,
                task_id=node.id,
                result=result,
                duration_ms=duration_ms
            )

    async def _notify_progress(
        self,
        task_id: str,
        status: TaskStatus,
        event: Optional[StreamEvent] = None
    ) -> None:
        """Notify progress callback."""
        if self._on_progress:
            try:
                await self._on_progress(task_id, status, event)
            except Exception:
                pass  # Don't let callback errors affect execution

    def cancel(self) -> None:
        """Cancel orchestrator execution."""
        self._cancelled = True

    def get_execution_order(self) -> List[List[str]]:
        """Get the planned execution order (layers).

        Returns:
            List of layers, each layer contains task IDs that can run in parallel
        """
        layers: List[List[str]] = []
        completed: Set[str] = set()
        remaining = set(self._tasks.keys())

        while remaining:
            # Find tasks with all dependencies satisfied
            layer = []
            for task_id in remaining:
                task = self._tasks[task_id]
                if task.depends_on <= completed:
                    layer.append(task_id)

            if not layer:
                # Circular dependency detected
                raise ValueError(f"Circular dependency detected in tasks: {remaining}")

            layers.append(layer)
            completed.update(layer)
            remaining -= set(layer)

        return layers


# =============================================================================
# Convenience Functions
# =============================================================================

async def run_with_dependencies(
    tasks: Dict[str, TaskSpec],
    dependencies: Dict[str, List[str]],
    max_concurrent: int = 4,
    retry_policy: Optional[RetryPolicy] = None,
    config: Optional[ClaudeConfig] = None,
) -> CombinedResult:
    """Run tasks with explicit dependency specification.

    Args:
        tasks: Mapping of task_id -> TaskSpec
        dependencies: Mapping of task_id -> list of dependency task_ids
        max_concurrent: Maximum concurrent tasks
        retry_policy: Retry policy
        config: Claude configuration

    Returns:
        CombinedResult with all results

    Example:
        >>> tasks = {
        ...     "a": TaskSpec.prompt_task("Task A"),
        ...     "b": TaskSpec.prompt_task("Task B"),
        ...     "c": TaskSpec.prompt_task("Task C"),
        ... }
        >>> deps = {"c": ["a", "b"]}  # c depends on a and b
        >>> results = await run_with_dependencies(tasks, deps)
    """
    async with Orchestrator(
        config=config,
        max_concurrent=max_concurrent,
        retry_policy=retry_policy
    ) as orch:
        # Add tasks in dependency order
        added: Set[str] = set()

        def add_with_deps(task_id: str) -> None:
            if task_id in added:
                return
            # Add dependencies first
            for dep in dependencies.get(task_id, []):
                add_with_deps(dep)
            # Add this task
            orch.add_task(
                task_id,
                tasks[task_id],
                depends_on=dependencies.get(task_id)
            )
            added.add(task_id)

        for task_id in tasks:
            add_with_deps(task_id)

        return await orch.run()


async def run_pipeline(
    stages: List[List[TaskSpec]],
    max_concurrent: int = 4,
    config: Optional[ClaudeConfig] = None,
) -> CombinedResult:
    """Run tasks in pipeline stages.

    Each stage completes before the next begins.
    Tasks within a stage run in parallel.

    Args:
        stages: List of stages, each stage is a list of TaskSpecs
        max_concurrent: Maximum concurrent tasks per stage
        config: Claude configuration

    Returns:
        CombinedResult with all results

    Example:
        >>> stages = [
        ...     [TaskSpec.prompt_task("Analyze A"), TaskSpec.prompt_task("Analyze B")],
        ...     [TaskSpec.prompt_task("Combine results")],
        ... ]
        >>> results = await run_pipeline(stages)
    """
    async with Orchestrator(config=config, max_concurrent=max_concurrent) as orch:
        prev_stage_ids: List[str] = []

        for stage_idx, stage in enumerate(stages):
            stage_ids: List[str] = []

            for task_idx, spec in enumerate(stage):
                task_id = f"stage{stage_idx}_task{task_idx}"
                orch.add_task(
                    task_id,
                    spec,
                    depends_on=prev_stage_ids if prev_stage_ids else None
                )
                stage_ids.append(task_id)

            prev_stage_ids = stage_ids

        return await orch.run()
