"""
OmniSync Hub Client - Communication with OmniSync Hub
"""

import aiohttp
import logging
from typing import List, Optional, Dict, Any
from .protocol import IntentMessage

logger = logging.getLogger(__name__)


class HubClient:
    """Client for communicating with OmniSync Hub"""
    
    def __init__(self, hub_url: str = "http://localhost:8080", agent_id: str = "default"):
        self.hub_url = hub_url.rstrip("/")
        self.agent_id = agent_id
        self.session: Optional[aiohttp.ClientSession] = None
        self.ws: Optional[aiohttp.ClientWebSocketResponse] = None
    
    async def connect(self):
        """Connect to the hub"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        logger.info(f"Connected to hub at {self.hub_url}")
    
    async def disconnect(self):
        """Disconnect from the hub"""
        if self.ws:
            await self.ws.close()
            self.ws = None
        if self.session:
            await self.session.close()
            self.session = None
    
    async def send_message(self, message: IntentMessage) -> bool:
        """Send a message to the hub"""
        if not self.session:
            await self.connect()
        
        try:
            async with self.session.post(
                f"{self.hub_url}/api/messages",
                json=message.dict(by_alias=True),
            ) as response:
                if response.status == 200:
                    logger.debug(f"Message {message.id} sent successfully")
                    return True
                else:
                    logger.error(f"Failed to send message: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    async def get_messages(self, agent_id: Optional[str] = None) -> List[IntentMessage]:
        """Get pending messages for an agent"""
        if not self.session:
            await self.connect()
        
        target_id = agent_id or self.agent_id
        
        try:
            async with self.session.get(
                f"{self.hub_url}/api/messages/{target_id}",
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    messages = []
                    for msg_data in data.get("messages", []):
                        try:
                            msg = IntentMessage(**msg_data)
                            messages.append(msg)
                        except Exception as e:
                            logger.error(f"Error parsing message: {e}")
                    return messages
                else:
                    logger.error(f"Failed to get messages: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error getting messages: {e}")
            return []
    
    async def register_agent(self, agent_info: Dict[str, Any]) -> bool:
        """Register agent with the hub"""
        if not self.session:
            await self.connect()
        
        try:
            async with self.session.post(
                f"{self.hub_url}/api/agents/register",
                json=agent_info,
            ) as response:
                if response.status == 200:
                    logger.info(f"Agent {agent_info.get('agent_id')} registered")
                    return True
                else:
                    logger.error(f"Failed to register agent: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Error registering agent: {e}")
            return False
    
    async def get_agents(self) -> List[Dict[str, Any]]:
        """Get list of registered agents"""
        if not self.session:
            await self.connect()
        
        try:
            async with self.session.get(f"{self.hub_url}/api/agents") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("agents", [])
                else:
                    logger.error(f"Failed to get agents: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error getting agents: {e}")
            return []

