"""
Simple test to verify OmniSync SDK works end-to-end
Tests message sending and receiving between two agents.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sdk', 'python'))

from omnisync import Agent, IntentType


async def main():
    # Create two simple agents
    agent_a = Agent(
        name="AgentA",
        framework="OmniSync",
        hub_url="http://localhost:8080",
    )
    
    agent_b = Agent(
        name="AgentB",
        framework="OmniSync",
        hub_url="http://localhost:8080",
    )
    
    # Agent A handles queries
    @agent_a.on("query")
    async def handle_query(msg):
        print(f"Agent A received query: {msg.content.get('query')}")
        return {"answer": "I am Agent A responding via OmniSync!"}
    
    # Agent B handles notifications
    @agent_b.on("notify")
    async def handle_notify(msg):
        print(f"Agent B received notification: {msg.content.get('message')}")
        return {"status": "acknowledged"}
    
    # Start agents
    await agent_a.start()
    await agent_b.start()
    
    print("Agents started!")
    print(f"Agent A ID: {agent_a.agent_id}")
    print(f"Agent B ID: {agent_b.agent_id}")
    
    # Wait for registration
    await asyncio.sleep(2)
    
    # Agent B sends a query to Agent A
    print("\n📤 Agent B sending query to Agent A...")
    query_msg = await agent_b.send(
        IntentType.QUERY,
        agent_a.agent_id,
        {"query": "Hello from Agent B!"}
    )
    print(f"Query message ID: {query_msg.id}")
    
    # Wait for response
    await asyncio.sleep(2)
    
    # Agent A sends a notification to Agent B
    print("\n📤 Agent A sending notification to Agent B...")
    notify_msg = await agent_a.send(
        IntentType.NOTIFY,
        agent_b.agent_id,
        {
            "event": "status_update",
            "message": "Task completed successfully"
        }
    )
    print(f"Notification message ID: {notify_msg.id}")
    
    # Wait a bit more
    await asyncio.sleep(2)
    
    print("\n✅ Test completed!")
    
    await agent_a.stop()
    await agent_b.stop()


if __name__ == "__main__":
    asyncio.run(main())

