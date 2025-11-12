"""
OmniSync Agent - Core agent implementation
"""

import asyncio
import logging
from typing import Any, Callable, Dict, Optional
from .protocol import IntentMessage, IntentType, create_intent_message
from .hub_client import HubClient

logger = logging.getLogger(__name__)


class Agent:
    """OmniSync Agent - can send and receive OSP messages"""
    
    def __init__(
        self,
        name: str,
        framework: str = "OmniSync",
        hub_url: str = "http://localhost:8080",
        model: Optional[str] = None,
        capabilities: Optional[list] = None,
    ):
        self.name = name
        self.framework = framework
        self.agent_id = f"{framework.lower()}_{name}"
        self.hub_client = HubClient(hub_url=hub_url, agent_id=self.agent_id)
        self.model = model
        self.capabilities = capabilities or []
        self.handlers: Dict[IntentType, Callable] = {}
        self.running = False
        
    def on(self, intent: str):
        """Decorator to register intent handlers"""
        def decorator(func: Callable):
            intent_type = IntentType(intent)
            self.handlers[intent_type] = func
            return func
        return decorator
    
    async def handle_message(self, message: IntentMessage) -> Optional[IntentMessage]:
        """Handle incoming message"""
        handler = self.handlers.get(message.intent)
        if handler:
            try:
                result = await handler(message) if asyncio.iscoroutinefunction(handler) else handler(message)
                if isinstance(result, dict):
                    # Create response message
                    response = create_intent_message(
                        intent=message.intent,
                        from_agent=self.agent_id,
                        to_agent=message.from_agent,
                        content=result,
                        metadata={
                            "framework": self.framework,
                            "model": self.model,
                            "capabilities": self.capabilities,
                        },
                    )
                    response.response_to = message.id
                    return response
                elif isinstance(result, IntentMessage):
                    return result
            except Exception as e:
                logger.error(f"Error handling message {message.id}: {e}")
                return None
        else:
            logger.warning(f"No handler for intent {message.intent}")
        return None
    
    async def send(
        self,
        intent: IntentType,
        to_agent: str,
        content: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> IntentMessage:
        """Send an intent message"""
        message = create_intent_message(
            intent=intent,
            from_agent=self.agent_id,
            to_agent=to_agent,
            content=content,
            metadata=metadata or {
                "framework": self.framework,
                "model": self.model,
                "capabilities": self.capabilities,
            },
            context=context,
        )
        await self.hub_client.send_message(message)
        return message
    
    async def broadcast(
        self,
        intent: IntentType,
        content: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> IntentMessage:
        """Broadcast message to all agents"""
        return await self.send(intent, "broadcast", content, metadata)
    
    async def start(self):
        """Start the agent and begin listening for messages"""
        self.running = True
        await self.hub_client.connect()
        logger.info(f"Agent {self.agent_id} started")
        
        # Register agent with hub
        agent_info = {
            "agent_id": self.agent_id,
            "name": self.name,
            "framework": self.framework,
            "capabilities": self.capabilities or [],
        }
        if self.model:
            agent_info["model"] = self.model
        
        success = await self.hub_client.register_agent(agent_info)
        if not success:
            logger.warning(f"Failed to register agent {self.agent_id}, but continuing...")
        
        # Start message listener
        asyncio.create_task(self._message_loop())
    
    async def _message_loop(self):
        """Continuously listen for messages"""
        while self.running:
            try:
                messages = await self.hub_client.get_messages(self.agent_id)
                for message in messages:
                    response = await self.handle_message(message)
                    if response:
                        await self.hub_client.send_message(response)
                await asyncio.sleep(0.1)  # Small delay to prevent busy waiting
            except Exception as e:
                logger.error(f"Error in message loop: {e}")
                await asyncio.sleep(1)
    
    async def stop(self):
        """Stop the agent"""
        self.running = False
        try:
            await self.hub_client.disconnect()
        except Exception as e:
            logger.error(f"Error disconnecting: {e}")
        logger.info(f"Agent {self.agent_id} stopped")


# Convenience functions
async def send_intent(
    intent: IntentType,
    from_agent: str,
    to_agent: str,
    content: Dict[str, Any],
    hub_url: str = "http://localhost:8080",
) -> IntentMessage:
    """Send an intent message directly"""
    client = HubClient(hub_url=hub_url, agent_id=from_agent)
    await client.connect()
    message = create_intent_message(intent, from_agent, to_agent, content)
    await client.send_message(message)
    await client.disconnect()
    return message


async def broadcast_intent(
    intent: IntentType,
    from_agent: str,
    content: Dict[str, Any],
    hub_url: str = "http://localhost:8080",
) -> IntentMessage:
    """Broadcast an intent message"""
    return await send_intent(intent, from_agent, "broadcast", content, hub_url)

