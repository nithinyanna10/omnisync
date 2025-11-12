"""
Example: LangChain and AutoGen agents communicating via OmniSync
This demonstrates cross-framework interoperability using Ollama as the LLM backend.
"""

import asyncio
import sys
import os

# Add SDK to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sdk', 'python'))

from omnisync import Agent, IntentType
from omnisync.ollama_integration import OllamaClient, create_ollama_agent_handler


async def main():
    # Initialize LLM client (assuming Ollama is running locally)
    ollama_client = OllamaClient(model="gpt-oss:120b-cloud")
    
    # Create LangChain-style agent (Planner)
    planner = Agent(
        name="Planner",
        framework="LangChain",
        hub_url="http://localhost:8080",
        model="gpt-oss:120b-cloud",
        capabilities=["plan", "query"],
    )
    
    # Create handler for planner using Ollama
    planner_handler = create_ollama_agent_handler(
        ollama_client,
        system_prompt="You are a planning agent. Create step-by-step plans to achieve goals."
    )
    
    @planner.on("query")
    async def handle_planner_query(msg):
        query = msg.content.get("query", "")
        response = await planner_handler(msg, "query")
        return response
    
    @planner.on("plan")
    async def handle_plan_request(msg):
        goal = msg.content.get("goal", "")
        # Use Ollama to create a plan
        prompt = f"Create a detailed plan to achieve this goal: {goal}\n\nPlan:"
        plan_text = await ollama_client.generate(prompt)
        return {
            "goal": goal,
            "steps": [
                {"action": "step1", "description": plan_text[:100]},
                {"action": "step2", "description": "Continue execution"},
            ],
            "priority": "high"
        }
    
    # Create AutoGen-style agent (Executor)
    executor = Agent(
        name="Executor",
        framework="AutoGen",
        hub_url="http://localhost:8080",
        model="gpt-oss:120b-cloud",
        capabilities=["execute", "notify"],
    )
    
    executor_handler = create_ollama_agent_handler(
        ollama_client,
        system_prompt="You are an execution agent. Execute tasks efficiently."
    )
    
    @executor.on("execute")
    async def handle_execute(msg):
        task = msg.content.get("task", "")
        # Use Ollama to simulate task execution
        prompt = f"Execute this task: {task}\n\nStatus:"
        status = await ollama_client.generate(prompt)
        return {
            "status": "completed",
            "task": task,
            "result": status[:200],
        }
    
    @executor.on("plan")
    async def handle_executor_plan(msg):
        # Executor receives plan and starts executing
        goal = msg.content.get("goal", "")
        steps = msg.content.get("steps", [])
        
        # Execute first step
        if steps:
            first_step = steps[0]
            await executor.send(
                IntentType.EXECUTE,
                "executor_executor",
                {"task": first_step.get("action", ""), "parameters": first_step},
            )
        
        return {"status": "plan_received", "steps_count": len(steps)}
    
    # Start both agents
    await planner.start()
    await executor.start()
    
    print("Agents started! Waiting for messages...")
    print("Planner ID:", planner.agent_id)
    print("Executor ID:", executor.agent_id)
    
    # Simulate a conversation
    await asyncio.sleep(2)  # Wait for agents to register
    
    # Planner creates a plan
    print("\n📋 Planner creating a plan...")
    plan_msg = await planner.send(
        IntentType.PLAN,
        "broadcast",
        {
            "goal": "Summarize today's financial news",
            "priority": "high"
        }
    )
    print(f"Plan message sent: {plan_msg.id}")
    
    # Wait a bit for processing
    await asyncio.sleep(3)
    
    # Executor queries for more info
    print("\n🔍 Executor querying for details...")
    query_msg = await executor.send(
        IntentType.QUERY,
        planner.agent_id,
        {
            "query": "What sources should I use for financial news?",
        }
    )
    print(f"Query message sent: {query_msg.id}")
    
    # Keep running for a while to see the conversation
    print("\n💬 Agents are communicating... (Press Ctrl+C to stop)")
    try:
        await asyncio.sleep(30)
    except KeyboardInterrupt:
        print("\n\nStopping agents...")
    
    await planner.stop()
    await executor.stop()
    await ollama_client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

