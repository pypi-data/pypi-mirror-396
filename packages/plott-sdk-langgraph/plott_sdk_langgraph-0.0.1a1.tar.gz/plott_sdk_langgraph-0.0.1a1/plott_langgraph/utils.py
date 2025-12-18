"""Utility functions for Plott LangGraph SDK."""

import json
import re
from enum import Enum
from typing import Any, Dict, Optional, List
from dataclasses import is_dataclass, asdict
from datetime import date, datetime

from .types import LangGraphReasoning


# Keys to exclude from state snapshots by default (matches TS getStateSnapshot behavior)
DEFAULT_EXCLUDED_STATE_KEYS = ["messages"]


def filter_state_snapshot(
    state: Dict[str, Any],
    exclude_keys: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Filter state to exclude messages and other specified keys.

    This matches the TypeScript SDK's getStateSnapshot() behavior where
    certain keys (like 'messages') are filtered out of state snapshots.

    Args:
        state: The state dictionary to filter.
        exclude_keys: Optional list of keys to exclude. Defaults to DEFAULT_EXCLUDED_STATE_KEYS.

    Returns:
        A filtered copy of the state dictionary.
    """
    if not state:
        return {}
    exclude = exclude_keys if exclude_keys is not None else DEFAULT_EXCLUDED_STATE_KEYS
    return {k: v for k, v in state.items() if k not in exclude}


def resolve_message_content(content: Any) -> Optional[str]:
    """
    Extract text content from various message content formats.

    Handles:
    - Plain strings
    - Lists with text blocks (multimodal content)
    - LangChain message chunk content (AIMessageChunk, etc.)
    - None values

    Args:
        content: The message content to resolve.

    Returns:
        The extracted text content, or None if no text found.
    """
    if content is None:
        return None

    # Handle empty string - this is valid content for streaming
    if isinstance(content, str):
        return content if content else None

    # Handle list content (multimodal format from OpenAI/Anthropic)
    if isinstance(content, list):
        if not content:
            return None
        # Collect all text parts
        text_parts = []
        for item in content:
            if isinstance(item, str):
                text_parts.append(item)
            elif isinstance(item, dict):
                if item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
                elif "text" in item:
                    text_parts.append(item.get("text", ""))
        return "".join(text_parts) if text_parts else None

    # Handle objects that might have a text representation
    # This catches cases where content is an unexpected type
    try:
        str_content = str(content)
        # Don't return object repr strings like "<AIMessageChunk ...>"
        if str_content and not str_content.startswith("<"):
            return str_content
    except Exception:
        pass

    return None


def resolve_reasoning_content(chunk: Any) -> Optional[LangGraphReasoning]:
    """
    Extract reasoning/thinking content from LLM response chunks.

    Handles both Anthropic and OpenAI reasoning formats.

    Args:
        chunk: The LLM response chunk.

    Returns:
        LangGraphReasoning dict if reasoning found, None otherwise.
    """
    content = getattr(chunk, "content", None)
    if not content:
        return None

    # Anthropic reasoning response format
    if isinstance(content, list) and content and content[0]:
        thinking = content[0].get("thinking") if isinstance(content[0], dict) else None
        if thinking:
            return LangGraphReasoning(
                text=thinking,
                type="text",
                index=content[0].get("index", 0)
            )

    # OpenAI reasoning response format
    if hasattr(chunk, "additional_kwargs"):
        reasoning = chunk.additional_kwargs.get("reasoning", {})
        summary = reasoning.get("summary", [])
        if summary:
            data = summary[0]
            if data and data.get("text"):
                return LangGraphReasoning(
                    type="text",
                    text=data["text"],
                    index=data.get("index", 0)
                )

    return None


def json_safe_stringify(obj: Any) -> Any:
    """
    Convert an object to a JSON-serializable form.

    Handles dataclasses, pydantic models, and other common types.

    Args:
        obj: The object to convert.

    Returns:
        A JSON-serializable representation of the object.
    """
    if is_dataclass(obj):
        return asdict(obj)
    if hasattr(obj, "model_dump"):  # pydantic v2
        return obj.model_dump()
    if hasattr(obj, "dict"):  # pydantic v1
        return obj.dict()
    if hasattr(obj, "__dict__"):  # plain objects
        return vars(obj)
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return str(obj)


def make_json_safe(value: Any, _seen: Optional[set] = None) -> Any:
    """
    Recursively convert a value to a JSON-serializable form.

    Handles cycles, enums, dataclasses, pydantic models, and other types.

    Args:
        value: The value to convert.
        _seen: Set of seen object IDs for cycle detection.

    Returns:
        A JSON-serializable version of the value.
    """
    if _seen is None:
        _seen = set()

    obj_id = id(value)
    if obj_id in _seen:
        return "<recursive>"

    # 1. Primitives
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value

    # 2. Enum - use underlying value
    if isinstance(value, Enum):
        return make_json_safe(value.value, _seen)

    # 3. Dicts
    if isinstance(value, dict):
        _seen.add(obj_id)
        return {
            make_json_safe(k, _seen): make_json_safe(v, _seen)
            for k, v in value.items()
        }

    # 4. Iterable containers
    if isinstance(value, (list, tuple, set, frozenset)):
        _seen.add(obj_id)
        return [make_json_safe(v, _seen) for v in value]

    # 5. Dataclasses
    if is_dataclass(value):
        _seen.add(obj_id)
        return make_json_safe(asdict(value), _seen)

    # 6. Pydantic v2 models
    if hasattr(value, "model_dump") and callable(getattr(value, "model_dump")):
        _seen.add(obj_id)
        try:
            return make_json_safe(value.model_dump(), _seen)
        except Exception:
            pass

    # 7. Pydantic v1 / other libs with .dict()
    if hasattr(value, "dict") and callable(getattr(value, "dict")):
        _seen.add(obj_id)
        try:
            return make_json_safe(value.dict(), _seen)
        except Exception:
            pass

    # 8. Generic "to_dict" pattern
    if hasattr(value, "to_dict") and callable(getattr(value, "to_dict")):
        _seen.add(obj_id)
        try:
            return make_json_safe(value.to_dict(), _seen)
        except Exception:
            pass

    # 9. Generic Python objects with __dict__
    if hasattr(value, "__dict__"):
        _seen.add(obj_id)
        try:
            return make_json_safe(vars(value), _seen)
        except Exception:
            pass

    # 10. Last resort
    return repr(value)


def dump_json_safe(value: Any) -> str:
    """
    Safely dump a value to a JSON string.

    Args:
        value: The value to dump.

    Returns:
        JSON string representation.
    """
    if isinstance(value, str):
        return value
    return json.dumps(value, default=json_safe_stringify)


def camel_to_snake(name: str) -> str:
    """
    Convert camelCase to snake_case.

    Args:
        name: The camelCase string.

    Returns:
        The snake_case string.
    """
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


def extract_last_user_message(input_data: Dict[str, Any]) -> Optional[str]:
    """
    Extract the content of the last user message from input.

    Args:
        input_data: The input dictionary, typically containing a 'messages' list.

    Returns:
        The content of the last user message, or None if not found.
    """
    messages = input_data.get("messages", [])
    if not messages:
        return None

    last_message = messages[-1]

    # Handle different message formats
    if hasattr(last_message, "content"):
        return resolve_message_content(last_message.content)
    elif isinstance(last_message, dict):
        return resolve_message_content(last_message.get("content"))

    return None
