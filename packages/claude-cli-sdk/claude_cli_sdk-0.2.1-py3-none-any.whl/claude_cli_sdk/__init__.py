"""
Claude CLI SDK
==============

A Python library that wraps Claude CLI as a subprocess, providing SDK-like usage.
Use all Claude CLI features including Skills, Hooks, Slash Commands, and Agents
without requiring an official SDK.

Basic Usage
-----------
>>> from claude_cli_sdk import Claude, ClaudeSync
>>>
>>> # Async usage
>>> async with Claude() as claude:
...     result = await claude.run("Hello!")
...     print(result.text)
>>>
>>> # Sync usage
>>> claude = ClaudeSync()
>>> result = claude.run("Hello!")
>>> print(result.text)

Skills
------
>>> result = await claude.skill("frontend-design", "Create a button")

Agents
------
>>> result = await claude.agent("Explore", "Find Python files")

Slash Commands
--------------
>>> result = await claude.command("code-review")

Parallel Execution
------------------
>>> from claude_cli_sdk import run_parallel_prompts
>>> results = await run_parallel_prompts(["Hello", "World"], max_concurrent=2)

Orchestration (DAG-based)
-------------------------
>>> from claude_cli_sdk import Orchestrator, TaskSpec
>>> async with Orchestrator() as orch:
...     orch.add_task("analyze", TaskSpec.prompt_task("Analyze code"))
...     orch.add_task("fix", TaskSpec.prompt_task("Fix issues"), depends_on=["analyze"])
...     results = await orch.run()
"""

__version__ = "0.2.0"
__author__ = "Claude CLI SDK Contributors"

from .config import ClaudeConfig, PermissionMode, OutputFormat
from .models import StreamEvent, ClaudeResult, Message
from .client import Claude, ClaudeSync, CancellationToken, check_claude_cli
from .exceptions import (
    ClaudeSDKError,
    CLINotFoundError,
    SessionNotFoundError,
    SessionNotStartedError,
    ExecutionTimeoutError,
    ExecutionCancelledError,
    ResourceLimitExceededError,
    InvalidConfigError,
)
from .hooks import (
    Hook,
    HookType,
    HookConfig,
    HookManager,
    create_bash_validator,
    create_file_logger,
    create_edit_backup,
    quick_hook_setup,
)
from .utils import (
    quick_run,
    quick_skill,
    quick_agent,
    quick_run_sync,
    quick_run_with_files,
    quick_run_with_files_sync,
    quick_command,
    quick_command_sync,
    quick_streaming,
    quick_skill_sync,
    quick_agent_sync,
)
from .parallel import (
    TaskSpec,
    SessionResult,
    CombinedResult,
    ClaudeSession,
    SessionManager,
    aggregate_results,
    run_parallel_prompts,
    run_parallel_tasks,
)
from .orchestrator import (
    Orchestrator,
    TaskNode,
    TaskStatus,
    RetryPolicy,
    RetryStrategy,
    SharedContext,
    run_with_dependencies,
    run_pipeline,
)

__all__ = [
    # Main classes
    "Claude",
    "ClaudeSync",
    "CancellationToken",
    "check_claude_cli",
    # Config
    "ClaudeConfig",
    "PermissionMode",
    "OutputFormat",
    # Models
    "StreamEvent",
    "ClaudeResult",
    "Message",
    # Exceptions
    "ClaudeSDKError",
    "CLINotFoundError",
    "SessionNotFoundError",
    "SessionNotStartedError",
    "ExecutionTimeoutError",
    "ExecutionCancelledError",
    "ResourceLimitExceededError",
    "InvalidConfigError",
    # Hooks
    "Hook",
    "HookType",
    "HookConfig",
    "HookManager",
    "create_bash_validator",
    "create_file_logger",
    "create_edit_backup",
    "quick_hook_setup",
    # Parallel Execution
    "TaskSpec",
    "SessionResult",
    "CombinedResult",
    "ClaudeSession",
    "SessionManager",
    "aggregate_results",
    "run_parallel_prompts",
    "run_parallel_tasks",
    # Orchestration
    "Orchestrator",
    "TaskNode",
    "TaskStatus",
    "RetryPolicy",
    "RetryStrategy",
    "SharedContext",
    "run_with_dependencies",
    "run_pipeline",
    # Utils - Async
    "quick_run",
    "quick_skill",
    "quick_agent",
    "quick_command",
    "quick_run_with_files",
    "quick_streaming",
    # Utils - Sync
    "quick_run_sync",
    "quick_skill_sync",
    "quick_agent_sync",
    "quick_command_sync",
    "quick_run_with_files_sync",
]
