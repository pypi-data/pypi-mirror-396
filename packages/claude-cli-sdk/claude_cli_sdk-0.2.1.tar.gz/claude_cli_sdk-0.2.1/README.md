# Claude CLI SDK

A Python library that wraps Claude CLI as a subprocess, providing SDK-like usage.
Use all Claude CLI features including Skills, Hooks, Slash Commands, and Agents without requiring an official SDK.

## Installation

```bash
pip install claude-cli-sdk
```

**Prerequisites:**
- Python >= 3.10
- Claude CLI installed and authenticated (`claude --version` to verify)
- Valid Anthropic API key configured in Claude CLI

```python
# Verify Claude CLI is available
from claude_cli_sdk import check_claude_cli

if check_claude_cli():
    print("Claude CLI is ready!")
else:
    print("Please install Claude CLI first")
```

## Quick Start

### Async Usage

```python
import asyncio
from claude_cli_sdk import Claude

async def main():
    async with Claude() as claude:
        result = await claude.run("What is Python?")
        print(result.text)

asyncio.run(main())
```

### Sync Usage

```python
from claude_cli_sdk import ClaudeSync

claude = ClaudeSync()
result = claude.run("Hello!")
print(result.text)
```

## Features

| Feature | Description |
|---------|-------------|
| **Skills** | Call registered skills via `--setting-sources` |
| **Hooks** | Auto-load hooks from settings |
| **Agents (Task tool)** | Use Explore, Plan, and other agents |
| **Slash Commands** | Execute custom slash commands |
| **MCP Servers** | Configure via `--mcp-config` |
| **CLAUDE.md** | Auto-load project context |
| **Streaming** | Real-time event streaming |
| **Cancellation** | Cancel long-running operations |
| **Parallel Execution** | Run multiple sessions concurrently with resource management |
| **Orchestration** | DAG-based task execution with dependencies, retry, and shared context |

## Usage Examples

### Configuration

```python
from claude_cli_sdk import Claude, ClaudeConfig, PermissionMode

config = ClaudeConfig(
    model="sonnet",                              # Model to use
    permission_mode=PermissionMode.ACCEPT_EDITS, # Auto-approve edits
    allowed_tools=["Read", "Write", "Bash"],     # Allowed tools
    max_turns=5,                                 # Max conversation turns
    timeout=120.0,                               # Timeout in seconds
    cwd="/path/to/project",                      # Working directory
    system_prompt="You are a helpful assistant"  # Custom system prompt
)

async with Claude(config) as claude:
    result = await claude.run("Analyze the codebase")
```

### Using Skills

```python
# Async
result = await claude.skill("frontend-design", "Create a login form with validation")

# Sync
result = claude.skill("frontend-design", "Create a responsive navbar")
```

### Using Agents

```python
# Explore agent - search and understand codebase
result = await claude.agent("Explore", "Find all API endpoints in the project")

# Plan agent - design implementation strategies
result = await claude.agent("Plan", "Design a user authentication system")
```

### Slash Commands

```python
# Execute a slash command
result = await claude.command("code-review")

# With arguments
result = await claude.command("feature-dev", "Add user profile page")
```

### Streaming Execution

```python
async for event in claude.run_streaming("Explain async programming"):
    print(f"[{event.type}]", end=" ")
    if event.type == "assistant":
        print(event.message)
    elif event.type == "result":
        print(event.result_text)
```

### With File Context

```python
# Include files as context
result = await claude.run_with_files(
    "Review these files for security issues",
    ["src/auth.py", "src/database.py", "config.yaml"]
)
```

### Cancellation

```python
from claude_cli_sdk import CancellationToken

token = CancellationToken()

# Start a long-running task
task = asyncio.create_task(
    claude.run("Complex analysis task", cancel_token=token)
)

# Cancel after 10 seconds
await asyncio.sleep(10)
token.cancel()
```

### Progress Callback

```python
def on_progress(event_type: str, data: dict):
    if event_type == "assistant":
        print("Claude is responding...")
    elif event_type == "tool_use":
        print(f"Using tool: {data.get('name')}")

result = await claude.run(
    "Create a Python script",
    on_progress=on_progress
)
```

### Session Continuation

```python
# First interaction
result1 = await claude.run("My name is Alice")

# Continue the conversation
result2 = await claude.continue_conversation("What is my name?")
print(result2.text)  # "Your name is Alice"
```

### Hook Management

Programmatically manage Claude CLI hooks without editing settings.json manually:

```python
from claude_cli_sdk import HookManager, Hook, quick_hook_setup

# Create a hook manager
hooks = HookManager()

# Add pre-tool hooks (called before tool executes)
hooks.add_pre_tool_use(Hook(
    matcher="Bash",           # Match Bash tool
    command="./validate.sh",  # Run this script
    timeout=5000              # 5 second timeout
))

# Add post-tool hooks (called after tool completes)
hooks.add_post_tool_use(Hook(
    matcher="*",              # Match all tools
    command="./log_tool.sh"
))

# Save to project settings (.claude/settings.json)
hooks.save_to_project()

# Or save to user settings (~/.claude/settings.json)
hooks.save_to_user()
```

#### Quick Hook Setup

```python
from claude_cli_sdk import quick_hook_setup

# One-liner for common hook configurations
hooks = quick_hook_setup(
    validate_bash="./scripts/validate_bash.sh",  # Validate Bash commands
    log_tools="./scripts/log_all_tools.sh",      # Log all tool usage
    backup_edits="./scripts/backup_before_edit.sh"  # Backup before editing
)
hooks.save_to_project()
```

#### Convenience Hook Creators

```python
from claude_cli_sdk import (
    create_bash_validator,
    create_file_logger,
    create_edit_backup
)

# Create specific hooks easily
bash_hook = create_bash_validator("./validate.sh", timeout=3000)
log_hook = create_file_logger("./log.sh", tools="Write")
backup_hook = create_edit_backup("./backup.sh")

hooks = HookManager()
hooks.add_pre_tool_use(bash_hook)
hooks.add_pre_tool_use(backup_hook)
hooks.add_post_tool_use(log_hook)
hooks.save_to_project()
```

#### Load and Modify Existing Hooks

```python
hooks = HookManager()
hooks.load_from_project()  # Load existing hooks

# Modify
hooks.add_pre_tool_use(Hook(matcher="Write", command="./check_write.sh"))

# Save back
hooks.save_to_project()

# Remove all hooks
hooks.remove_from_project()
```

### Quick Functions (One-liners)

```python
from claude_cli_sdk import (
    quick_run, quick_run_sync,
    quick_skill, quick_skill_sync,
    quick_agent, quick_agent_sync,
    quick_command, quick_streaming
)

# Async one-liners
result = await quick_run("Hello!")
result = await quick_skill("frontend-design", "Create a button")
result = await quick_agent("Explore", "Find Python files")
result = await quick_command("code-review")

# Sync one-liners
result = quick_run_sync("Hello!")

# Streaming
async for event in quick_streaming("Explain this"):
    print(event.type)

# With config options
result = await quick_run("Explain this", model="opus", max_turns=3)
```

## Result Object

The `ClaudeResult` object provides rich access to execution results:

```python
result = await claude.run("Create a script")

# Basic properties
result.text          # Final result text
result.success       # True if successful
result.session_id    # Session ID for continuation
result.stderr        # Standard error output

# Execution info
result.cost          # Cost information (if available)
result.duration_ms   # Execution duration in ms
result.num_turns     # Number of conversation turns

# Tool usage
result.tools_used    # List of tools used: ["Write", "Bash", ...]
result.has_tool("Write")  # Check if specific tool was used
result.get_tool_results("Read")  # Get results from specific tool

# Messages
result.get_assistant_messages()  # All assistant text messages
result.get_events_by_type("tool_use")  # Filter events by type

# Iteration
for event in result.iter_events():
    print(event.type, event.data)

# Boolean check
if result:  # True if success
    print("Success!")
```

## Configuration Options

```python
from claude_cli_sdk import ClaudeConfig, PermissionMode, OutputFormat

config = ClaudeConfig(
    # Model selection
    model="sonnet",  # or "opus", "haiku", etc.

    # Permission handling
    permission_mode=PermissionMode.ACCEPT_EDITS,  # Auto-approve file edits
    # Options: DEFAULT, ACCEPT_EDITS, BYPASS_PERMISSIONS

    # Output format (usually keep default)
    output_format=OutputFormat.STREAM_JSON,

    # Settings sources for Skills, Hooks, CLAUDE.md
    setting_sources=["user", "project"],

    # Tool permissions
    allowed_tools=["Read", "Write", "Bash", "Glob", "Grep"],
    disallowed_tools=["dangerous_tool"],

    # MCP configuration
    mcp_config="/path/to/mcp-config.json",

    # Working directory
    cwd="/path/to/project",

    # Conversation limits
    max_turns=10,

    # Custom system prompt
    system_prompt="You are a code review expert",

    # Timeout
    timeout=300.0,  # 5 minutes

    # Claude CLI path (if not in PATH)
    claude_path="/usr/local/bin/claude"
)
```

## Event Types

When streaming or analyzing results, you'll encounter these event types:

| Type | Description |
|------|-------------|
| `system` | Session information (contains `session_id`) |
| `assistant` | Claude's response (text and tool calls) |
| `tool_use` | Tool invocation details |
| `tool_result` | Tool execution results |
| `result` | Final result of the execution |
| `error` | Error information |

## Architecture

```
┌─────────────────────────────────────────┐
│         Your Python Application          │
├─────────────────────────────────────────┤
│           claude_cli_sdk                 │
│  - Async/Sync clients                    │
│  - subprocess.Popen("claude", ...)       │
│  - JSON stream parsing                   │
│  - Event handling                        │
├─────────────────────────────────────────┤
│              Claude CLI                  │
│  (All features exposed via flags)        │
└─────────────────────────────────────────┘
```

## Parallel Execution

Execute multiple prompts or tasks concurrently across separate sessions:

### Simple Parallel Prompts

```python
from claude_cli_sdk import run_parallel_prompts

# Run multiple prompts in parallel
results = await run_parallel_prompts([
    "What is Python?",
    "What is JavaScript?",
    "What is Rust?",
], max_concurrent=3)

print(f"Completed: {results.success_count}/{results.total_count}")
for result in results.sessions:
    if result.is_success:
        print(f"[{result.task_id}] {result.text[:100]}...")
```

### Using SessionManager

For more control over parallel execution:

```python
from claude_cli_sdk import SessionManager, TaskSpec, ClaudeConfig

config = ClaudeConfig(max_turns=3)

async with SessionManager(config, max_concurrent_sessions=4) as manager:
    # Create multiple sessions
    research_session = await manager.create_session("research")
    coding_session = await manager.create_session("coding")

    # Assign tasks to sessions
    results = await manager.run_sessions_parallel({
        research_session: [
            TaskSpec.prompt_task("Explain asyncio"),
            TaskSpec.prompt_task("Explain threading"),
        ],
        coding_session: [
            TaskSpec.agent_task("Explore", "Find Python files"),
            TaskSpec.skill_task("frontend-design", "Create a button"),
        ],
    })

    # Process results
    for session, session_results in results.items():
        print(f"\nSession '{session.name}':")
        for r in session_results:
            status = "✓" if r.is_success else "✗"
            print(f"  {status} [{r.task_id}] {r.duration_ms:.0f}ms")
```

### Parallel Execution Strategy

```
┌─────────────────────────────────────────────────────────┐
│                    SessionManager                        │
│  (max_concurrent_sessions=4, semaphore-based limiting)   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ Session1 │  │ Session2 │  │ Session3 │  │ Session4 │ │
│  │ (serial) │  │ (serial) │  │ (serial) │  │ (serial) │ │
│  │ Task1    │  │ Task1    │  │ Task1    │  │ Task1    │ │
│  │ Task2    │  │ Task2    │  │          │  │          │ │
│  │ Task3    │  │          │  │          │  │          │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
│       │             │             │             │        │
│       └─────────────┴─────────────┴─────────────┘        │
│                         │                                │
│                    Parallel                              │
│                  (across sessions)                       │
└─────────────────────────────────────────────────────────┘
```

**Key Design Decisions:**
- **Within a session**: Tasks execute sequentially (CLI architecture constraint)
- **Across sessions**: Sessions run in parallel via asyncio
- **Resource control**: Semaphore limits concurrent sessions
- **Result aggregation**: Collected and combined in Python

## Orchestration (Advanced)

For complex workflows with dependencies, use the `Orchestrator` class:

### DAG-based Task Execution

```python
from claude_cli_sdk import Orchestrator, TaskSpec, RetryPolicy, RetryStrategy

async def analyze_codebase():
    async with Orchestrator(
        max_concurrent=4,
        retry_policy=RetryPolicy(
            max_retries=3,
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF
        )
    ) as orch:
        # Add independent tasks (run in parallel)
        orch.add_task("frontend", TaskSpec.prompt_task("Analyze frontend code"))
        orch.add_task("backend", TaskSpec.prompt_task("Analyze backend code"))
        orch.add_task("security", TaskSpec.agent_task("Explore", "Find security issues"))

        # Add dependent task (waits for all above)
        orch.add_task(
            "integration",
            TaskSpec.prompt_task("Combine all analysis results"),
            depends_on=["frontend", "backend", "security"]
        )

        results = await orch.run()
        print(f"Completed: {results.metadata['completed']}/{results.metadata['total_tasks']}")
```

### Execution Order Visualization

```
Layer 0 (parallel):  [frontend]  [backend]  [security]
                          │          │          │
                          └──────────┼──────────┘
                                     │
Layer 1 (waits):              [integration]
```

### Shared Context Between Tasks

```python
async with Orchestrator() as orch:
    # Tasks can share data via context
    orch.add_task("scan", TaskSpec.prompt_task("Scan for vulnerabilities"))

    # Access context in progress callback
    async def on_progress(task_id, status, event):
        if status == TaskStatus.COMPLETED:
            findings = await orch.context.read(f"result:{task_id}")
            print(f"Task {task_id} found: {findings}")

    results = await orch.run()

    # Read all shared results
    all_data = await orch.context.read_all()
```

### Pipeline Execution (Stages)

```python
from claude_cli_sdk import run_pipeline

# Execute in stages: all tasks in stage N complete before stage N+1 starts
results = await run_pipeline([
    # Stage 0: Analysis (parallel)
    [
        TaskSpec.prompt_task("Analyze module A"),
        TaskSpec.prompt_task("Analyze module B"),
    ],
    # Stage 1: Integration (after stage 0)
    [
        TaskSpec.prompt_task("Combine analysis results"),
    ],
    # Stage 2: Report (after stage 1)
    [
        TaskSpec.prompt_task("Generate final report"),
    ],
])
```

### Retry Strategies

| Strategy | Behavior |
|----------|----------|
| `IMMEDIATE` | Retry immediately (no delay) |
| `LINEAR_BACKOFF` | 1s, 2s, 3s, ... |
| `EXPONENTIAL_BACKOFF` | 1s, 2s, 4s, 8s, ... (default) |

```python
# Custom retry policy
policy = RetryPolicy(
    max_retries=5,
    base_delay=0.5,        # Start with 0.5s
    max_delay=30.0,        # Cap at 30s
    strategy=RetryStrategy.EXPONENTIAL_BACKOFF
)
```

## Exception Handling

The SDK provides specific exception types for better error handling:

```python
from claude_cli_sdk import (
    Claude,
    ClaudeSDKError,        # Base exception
    CLINotFoundError,      # Claude CLI not found
    SessionNotFoundError,  # No session to continue
    SessionNotStartedError, # Session not started
    ExecutionTimeoutError, # Timeout exceeded
    ExecutionCancelledError, # Cancelled by user
)

try:
    async with Claude() as claude:
        result = await claude.run("Hello")
except CLINotFoundError:
    print("Please install Claude CLI first")
except SessionNotFoundError:
    print("No previous session to continue")
except ExecutionTimeoutError as e:
    print(f"Timed out after {e.timeout}s")
except ClaudeSDKError as e:
    print(f"SDK error: {e}")
```

## CLI Flags Reference

The SDK uses these Claude CLI flags internally:

| Flag | Purpose |
|------|---------|
| `--setting-sources "user,project"` | Load Skills, Hooks, CLAUDE.md |
| `--allowed-tools "Tool1,Tool2"` | Specify allowed tools |
| `--output-format stream-json` | JSON stream output |
| `--verbose` | Required for stream-json |
| `--permission-mode acceptEdits` | Auto-approve file edits |
| `--max-turns N` | Limit conversation turns |
| `--mcp-config path` | MCP server configuration |
| `--model name` | Model selection |
| `--system-prompt text` | Custom system prompt |

## Limitations

### Claude CLI Dependency
- Claude CLI must be installed and authenticated before using this SDK
- The SDK wraps CLI subprocess calls; it does not use the Anthropic API directly

### Parallel Execution Constraints
- **Within-session serialization**: Tasks in the same session always run sequentially
- **Resource consumption**: Each session spawns a separate subprocess
- **Recommended concurrent sessions**: 2-8 depending on system resources

### Platform Support
- **Linux/macOS**: Fully tested and supported
- **Windows**: Should work but not extensively tested (subprocess behavior may differ)

### Other Limitations
- **Streaming interruption**: No automatic recovery if network connection drops
- **Cost tracking**: `result.cost` only available when Claude CLI provides it
- **File lock conflicts**: Concurrent sessions writing to the same files may conflict

### Recommended Practices
1. Use `check_claude_cli()` before creating clients
2. Set appropriate `max_turns` to prevent runaway sessions
3. Use `max_concurrent_sessions` based on your system's resources
4. Handle exceptions appropriately for production use

## License

MIT License
