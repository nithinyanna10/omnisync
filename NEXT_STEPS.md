# Next Steps - OmniSync Setup

## ✅ Current Status
- Docker containers are running
- Backend API: http://localhost:8080
- Frontend UI: http://localhost:3001 (may still be building)
- PostgreSQL: localhost:5433
- Redis: localhost:6380

## 🚀 Step-by-Step Guide

### Step 1: Verify Services Are Running

```bash
# Check all containers
docker-compose ps

# Check backend logs
docker-compose logs hub-backend --tail 20

# Check if backend is responding
curl http://localhost:8080/
```

### Step 2: Install Python SDK

```bash
# Navigate to SDK directory
cd sdk/python

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

### Step 3: Test Basic Agent Communication

```bash
# From the omnisync root directory
cd examples

# Run simple two-agent test (no LLM needed)
python simple_agent_test.py
```

**Expected Output:**
```
Agents started!
Agent A ID: omnisync_agenta
Agent B ID: omnisync_agentb
📤 Agent B sending query to Agent A...
✅ Test completed!
```

### Step 4: View Hub UI

Open your browser:
- **Hub UI**: http://localhost:3001
- **API Docs**: http://localhost:8080/docs

You should see:
- Agent network graph
- Message timeline
- Statistics panel

### Step 5: Set Up Ollama (for LLM-powered agents)

```bash
# Check if Ollama is installed
ollama --version

# Pull the gpt-oss:120b-cloud model
ollama pull gpt-oss:120b-cloud

# Verify model is available
ollama list
```

### Step 6: Run Multi-Agent Demo with LLM

```bash
# Make sure you're in the examples directory
cd examples

# Run the multi-agent demo
python ollama_multi_agent.py
```

This will:
1. Start Planner, Executor, and Evaluator agents
2. Create a plan using the LLM
3. Execute tasks
4. Evaluate results

**Watch the conversation in the Hub UI at http://localhost:3001!**

### Step 7: Try Other Examples

```bash
# LangChain + AutoGen demo
python langchain_autogen_demo.py

# CrewAI + LlamaIndex demo
python crewai_llamaindex_demo.py
```

## 🔍 Troubleshooting

### Backend not responding?
```bash
# Check logs
docker-compose logs hub-backend

# Restart backend
docker-compose restart hub-backend
```

### Frontend not loading?
```bash
# Check if frontend container is running
docker-compose ps hub-frontend

# Check frontend logs
docker-compose logs hub-frontend

# Rebuild frontend if needed
docker-compose build hub-frontend
docker-compose up -d hub-frontend
```

### Python import errors?
```bash
# Make sure you installed the SDK
cd sdk/python
pip install -e .

# Verify installation
python3 -c "import omnisync; print(omnisync.__version__)"
```

### Ollama connection errors?
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Make sure model is pulled
ollama list | grep gpt-oss
```

## 📚 Additional Resources

- **Full Documentation**: See README.md
- **Quick Start**: See QUICKSTART.md
- **Protocol Spec**: See spec/omnisync_protocol_v0.1.md
- **API Documentation**: http://localhost:8080/docs

## 🎯 Quick Commands Reference

```bash
# View all running containers
docker-compose ps

# View logs
docker-compose logs -f

# Stop all services
docker-compose stop

# Start all services
docker-compose start

# Restart a specific service
docker-compose restart hub-backend

# Rebuild and restart
docker-compose up -d --build
```

## 🎉 You're Ready!

Start with Step 3 (simple agent test) to verify everything works, then move to Step 6 for the full multi-agent LLM demo!

