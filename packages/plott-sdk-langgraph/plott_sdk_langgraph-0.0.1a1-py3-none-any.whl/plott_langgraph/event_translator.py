"""Event translator for converting LangGraph events to Plott analytics events."""

import json
import time
from typing import Any, Dict, List, Optional

from plott_core import PlottAnalytics

from .types import (
    LangGraphEventTypes,
    RunMetadata,
    LLMCallTiming,
    CurrentToolCall,
)
from .utils import (
    resolve_message_content,
    make_json_safe,
    dump_json_safe,
    extract_last_user_message,
    filter_state_snapshot,
)


class EventTracker:
    """
    Translates LangGraph stream events to Plott analytics events.

    This class processes events from LangGraph's astream_events() and converts
    them into the appropriate Plott analytics events (MESSAGE, TOOL, STATE_SNAPSHOT, etc.).

    Event processing strategy:
    - on_chat_model_start: Record start time for latency tracking
    - on_chat_model_stream: Track first token time for streaming latency
    - on_chat_model_end: Track LLM_CALL metrics (tokens, latency) and tool calls (started)
    - on_chain_end: Extract messages (AIMessage -> MESSAGE) and tool results (ToolMessage -> TOOL completed)
    - State snapshots are tracked on node change

    This design avoids streaming accumulation by extracting complete data from on_chain_end.
    """

    def __init__(self, client: PlottAnalytics):
        """
        Initialize the event tracker.

        Args:
            client: The PlottAnalytics client for sending events.
        """
        self._client = client
        self._active_run: Optional[RunMetadata] = None
        self._current_state: Dict[str, Any] = {}
        # LLM call tracking - only for timing/metrics
        # Maps llm_run_id -> timing data
        self._llm_call_timings: Dict[str, LLMCallTiming] = {}
        # Tool call tracking - maps tool_call_id -> tool info
        # Used to match tool started (from on_chat_model_end) with tool completed (from on_chain_end)
        self._pending_tool_calls: Dict[str, CurrentToolCall] = {}
        # Node tracking for state snapshots
        self._current_node_name: Optional[str] = None

    def create_active_run(self, run_id: str, thread_id: Optional[str] = None) -> None:
        """
        Initialize or update the active run context.

        Args:
            run_id: The unique identifier for this run.
            thread_id: The thread/session identifier.
        """
        if self._active_run is None or not self._active_run.get("id"):
            self._active_run = RunMetadata(
                id=run_id,
                thread_id=thread_id,
                has_function_streaming=False,
            )

    def handle_input_event(
        self,
        input_data: Dict[str, Any],
        run_id: str,
        thread_id: Optional[str] = None,
    ) -> None:
        """
        Track the user's input message.

        Args:
            input_data: The input passed to the graph (typically contains 'messages').
            run_id: The run identifier.
            thread_id: The thread/session identifier.
        """
        last_user_content = extract_last_user_message(input_data)
        if last_user_content:
            self._client.track_message_event(
                role="user",
                content=last_user_content,
                session_id=thread_id,
                run_id=run_id,
            )
            if input_data.get("state", None) is not None:
                self._client.track_state_snapshot_event(
                    snapshot=make_json_safe(input_data.get("state")),
                    role="assistant",
                    run_id=run_id,
                )

    def track_run_start(self, run_id: Optional[str] = None, thread_id: Optional[str] = None) -> None:
        """
        Track the start of a run.

        Args:
            run_id: The run identifier.
            :param run_id:
            :param thread_id:
        """

        print(1, run_id)
        print(2, thread_id)

        self._client.track_run_event(
            value="start",
            run_id=run_id or (self._active_run.get("id") if self._active_run else None),
            session_id=thread_id or (self._active_run.get("thread_id")if self._active_run else None),
        )

    def track_run_end(self, run_id: Optional[str] = None, thread_id: Optional[str] = None) -> None:
        """
        Track the end of a run.

        Args:
            run_id: The run identifier.
            :param run_id:
            :param thread_id:
        """
        self._maybe_emit_state_snapshot(
            run_id,
            thread_id or (self._active_run.get("thread_id") if self._active_run else None),
            self._active_run.get("last_metadata") if self._active_run else None,
        )
        self._client.track_run_event(
            value="end",
            run_id=run_id or (self._active_run.get("id") if self._active_run else None),
            session_id=thread_id or (self._active_run.get("thread_id") if self._active_run else None),
        )

    async def handle_single_event(
        self,
        event: Dict[str, Any],
        compiled: Any = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Process a single LangGraph stream event.

        This is the main entry point for event translation. It routes events
        to the appropriate handler based on event type.

        Args:
            event: The LangGraph stream event dictionary.
            compiled: The compiled LangGraph for state retrieval.
            config: The config passed to the graph execution.
        """
        # Store graph and config for state retrieval in _handle_chain_end
        self._graph = compiled
        self._config = config

        metadata = event.get("metadata", {})
        run_id = metadata.get("run_id") or event.get("run_id")
        thread_id = metadata.get("thread_id")

        if run_id:
            self.create_active_run(run_id, thread_id)

        # Track current node from metadata (set on entry, cleared on exit)
        current_node_name = metadata.get("langgraph_node")
        if current_node_name and self._current_node_name != current_node_name:
            self._current_node_name = current_node_name
            if self._active_run:
                self._active_run["node_name"] = current_node_name

        event_type = event.get("event")
        llm_run_id = event.get("run_id")

        try:
            # LLM call start tracking (matches TS implementation)
            if event_type == LangGraphEventTypes.OnChatModelStart.value:
                self._handle_chat_model_start(event, llm_run_id)
            elif event_type == LangGraphEventTypes.OnChatModelStream.value:
                self._handle_chat_model_stream(event, llm_run_id)
            elif event_type == LangGraphEventTypes.OnChatModelEnd.value:
                self._handle_chat_model_end(event, llm_run_id)
            elif event_type == LangGraphEventTypes.OnToolEnd.value:
                self._handle_tool_end(event)
            elif event_type == LangGraphEventTypes.OnChainEnd.value:
                self._handle_chain_end(event)
            elif event_type == "error":
                self._handle_error(event)
        except Exception:
            # Silently swallow errors - never affect the user's stream
            pass

    def _get_state_snapshot(self, state: Any) -> Dict[str, Any]:
        """
        Extract state values from a StateSnapshot or dict, filtering out messages.

        This matches the TypeScript SDK's getStateSnapshot() behavior where
        the 'messages' key is excluded from state snapshots.

        Args:
            state: The state object (could be StateSnapshot or dict).

        Returns:
            Dictionary of state values with messages filtered out.
        """
        # LangGraph StateSnapshot has a .values attribute
        if hasattr(state, "values"):
            state_values = dict(state.values) if state.values else {}
        elif isinstance(state, dict):
            state_values = state
        else:
            state_values = {}

        # Filter out messages (matches TS getStateSnapshot behavior)
        return filter_state_snapshot(state_values)

    def _handle_chat_model_start(self, event: Dict[str, Any], llm_run_id: Optional[str]) -> None:
        """
        Handle the start of chat model generation.

        Records the start time for latency tracking.

        Args:
            event: The on_chat_model_start event.
            llm_run_id: The LLM run ID for this call.
        """
        if llm_run_id:
            self._llm_call_timings[llm_run_id] = LLMCallTiming(
                start_time=time.time(),
                is_streaming=False,
            )

    def _handle_chat_model_stream(self, event: Dict[str, Any], llm_run_id: Optional[str] = None) -> None:
        """
        Handle streaming content from the chat model.

        Only tracks first token time for latency metrics. Messages are extracted
        from on_chain_end instead of accumulating streaming chunks.

        Args:
            event: The on_chat_model_stream event.
            llm_run_id: The LLM run ID for this call.
        """
        if not llm_run_id:
            return

        # Track first token time for streaming latency metrics
        if llm_run_id in self._llm_call_timings:
            timing = self._llm_call_timings[llm_run_id]
            if timing.get("first_token_time") is None:
                timing["first_token_time"] = time.time()
                timing["is_streaming"] = True

    def _handle_chat_model_end(self, event: Dict[str, Any], llm_run_id: Optional[str] = None) -> None:
        """
        Handle the end of chat model generation.

        Tracks LLM call metrics (tokens, latency) and tool calls as started.
        Messages are extracted from on_chain_end instead.

        Args:
            event: The on_chat_model_end event.
            llm_run_id: The LLM run ID for this call.
        """
        metadata = event.get("metadata", {})
        data = event.get("data", {})
        output = data.get("output", {})

        run_id = self._active_run.get("id") if self._active_run else None
        session_id = self._active_run.get("thread_id") if self._active_run else None

        # Extract tool calls and track as started
        tool_calls = None
        if hasattr(output, "tool_calls"):
            tool_calls = output.tool_calls
        elif isinstance(output, dict):
            kwargs = output.get("kwargs", {})
            tool_calls = kwargs.get("tool_calls") or output.get("tool_calls")

        if tool_calls:
            for tc in tool_calls:
                tool_call_id = tc.get("id") if isinstance(tc, dict) else getattr(tc, "id", None)
                tool_name = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", None)
                tool_args = tc.get("args") if isinstance(tc, dict) else getattr(tc, "args", None)

                if tool_call_id and tool_name:
                    # Track tool call as started
                    self._client.track_tool_event(
                        tool_call_id=tool_call_id,
                        tool_name=tool_name,
                        tool_status="started",
                        args=dump_json_safe(tool_args) if tool_args else None,
                        run_id=run_id,
                        session_id=session_id,
                        context={"metadata": metadata},
                    )
                    # Store for matching with completion later
                    self._pending_tool_calls[tool_call_id] = CurrentToolCall(
                        tool_call_id=tool_call_id,
                        tool_name=tool_name,
                        status="started",
                        args=dump_json_safe(tool_args) if tool_args else None,
                    )

        # Track LLM call metrics
        end_time = time.time()
        timing = self._llm_call_timings.get(llm_run_id) if llm_run_id else None

        # Extract usage metadata from output
        usage = None
        if hasattr(output, "usage_metadata"):
            usage = output.usage_metadata
        elif isinstance(output, dict):
            kwargs = output.get("kwargs", {})
            usage = kwargs.get("usage_metadata") or output.get("usage_metadata")

        finish_reason = "tool_calls" if tool_calls and len(tool_calls) > 0 else "stop"

        # Calculate latencies
        latency_ms = int((end_time - timing["start_time"]) * 1000) if timing else 0
        first_token_latency_ms = None
        if timing and timing.get("first_token_time"):
            first_token_latency_ms = int((timing["first_token_time"] - timing["start_time"]) * 1000)

        # Get token counts
        input_tokens = 0
        output_tokens = 0
        if usage:
            if hasattr(usage, "input_tokens"):
                input_tokens = usage.input_tokens or 0
            elif isinstance(usage, dict):
                input_tokens = usage.get("input_tokens", 0)
            if hasattr(usage, "output_tokens"):
                output_tokens = usage.output_tokens or 0
            elif isinstance(usage, dict):
                output_tokens = usage.get("output_tokens", 0)

        # Get model and provider from metadata
        model = metadata.get("ls_model_name", "")
        provider = metadata.get("ls_provider", "")

        # Track LLM call event
        self._client.track_llm_call_event(
            model=model or "unknown",
            provider=provider,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            finish_reason=finish_reason,
            is_streaming=timing.get("is_streaming", False) if timing else False,
            first_token_latency_ms=first_token_latency_ms,
            session_id=session_id,
            run_id=run_id,
            context={"metadata": metadata},
        )

        # Clean up timing data
        if llm_run_id and llm_run_id in self._llm_call_timings:
            del self._llm_call_timings[llm_run_id]

    def _handle_tool_end(self, event: Dict[str, Any]) -> None:
        """
        Handle tool execution completion (on_tool_end event).

        Note: Tool completions are primarily tracked via _handle_chain_end which
        processes ToolMessage objects from the node output. This handler is kept
        as a fallback but typically won't track events since _handle_chain_end
        handles them first.

        Args:
            event: The on_tool_end event.
        """
        # Tool completions are handled in _handle_chain_end via ToolMessage extraction
        # This handler is kept for compatibility but does minimal work
        pass

    def _handle_chain_end(self, event: Dict[str, Any]) -> None:
        """
        Handle chain (LangGraph node) completion.

        This is the primary place where we extract:
        - Assistant messages (AIMessage with content)
        - Tool call completions (ToolMessage with result)

        Args:
            event: The on_chain_end event.
        """
        metadata = event.get("metadata", {})
        node_name = metadata.get("langgraph_node")

        # Only process LangGraph node completions (not internal chains)
        if not node_name:
            return

        data = event.get("data", {})
        output = data.get("output")

        if not output:
            return

        run_id = self._active_run.get("id") if self._active_run else None
        session_id = self._active_run.get("thread_id") if self._active_run else None

        # Extract messages from various output formats
        messages = []

        # Command object (LangGraph): has .update with messages
        if hasattr(output, "update"):
            update_dict = output.update
            if isinstance(update_dict, dict):
                messages = update_dict.get("messages", [])
        # Dict with messages key
        elif isinstance(output, dict) and "messages" in output:
            messages = output.get("messages", [])

        # Process each message
        for msg in messages:
            msg_type = type(msg).__name__
            content = getattr(msg, "content", None)

            # Track AIMessage as assistant message
            if "AIMessage" in msg_type and content:
                resolved_content = resolve_message_content(content)
                if resolved_content:
                    self._client.track_message_event(
                        role="assistant",
                        content=resolved_content,
                        run_id=run_id,
                        session_id=session_id,
                        context={"metadata": metadata, "node": node_name},
                    )

            # Track ToolMessage as tool completion
            elif "ToolMessage" in msg_type:
                tool_call_id = getattr(msg, "tool_call_id", None)
                if tool_call_id:
                    # Look up the pending tool call to get the name
                    pending = self._pending_tool_calls.get(tool_call_id)
                    tool_name = pending.get("tool_name") if pending else getattr(msg, "name", None)

                    self._client.track_tool_event(
                        tool_call_id=tool_call_id,
                        tool_name=tool_name,
                        tool_status="completed",
                        result=dump_json_safe(content) if content else None,
                        run_id=run_id,
                        session_id=session_id,
                        context={"metadata": metadata, "node": node_name},
                    )

                    # Clean up pending tool call
                    if tool_call_id in self._pending_tool_calls:
                        del self._pending_tool_calls[tool_call_id]

        # Save metadata for use in track_run_end
        if self._active_run:
            self._active_run["last_metadata"] = metadata

        # Track state snapshot on node exit
        # Only emit if this is the node we've been tracking AND state has changed
        if node_name == self._current_node_name:
            self._maybe_emit_state_snapshot(run_id, session_id, metadata)

    def _maybe_emit_state_snapshot(
        self,
        run_id: Optional[str],
        session_id: Optional[str],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Emit state snapshot if state has changed since last snapshot."""
        if not hasattr(self, "_graph") or not self._graph or not hasattr(self, "_config") or not self._config:
            return

        try:
            # Use sync get_state (we're in a sync method)
            if hasattr(self._graph, "get_state"):
                state = self._graph.get_state(self._config)
            else:
                return

            if state is not None:
                state_values = self._get_state_snapshot(state)
                current_json = json.dumps(make_json_safe(self._current_state), sort_keys=True)
                new_json = json.dumps(make_json_safe(state_values), sort_keys=True)

                if current_json != new_json:
                    self._current_state = state_values
                    self._client.track_state_snapshot_event(
                        snapshot=make_json_safe(state_values),
                        role="assistant",
                        run_id=run_id,
                        session_id=session_id,
                        context={"metadata": metadata},
                    )
        except Exception:
            pass  # Never affect user stream

    def _handle_error(self, event: Dict[str, Any]) -> None:
        """
        Handle error events.

        Args:
            event: The error event.
        """
        data = event.get("data", {})
        message = data.get("message", "Unknown error")
        code = data.get("code")
        metadata = event.get("metadata", {})

        run_id = self._active_run.get("id") if self._active_run else None
        session_id = self._active_run.get("thread_id") if self._active_run else None

        self._client.track_error_event(
            error={
                "name": "",
                "message": message,
                "code": code,
            },
            run_id=run_id,
            session_id=session_id,
            context={"metadata": metadata},
        )

    def process_invoke_result(
        self,
        input: Any,
        result: Any,
        run_id: Optional[str],
        session_id: Optional[str],
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Process messages from invoke/ainvoke result for tracking.

        Unlike astream_events which gets timing data, invoke results only
        contain the final state. We extract what we can from response_metadata.

        Args:
            input: The input passed to invoke/ainvoke.
            result: The result dict from invoke/ainvoke (contains 'messages' key).
            run_id: The run identifier.
            session_id: The session/thread identifier.
            context: Optional context dict with metadata, tags, and other fields.
        """
        if not isinstance(result, dict):
            return

        # Use provided context or empty dict
        context = context or {}

        self.handle_input_event(input, run_id, session_id)

        messages = result.get("messages", [])

        for msg in messages:
            msg_type = type(msg).__name__

            if "AIMessage" in msg_type:
                response_metadata = getattr(msg, "response_metadata", {}) or {}
                tool_calls = getattr(msg, "tool_calls", []) or []
                content = getattr(msg, "content", "")

                # 1. Track LLM call if we have token usage
                token_usage = response_metadata.get("token_usage")
                if token_usage:
                    model = response_metadata.get("model_name", "unknown")
                    provider = response_metadata.get("model_provider", "")
                    finish_reason = response_metadata.get("finish_reason", "stop")

                    self._client.track_llm_call_event(
                        model=model,
                        provider=provider,
                        input_tokens=token_usage.get("prompt_tokens", 0),
                        output_tokens=token_usage.get("completion_tokens", 0),
                        latency_ms=0,  # Not available from invoke result
                        finish_reason=finish_reason,
                        is_streaming=False,
                        first_token_latency_ms=None,
                        session_id=session_id,
                        run_id=run_id,
                        context=context,
                    )

                # 2. Track tool calls (started)
                for tc in tool_calls:
                    tool_call_id = tc.get("id") if isinstance(tc, dict) else getattr(tc, "id", None)
                    tool_name = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", None)
                    tool_args = tc.get("args") if isinstance(tc, dict) else getattr(tc, "args", None)

                    if tool_call_id and tool_name:
                        # Track as started
                        self._client.track_tool_event(
                            tool_call_id=tool_call_id,
                            tool_name=tool_name,
                            tool_status="started",
                            args=dump_json_safe(tool_args) if tool_args else None,
                            run_id=run_id,
                            session_id=session_id,
                            context=context,
                        )
                        # Store for matching with ToolMessage
                        self._pending_tool_calls[tool_call_id] = CurrentToolCall(
                            tool_call_id=tool_call_id,
                            tool_name=tool_name,
                            status="started",
                            args=dump_json_safe(tool_args) if tool_args else None,
                        )

                # 3. Track assistant message if has content
                if content:
                    resolved_content = resolve_message_content(content)
                    if resolved_content:
                        self._client.track_message_event(
                            role="assistant",
                            content=resolved_content,
                            run_id=run_id,
                            session_id=session_id,
                            context=context,
                        )

            elif "ToolMessage" in msg_type:
                # Track tool completion
                tool_call_id = getattr(msg, "tool_call_id", None)
                content = getattr(msg, "content", None)

                if tool_call_id:
                    pending = self._pending_tool_calls.get(tool_call_id)
                    tool_name = pending.get("tool_name") if pending else getattr(msg, "name", None)

                    self._client.track_tool_event(
                        tool_call_id=tool_call_id,
                        tool_name=tool_name,
                        tool_status="completed",
                        result=dump_json_safe(content) if content else None,
                        run_id=run_id,
                        session_id=session_id,
                        context=context,
                    )

                    if tool_call_id in self._pending_tool_calls:
                        del self._pending_tool_calls[tool_call_id]

        class StateWrapper:
            def __init__(self, values):
                self.values = values

        self._get_state_snapshot(StateWrapper(result))
        self._client.track_state_snapshot_event(
            snapshot=make_json_safe(self._current_state),
            role="assistant",
            run_id=run_id,
            session_id=session_id,
            context=context,
        )
