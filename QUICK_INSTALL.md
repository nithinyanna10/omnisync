# Quick Install & Run Guide

## Option 1: Automated Script (Easiest)

```bash
# From the omnisync root directory
./INSTALL_AND_RUN.sh
```

## Option 2: Manual Installation

### Step 1: Install Python SDK

```bash
# Navigate to SDK directory
cd sdk/python

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

### Step 2: Verify Installation

```bash
# Test import
python3 -c "import omnisync; print(omnisync.__version__)"
```

### Step 3: Run Simple Test

```bash
# Navigate to examples
cd ../../examples

# Run simple agent test
python3 simple_agent_test.py
```

## Option 3: One-Line Install (if you're already in omnisync directory)

```bash
cd sdk/python && python3 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt && pip install -e . && cd ../../examples && python3 simple_agent_test.py
```

## Expected Output

When running `simple_agent_test.py`, you should see:

```
Agents started!
Agent A ID: omnisync_agenta
Agent B ID: omnisync_agentb
📤 Agent B sending query to Agent A...
Query message ID: <uuid>
📤 Agent A sending notification to Agent B...
Notification message ID: <uuid>
✅ Test completed!
```

## Troubleshooting

### Import Error?
```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Reinstall
pip install -e .
```

### Connection Error?
```bash
# Make sure Docker containers are running
docker-compose ps

# Check backend is up
curl http://localhost:8080/
```

### Port Already in Use?
```bash
# Check what's using the port
lsof -i :8080

# Restart containers
docker-compose restart
```

