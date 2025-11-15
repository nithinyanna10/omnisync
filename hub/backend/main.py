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


# ============================================================================
# v0.3: Enhanced API v1 endpoints
# ============================================================================

@app.get("/api/v1/logs")
async def get_logs(
    limit: int = 1000,
    offset: int = 0,
    intent: Optional[str] = None,
    from_agent: Optional[str] = None,
    to_agent: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get message logs with filtering (v0.3)"""
    try:
        query = db.query(Message)
        
        # Apply filters
        if intent:
            query = query.filter(Message.intent == intent)
        if from_agent:
            query = query.filter(Message.from_agent == from_agent)
        if to_agent:
            query = query.filter(Message.to_agent == to_agent)
        if start_time:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            query = query.filter(Message.timestamp >= start_dt)
        if end_time:
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            query = query.filter(Message.timestamp <= end_dt)
        
        # Get total count before pagination
        total = query.count()
        
        # Apply pagination
        messages = query.order_by(Message.timestamp.desc()).offset(offset).limit(limit).all()
        
        result = []
        for msg in messages:
            result.append({
                "id": msg.id,
                "timestamp": msg.timestamp.isoformat() + "Z",
                "intent": msg.intent,
                "from": msg.from_agent,
                "to": msg.to_agent,
                "content": msg.content,
                "metadata": msg.message_metadata,
                "response_to": msg.response_to,
            })
        
        return {
            "logs": result,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/sessions")
async def get_sessions(
    session_id: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get session information (v0.3)"""
    try:
        if session_id:
            # Get messages for specific session
            messages = db.query(Message).filter(
                Message.message_metadata.contains({"session_id": session_id})
            ).order_by(Message.timestamp.asc()).all()
            
            if not messages:
                raise HTTPException(status_code=404, detail="Session not found")
            
            # Extract session info from first message
            first_msg = messages[0]
            metadata = first_msg.message_metadata or {}
            
            session_info = {
                "session_id": session_id,
                "start_time": first_msg.timestamp.isoformat() + "Z",
                "end_time": messages[-1].timestamp.isoformat() + "Z",
                "message_count": len(messages),
                "agents": list(set([m.from_agent for m in messages] + [m.to_agent for m in messages if m.to_agent != "broadcast"])),
                "intents_used": list(set([m.intent for m in messages])),
                "trace_id": metadata.get("trace_id"),
            }
            
            return {"session": session_info, "messages": len(messages)}
        else:
            # Get all unique sessions
            all_messages = db.query(Message).filter(
                Message.message_metadata.isnot(None)
            ).order_by(Message.timestamp.desc()).limit(limit * 10).all()
            
            sessions_map = {}
            for msg in all_messages:
                session_id_val = (msg.message_metadata or {}).get("session_id")
                if session_id_val and session_id_val not in sessions_map:
                    sessions_map[session_id_val] = {
                        "session_id": session_id_val,
                        "start_time": msg.timestamp.isoformat() + "Z",
                        "message_count": 1,
                        "agents": [msg.from_agent, msg.to_agent] if msg.to_agent != "broadcast" else [msg.from_agent],
                    }
                elif session_id_val:
                    sessions_map[session_id_val]["message_count"] += 1
            
            sessions = list(sessions_map.values())[:limit]
            return {"sessions": sessions, "total": len(sessions)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/traces")
async def get_traces(
    trace_id: Optional[str] = None,
    session_id: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get trace information (v0.3)"""
    try:
        query = db.query(Message)
        
        if trace_id:
            query = query.filter(Message.message_metadata.contains({"trace_id": trace_id}))
        elif session_id:
            query = query.filter(Message.message_metadata.contains({"session_id": session_id}))
        else:
            # Get recent traces
            query = query.filter(Message.message_metadata.isnot(None))
        
        messages = query.order_by(Message.timestamp.asc()).limit(limit * 10).all()
        
        if not messages:
            return {"traces": [], "total": 0}
        
        # Group by trace_id
        traces_map = {}
        for msg in messages:
            metadata = msg.message_metadata or {}
            trace_id_val = metadata.get("trace_id")
            session_id_val = metadata.get("session_id")
            
            if trace_id_val:
                if trace_id_val not in traces_map:
                    traces_map[trace_id_val] = {
                        "trace_id": trace_id_val,
                        "session_id": session_id_val,
                        "start_time": msg.timestamp.isoformat() + "Z",
                        "message_count": 0,
                        "agents": set(),
                        "intents": set(),
                        "messages": []
                    }
                
                trace_info = traces_map[trace_id_val]
                trace_info["message_count"] += 1
                trace_info["agents"].add(msg.from_agent)
                if msg.to_agent != "broadcast":
                    trace_info["agents"].add(msg.to_agent)
                trace_info["intents"].add(msg.intent)
                trace_info["messages"].append({
                    "id": msg.id,
                    "timestamp": msg.timestamp.isoformat() + "Z",
                    "from": msg.from_agent,
                    "to": msg.to_agent,
                    "intent": msg.intent,
                    "response_to": msg.response_to,
                })
                trace_info["end_time"] = msg.timestamp.isoformat() + "Z"
        
        # Convert sets to lists and limit results
        traces = []
        for trace_id_val, trace_info in list(traces_map.items())[:limit]:
            trace_info["agents"] = list(trace_info["agents"])
            trace_info["intents"] = list(trace_info["intents"])
            traces.append(trace_info)
        
        return {"traces": traces, "total": len(traces)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/metrics")
async def get_metrics(
    time_range: str = "1h",  # 1h, 24h, 7d, 30d
    db: Session = Depends(get_db)
):
    """Get hub metrics (v0.3)"""
    try:
        # Calculate time range
        now = datetime.utcnow()
        if time_range == "1h":
            start_time = now - timedelta(hours=1)
        elif time_range == "24h":
            start_time = now - timedelta(hours=24)
        elif time_range == "7d":
            start_time = now - timedelta(days=7)
        elif time_range == "30d":
            start_time = now - timedelta(days=30)
        else:
            start_time = now - timedelta(hours=1)
        
        # Get messages in time range
        messages = db.query(Message).filter(
            Message.timestamp >= start_time
        ).all()
        
        # Calculate metrics
        total_messages = len(messages)
        avg_latency = 0
        avg_cpu = 0
        avg_mem = 0
        latency_count = 0
        cpu_count = 0
        mem_count = 0
        
        for msg in messages:
            metadata = msg.message_metadata or {}
            if "latency_ms" in metadata:
                avg_latency += metadata["latency_ms"]
                latency_count += 1
            if "cpu_usage" in metadata:
                avg_cpu += metadata["cpu_usage"]
                cpu_count += 1
            if "mem_usage" in metadata:
                avg_mem += metadata["mem_usage"]
                mem_count += 1
        
        return {
            "time_range": time_range,
            "total_messages": total_messages,
            "average_latency_ms": avg_latency / latency_count if latency_count > 0 else 0,
            "average_cpu_usage": avg_cpu / cpu_count if cpu_count > 0 else 0,
            "average_memory_usage": avg_mem / mem_count if mem_count > 0 else 0,
            "messages_per_minute": total_messages / max((now - start_time).total_seconds() / 60, 1),
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

