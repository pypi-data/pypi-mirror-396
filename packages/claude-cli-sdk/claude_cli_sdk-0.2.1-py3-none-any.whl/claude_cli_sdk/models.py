"""Data model definitions for Claude CLI SDK."""

from dataclasses import dataclass, field, asdict
from typing import Optional, Any, Iterator


@dataclass
class Message:
    """Message structure.

    Attributes:
        role: Role ("user" or "assistant")
        content: Message content
        tool_use: Tool use information (if present)
        tool_result: Tool execution result (if present)
    """
    role: str
    content: str
    tool_use: Optional[dict] = None
    tool_result: Optional[dict] = None


@dataclass
class StreamEvent:
    """Stream event from Claude CLI.

    Attributes:
        type: Event type (system, assistant, tool_use, tool_result, result)
        data: Event data
        raw: Raw JSON string
    """
    type: str
    data: dict
    raw: str

    @property
    def session_id(self) -> Optional[str]:
        """Session ID (for system events)."""
        if self.type == "system":
            return self.data.get("session_id")
        return None

    @property
    def message(self) -> Optional[dict]:
        """Message (for assistant events)."""
        if self.type == "assistant":
            return self.data.get("message")
        return None

    @property
    def result_text(self) -> Optional[str]:
        """Result text (for result events)."""
        if self.type == "result":
            return self.data.get("result")
        return None

    @property
    def tool_name(self) -> Optional[str]:
        """Tool name (for tool_use events)."""
        if self.type == "tool_use":
            return self.data.get("name")
        return None

    @property
    def tool_input(self) -> Optional[dict]:
        """Tool input (for tool_use events)."""
        if self.type == "tool_use":
            return self.data.get("input")
        return None

    @property
    def is_error(self) -> bool:
        """Whether this is an error event."""
        return self.type == "error" or self.data.get("is_error", False)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {"type": self.type, "data": self.data, "raw": self.raw}


@dataclass
class ClaudeResult:
    """Claude execution result.

    Attributes:
        events: List of all events
        result: Final result event
        session_id: Session ID
        stderr: Standard error output
        success: Whether execution was successful

    Properties:
        text: Result text
        tools_used: List of tools used
    """
    events: list[dict] = field(default_factory=list)
    result: Optional[dict] = None
    session_id: Optional[str] = None
    stderr: Optional[str] = None
    success: bool = True

    @property
    def text(self) -> str:
        """Get result text."""
        if self.result:
            return self.result.get("result", "")
        return ""

    @property
    def tools_used(self) -> list[str]:
        """Get list of tools used."""
        tools = []
        for event in self.events:
            if event.get("type") == "assistant":
                content = event.get("message", {}).get("content", [])
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "tool_use":
                        tool_name = item.get("name")
                        if tool_name and tool_name not in tools:
                            tools.append(tool_name)
        return tools

    def get_tool_results(self, tool_name: Optional[str] = None) -> list[dict]:
        """Get results from specific tool.

        Args:
            tool_name: Tool name to filter by. If None, returns all tool results.

        Returns:
            List of tool result events.
        """
        results = []
        for event in self.events:
            if event.get("type") == "tool_result":
                if tool_name is None or event.get("name") == tool_name:
                    results.append(event)
        return results

    def __repr__(self) -> str:
        text_preview = self.text[:50] + "..." if len(self.text) > 50 else self.text
        return f"ClaudeResult(success={self.success}, text='{text_preview}')"

    def __bool__(self) -> bool:
        """Returns success status. Allows `if result:` syntax."""
        return self.success

    @property
    def is_error(self) -> bool:
        """Whether execution failed."""
        return not self.success

    @property
    def cost(self) -> Optional[dict]:
        """Cost information (if available)."""
        if self.result:
            return self.result.get("cost")
        return None

    @property
    def duration_ms(self) -> Optional[int]:
        """Execution duration in milliseconds."""
        if self.result:
            return self.result.get("duration_ms")
        return None

    @property
    def num_turns(self) -> int:
        """Number of conversation turns."""
        if self.result:
            return self.result.get("num_turns", 0)
        return len([e for e in self.events if e.get("type") == "assistant"])

    def get_events_by_type(self, event_type: str) -> list[dict]:
        """Get events of a specific type.

        Args:
            event_type: Event type to filter by.

        Returns:
            List of matching events.
        """
        return [e for e in self.events if e.get("type") == event_type]

    def get_assistant_messages(self) -> list[str]:
        """Get list of assistant message texts.

        Returns:
            List of text content from assistant messages.
        """
        messages = []
        for event in self.events:
            if event.get("type") == "assistant":
                content = event.get("message", {}).get("content", [])
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        messages.append(item.get("text", ""))
                    elif isinstance(item, str):
                        messages.append(item)
        return messages

    def has_tool(self, tool_name: str) -> bool:
        """Check if a specific tool was used.

        Args:
            tool_name: Name of the tool to check.

        Returns:
            True if the tool was used.
        """
        return tool_name in self.tools_used

    def iter_events(self) -> Iterator[StreamEvent]:
        """Iterate over events as StreamEvent objects.

        Yields:
            StreamEvent objects.
        """
        import json
        for event in self.events:
            yield StreamEvent(
                type=event.get("type", "unknown"),
                data=event,
                raw=json.dumps(event)
            )

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Dictionary representation of the result.
        """
        return {
            "events": self.events,
            "result": self.result,
            "session_id": self.session_id,
            "stderr": self.stderr,
            "success": self.success,
        }
