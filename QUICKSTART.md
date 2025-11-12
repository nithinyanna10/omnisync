# OmniSync Quick Start Guide

Get OmniSync running in 5 minutes!

## Prerequisites Check

```bash
# Check Docker
docker --version
docker-compose --version

# Check Python
python3 --version  # Should be 3.8+

# Check Node.js (for frontend)
node --version  # Should be 18+

# Check Ollama (optional, for LLM testing)
ollama --version
```

## Step 1: Start Infrastructure

```bash
# Clone or navigate to omnisync directory
cd omnisync

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f hub-backend
```

Wait for services to be healthy (about 30 seconds).

## Step 2: Install Python SDK

```bash
cd sdk/python

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

## Step 3: Start Ollama (Optional)

If you want to use local LLM for agent reasoning:

```bash
# Pull a model (adjust to your preference)
ollama pull gpt-oss:120b-cloud

# Or use your 120B model
ollama pull llama3:70b
# or
ollama pull mistral:120b
```

Verify Ollama is running:
```bash
curl http://localhost:11434/api/tags
```

## Step 4: Run Your First Test

```bash
# From the omnisync root directory
cd examples

# Simple two-agent test (no Ollama needed)
python simple_agent_test.py
```

You should see:
```
Agents started!
Agent A ID: omnisync_agenta
Agent B ID: omnisync_agentb
📤 Agent B sending query to Agent A...
✅ Test completed!
```

## Step 5: View in Hub UI

Open your browser:
- **Hub UI**: http://localhost:3001
- **API Docs**: http://localhost:8080/docs

You should see:
- Agent network graph
- Message timeline
- Statistics panel

## Step 6: Run Multi-Agent Demo

```bash
# Make sure Ollama is running with your model
ollama list

# Run the multi-agent demo
python ollama_multi_agent.py
```

This will:
1. Start Planner, Executor, and Evaluator agents
2. Create a plan
3. Execute tasks
4. Evaluate results

Watch the conversation in the Hub UI!

## Troubleshooting

### Services won't start
```bash
# Check if ports are in use
lsof -i :8080  # Backend
lsof -i :3001  # Frontend
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis

# Restart services
docker-compose down
docker-compose up -d
```

### Python import errors
```bash
# Make sure you're in the right directory
cd sdk/python
pip install -e .

# Check Python path
python3 -c "import omnisync; print(omnisync.__version__)"
```

### Ollama connection errors
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Update model name in examples
# Using gpt-oss:120b-cloud model
```

### Database connection errors
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d
```

## Next Steps

1. **Explore Examples**: Check out `examples/` directory
2. **Read Protocol Spec**: See `spec/omnisync_protocol_v0.1.md`
3. **Build Your Agent**: Use the SDK to create custom agents
4. **Integrate Frameworks**: Use adapters for LangChain, AutoGen, etc.

## Common Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Restart a service
docker-compose restart hub-backend

# Access PostgreSQL
docker-compose exec postgres psql -U postgres -d omnisync

# Access Redis CLI
docker-compose exec redis redis-cli
```

## Need Help?

- Check the main [README.md](README.md)
- Review protocol specification in `spec/`
- Look at example code in `examples/`
- Open an issue on GitHub

Happy agent building! 🚀

