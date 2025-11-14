"""
Trace visualization utilities for OmniSync
Prepares message data for graph rendering (D3, Mermaid, etc.)
"""

from typing import List, Dict, Any, Optional
from datetime import datetime


def prepare_sequence_diagram(messages: List[Dict[str, Any]]) -> str:
    """
    Generate Mermaid sequence diagram from messages
    
    Args:
        messages: List of message dictionaries with from, to, intent, timestamp
        
    Returns:
        Mermaid sequence diagram string
    """
    lines = ["sequenceDiagram"]
    
    # Sort by timestamp
    sorted_messages = sorted(messages, key=lambda m: m.get("timestamp", ""))
    
    for msg in sorted_messages:
        from_agent = msg.get("from", "Unknown")
        to_agent = msg.get("to", "Unknown")
        intent = msg.get("intent", "unknown").upper()
        
        # Shorten agent names for readability
        from_short = from_agent.split("_")[-1] if "_" in from_agent else from_agent
        to_short = to_agent.split("_")[-1] if "_" in to_agent else to_agent
        
        lines.append(f"    {from_short}->>{to_short}: {intent}")
    
    return "\n".join(lines)


def prepare_force_graph_data(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Prepare data structure for D3 force-directed graph
    
    Args:
        messages: List of message dictionaries
        
    Returns:
        Dictionary with nodes and links for D3 force graph
    """
    nodes_map = {}
    links = []
    
    for msg in messages:
        from_agent = msg.get("from")
        to_agent = msg.get("to")
        intent = msg.get("intent", "unknown")
        msg_id = msg.get("id")
        response_to = msg.get("response_to")
        timestamp = msg.get("timestamp")
        
        # Add nodes
        if from_agent and from_agent not in nodes_map:
            nodes_map[from_agent] = {
                "id": from_agent,
                "name": from_agent.split("_")[-1] if "_" in from_agent else from_agent,
                "framework": msg.get("metadata", {}).get("framework", "Unknown"),
                "group": 1
            }
        
        if to_agent and to_agent != "broadcast" and to_agent not in nodes_map:
            nodes_map[to_agent] = {
                "id": to_agent,
                "name": to_agent.split("_")[-1] if "_" in to_agent else to_agent,
                "framework": "Unknown",
                "group": 1
            }
        
        # Add links
        if from_agent and to_agent and to_agent != "broadcast":
            links.append({
                "source": from_agent,
                "target": to_agent,
                "intent": intent,
                "message_id": msg_id,
                "response_to": response_to,
                "timestamp": timestamp,
                "value": 1
            })
    
    return {
        "nodes": list(nodes_map.values()),
        "links": links
    }


def prepare_trace_log(messages: List[Dict[str, Any]], format: str = "text") -> str:
    """
    Generate trace log in various formats
    
    Args:
        messages: List of message dictionaries
        format: Output format ("text", "json", "csv")
        
    Returns:
        Formatted trace log string
    """
    sorted_messages = sorted(messages, key=lambda m: m.get("timestamp", ""))
    
    if format == "text":
        lines = ["OmniSync Trace Log", "=" * 80]
        for msg in sorted_messages:
            from_agent = msg.get("from", "Unknown")
            to_agent = msg.get("to", "Unknown")
            intent = msg.get("intent", "unknown")
            timestamp = msg.get("timestamp", "")
            response_to = msg.get("response_to")
            
            line = f"{timestamp} | {from_agent} → {to_agent} | {intent.upper()}"
            if response_to:
                line += f" | Response to: {response_to}"
            lines.append(line)
        
        return "\n".join(lines)
    
    elif format == "json":
        import json
        return json.dumps({
            "trace": sorted_messages,
            "summary": {
                "total_messages": len(messages),
                "unique_agents": len(set(m.get("from") for m in messages) | set(m.get("to") for m in messages)),
                "intents_used": list(set(m.get("intent") for m in messages))
            }
        }, indent=2)
    
    elif format == "csv":
        lines = ["timestamp,from,to,intent,message_id,response_to"]
        for msg in sorted_messages:
            lines.append(f"{msg.get('timestamp')},{msg.get('from')},{msg.get('to')},{msg.get('intent')},{msg.get('id')},{msg.get('response_to', '')}")
        return "\n".join(lines)
    
    return ""


def extract_conversation_thread(messages: List[Dict[str, Any]], root_message_id: str) -> List[Dict[str, Any]]:
    """
    Extract a conversation thread starting from a root message
    
    Args:
        messages: List of all messages
        root_message_id: ID of the root message
        
    Returns:
        List of messages in the thread (ordered by timestamp)
    """
    thread = []
    message_map = {m.get("id"): m for m in messages}
    
    # Find root message
    root = message_map.get(root_message_id)
    if not root:
        return []
    
    thread.append(root)
    
    # Find all responses
    def find_responses(msg_id):
        for msg in messages:
            if msg.get("response_to") == msg_id:
                thread.append(msg)
                find_responses(msg.get("id"))
    
    find_responses(root_message_id)
    
    # Sort by timestamp
    return sorted(thread, key=lambda m: m.get("timestamp", ""))


def generate_trace_summary(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate summary statistics for a trace
    
    Args:
        messages: List of message dictionaries
        
    Returns:
        Dictionary with summary statistics
    """
    intents = {}
    agents = set()
    sessions = set()
    traces = set()
    
    for msg in messages:
        intent = msg.get("intent", "unknown")
        intents[intent] = intents.get(intent, 0) + 1
        
        if msg.get("from"):
            agents.add(msg.get("from"))
        if msg.get("to") and msg.get("to") != "broadcast":
            agents.add(msg.get("to"))
        
        metadata = msg.get("metadata", {})
        if metadata.get("session_id"):
            sessions.add(metadata.get("session_id"))
        if metadata.get("trace_id"):
            traces.add(metadata.get("trace_id"))
    
    return {
        "total_messages": len(messages),
        "unique_agents": len(agents),
        "unique_sessions": len(sessions),
        "unique_traces": len(traces),
        "intent_distribution": intents,
        "agents": sorted(list(agents)),
        "time_span": {
            "start": min((m.get("timestamp", "") for m in messages), default=""),
            "end": max((m.get("timestamp", "") for m in messages), default="")
        }
    }

