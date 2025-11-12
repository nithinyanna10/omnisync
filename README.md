# OmniSync Protocol (OSP)

**The Open Protocol for AI-to-AI Communication**

OmniSync enables interoperability between different AI agent frameworks (LangChain, AutoGen, CrewAI, LlamaIndex, etc.) through a standardized JSON-based communication protocol.

![OmniSync Architecture](https://via.placeholder.com/800x400?text=OmniSync+Architecture)

## 🎯 Core Vision

**Problem**: Agents today live in silos. A LangChain agent can't directly talk to an AutoGen swarm or a CrewAI coordinator — their internal schemas, message formats, and memory differ.

**Solution**: OmniSync provides a standard communication layer — like OpenAPI or gRPC — that lets any agent framework interoperate using a shared JSON schema and intent model.

## 🏗️ Architecture

### Protocol Layer

The **OmniSync Protocol (OSP)** defines a JSON-based message specification with:

- **Intent**: Goal or action request (query, plan, execute, reflect, evaluate, notify)
- **Metadata**: Agent ID, framework, capabilities
- **Context**: Relevant memory or tools
- **Content**: Natural-language message or structured data
- **Attachments**: Embeddings, files, code snippets, or observations

### SDK Layer

- **Python SDK**: Integrates with LangChain, LlamaIndex, AutoGen, CrewAI
- **JavaScript SDK**: Integrates with web-based orchestrators

### OmniSync Hub

A visualization and control center that:
- Visualizes agent conversations as a graph
- Provides real-time metrics (latency, token usage, response quality)
- Logs all messages for analysis
- Supports WebSocket for real-time updates

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.8+ (for Python SDK)
- Node.js 18+ (for JavaScript SDK and Hub frontend)
- Ollama (for local LLM testing) - [Install Ollama](https://ollama.ai)

### 1. Start Infrastructure with Docker

```bash
# Start PostgreSQL, Redis, and Hub services
docker-compose up -d

# Verify services are running
docker-compose ps
```

The Hub will be available at:
- **Backend API**: http://localhost:8080
- **Frontend UI**: http://localhost:3001
- **API Docs**: http://localhost:8080/docs

### 2. Install Python SDK

```bash
cd sdk/python
pip install -r requirements.txt
pip install -e .
```

### 3. Start Ollama (if using local LLM)

```bash
# Pull a model (adjust to your 120B model)
ollama pull gpt-oss:120b-cloud

# Or use your 120B model
ollama pull llama3:70b  # or mistral:120b, mixtral:8x7b, etc.
```

### 4. Run Example Agents

```bash
# Simple two-agent test
cd examples
python simple_agent_test.py

# Multi-agent conversation with Ollama
python ollama_multi_agent.py

# LangChain + AutoGen demo
python langchain_autogen_demo.py

# CrewAI + LlamaIndex demo
python crewai_llamaindex_demo.py
```

## 📖 Usage Examples

### Basic Agent Setup

```python
from omnisync import Agent, IntentType
import asyncio

# Create an agent
agent = Agent(
    name="MyAgent",
    framework="LangChain",
    hub_url="http://localhost:8080",
    model="gpt-oss:120b-cloud",
    capabilities=["query", "plan"]
)

# Register intent handlers
@agent.on("query")
async def handle_query(msg):
    query = msg.content.get("query", "")
    return {"answer": f"Response to: {query}"}

# Start the agent
async def main():
    await agent.start()
    # Agent is now listening for messages
    
    # Send a message
    await agent.send(
        IntentType.QUERY,
        "other_agent_id",
        {"query": "What is the weather?"}
    )
    
    await asyncio.sleep(10)
    await agent.stop()

asyncio.run(main())
```

### Using Ollama Integration

```python
from omnisync import Agent, IntentType
from omnisync.ollama_integration import OllamaClient, create_ollama_agent_handler

# Initialize Ollama client
ollama = OllamaClient(model="gpt-oss:120b-cloud")

# Create agent with Ollama handler
agent = Agent(name="OllamaAgent", framework="OmniSync")
handler = create_ollama_agent_handler(ollama, "You are a helpful assistant.")

@agent.on("query")
async def handle_query(msg):
    return await handler(msg, "query")

await agent.start()
```

### Multi-Agent Workflow

```python
# Planner Agent
planner = Agent(name="Planner", framework="LangChain")
@planner.on("plan")
async def create_plan(msg):
    goal = msg.content.get("goal", "")
    return {
        "goal": goal,
        "steps": [{"action": "step1"}, {"action": "step2"}]
    }

# Executor Agent
executor = Agent(name="Executor", framework="AutoGen")
@executor.on("execute")
async def execute_task(msg):
    task = msg.content.get("task", "")
    return {"status": "completed", "task": task}

# Start workflow
await planner.start()
await executor.start()

# Planner creates plan
await planner.send(
    IntentType.PLAN,
    "broadcast",
    {"goal": "Process financial data"}
)
```

## 🧪 Testing

### Protocol Validation Tests

```bash
cd sdk/python
pytest tests/test_protocol.py
```

### SDK Roundtrip Test

```bash
python examples/simple_agent_test.py
```

### End-to-End Multi-Agent Test

```bash
python examples/ollama_multi_agent.py
```

## 📁 Project Structure

```
omnisync/
├── spec/
│   └── omnisync_protocol_v0.1.md    # Protocol specification
├── sdk/
│   ├── python/                       # Python SDK
│   │   ├── omnisync/
│   │   │   ├── protocol.py          # Pydantic models
│   │   │   ├── agent.py             # Agent implementation
│   │   │   ├── hub_client.py        # Hub communication
│   │   │   ├── adapters.py          # Framework adapters
│   │   │   └── ollama_integration.py # Ollama integration
│   │   ├── setup.py
│   │   └── requirements.txt
│   └── js/                           # JavaScript SDK
│       ├── src/
│       │   ├── protocol.ts          # Zod schemas
│       │   ├── agent.ts             # Agent implementation
│       │   └── hub-client.ts        # Hub communication
│       └── package.json
├── hub/
│   ├── backend/                      # FastAPI backend
│   │   ├── main.py                  # API server
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── frontend/                     # React frontend
│       ├── app/
│       ├── components/
│       └── package.json
├── examples/
│   ├── simple_agent_test.py
│   ├── ollama_multi_agent.py
│   ├── langchain_autogen_demo.py
│   └── crewai_llamaindex_demo.py
├── docker-compose.yml                # Infrastructure setup
└── README.md
```

## 🔌 Framework Adapters

### LangChain

```python
from omnisync.adapters import LangChainAdapter
from langchain.agents import create_agent

langchain_agent = create_agent(...)
adapter = LangChainAdapter(omnisync_agent, langchain_agent)
```

### AutoGen

```python
from omnisync.adapters import AutoGenAdapter
import autogen

autogen_agent = autogen.AssistantAgent(...)
adapter = AutoGenAdapter(omnisync_agent, autogen_agent)
```

### CrewAI

```python
from omnisync.adapters import CrewAIAdapter
from crewai import Agent

crewai_agent = Agent(...)
adapter = CrewAIAdapter(omnisync_agent, crewai_agent)
```

### LlamaIndex

```python
from omnisync.adapters import LlamaIndexAdapter
from llama_index.agent import ReActAgent

llamaindex_agent = ReActAgent(...)
adapter = LlamaIndexAdapter(omnisync_agent, llamaindex_agent)
```

## 🌐 Hub API

### Endpoints

- `POST /api/messages` - Send a message
- `GET /api/messages/{agent_id}` - Get messages for an agent
- `GET /api/messages` - Get all messages (for visualization)
- `POST /api/agents/register` - Register an agent
- `GET /api/agents` - List all agents
- `GET /api/stats` - Get hub statistics
- `WS /ws` - WebSocket for real-time updates

### Example API Usage

```bash
# Register an agent
curl -X POST http://localhost:8080/api/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "test_agent",
    "name": "Test Agent",
    "framework": "OmniSync",
    "capabilities": ["query"]
  }'

# Send a message
curl -X POST http://localhost:8080/api/messages \
  -H "Content-Type: application/json" \
  -d '{
    "type": "intent_message",
    "version": "0.1",
    "id": "msg-123",
    "intent": "query",
    "from": "agent_a",
    "to": "agent_b",
    "content": {"query": "Hello!"},
    "timestamp": "2025-01-01T00:00:00Z"
  }'
```

## 🎨 Hub Visualization

The Hub frontend provides:

1. **Agent Network Graph**: Visual representation of agents and message flows (D3.js)
2. **Message Timeline**: Chronological view of all messages
3. **Statistics Panel**: Real-time metrics and counts
4. **Agent Filtering**: Filter messages by agent

Access at: http://localhost:3001

## 🔒 Security Considerations

- **Message Signatures**: Optional cryptographic signatures for message authentication
- **Agent Authentication**: Hub verifies agent identities
- **Content Validation**: SDKs validate all message schemas
- **Rate Limiting**: Hub enforces rate limits per agent (to be implemented)

## 🧠 Research & Innovation

- **Cross-framework ontology**: Minimal shared intent taxonomy (Query, Act, Reflect, Plan, Evaluate)
- **Inter-agent reasoning**: Study how LLM agents coordinate via standardized message formats
- **Verification**: Message authentication and safety validators
- **Benchmarking**: Multi-agent conversation log datasets

## 🛣️ Roadmap

### Phase 1 — Protocol Spec ✅
- [x] Define JSON schema + types
- [x] Publish OSP 0.1 draft
- [x] Build Python validator (Pydantic)

### Phase 2 — SDKs ✅
- [x] omnisync-py: adapter for LangChain, AutoGen, CrewAI, LlamaIndex
- [x] omnisync-js: adapter for browser/Node agents
- [x] Unified event bus (Redis)

### Phase 3 — Hub UI ✅
- [x] Agent Graph visualization (D3.js)
- [x] Conversation replay view
- [x] API for querying message logs

### Phase 4 — Open-Source Launch 🚧
- [ ] Publish spec.md + SDKs on GitHub
- [ ] Write blog post
- [ ] Invite collaboration from open agent projects

## 🤝 Contributing

We welcome contributions! Areas of interest:

- Additional framework adapters
- Protocol extensions
- Hub UI improvements
- Documentation
- Test coverage

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

Inspired by the need for interoperability in the AI agent ecosystem. Built with:
- FastAPI
- React + Next.js
- D3.js
- Pydantic
- Zod
- PostgreSQL
- Redis

## 📞 Contact

- GitHub Issues: [Report bugs or request features]
- Discussions: [Join the conversation]

---

**OmniSync**: Breaking down the walls between AI agent frameworks, one message at a time. 🚀

