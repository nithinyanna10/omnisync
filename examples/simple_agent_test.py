"""
Realistic OmniSync SDK demonstration
Shows how agents communicate with full message structure, metadata, and real-world scenarios.
"""

import asyncio
import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sdk', 'python'))

from omnisync import Agent, IntentType, ContentType, create_content
from omnisync.ollama_integration import OllamaClient


def print_message_details(msg, direction="→"):
    """Print detailed message information for real-world visibility"""
    print(f"\n{'='*80}")
    print(f"{direction} MESSAGE DETAILS")
    print(f"{'='*80}")
    print(f"📨 Message ID: {msg.id}")
    print(f"🕐 Timestamp: {msg.timestamp}")
    intent_value = msg.intent.value if hasattr(msg.intent, 'value') else str(msg.intent)
    print(f"📋 Intent: {intent_value.upper()}")
    print(f"👤 From: {msg.from_agent}")
    print(f"👥 To: {msg.to_agent}")
    print(f"📊 Schema Version: {msg.schema_version}")
    
    # Metadata details
    if msg.metadata:
        print(f"\n📦 METADATA:")
        print(f"   Framework: {msg.metadata.get('framework', 'N/A')}")
        print(f"   Model: {msg.metadata.get('model', 'N/A')}")
        print(f"   Hop Count: {msg.metadata.get('hop_count', 0)}")
        print(f"   TTL: {msg.metadata.get('ttl', 3)}")
        if 'latency_ms' in msg.metadata:
            print(f"   Latency: {msg.metadata.get('latency_ms')}ms")
        if 'session_id' in msg.metadata:
            print(f"   Session ID: {msg.metadata.get('session_id')}")
        if 'trace_id' in msg.metadata:
            print(f"   Trace ID: {msg.metadata.get('trace_id')}")
        if 'capabilities' in msg.metadata:
            print(f"   Capabilities: {', '.join(msg.metadata.get('capabilities', []))}")
    
    # Content details
    print(f"\n💬 CONTENT:")
    content_type = msg.content.get('type', 'raw')
    if content_type == 'text_response':
        print(f"   Type: {content_type}")
        print(f"   Data: {msg.content.get('data', '')[:100]}...")
        if 'confidence' in msg.content:
            print(f"   Confidence: {msg.content.get('confidence')}")
    else:
        print(f"   {json.dumps(msg.content, indent=2)}")
    
    if msg.response_to:
        print(f"\n🔗 Response To: {msg.response_to}")
    
    print(f"{'='*80}\n")


async def main():
    # Initialize Ollama for dynamic responses (optional)
    try:
        ollama_client = OllamaClient(model="gpt-oss:120b-cloud")
        await ollama_client.connect()
        use_ollama = True
        print("✅ Ollama connected - using dynamic LLM responses")
    except Exception as e:
        print(f"⚠️  Ollama not available, using realistic static responses: {e}")
        use_ollama = False
        ollama_client = None
    
    # Create agents with realistic capabilities
    agent_a = Agent(
        name="DataAnalyst",
        framework="OmniSync",
        hub_url="http://localhost:8080",
        model="gpt-oss:120b-cloud" if use_ollama else "gpt-4",
        capabilities=["query", "plan", "evaluate"]
    )
    
    agent_b = Agent(
        name="TaskExecutor",
        framework="OmniSync",
        hub_url="http://localhost:8080",
        model="gpt-oss:120b-cloud" if use_ollama else "gpt-4",
        capabilities=["act", "execute", "notify"]
    )
    
    # Agent A: Data Analyst - handles queries with detailed analysis
    @agent_a.on("query")
    async def handle_query(msg):
        query = msg.content.get('query', '')
        context = msg.content.get('context', {})
        print(f"\n🔍 [DataAnalyst] Received query: {query}")
        if context:
            print(f"   Context: {context}")
        print_message_details(msg, "← RECEIVED")
        
        # Simulate real data analysis
        if use_ollama and ollama_client:
            prompt = f"As a data analyst, analyze this query: {query}. Provide a structured analysis."
            try:
                response_text = await ollama_client.generate(prompt)
                analysis_data = response_text[:300]
            except:
                analysis_data = "Based on the query analysis, I've identified key patterns and insights."
        else:
            analysis_data = (
                "Analysis Results:\n"
                "- Query complexity: Medium\n"
                "- Required data sources: 3\n"
                "- Estimated processing time: 2.5s\n"
                "- Confidence level: High"
            )
        
        response = create_content(
            ContentType.TEXT_RESPONSE,
            analysis_data,
            confidence=0.92,
            sources=["internal_db", "api_cache", "analytics_engine"]
        )
        
        print(f"\n📤 [DataAnalyst] Sending analysis response...")
        return response
    
    # Agent B: Task Executor - handles actions and notifications
    @agent_b.on("act")
    async def handle_act(msg):
        action = msg.content.get('action') or msg.content.get('task', '')
        params = msg.content.get('parameters', {})
        print(f"\n⚙️  [TaskExecutor] Received action: {action}")
        print_message_details(msg, "← RECEIVED")
        
        # Simulate task execution
        result = {
            "type": "json_data",
            "data": {
                "action": action,
                "status": "completed",
                "execution_time_ms": 1250,
                "result": {
                    "records_processed": 150,
                    "success_rate": 0.98,
                    "output_location": "/data/results/2025-11-12/output.json"
                },
                "metadata": {
                    "worker_id": "worker-42",
                    "queue_time": "2025-11-12T18:30:00Z",
                    "completion_time": "2025-11-12T18:30:01.25Z"
                }
            }
        }
        
        print(f"\n📤 [TaskExecutor] Task completed, sending result...")
        return result
    
    @agent_b.on("notify")
    async def handle_notify(msg):
        event = msg.content.get('event', '')
        message = msg.content.get('message', '')
        print(f"\n🔔 [TaskExecutor] Received notification: {event}")
        print_message_details(msg, "← RECEIVED")
        
        response = create_content(
            ContentType.TEXT_RESPONSE,
            f"Notification acknowledged: {event} - {message}",
            confidence=1.0
        )
        
        print(f"\n📤 [TaskExecutor] Sending acknowledgment...")
        return response
    
    # Start agents
    print("\n" + "="*80)
    print("🚀 STARTING OMNISYNC AGENTS")
    print("="*80)
    await agent_a.start()
    await agent_b.start()
    
    print(f"\n✅ Agent Registered: {agent_a.agent_id} (DataAnalyst)")
    print(f"   Capabilities: {', '.join(agent_a.capabilities)}")
    print(f"   Framework: {agent_a.framework}")
    print(f"   Model: {agent_a.model}")
    
    print(f"\n✅ Agent Registered: {agent_b.agent_id} (TaskExecutor)")
    print(f"   Capabilities: {', '.join(agent_b.capabilities)}")
    print(f"   Framework: {agent_b.framework}")
    print(f"   Model: {agent_b.model}")
    
    # Wait for registration
    await asyncio.sleep(2)
    
    # Scenario 1: Data Analyst queries Task Executor for status
    print("\n" + "="*80)
    print("📊 SCENARIO 1: Data Query")
    print("="*80)
    print(f"\n📤 [TaskExecutor] → [DataAnalyst]: Query about data processing status")
    
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    trace_id = f"trace_{datetime.now().timestamp()}"
    
    query_msg = await agent_b.send(
        IntentType.QUERY,
        agent_a.agent_id,
        {
            "query": "What is the current status of the data processing pipeline? I need metrics on throughput and error rates.",
            "type": "text",
            "context": {
                "requested_metrics": ["throughput", "error_rates"],
                "time_range": "last_24_hours"
            }
        },
        session_id=session_id,
        trace_id=trace_id
    )
    print_message_details(query_msg, "→ SENT")
    
    # Wait for response
    await asyncio.sleep(3)
    
    # Scenario 2: Task Executor performs an action
    print("\n" + "="*80)
    print("⚙️  SCENARIO 2: Task Execution")
    print("="*80)
    print(f"\n📤 [DataAnalyst] → [TaskExecutor]: Request to process data batch")
    
    act_msg = await agent_a.send(
        IntentType.ACT,
        agent_b.agent_id,
        {
            "action": "process_data_batch",
            "parameters": {
                "batch_id": "batch_2025_11_12_001",
                "source": "data_warehouse",
                "target": "analytics_db",
                "transformations": ["normalize", "validate", "aggregate"]
            },
            "priority": "high",
            "timeout_seconds": 30
        },
        session_id=session_id,
        trace_id=trace_id
    )
    print_message_details(act_msg, "→ SENT")
    
    # Wait for response
    await asyncio.sleep(3)
    
    # Scenario 3: Status notification
    print("\n" + "="*80)
    print("🔔 SCENARIO 3: Status Notification")
    print("="*80)
    print(f"\n📤 [TaskExecutor] → [DataAnalyst]: Notify completion status")
    
    notify_msg = await agent_b.send(
        IntentType.NOTIFY,
        agent_a.agent_id,
        {
            "event": "pipeline_status_update",
            "message": "Data processing pipeline completed successfully",
            "details": {
                "records_processed": 15000,
                "success_rate": 0.998,
                "duration_seconds": 45.2,
                "next_batch_eta": "2025-11-12T19:00:00Z"
            }
        },
        session_id=session_id,
        trace_id=trace_id
    )
    print_message_details(notify_msg, "→ SENT")
    
    # Wait for final processing
    await asyncio.sleep(2)
    
    print("\n" + "="*80)
    print("✅ DEMONSTRATION COMPLETED")
    print("="*80)
    print(f"\n📊 Session Summary:")
    print(f"   Session ID: {session_id}")
    print(f"   Trace ID: {trace_id}")
    print(f"   Messages exchanged: 3")
    print(f"   Agents involved: 2")
    print(f"   Intents used: query, act, notify")
    print(f"\n💡 This demonstrates real-world OmniSync usage with:")
    print(f"   • Full message structure visibility")
    print(f"   • Metadata tracking (session, trace, latency)")
    print(f"   • Structured content types")
    print(f"   • Multi-agent collaboration")
    print(f"   • Production-ready logging")
    
    await agent_a.stop()
    await agent_b.stop()
    
    if ollama_client:
        await ollama_client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

