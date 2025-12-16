"""Convenience functions for Claude CLI SDK."""

from pathlib import Path
from typing import Any, Union, AsyncIterator

from .config import ClaudeConfig
from .models import ClaudeResult, StreamEvent


async def quick_run(prompt: str, **kwargs: Any) -> ClaudeResult:
    """Quick async execution.

    Suitable for one-off prompt execution.

    Args:
        prompt: Prompt to execute
        **kwargs: Arguments passed to ClaudeConfig

    Returns:
        ClaudeResult: Execution result

    Example:
        >>> result = await quick_run("Hello!")
        >>> print(result.text)

        >>> result = await quick_run("Explain this", model="opus")
    """
    from .client import Claude

    config = ClaudeConfig(**kwargs)
    async with Claude(config) as claude:
        return await claude.run(prompt)


async def quick_skill(skill_name: str, prompt: str, **kwargs: Any) -> ClaudeResult:
    """Quick skill execution.

    Args:
        skill_name: Name of the skill
        prompt: Prompt to pass to the skill
        **kwargs: Arguments passed to ClaudeConfig

    Returns:
        ClaudeResult: Execution result

    Example:
        >>> result = await quick_skill("frontend-design", "Create a button")
    """
    from .client import Claude

    config = ClaudeConfig(**kwargs)
    async with Claude(config) as claude:
        return await claude.skill(skill_name, prompt)


async def quick_agent(agent_type: str, task: str, **kwargs: Any) -> ClaudeResult:
    """Quick agent execution.

    Args:
        agent_type: Agent type (e.g., "Explore", "Plan")
        task: Task to pass to the agent
        **kwargs: Arguments passed to ClaudeConfig

    Returns:
        ClaudeResult: Execution result

    Example:
        >>> result = await quick_agent("Explore", "Find Python files")
    """
    from .client import Claude

    config = ClaudeConfig(**kwargs)
    async with Claude(config) as claude:
        return await claude.agent(agent_type, task)


def quick_run_sync(prompt: str, **kwargs: Any) -> ClaudeResult:
    """Quick synchronous execution.

    Args:
        prompt: Prompt to execute
        **kwargs: Arguments passed to ClaudeConfig

    Returns:
        ClaudeResult: Execution result

    Example:
        >>> result = quick_run_sync("Hello!")
        >>> print(result.text)
    """
    from .client import ClaudeSync

    config = ClaudeConfig(**kwargs)
    with ClaudeSync(config) as claude:
        return claude.run(prompt)


async def quick_run_with_files(
    prompt: str,
    files: list[Union[str, Path]],
    **kwargs: Any
) -> ClaudeResult:
    """Quick async execution with file context.

    Args:
        prompt: Prompt to execute
        files: List of file paths to include as context
        **kwargs: Arguments passed to ClaudeConfig

    Returns:
        ClaudeResult: Execution result

    Example:
        >>> result = await quick_run_with_files(
        ...     "Analyze these files",
        ...     ["src/main.py", "src/utils.py"]
        ... )
    """
    from .client import Claude

    config = ClaudeConfig(**kwargs)
    async with Claude(config) as claude:
        return await claude.run_with_files(prompt, files)


def quick_run_with_files_sync(
    prompt: str,
    files: list[Union[str, Path]],
    **kwargs: Any
) -> ClaudeResult:
    """Quick synchronous execution with file context.

    Args:
        prompt: Prompt to execute
        files: List of file paths to include as context
        **kwargs: Arguments passed to ClaudeConfig

    Returns:
        ClaudeResult: Execution result

    Example:
        >>> result = quick_run_with_files_sync(
        ...     "Analyze these files",
        ...     ["src/main.py", "src/utils.py"]
        ... )
    """
    from .client import ClaudeSync

    config = ClaudeConfig(**kwargs)
    with ClaudeSync(config) as claude:
        return claude.run_with_files(prompt, files)


async def quick_command(command_name: str, **kwargs: Any) -> ClaudeResult:
    """Quick slash command execution.

    Args:
        command_name: Command name (without slash)
        **kwargs: Arguments passed to ClaudeConfig

    Returns:
        ClaudeResult: Execution result

    Example:
        >>> result = await quick_command("code-review")
    """
    from .client import Claude

    config = ClaudeConfig(**kwargs)
    async with Claude(config) as claude:
        return await claude.command(command_name)


def quick_command_sync(command_name: str, **kwargs: Any) -> ClaudeResult:
    """Quick synchronous slash command execution.

    Args:
        command_name: Command name (without slash)
        **kwargs: Arguments passed to ClaudeConfig

    Returns:
        ClaudeResult: Execution result

    Example:
        >>> result = quick_command_sync("code-review")
    """
    from .client import ClaudeSync

    config = ClaudeConfig(**kwargs)
    with ClaudeSync(config) as claude:
        return claude.command(command_name)


async def quick_streaming(prompt: str, **kwargs: Any) -> AsyncIterator[StreamEvent]:
    """Quick streaming execution.

    Args:
        prompt: Prompt to execute
        **kwargs: Arguments passed to ClaudeConfig

    Yields:
        StreamEvent: Stream events

    Example:
        >>> async for event in quick_streaming("Hello!"):
        ...     print(event.type, event.data)
    """
    from .client import Claude

    config = ClaudeConfig(**kwargs)
    async with Claude(config) as claude:
        async for event in claude.run_streaming(prompt):
            yield event


def quick_skill_sync(skill_name: str, prompt: str, **kwargs: Any) -> ClaudeResult:
    """Quick synchronous skill execution.

    Args:
        skill_name: Name of the skill
        prompt: Prompt to pass to the skill
        **kwargs: Arguments passed to ClaudeConfig

    Returns:
        ClaudeResult: Execution result

    Example:
        >>> result = quick_skill_sync("frontend-design", "Create a button")
    """
    from .client import ClaudeSync

    config = ClaudeConfig(**kwargs)
    with ClaudeSync(config) as claude:
        return claude.skill(skill_name, prompt)


def quick_agent_sync(agent_type: str, task: str, **kwargs: Any) -> ClaudeResult:
    """Quick synchronous agent execution.

    Args:
        agent_type: Agent type (e.g., "Explore", "Plan")
        task: Task to pass to the agent
        **kwargs: Arguments passed to ClaudeConfig

    Returns:
        ClaudeResult: Execution result

    Example:
        >>> result = quick_agent_sync("Explore", "Find Python files")
    """
    from .client import ClaudeSync

    config = ClaudeConfig(**kwargs)
    with ClaudeSync(config) as claude:
        return claude.agent(agent_type, task)
