# OmniSync Python SDK

Interoperability layer for AI agent frameworks using the OmniSync Protocol (OSP).

## Installation

```bash
pip install -e .
```

## Quick Start

```python
from omnisync import Agent, IntentType

# Create an agent
agent = Agent(
    name="MyAgent",
    framework="OmniSync",
    hub_url="http://localhost:8080"
)

# Register intent handler
@agent.on("query")
async def handle_query(msg):
    return {"answer": "Response here"}

# Start agent
await agent.start()

# Send a message
await agent.send(
    IntentType.QUERY,
    "target_agent_id",
    {"query": "Hello!"}
)
```

## Features

- Full OSP v0.2 support
- Session and trace tracking
- ACK intent for acknowledgments
- Enhanced metadata (CPU, memory, latency)
- Trace visualization utilities
- Dataset export for benchmarking
- Cross-framework adapters

## Documentation

See the main [OmniSync repository](https://github.com/nithinyanna10/omnisync) for complete documentation.

