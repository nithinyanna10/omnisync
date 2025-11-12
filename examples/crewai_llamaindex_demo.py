"""
Example: CrewAI and LlamaIndex agents communicating via OmniSync
This demonstrates evaluation and query workflows using Ollama.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sdk', 'python'))

from omnisync import Agent, IntentType
from omnisync.ollama_integration import OllamaClient, create_ollama_agent_handler


async def main():
    ollama_client = OllamaClient(model="gpt-oss:120b-cloud")
    
    # CrewAI-style agent (Evaluator)
    evaluator = Agent(
        name="Evaluator",
        framework="CrewAI",
        hub_url="http://localhost:8080",
        model="gpt-oss:120b-cloud",
        capabilities=["evaluate", "reflect"],
    )
    
    @evaluator.on("evaluate")
    async def handle_evaluate(msg):
        target = msg.content.get("target", "")
        criteria = msg.content.get("criteria", ["quality", "feasibility"])
        
        prompt = f"Evaluate this target: {target}\n\nCriteria: {', '.join(criteria)}\n\nEvaluation:"
        evaluation = await ollama_client.generate(prompt)
        
        return {
            "target": target,
            "criteria": criteria,
            "scores": {"quality": 0.9, "feasibility": 0.8},
            "feedback": evaluation[:200],
        }
    
    # LlamaIndex-style agent (Query Agent)
    query_agent = Agent(
        name="QueryAgent",
        framework="LlamaIndex",
        hub_url="http://localhost:8080",
        model="gpt-oss:120b-cloud",
        capabilities=["query", "reflect"],
    )
    
    @query_agent.on("query")
    async def handle_query(msg):
        query = msg.content.get("query", "")
        prompt = f"Answer this query: {query}\n\nAnswer:"
        answer = await ollama_client.generate(prompt)
        
        return {
            "answer": answer,
            "sources": ["doc1", "doc2"],
        }
    
    @query_agent.on("evaluate")
    async def handle_query_evaluate(msg):
        # Query agent can also evaluate queries
        return await handle_evaluate(msg)
    
    await evaluator.start()
    await query_agent.start()
    
    print("Agents started!")
    print("Evaluator ID:", evaluator.agent_id)
    print("QueryAgent ID:", query_agent.agent_id)
    
    await asyncio.sleep(2)
    
    # Query agent asks a question
    print("\n❓ QueryAgent asking a question...")
    query_msg = await query_agent.send(
        IntentType.QUERY,
        "broadcast",
        {"query": "What are the key factors in real estate investment?"}
    )
    
    await asyncio.sleep(3)
    
    # Evaluator evaluates the query
    print("\n📊 Evaluator evaluating the query...")
    eval_msg = await evaluator.send(
        IntentType.EVALUATE,
        query_agent.agent_id,
        {
            "target": query_msg.id,
            "criteria": ["relevance", "clarity"],
            "scores": {},
        }
    )
    
    print("\n💬 Agents are communicating... (Press Ctrl+C to stop)")
    try:
        await asyncio.sleep(30)
    except KeyboardInterrupt:
        print("\n\nStopping agents...")
    
    await evaluator.stop()
    await query_agent.stop()
    await ollama_client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

