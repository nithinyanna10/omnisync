# How to View Messages for Testing

## Option 1: Use the View Messages Script (Easiest)

```bash
cd examples
source ../sdk/python/venv/bin/activate
python3 view_messages.py
```

### View specific things:

```bash
# View all messages
python3 view_messages.py --messages

# View registered agents
python3 view_messages.py --agents

# View statistics
python3 view_messages.py --stats

# View everything
python3 view_messages.py --all

# Limit number of messages
python3 view_messages.py --messages --limit 20
```

## Option 2: Use the API Directly

### View all messages:
```bash
curl http://localhost:8080/api/messages | python3 -m json.tool
```

### View registered agents:
```bash
curl http://localhost:8080/api/agents | python3 -m json.tool
```

### View statistics:
```bash
curl http://localhost:8080/api/stats | python3 -m json.tool
```

### View messages for a specific agent:
```bash
curl http://localhost:8080/api/messages/omnisync_AgentA | python3 -m json.tool
```

## Option 3: Use the API Documentation

Open in browser:
**http://localhost:8080/docs**

This gives you an interactive API explorer where you can:
- View all endpoints
- Test API calls
- See request/response formats

## Option 4: Fix Frontend UI (localhost:3001)

The frontend is currently not working. To fix it:

```bash
# Rebuild frontend
docker-compose build hub-frontend

# Start frontend
docker-compose up -d hub-frontend

# Check logs
docker-compose logs hub-frontend
```

Or run frontend locally (without Docker):

```bash
cd hub/frontend
npm install
npm run dev
```

Then open: http://localhost:3001

## Quick Test Commands

```bash
# 1. Start your agents
cd examples
source ../sdk/python/venv/bin/activate
python3 simple_agent_test.py

# 2. In another terminal, view messages
cd examples
python3 view_messages.py --all
```

## Troubleshooting

### Backend not responding?
```bash
# Check if backend is running
curl http://localhost:8080/

# Check backend logs
docker-compose logs hub-backend --tail 20
```

### No messages showing?
- Make sure agents are running and sending messages
- Check that messages are being sent to the hub
- Verify Redis is working: `docker-compose logs redis`

