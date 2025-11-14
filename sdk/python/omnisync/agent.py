"""
OmniSync Agent - Core agent implementation
"""

import asyncio
import logging
from typing import Any, Callable, Dict, Optional
from .protocol import IntentMessage, IntentType, create_intent_message
from .hub_client import HubClient
from .content_types import normalize_content, ContentType

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
        session_id: Optional[str] = None,
        trace_id: Optional[str] = None,
    ):
        self.name = name
        self.framework = framework
        self.agent_id = f"{framework.lower()}_{name}"
        self.hub_client = HubClient(hub_url=hub_url, agent_id=self.agent_id)
        self.model = model
        self.capabilities = capabilities or []
        self.handlers: Dict[IntentType, Callable] = {}
        self.running = False
        
        # Session and trace tracking - set at initialization
        import time
        from datetime import datetime
        self.default_session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.default_trace_id = trace_id or f"trace_{time.time()}"
        
    def on(self, intent: str):
        """Decorator to register intent handlers"""
        def decorator(func: Callable):
            intent_type = IntentType(intent)
            self.handlers[intent_type] = func
            return func
        return decorator
    
    async def handle_message(self, message: IntentMessage) -> Optional[IntentMessage]:
        """Handle incoming message"""
        # Anti-loop mechanism: Check TTL and hop count
        if not message.increment_hop():
            logger.warning(f"Message {message.id} exceeded TTL (hops: {message.metadata.get('hop_count')}, TTL: {message.metadata.get('ttl')}), dropping")
            return None
        
        # Skip processing if this is a response to our message (to avoid loops)
        if message.response_to:
            logger.debug(f"Received response message {message.id} (response to {message.response_to}), skipping handler")
            return None
        
        handler = self.handlers.get(message.intent)
        if handler:
            try:
                result = await handler(message) if asyncio.iscoroutinefunction(handler) else handler(message)
                if isinstance(result, dict):
                    # Normalize content to structured format
                    normalized_content = normalize_content(result)
                    
                    import time
                    import psutil
                    response_start = time.time()
                    
                    # Enhanced metadata with diagnostics - propagate session/trace
                    response_metadata = {
                        "framework": self.framework,
                        "framework_version": "0.1.0",
                        "model": self.model,
                        "capabilities": self.capabilities,
                        "hop_count": 0,  # Reset hop count for response
                        "ttl": message.metadata.get("ttl", 3),
                        "session_id": message.metadata.get("session_id") or self.default_session_id,  # A: Propagate session
                        "trace_id": message.metadata.get("trace_id") or self.default_trace_id,  # A: Propagate trace
                        "parent_message_id": message.id,
                        # D: System metrics
                        "cpu_usage": psutil.cpu_percent(interval=0.1),
                        "mem_usage": psutil.virtual_memory().percent,
                    }
                    
                    # Add latency if available
                    if "latency_ms" in message.metadata:
                        response_metadata["latency_ms"] = message.metadata.get("latency_ms")
                    
                    response_time_ms = int((time.time() - response_start) * 1000)
                    response_metadata["response_time_ms"] = response_time_ms
                    
                    response = IntentMessage(
                        intent=message.intent,  # Keep same intent for tracking
                        from_agent=self.agent_id,
                        to_agent=message.from_agent,
                        content=normalized_content,  # Use normalized structured content
                        metadata=response_metadata,
                    )
                    response.response_to = message.id
                    return response
                elif isinstance(result, IntentMessage):
                    return result
            except Exception as e:
                logger.error(f"Error handling message {message.id}: {e}")
                return None
        else:
            logger.debug(f"No handler for intent {message.intent} (this is normal for response messages)")
        return None
    
    async def send(
        self,
        intent: IntentType,
        to_agent: str,
        content: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        trace_id: Optional[str] = None,
    ) -> IntentMessage:
        """Send an intent message with enhanced metadata"""
        import time
        import psutil
        start_time = time.time()
        
        # Use provided session/trace IDs or fall back to agent defaults
        final_session_id = session_id or self.default_session_id
        final_trace_id = trace_id or self.default_trace_id
        
        # Enhanced metadata with diagnostics
        enhanced_metadata = {
            "framework": self.framework,
            "framework_version": "0.1.0",  # D: Framework version
            "model": self.model,
            "capabilities": self.capabilities,
            "hop_count": 0,
            "ttl": 3,
            "session_id": final_session_id,
            "trace_id": final_trace_id,
            # D: System metrics
            "cpu_usage": psutil.cpu_percent(interval=0.1),
            "mem_usage": psutil.virtual_memory().percent,
        }
        
        if metadata:
            enhanced_metadata.update(metadata)
        
        message = create_intent_message(
            intent=intent,
            from_agent=self.agent_id,
            to_agent=to_agent,
            content=content,
            metadata=enhanced_metadata,
            context=context,
        )
        
        # Calculate latency after sending
        latency_ms = int((time.time() - start_time) * 1000)
        message.metadata["latency_ms"] = latency_ms
        message.metadata["response_time_ms"] = latency_ms  # D: Response time
        
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
        processed_message_ids = set()  # Track processed messages to avoid duplicates
        while self.running:
            try:
                messages = await self.hub_client.get_messages(self.agent_id)
                for message in messages:
                    # Skip if already processed
                    if message.id in processed_message_ids:
                        continue
                    processed_message_ids.add(message.id)
                    
                    # Only process messages that are not responses (responses are handled differently)
                    if not message.response_to:
                        response = await self.handle_message(message)
                        if response:
                            await self.hub_client.send_message(response)
                    else:
                        # Log response messages but don't process them through handlers
                        logger.debug(f"Received response {message.id} from {message.from_agent}")
                
                # Clean up old processed IDs to prevent memory growth
                if len(processed_message_ids) > 1000:
                    processed_message_ids.clear()
                    
                await asyncio.sleep(0.5)  # Increased delay to reduce polling frequency
            except Exception as e:
                logger.error(f"Error in message loop: {e}")
                await asyncio.sleep(1)
    
    async def stop(self):
        """Stop the agent (B: Proper session cleanup)"""
        self.running = False
        # Give message loop time to finish
        await asyncio.sleep(0.5)
        
        # Properly close hub client session
        try:
            await self.hub_client.disconnect()
        except Exception as e:
            logger.error(f"Error disconnecting hub client: {e}")
        
        # Additional cleanup - ensure all pending tasks complete
        await asyncio.sleep(0.2)
        
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

