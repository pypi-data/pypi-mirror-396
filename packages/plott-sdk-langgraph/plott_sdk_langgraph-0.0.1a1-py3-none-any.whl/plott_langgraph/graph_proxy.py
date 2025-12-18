"""Graph proxy for wrapping LangGraph graphs with Plott analytics tracking."""

import os
from typing import Any, Dict, Optional, AsyncIterator, TypeVar, Union

from plott_core import PlottAnalytics, PlottConfig

from .event_translator import EventTracker

# Generic type for the graph
T = TypeVar("T")


def _create_tracked_graph_class(original_graph: Any, client: PlottAnalytics, base_context: Dict[str, Any]) -> type:
    """
    Dynamically create a TrackedGraph class that inherits from the original graph's class.

    This ensures isinstance() checks pass (e.g., isinstance(proxy, CompiledStateGraph)).
    Similar to JavaScript's Proxy pattern but using Python's dynamic class creation.
    """
    original_class = type(original_graph)

    class TrackedGraphProxy(original_class):
        """
        Dynamic proxy class that inherits from the original graph's class.

        This passes isinstance() checks while intercepting tracked methods.
        """

        # Prevent calling parent __init__
        def __new__(cls):
            # Create instance without calling __init__
            instance = object.__new__(cls)
            return instance

        def __init__(self):
            # Store tracking references (don't call parent __init__)
            object.__setattr__(self, '_tracking_original', original_graph)
            object.__setattr__(self, '_tracking_client', client)
            object.__setattr__(self, '_tracking_base_context', base_context)

        def __getattribute__(self, name: str) -> Any:
            # Access our tracking attributes directly
            if name in ('_tracking_original', '_tracking_client', '_tracking_base_context'):
                return object.__getattribute__(self, name)

            # For tracked methods, return our wrapped versions
            if name == 'astream_events':
                return object.__getattribute__(self, '_tracked_astream_events')
            if name == 'astream':
                return object.__getattribute__(self, '_tracked_astream')
            if name == 'invoke':
                return object.__getattribute__(self, '_tracked_invoke')
            if name == 'ainvoke':
                return object.__getattribute__(self, '_tracked_ainvoke')
            if name == 'shutdown':
                return object.__getattribute__(self, '_tracked_shutdown')

            # For our internal tracked methods, access directly
            if name.startswith('_tracked_'):
                return object.__getattribute__(self, name)

            # Everything else - proxy to original graph
            orig = object.__getattribute__(self, '_tracking_original')
            return getattr(orig, name)

        def __setattr__(self, name: str, value: Any) -> None:
            if name in ('_tracking_original', '_tracking_client'):
                object.__setattr__(self, name, value)
            else:
                orig = object.__getattribute__(self, '_tracking_original')
                setattr(orig, name, value)

        async def _tracked_astream_events(
                self,
                input: Any,
                config: Optional[Dict[str, Any]] = None,
                **kwargs: Any,
        ) -> AsyncIterator[Dict[str, Any]]:
            """Stream events with analytics tracking."""
            orig = object.__getattribute__(self, '_tracking_original')
            cli = object.__getattribute__(self, '_tracking_client')
            tracker = EventTracker(client=cli)

            configurable = (config or {}).get("configurable", {})
            run_id = configurable.get("run_id") or kwargs.get("run_id")
            thread_id = configurable.get("thread_id")

            if run_id:
                tracker.create_active_run(run_id, thread_id)

            tracker.track_run_start(run_id, thread_id)

            if isinstance(input, dict):
                tracker.handle_input_event(input, run_id, thread_id)

            try:
                if "version" not in kwargs:
                    kwargs["version"] = "v2"

                async for event in orig.astream_events(input, config, **kwargs):
                    try:
                        await tracker.handle_single_event(event, orig, config)
                    except Exception:
                        pass
                    yield event

            finally:
                tracker.track_run_end(run_id)

        async def _tracked_astream(
                self,
                input: Any,
                config: Optional[Dict[str, Any]] = None,
                **kwargs: Any,
        ) -> AsyncIterator[Any]:
            """Stream state chunks with lifecycle tracking."""
            orig = object.__getattribute__(self, '_tracking_original')
            cli = object.__getattribute__(self, '_tracking_client')
            tracker = EventTracker(client=cli)

            configurable = (config or {}).get("configurable", {})
            run_id = configurable.get("run_id") or kwargs.get("run_id")
            thread_id = configurable.get("thread_id")

            if run_id:
                tracker.create_active_run(run_id, thread_id)

            tracker.track_run_start(run_id)

            if isinstance(input, dict):
                tracker.handle_input_event(input, run_id, thread_id)

            try:
                async for chunk in orig.astream(input, config, **kwargs):
                    await tracker.handle_single_event(chunk, orig, config)
                    yield chunk
            finally:
                tracker.track_run_end(run_id)

        def _tracked_invoke(
                self,
                input: Any,
                config: Optional[Dict[str, Any]] = None,
                **kwargs: Any,
        ) -> Any:
            """Invoke synchronously with lifecycle tracking."""
            orig = object.__getattribute__(self, '_tracking_original')
            cli = object.__getattribute__(self, '_tracking_client')
            tracker = EventTracker(client=cli)

            configurable = (config or {}).get("configurable", {})
            run_id = configurable.get("run_id") or kwargs.get("run_id")
            thread_id = configurable.get("thread_id")

            if run_id:
                tracker.create_active_run(run_id, thread_id)

            tracker.track_run_start(run_id)

            if isinstance(input, dict):
                tracker.handle_input_event(input, run_id, thread_id)

            try:
                return orig.invoke(input, config, **kwargs)
            finally:
                tracker.track_run_end(run_id)

        async def _tracked_ainvoke(
                self,
                input: Any,
                config: Optional[Dict[str, Any]] = None,
                **kwargs: Any,
        ) -> Any:
            """Invoke asynchronously with lifecycle tracking."""
            orig = object.__getattribute__(self, '_tracking_original')
            cli = object.__getattribute__(self, '_tracking_client')
            base_ctx = object.__getattribute__(self, '_tracking_base_context')
            tracker = EventTracker(client=cli)

            configurable = (config or {}).get("configurable", {})
            run_id = configurable.get("run_id") or kwargs.get("run_id")
            thread_id = configurable.get("thread_id")

            # Extract metadata and tags from config (top-level, not in configurable)
            metadata = (config or {}).get("metadata", {})
            tags = (config or {}).get("tags", [])

            # Merge: base context is the default, per-invocation overrides
            context = {
                **base_ctx,  # Base context from initialization
                "metadata": {**base_ctx.get("metadata", {}), **metadata},
                "tags": list(set(base_ctx.get("tags", []) + tags)),
            }

            result = await orig.ainvoke(input, config, **kwargs)

            try:
                if run_id:
                    tracker.create_active_run(run_id, thread_id)

                tracker.track_run_start(run_id, thread_id)

                # Process result messages for tracking
                tracker.process_invoke_result(input, result, run_id, thread_id, context)
                tracker.track_run_end(run_id, thread_id)

                return result
            except Exception as e:
                print(e)
                pass
            finally:
                pass


        async def _tracked_shutdown(self) -> None:
            """Shutdown the analytics client."""
            cli = object.__getattribute__(self, '_tracking_client')
            await cli.shutdown()

    return TrackedGraphProxy


def plott_tracked_graph(
        graph: T,
        config: Optional[Union[PlottConfig, Dict[str, Any]]] = None,
) -> T:
    """
    Wrap a LangGraph graph with Plott analytics tracking.

    This is the main entry point for adding analytics to a LangGraph graph.
    The wrapped graph can be used exactly like the original - all methods
    are proxied through, and analytics are collected transparently.

    Example:
        ```python
        from langgraph.graph import StateGraph
        from plott_langgraph import plott_tracked_graph

        # Create your graph normally
        workflow = StateGraph(AgentState)
        workflow.add_node("chat", chat_node)
        graph = workflow.compile()

        # Wrap with Plott
        tracked = plott_tracked_graph(graph, {"environment": "development"})

        # Use normally - analytics are automatic
        async for event in tracked.astream_events(
            {"messages": [HumanMessage("Hello")]},
            config={"configurable": {"thread_id": "123"}}
        ):
            # Your normal handling
            pass
        ```

    Args:
        graph: The compiled LangGraph graph to wrap.
        config: Optional PlottConfig dict. If api_key is not provided,
                it will be read from the PLOTT_API_KEY environment variable.

    Returns:
        A wrapped graph that tracks analytics.

    Raises:
        ValueError: If no API key is provided and PLOTT_API_KEY is not set.
    """
    config = config or {}

    # Get API key from config or environment
    api_key = config.get("api_key") or os.environ.get("PLOTT_API_KEY")
    if not api_key:
        raise ValueError(
            "[Plott SDK] PLOTT_API_KEY is not set. "
            "Provide it in config or set the PLOTT_API_KEY environment variable."
        )

    # Extract base context from config (will be merged with per-invocation context)
    base_context = config.get("context", {})

    # Create the analytics client
    client_config: PlottConfig = {
        **config,
        "api_key": api_key,
    }
    client = PlottAnalytics(client_config)

    # Create dynamic proxy class that inherits from the graph's class
    # This ensures isinstance() checks pass for LangGraph loaders
    TrackedGraphProxy = _create_tracked_graph_class(graph, client, base_context)
    return TrackedGraphProxy()  # type: ignore

