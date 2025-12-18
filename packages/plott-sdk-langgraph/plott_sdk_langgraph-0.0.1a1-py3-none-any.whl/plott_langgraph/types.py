"""Type definitions for Plott LangGraph SDK."""

from enum import Enum
from typing import TypedDict, Optional, List, Any, Dict
from typing_extensions import NotRequired


class LangGraphEventTypes(str, Enum):
    """LangGraph stream event types."""
    OnChainStart = "on_chain_start"
    OnChainStream = "on_chain_stream"
    OnChainEnd = "on_chain_end"
    OnChatModelStart = "on_chat_model_start"
    OnChatModelStream = "on_chat_model_stream"
    OnChatModelEnd = "on_chat_model_end"
    OnToolStart = "on_tool_start"
    OnToolEnd = "on_tool_end"
    OnCustomEvent = "on_custom_event"
    OnInterrupt = "on_interrupt"


class CustomEventNames(str, Enum):
    """Custom event names used in LangGraph."""
    ManuallyEmitMessage = "manually_emit_message"
    ManuallyEmitToolCall = "manually_emit_tool_call"
    ManuallyEmitState = "manually_emit_state"
    Exit = "exit"


# Generic state type
State = Dict[str, Any]


class MessageInProgress(TypedDict, total=False):
    """Tracks a message or tool call currently being streamed."""
    id: str
    tool_call_id: Optional[str]
    tool_call_name: Optional[str]


class RunMetadata(TypedDict, total=False):
    """Metadata for the current run being tracked."""
    id: str
    thread_id: Optional[str]
    node_name: Optional[str]
    has_function_streaming: bool
    current_text_message: Optional[str]


# Type alias for the messages in progress record
MessagesInProgressRecord = Dict[str, Optional[MessageInProgress]]


class ToolCall(TypedDict):
    """Tool call structure."""
    id: str
    name: str
    args: Dict[str, Any]


class LangGraphReasoning(TypedDict):
    """Reasoning/thinking content from LLM."""
    type: str
    text: str
    index: int


class LLMCallTiming(TypedDict, total=False):
    """Timing data for LLM call tracking."""
    start_time: float  # time.time() in seconds
    first_token_time: Optional[float]
    is_streaming: bool


class CurrentToolCall(TypedDict, total=False):
    """Current tool call being tracked."""
    tool_call_id: str
    tool_name: str
    status: str  # 'started' | 'completed'
    args: Optional[Any]
