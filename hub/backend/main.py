"""
OmniSync Hub Backend - FastAPI server for message routing and visualization
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, Column, String, JSON, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
import redis
import os
from dotenv import load_dotenv

load_dotenv()

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/omnisync")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis connection
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# Database models
class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True)
    type = Column(String, nullable=False)
    version = Column(String, nullable=False)
    intent = Column(String, nullable=False)
    from_agent = Column(String, nullable=False)
    to_agent = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    message_metadata = Column("metadata", JSON)  # Use different Python name, same DB column
    content = Column(JSON)
    context = Column(JSON)
    attachments = Column(JSON)
    response_to = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Agent(Base):
    __tablename__ = "agents"
    
    agent_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    framework = Column(String, nullable=False)
    capabilities = Column(JSON)
    model = Column(String)
    registered_at = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)


# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(title="OmniSync Hub", version="0.1.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    return {"message": "OmniSync Hub API", "version": "0.1.0"}


@app.post("/api/messages")
async def create_message(message: dict, db: Session = Depends(get_db)):
    """Receive and route a message"""
    try:
        # Store message in database
        msg = Message(
            id=message.get("id"),
            type=message.get("type", "intent_message"),
            version=message.get("version", "0.1"),
            intent=message.get("intent"),
            from_agent=message.get("from"),
            to_agent=message.get("to"),
            timestamp=datetime.fromisoformat(message.get("timestamp", datetime.utcnow().isoformat()).replace("Z", "+00:00")),
            message_metadata=message.get("metadata", {}),
            content=message.get("content", {}),
            context=message.get("context"),
            attachments=message.get("attachments", []),
            response_to=message.get("response_to"),
        )
        db.add(msg)
        db.commit()
        
        # Store in Redis for real-time access
        redis_client.lpush(f"messages:{message.get('to')}", json.dumps(message))
        redis_client.lpush("messages:all", json.dumps(message))
        
        # Broadcast to WebSocket clients
        await manager.broadcast({"type": "new_message", "message": message})
        
        return {"status": "success", "message_id": message.get("id")}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/messages/{agent_id}")
async def get_messages(agent_id: str, limit: int = 100, db: Session = Depends(get_db)):
    """Get messages for an agent"""
    try:
        # Try Redis first (unprocessed messages)
        messages_data = redis_client.lrange(f"messages:{agent_id}", 0, limit - 1)
        if messages_data:
            messages = [json.loads(msg) for msg in messages_data]
            # Clear after reading to prevent duplicate processing
            redis_client.delete(f"messages:{agent_id}")
            return {"messages": messages}
        
        # Fallback to database - get unprocessed messages
        # Use a flag or timestamp to track processed messages
        messages = db.query(Message).filter(
            ((Message.to_agent == agent_id) | (Message.to_agent == "broadcast"))
            & (Message.timestamp > datetime.utcnow() - timedelta(minutes=5))  # Only recent messages
        ).order_by(Message.timestamp.desc()).limit(limit).all()
        
        result = []
        processed_ids = set()
        for msg in messages:
            # Avoid duplicates
            if msg.id in processed_ids:
                continue
            processed_ids.add(msg.id)
            result.append({
                "id": msg.id,
                "type": msg.type,
                "version": msg.version,
                "intent": msg.intent,
                "from": msg.from_agent,
                "to": msg.to_agent,
                "timestamp": msg.timestamp.isoformat() + "Z",
                "metadata": msg.message_metadata,
                "content": msg.content,
                "context": msg.context,
                "attachments": msg.attachments,
                "response_to": msg.response_to,
            })
        
        return {"messages": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/messages")
async def get_all_messages(limit: int = 1000, db: Session = Depends(get_db)):
    """Get all messages (for visualization)"""
    try:
        messages = db.query(Message).order_by(Message.timestamp.desc()).limit(limit).all()
        result = []
        for msg in messages:
            result.append({
                "id": msg.id,
                "type": msg.type,
                "version": msg.version,
                "intent": msg.intent,
                "from": msg.from_agent,
                "to": msg.to_agent,
                "timestamp": msg.timestamp.isoformat() + "Z",
                "metadata": msg.message_metadata,
                "content": msg.content,
                "context": msg.context,
                "attachments": msg.attachments,
                "response_to": msg.response_to,
            })
        return {"messages": result, "count": len(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/conversations/{conversation_id}")
async def get_conversation_thread(conversation_id: str, db: Session = Depends(get_db)):
    """Get conversation thread by trace_id or session_id"""
    try:
        # Find messages by trace_id or session_id in metadata
        messages = db.query(Message).filter(
            (Message.message_metadata.contains({"trace_id": conversation_id})) |
            (Message.message_metadata.contains({"session_id": conversation_id}))
        ).order_by(Message.timestamp.asc()).all()
        
        result = []
        for msg in messages:
            result.append({
                "id": msg.id,
                "intent": msg.intent,
                "from": msg.from_agent,
                "to": msg.to_agent,
                "timestamp": msg.timestamp.isoformat() + "Z",
                "content": msg.content,
                "response_to": msg.response_to,
                "metadata": msg.message_metadata,
            })
        
        return {"conversation_id": conversation_id, "messages": result, "count": len(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/conversations")
async def get_conversation_graph(db: Session = Depends(get_db)):
    """Get conversation graph structure for visualization"""
    try:
        # Get recent messages with response_to relationships
        messages = db.query(Message).filter(
            Message.timestamp > datetime.utcnow() - timedelta(hours=1)
        ).order_by(Message.timestamp.desc()).limit(500).all()
        
        # Build graph structure
        nodes = {}  # agent_id -> node info
        edges = []  # message relationships
        
        for msg in messages:
            # Add nodes
            if msg.from_agent not in nodes:
                nodes[msg.from_agent] = {
                    "id": msg.from_agent,
                    "label": msg.from_agent,
                    "framework": msg.message_metadata.get("framework", "Unknown") if msg.message_metadata else "Unknown",
                }
            if msg.to_agent not in nodes and msg.to_agent != "broadcast":
                nodes[msg.to_agent] = {
                    "id": msg.to_agent,
                    "label": msg.to_agent,
                    "framework": "Unknown",
                }
            
            # Add edges
            if msg.to_agent != "broadcast":
                edges.append({
                    "from": msg.from_agent,
                    "to": msg.to_agent,
                    "intent": msg.intent,
                    "message_id": msg.id,
                    "response_to": msg.response_to,
                    "timestamp": msg.timestamp.isoformat() + "Z",
                })
        
        return {
            "nodes": list(nodes.values()),
            "edges": edges,
            "message_count": len(messages),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agents/register")
async def register_agent(agent_info: dict, db: Session = Depends(get_db)):
    """Register an agent"""
    try:
        # Validate required fields
        if not agent_info.get("agent_id"):
            raise HTTPException(status_code=400, detail="agent_id is required")
        if not agent_info.get("name"):
            raise HTTPException(status_code=400, detail="name is required")
        if not agent_info.get("framework"):
            raise HTTPException(status_code=400, detail="framework is required")
        
        agent = Agent(
            agent_id=agent_info.get("agent_id"),
            name=agent_info.get("name"),
            framework=agent_info.get("framework"),
            capabilities=agent_info.get("capabilities", []),
            model=agent_info.get("model"),
        )
        db.merge(agent)  # Use merge to handle updates
        db.commit()
        
        # Store in Redis
        redis_client.sadd("agents:active", agent_info.get("agent_id"))
        # Convert agent_info to string dict for Redis
        redis_mapping = {k: str(v) if not isinstance(v, (str, int, float)) else v 
                        for k, v in agent_info.items()}
        redis_client.hset(f"agent:{agent_info.get('agent_id')}", mapping=redis_mapping)
        
        await manager.broadcast({"type": "agent_registered", "agent": agent_info})
        
        return {"status": "success", "agent_id": agent_info.get("agent_id")}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=400, detail=error_detail)


@app.get("/api/agents")
async def get_agents(db: Session = Depends(get_db)):
    """Get all registered agents"""
    try:
        agents = db.query(Agent).all()
        result = []
        for agent in agents:
            result.append({
                "agent_id": agent.agent_id,
                "name": agent.name,
                "framework": agent.framework,
                "capabilities": agent.capabilities,
                "model": agent.model,
                "registered_at": agent.registered_at.isoformat() + "Z",
                "last_seen": agent.last_seen.isoformat() + "Z",
            })
        return {"agents": result, "count": len(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get hub statistics"""
    try:
        total_messages = db.query(Message).count()
        total_agents = db.query(Agent).count()
        
        # Message counts by intent
        intent_counts = {}
        for intent in ["query", "plan", "execute", "reflect", "evaluate", "notify"]:
            count = db.query(Message).filter(Message.intent == intent).count()
            intent_counts[intent] = count
        
        return {
            "total_messages": total_messages,
            "total_agents": total_agents,
            "intent_counts": intent_counts,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo or handle client messages
            await websocket.send_json({"type": "echo", "data": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

