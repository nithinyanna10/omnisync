"""
Multi-Agent Benchmark Dataset
Save trace logs to JSON for reproducible experiments (v0.3)
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path


def save_trace_dataset(
    messages: List[Dict[str, Any]],
    output_path: str = "datasets/omnisync_trace_v0.2.json",
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Save trace logs to JSON dataset format
    
    Args:
        messages: List of message dictionaries
        output_path: Path to save the dataset
        metadata: Additional metadata about the dataset
        
    Returns:
        Path to saved dataset
    """
    # Ensure directory exists
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Prepare dataset structure
    dataset = {
        "version": "0.2",
        "schema_version": "osp-0.2",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "metadata": metadata or {
            "description": "OmniSync Protocol trace dataset",
            "total_messages": len(messages),
            "source": "omnisync_hub"
        },
        "traces": []
    }
    
    # Group messages by trace_id
    traces_map = {}
    for msg in messages:
        metadata = msg.get("metadata", {})
        trace_id = metadata.get("trace_id") or "untraced"
        session_id = metadata.get("session_id") or "unsessioned"
        
        if trace_id not in traces_map:
            traces_map[trace_id] = {
                "trace_id": trace_id,
                "session_id": session_id,
                "messages": [],
                "start_time": msg.get("timestamp"),
                "agents": set(),
                "intents": set()
            }
        
        trace = traces_map[trace_id]
        trace["messages"].append(msg)
        trace["agents"].add(msg.get("from"))
        if msg.get("to") and msg.get("to") != "broadcast":
            trace["agents"].add(msg.get("to"))
        trace["intents"].add(msg.get("intent"))
        trace["end_time"] = msg.get("timestamp")
    
    # Convert sets to lists and sort messages by timestamp
    for trace_id, trace in traces_map.items():
        trace["agents"] = sorted(list(trace["agents"]))
        trace["intents"] = sorted(list(trace["intents"]))
        trace["messages"] = sorted(trace["messages"], key=lambda m: m.get("timestamp", ""))
        trace["message_count"] = len(trace["messages"])
        dataset["traces"].append(trace)
    
    # Sort traces by start time
    dataset["traces"] = sorted(dataset["traces"], key=lambda t: t.get("start_time", ""))
    
    # Calculate summary statistics
    dataset["summary"] = {
        "total_traces": len(dataset["traces"]),
        "total_messages": len(messages),
        "unique_agents": len(set(agent for trace in dataset["traces"] for agent in trace["agents"])),
        "intent_distribution": {}
    }
    
    for trace in dataset["traces"]:
        for intent in trace["intents"]:
            dataset["summary"]["intent_distribution"][intent] = \
                dataset["summary"]["intent_distribution"].get(intent, 0) + 1
    
    # Save to file
    with open(output_file, 'w') as f:
        json.dump(dataset, f, indent=2)
    
    return str(output_file)


def load_trace_dataset(dataset_path: str) -> Dict[str, Any]:
    """
    Load trace dataset from JSON file
    
    Args:
        dataset_path: Path to dataset file
        
    Returns:
        Dataset dictionary
    """
    with open(dataset_path, 'r') as f:
        return json.load(f)


def export_trace_from_hub(
    hub_url: str = "http://localhost:8080",
    output_path: str = "datasets/omnisync_trace_v0.2.json",
    limit: int = 1000
) -> str:
    """
    Export trace dataset directly from OmniSync Hub
    
    Args:
        hub_url: Hub API URL
        output_path: Path to save dataset
        limit: Maximum number of messages to export
        
    Returns:
        Path to saved dataset
    """
    import requests
    
    # Fetch messages from hub
    response = requests.get(f"{hub_url}/api/messages?limit={limit}")
    if response.status_code != 200:
        raise Exception(f"Failed to fetch messages: {response.status_code}")
    
    data = response.json()
    messages = data.get("messages", [])
    
    # Save as dataset
    return save_trace_dataset(
        messages,
        output_path,
        metadata={
            "source": "omnisync_hub",
            "hub_url": hub_url,
            "exported_at": datetime.utcnow().isoformat() + "Z"
        }
    )

