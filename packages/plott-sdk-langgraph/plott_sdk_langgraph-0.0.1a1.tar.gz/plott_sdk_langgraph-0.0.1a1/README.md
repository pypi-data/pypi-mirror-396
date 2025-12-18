# Plott SDK for LangGraph

Automatic analytics tracking for LangGraph applications. Just wrap your graph and analytics are collected transparently.

## Installation

```bash
pip install plott-sdk-langgraph
```

## Quick Start

```python
from langgraph.graph import StateGraph
from langchain_core.messages import HumanMessage
from plott_langgraph import plott_tracked_graph

# Create and compile your graph
graph = workflow.compile(checkpointer=memory)

# Wrap with Plott - that's it!
tracked_graph = plott_tracked_graph(graph, {
    "api_key": "cpk_...",  # or set PLOTT_API_KEY env var
    "environment": "development",
})

# Use exactly like the original graph - analytics are automatic
async for event in tracked_graph.astream_events(
    {"messages": [HumanMessage(content="Hello!")]},
    config={"configurable": {"thread_id": "123", "run_id": "run-456"}},
):
    # Your normal event handling
    if event["event"] == "on_chat_model_stream":
        print(event["data"]["chunk"].content, end="", flush=True)
```

## What Gets Tracked

The SDK automatically tracks:

| Event | Description |
|-------|-------------|
| **Messages** | User input and assistant responses |
| **Tool Calls** | Tool executions with arguments and results |
| **State Snapshots** | State changes as the graph executes |
| **Run Lifecycle** | Start and end of each graph run |
| **Errors** | Any errors that occur during execution |

## Configuration

```python
tracked_graph = plott_tracked_graph(graph, {
    "api_key": "cpk_...",           # Required (or PLOTT_API_KEY env var)
    "environment": "production",     # production, staging, development, test
    "retry_attempts": 3,             # Number of retry attempts on failure
    "retry_delay": 1.0,              # Seconds between retries
    "debug": False,                  # Enable debug logging
})
```

## Environment Variables

- `PLOTT_API_KEY` - API key (if not provided in config)

## Tracked Methods

The following methods have analytics tracking:

- `astream_events()` - Full event streaming with detailed tracking
- `astream()` - State streaming with lifecycle tracking
- `invoke()` - Synchronous invocation with lifecycle tracking
- `ainvoke()` - Async invocation with lifecycle tracking

## License

Apache 2.0
