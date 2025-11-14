"""
Ollama integration for OmniSync agents
"""

import aiohttp
import json
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for interacting with Ollama API"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "gpt-oss:120b-cloud"):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def connect(self):
        """Initialize HTTP session"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def disconnect(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def generate(self, prompt: str, stream: bool = False) -> str:
        """Generate text using Ollama (B: Fixed session handling)"""
        # B: Use context manager for proper session cleanup
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": stream,
                    },
                ) as response:
                    if response.status == 200:
                        if stream:
                            full_response = ""
                            async for line in response.content:
                                if line:
                                    try:
                                        data = json.loads(line)
                                        if "response" in data:
                                            full_response += data["response"]
                                    except json.JSONDecodeError:
                                        continue
                            return full_response
                        else:
                            # Handle text/plain responses
                            content_type = response.headers.get('Content-Type', '')
                            if 'application/json' in content_type:
                                data = await response.json()
                                return data.get("response", "")
                            else:
                                # Fallback for text/plain responses
                                text = await response.text()
                                try:
                                    data = json.loads(text)
                                    return data.get("response", text)
                                except:
                                    return text
                    else:
                        error_text = await response.text()
                        logger.error(f"Ollama API error: {response.status}, {error_text}")
                        return ""
            except aiohttp.ClientError as e:
                logger.error(f"Ollama connection error: {e}")
                return ""
            except Exception as e:
                logger.error(f"Error calling Ollama: {e}")
                return ""
    
    async def chat(self, messages: list, stream: bool = False) -> str:
        """Chat with Ollama using messages format (B: Fixed session handling)"""
        # B: Use context manager for proper session cleanup
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": stream,
                    },
                ) as response:
                    if response.status == 200:
                        if stream:
                            full_response = ""
                            async for line in response.content:
                                if line:
                                    try:
                                        data = json.loads(line)
                                        if "message" in data and "content" in data["message"]:
                                            full_response += data["message"]["content"]
                                    except json.JSONDecodeError:
                                        continue
                            return full_response
                        else:
                            content_type = response.headers.get('Content-Type', '')
                            if 'application/json' in content_type:
                                data = await response.json()
                                return data.get("message", {}).get("content", "")
                            else:
                                text = await response.text()
                                try:
                                    data = json.loads(text)
                                    return data.get("message", {}).get("content", text)
                                except:
                                    return text
                    else:
                        error_text = await response.text()
                        logger.error(f"Ollama API error: {response.status}, {error_text}")
                        return ""
            except aiohttp.ClientError as e:
                logger.error(f"Ollama connection error: {e}")
                return ""
            except Exception as e:
                logger.error(f"Error calling Ollama: {e}")
                return ""


def create_ollama_agent_handler(ollama_client: OllamaClient, system_prompt: Optional[str] = None):
    """Create an agent handler that uses Ollama for reasoning"""
    
    async def handler(message, intent_type: str = "query"):
        """Generic handler that uses Ollama to process messages"""
        content = message.content
        
        if intent_type == "query":
            query = content.get("query", "")
            prompt = f"{system_prompt or 'You are a helpful AI assistant.'}\n\nQuery: {query}\n\nAnswer:"
            response = await ollama_client.generate(prompt)
            return {"answer": response}
        
        elif intent_type == "reflect":
            context = content.get("context", "")
            prompt = f"{system_prompt or 'You are a reflective AI assistant.'}\n\nContext: {context}\n\nAnalysis:"
            response = await ollama_client.generate(prompt)
            return {"analysis": response, "confidence": 0.85}
        
        elif intent_type == "evaluate":
            target = content.get("target", "")
            criteria = content.get("criteria", [])
            prompt = f"{system_prompt or 'You are an evaluator AI.'}\n\nTarget: {target}\n\nCriteria: {criteria}\n\nEvaluation:"
            response = await ollama_client.generate(prompt)
            return {"scores": {"quality": 0.9}, "feedback": response}
        
        else:
            # Generic handler
            prompt = f"{system_prompt or 'You are a helpful AI assistant.'}\n\nTask: {content}\n\nResponse:"
            response = await ollama_client.generate(prompt)
            return {"response": response}
    
    return handler

