"""
Tests for OmniSync Protocol message validation
"""

import pytest
from omnisync.protocol import (
    IntentMessage,
    QueryIntent,
    PlanIntent,
    ExecuteIntent,
    IntentType,
    create_intent_message,
)


def test_query_intent_creation():
    """Test creating a query intent message"""
    msg = QueryIntent(
        from_agent="agent_a",
        to_agent="agent_b",
        content={"query": "What is the weather?"},
    )
    assert msg.intent == IntentType.QUERY
    assert msg.from_agent == "agent_a"
    assert msg.to_agent == "agent_b"
    assert msg.content["query"] == "What is the weather?"


def test_plan_intent_creation():
    """Test creating a plan intent message"""
    msg = PlanIntent(
        from_agent="planner",
        to_agent="broadcast",
        content={"goal": "Process data", "steps": []},
    )
    assert msg.intent == IntentType.PLAN
    assert msg.to_agent == "broadcast"


def test_execute_intent_creation():
    """Test creating an execute intent message"""
    msg = ExecuteIntent(
        from_agent="executor",
        to_agent="executor",
        content={"task": "fetch_data", "parameters": {}},
    )
    assert msg.intent == IntentType.EXECUTE
    assert msg.content["task"] == "fetch_data"


def test_create_intent_message_factory():
    """Test the factory function"""
    msg = create_intent_message(
        IntentType.QUERY,
        "agent_a",
        "agent_b",
        {"query": "Hello"},
    )
    assert isinstance(msg, QueryIntent)
    assert msg.intent == IntentType.QUERY


def test_message_validation():
    """Test message validation"""
    # Valid message
    msg = QueryIntent(
        from_agent="agent_a",
        to_agent="agent_b",
        content={"query": "Test"},
    )
    assert msg.id is not None
    assert msg.timestamp is not None

    # Invalid: missing query
    with pytest.raises(Exception):
        QueryIntent(
            from_agent="agent_a",
            to_agent="agent_b",
            content={},  # Missing query
        )


def test_broadcast_message():
    """Test broadcast message"""
    msg = create_intent_message(
        IntentType.NOTIFY,
        "agent_a",
        "broadcast",
        {"event": "status_update", "message": "Hello all"},
    )
    assert msg.to_agent == "broadcast"


if __name__ == "__main__":
    pytest.main([__file__])

