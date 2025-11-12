"""
Multi-agent conversation using Ollama 120B model
Demonstrates Planner -> Executor -> Evaluator workflow
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sdk', 'python'))

from omnisync import Agent, IntentType
from omnisync.ollama_integration import OllamaClient, create_ollama_agent_handler


async def main():
    # Initialize LLM client with gpt-oss:120b-cloud model
    ollama_client = OllamaClient(model="gpt-oss:120b-cloud")
    
    # Planner Agent
    planner = Agent(
        name="Planner",
        framework="LangChain",
        hub_url="http://localhost:8080",
        model="gpt-oss:120b-cloud",
        capabilities=["plan"],
    )
    
    planner_handler = create_ollama_agent_handler(
        ollama_client,
        "You are a strategic planning agent. Create detailed, actionable plans."
    )
    
    @planner.on("query")
    async def planner_query(msg):
        return await planner_handler(msg, "query")
    
    # Executor Agent
    executor = Agent(
        name="Executor",
        framework="AutoGen",
        hub_url="http://localhost:8080",
        model="gpt-oss:120b-cloud",
        capabilities=["execute"],
    )
    
    executor_handler = create_ollama_agent_handler(
        ollama_client,
        "You are an execution agent. Execute tasks efficiently and report results."
    )
    
    @executor.on("execute")
    async def executor_execute(msg):
        task = msg.content.get("task", "")
        prompt = f"Execute this task step by step: {task}\n\nExecution plan:"
        execution_plan = await ollama_client.generate(prompt)
        return {
            "status": "completed",
            "task": task,
            "result": execution_plan[:300],
        }
    
    @executor.on("plan")
    async def executor_receive_plan(msg):
        goal = msg.content.get("goal", "")
        steps = msg.content.get("steps", [])
        
        print(f"\n🔧 Executor received plan for: {goal}")
        print(f"   Steps to execute: {len(steps)}")
        
        # Execute each step
        for i, step in enumerate(steps[:3], 1):  # Limit to 3 steps for demo
            print(f"\n   Executing step {i}: {step.get('action', 'unknown')}")
            await executor.send(
                IntentType.EXECUTE,
                executor.agent_id,  # Self-execute
                {"task": step.get("action", ""), "parameters": step}
            )
            await asyncio.sleep(1)
        
        return {"status": "plan_execution_started", "steps_processed": len(steps)}
    
    # Evaluator Agent
    evaluator = Agent(
        name="Evaluator",
        framework="CrewAI",
        hub_url="http://localhost:8080",
        model="gpt-oss:120b-cloud",
        capabilities=["evaluate"],
    )
    
    evaluator_handler = create_ollama_agent_handler(
        ollama_client,
        "You are an evaluation agent. Provide constructive feedback and scores."
    )
    
    @evaluator.on("evaluate")
    async def evaluator_evaluate(msg):
        target = msg.content.get("target", "")
        criteria = msg.content.get("criteria", ["quality", "feasibility", "completeness"])
        
        prompt = f"Evaluate this: {target}\n\nCriteria: {', '.join(criteria)}\n\nProvide scores (0-1) and feedback:"
        evaluation = await ollama_client.generate(prompt)
        
        return {
            "target": target,
            "criteria": criteria,
            "scores": {"quality": 0.9, "feasibility": 0.85, "completeness": 0.8},
            "feedback": evaluation[:250],
        }
    
    @evaluator.on("execute")
    async def evaluator_receive_execution(msg):
        # Evaluator can evaluate execution results
        task = msg.content.get("task", "")
        result = msg.content.get("result", "")
        
        print(f"\n📊 Evaluator reviewing execution: {task}")
        
        await evaluator.send(
            IntentType.EVALUATE,
            executor.agent_id,
            {
                "target": msg.id,
                "criteria": ["correctness", "efficiency"],
                "scores": {},
            }
        )
        
        return {"status": "evaluation_requested"}
    
    # Start all agents
    await planner.start()
    await executor.start()
    await evaluator.start()
    
    print("=" * 60)
    print("Multi-Agent System Started")
    print("=" * 60)
    print(f"Planner:   {planner.agent_id}")
    print(f"Executor:  {executor.agent_id}")
    print(f"Evaluator: {evaluator.agent_id}")
    print("=" * 60)
    
    await asyncio.sleep(3)  # Wait for registration
    
    # Start the workflow
    print("\n🚀 Starting workflow: Plan -> Execute -> Evaluate")
    
    # Step 1: Planner creates a plan
    print("\n1️⃣  Planner creating plan...")
    plan_msg = await planner.send(
        IntentType.PLAN,
        "broadcast",
        {
            "goal": "Analyze and summarize today's financial market trends",
            "priority": "high"
        }
    )
    print(f"   Plan message sent: {plan_msg.id}")
    
    await asyncio.sleep(3)
    
    # Step 2: Executor receives plan and starts execution
    # (This happens automatically via the handler)
    
    await asyncio.sleep(5)
    
    # Step 3: Evaluator evaluates the plan
    print("\n3️⃣  Evaluator evaluating the plan...")
    eval_msg = await evaluator.send(
        IntentType.EVALUATE,
        planner.agent_id,
        {
            "target": plan_msg.id,
            "criteria": ["quality", "feasibility", "clarity"],
            "scores": {},
        }
    )
    print(f"   Evaluation message sent: {eval_msg.id}")
    
    print("\n" + "=" * 60)
    print("💬 Agents are communicating...")
    print("   Check the Hub UI at http://localhost:3001")
    print("   Press Ctrl+C to stop")
    print("=" * 60)
    
    try:
        await asyncio.sleep(60)  # Run for 1 minute
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping agents...")
    
    await planner.stop()
    await executor.stop()
    await evaluator.stop()
    await ollama_client.disconnect()
    
    print("✅ All agents stopped.")


if __name__ == "__main__":
    asyncio.run(main())

