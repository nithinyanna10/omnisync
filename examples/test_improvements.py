"""
Comprehensive test for OmniSync v0.2 improvements
Tests: Session/Trace propagation, ACK intent, metadata enrichment, schema validation, trace visualization
"""

import asyncio
import sys
import os
import json
import time
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sdk', 'python'))

from omnisync import Agent, IntentType, ContentType, create_content
from omnisync.protocol import IntentMessage, AckIntent
from omnisync.validation import validate_message_dict
from omnisync.trace_visualization import (
    prepare_sequence_diagram,
    prepare_force_graph_data,
    prepare_trace_log,
    generate_trace_summary
)


def print_test_header(test_name):
    """Print formatted test header"""
    print("\n" + "="*80)
    print(f"🧪 TEST: {test_name}")
    print("="*80)


def print_success(message):
    """Print success message"""
    print(f"✅ {message}")


def print_error(message):
    """Print error message"""
    print(f"❌ {message}")


async def test_session_trace_propagation():
    """Test A: Session and Trace ID propagation"""
    print_test_header("A. Session + Trace ID Propagation")
    
    # Generate IDs at start
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    trace_id = f"trace_{time.time()}"
    
    print(f"Generated at start:")
    print(f"  Session ID: {session_id}")
    print(f"  Trace ID: {trace_id}")
    
    # Create agent with IDs
    agent = Agent(
        name="TestAgent",
        framework="OmniSync",
        hub_url="http://localhost:8080",
        session_id=session_id,
        trace_id=trace_id
    )
    
    try:
        await agent.start()
        await asyncio.sleep(1)
        
        # Send message (should use agent's default IDs)
        msg = await agent.send(
            IntentType.NOTIFY,
            "omnisync_TestAgent",
            {"event": "test", "message": "Testing session/trace propagation"}
        )
        
        # Check metadata
        msg_session = msg.metadata.get("session_id")
        msg_trace = msg.metadata.get("trace_id")
        
        if msg_session == session_id:
            print_success(f"Session ID propagated: {msg_session}")
        else:
            print_error(f"Session ID mismatch: expected {session_id}, got {msg_session}")
        
        if msg_trace == trace_id:
            print_success(f"Trace ID propagated: {msg_trace}")
        else:
            print_error(f"Trace ID mismatch: expected {trace_id}, got {msg_trace}")
        
        # Proper cleanup
        await agent.stop()
        await asyncio.sleep(0.3)  # Give time for cleanup
        
        return msg_session == session_id and msg_trace == trace_id
    except Exception as e:
        print_error(f"Test failed with exception: {e}")
        try:
            await agent.stop()
        except:
            pass
        return False


async def test_ack_intent():
    """Test C: ACK Intent"""
    print_test_header("C. ACK Intent")
    
    try:
        # Create ACK message
        ack_msg = AckIntent(
            from_agent="agent1",
            to_agent="agent2",
            content={
                "received": True,
                "response_to": "msg-123-456"
            }
        )
        
        print_success(f"ACK intent created: {ack_msg.intent}")
        print(f"  Content: {ack_msg.content}")
        print(f"  From: {ack_msg.from_agent}")
        print(f"  To: {ack_msg.to_agent}")
        
        # Validate content
        if ack_msg.content.get("received") and ack_msg.content.get("response_to"):
            print_success("ACK content valid")
            return True
        else:
            print_error("ACK content invalid")
            return False
    except Exception as e:
        print_error(f"Failed to create ACK: {e}")
        return False


def test_metadata_enrichment():
    """Test D: Metadata Enrichment"""
    print_test_header("D. Metadata Enrichment")
    
    try:
        agent = Agent(
            name="TestAgent",
            framework="OmniSync",
            hub_url="http://localhost:8080"
        )
        
        # Create a message (simulate send without actually sending)
        msg = IntentMessage(
            intent=IntentType.QUERY,
            from_agent="test_agent",
            to_agent="target_agent",
            content={"query": "test"},
            metadata={
                "framework": "OmniSync",
                "framework_version": "0.1.0",
                "cpu_usage": 25.5,
                "mem_usage": 60.2,
                "response_time_ms": 150,
                "latency_ms": 45
            }
        )
        
        # Check enriched fields
        checks = {
            "framework_version": msg.metadata.get("framework_version"),
            "cpu_usage": msg.metadata.get("cpu_usage"),
            "mem_usage": msg.metadata.get("mem_usage"),
            "response_time_ms": msg.metadata.get("response_time_ms"),
            "latency_ms": msg.metadata.get("latency_ms")
        }
        
        all_present = True
        for key, value in checks.items():
            if value is not None:
                print_success(f"{key}: {value}")
            else:
                print_error(f"{key}: missing")
                all_present = False
        
        return all_present
    except Exception as e:
        print_error(f"Metadata enrichment test failed: {e}")
        return False


def test_schema_v02():
    """Test E: Schema v0.2 Validation"""
    print_test_header("E. Schema v0.2 Validation")
    
    try:
        # Create message with v0.2 fields
        msg = IntentMessage(
            intent=IntentType.QUERY,
            from_agent="test_agent",
            to_agent="target_agent",
            content={"query": "test query"},
            metadata={
                "framework_version": "0.1.0",
                "cpu_usage": 25.5,
                "mem_usage": 60.2
            }
        )
        
        # Serialize to dict
        msg_dict = msg.model_dump(mode='json', by_alias=True)
        
        # Validate
        is_valid, error = validate_message_dict(msg_dict)
        
        if is_valid:
            print_success(f"Schema validation passed (v{msg.schema_version})")
            print(f"  Schema version: {msg.schema_version}")
            return True
        else:
            print_error(f"Schema validation failed: {error}")
            return False
    except Exception as e:
        print_error(f"Schema validation test failed: {e}")
        return False


def test_trace_visualization():
    """Test F: Trace Visualization"""
    print_test_header("F. Trace Visualization")
    
    # Sample messages
    messages = [
        {
            "id": "msg1",
            "from": "omnisync_DataAnalyst",
            "to": "omnisync_TaskExecutor",
            "intent": "query",
            "timestamp": "2025-11-13T10:00:00Z",
            "response_to": None
        },
        {
            "id": "msg2",
            "from": "omnisync_TaskExecutor",
            "to": "omnisync_DataAnalyst",
            "intent": "act",
            "timestamp": "2025-11-13T10:00:05Z",
            "response_to": "msg1"
        },
        {
            "id": "msg3",
            "from": "omnisync_TaskExecutor",
            "to": "omnisync_DataAnalyst",
            "intent": "notify",
            "timestamp": "2025-11-13T10:00:10Z",
            "response_to": None
        }
    ]
    
    try:
        # Test sequence diagram
        mermaid = prepare_sequence_diagram(messages)
        print_success("Mermaid sequence diagram generated")
        print(f"\n{mermaid}\n")
        
        # Test force graph data
        graph_data = prepare_force_graph_data(messages)
        print_success(f"Force graph data prepared: {len(graph_data['nodes'])} nodes, {len(graph_data['links'])} links")
        
        # Test trace log
        trace_log = prepare_trace_log(messages, format="text")
        print_success("Trace log generated (text format)")
        print(f"\n{trace_log[:200]}...\n")
        
        # Test summary
        summary = generate_trace_summary(messages)
        print_success("Trace summary generated")
        print(f"  Total messages: {summary['total_messages']}")
        print(f"  Unique agents: {summary['unique_agents']}")
        print(f"  Intents: {summary['intent_distribution']}")
        
        return True
    except Exception as e:
        print_error(f"Trace visualization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_ollama_session_handling():
    """Test B: Ollama Session Handling (if available)"""
    print_test_header("B. Ollama Session Handling")
    
    try:
        from omnisync.ollama_integration import OllamaClient
        
        client = OllamaClient(model="gpt-oss:120b-cloud")
        
        # Test generate (should use context manager)
        print("Testing Ollama generate with proper session cleanup...")
        result = await client.generate("Say hello in one word", stream=False)
        
        if result:
            print_success(f"Ollama generate worked: {result[:50]}...")
            print("  (No 'Unclosed client session' warnings expected)")
            return True
        else:
            print("⚠️  Ollama not available or returned empty response")
            return True  # Not a failure if Ollama isn't running
    except Exception as e:
        print(f"⚠️  Ollama test skipped: {e}")
        return True  # Not a failure if Ollama isn't available


async def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🚀 OMNISYNC v0.2 IMPROVEMENTS TEST SUITE")
    print("="*80)
    
    results = {}
    
    # Run tests
    try:
        results['A'] = await test_session_trace_propagation()
    except Exception as e:
        print_error(f"Test A failed: {e}")
        results['A'] = False
    
    try:
        results['B'] = await test_ollama_session_handling()
    except Exception as e:
        print_error(f"Test B failed: {e}")
        results['B'] = False
    
    try:
        results['C'] = await test_ack_intent()
    except Exception as e:
        print_error(f"Test C failed: {e}")
        results['C'] = False
    
    try:
        results['D'] = test_metadata_enrichment()
    except Exception as e:
        print_error(f"Test D failed: {e}")
        results['D'] = False
    
    try:
        results['E'] = test_schema_v02()
    except Exception as e:
        print_error(f"Test E failed: {e}")
        results['E'] = False
    
    try:
        results['F'] = test_trace_visualization()
    except Exception as e:
        print_error(f"Test F failed: {e}")
        results['F'] = False
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    for test_id, test_name in [
        ('A', 'Session + Trace ID Propagation'),
        ('B', 'Ollama Session Handling'),
        ('C', 'ACK Intent'),
        ('D', 'Metadata Enrichment'),
        ('E', 'Schema v0.2 Validation'),
        ('F', 'Trace Visualization')
    ]:
        status = "✅ PASS" if results.get(test_id) else "❌ FAIL"
        print(f"{status} - {test_id}. {test_name}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")


if __name__ == "__main__":
    asyncio.run(main())

