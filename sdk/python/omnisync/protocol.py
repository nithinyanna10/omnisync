"""
OmniSync Protocol (OSP) message definitions using Pydantic
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime
from uuid import uuid4
try:
    from pydantic import BaseModel, Field, validator, model_validator
    PYDANTIC_V2 = False
except ImportError:
    from pydantic import BaseModel, Field, model_validator
    from pydantic import field_validator as validator
    PYDANTIC_V2 = True


class IntentType(str, Enum):
    """Supported intent types - OmniIntent taxonomy"""
    QUERY = "query"      # Request info from another agent
    PLAN = "plan"        # Request multi-step goal reasoning
    ACT = "act"          # Perform a task
    EXECUTE = "execute"  # Execute a task (alias for act, maintained for compatibility)
    REFLECT = "reflect"  # Self-evaluate reasoning
    EVALUATE = "evaluate"  # Judge another agent's output
    NOTIFY = "notify"    # Passive update
    ACK = "ack"          # Protocol-level acknowledgment (C: New intent)


class BaseMessage(BaseModel):
    """Base message structure for OSP"""
    
    type: str = "intent_message"
    version: str = "0.1"
    schema_version: str = Field(default="osp-0.2", alias="schema_version")  # E: Schema v0.2
    id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    
    class Config:
        use_enum_values = True
        populate_by_name = True


class IntentMessage(BaseMessage):
    """Core OSP intent message"""
    
    intent: IntentType
    from_agent: str = Field(..., alias="from", serialization_alias="from")
    to_agent: str = Field(..., alias="to", serialization_alias="to")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    content: Dict[str, Any] = Field(default_factory=dict)
    context: Optional[Dict[str, Any]] = None
    attachments: List[Dict[str, Any]] = Field(default_factory=list)
    signature: Optional[str] = None
    response_to: Optional[str] = None
    
    @model_validator(mode='after')
    def set_default_metadata(self):
        """Set default metadata fields after initialization"""
        # Initialize metadata with default fields if not provided
        if not self.metadata:
            self.metadata = {}
        
        # Add hop_count and TTL for anti-loop mechanism if not present
        if "hop_count" not in self.metadata:
            self.metadata["hop_count"] = 0
        if "ttl" not in self.metadata:
            self.metadata["ttl"] = 3  # Default TTL of 3 hops
        
        return self
    
    def increment_hop(self) -> bool:
        """Increment hop count and check TTL. Returns False if TTL exceeded."""
        self.metadata["hop_count"] = self.metadata.get("hop_count", 0) + 1
        ttl = self.metadata.get("ttl", 3)
        if self.metadata["hop_count"] > ttl:
            return False
        return True
    
    @validator("to_agent")
    def validate_to_agent(cls, v):
        if v not in ["broadcast"] and not isinstance(v, str):
            raise ValueError("to_agent must be a string or 'broadcast'")
        return v
    
    class Config:
        # Pydantic v2 compatibility
        validate_by_name = True  # Allows using field names OR aliases
        populate_by_name = True  # Alias for validate_by_name


class QueryIntent(IntentMessage):
    """Query intent message"""
    
    intent: IntentType = IntentType.QUERY
    
    @validator("content")
    def validate_content(cls, v):
        if "query" not in v:
            raise ValueError("Query intent must include 'query' in content")
        return v


class PlanIntent(IntentMessage):
    """Plan intent message"""
    
    intent: IntentType = IntentType.PLAN
    
    @validator("content")
    def validate_content(cls, v):
        if "goal" not in v:
            raise ValueError("Plan intent must include 'goal' in content")
        return v


class ExecuteIntent(IntentMessage):
    """Execute intent message"""
    
    intent: IntentType = IntentType.EXECUTE
    
    @validator("content")
    def validate_content(cls, v):
        if "task" not in v:
            raise ValueError("Execute intent must include 'task' in content")
        return v


class ActIntent(IntentMessage):
    """Act intent message - perform a task"""
    
    intent: IntentType = IntentType.ACT
    
    @validator("content")
    def validate_content(cls, v):
        if "action" not in v and "task" not in v:
            raise ValueError("Act intent must include 'action' or 'task' in content")
        return v


class ReflectIntent(IntentMessage):
    """Reflect intent message"""
    
    intent: IntentType = IntentType.REFLECT
    
    @validator("content")
    def validate_content(cls, v):
        if "analysis" not in v:
            raise ValueError("Reflect intent must include 'analysis' in content")
        return v


class EvaluateIntent(IntentMessage):
    """Evaluate intent message"""
    
    intent: IntentType = IntentType.EVALUATE
    
    @validator("content")
    def validate_content(cls, v):
        if "target" not in v or "scores" not in v:
            raise ValueError("Evaluate intent must include 'target' and 'scores' in content")
        return v


class NotifyIntent(IntentMessage):
    """Notify intent message"""
    
    intent: IntentType = IntentType.NOTIFY
    
    @validator("content")
    def validate_content(cls, v):
        if "event" not in v:
            raise ValueError("Notify intent must include 'event' in content")
        return v


class AckIntent(IntentMessage):
    """Acknowledgment intent message - protocol-level ACK (C: New intent)"""
    
    intent: IntentType = IntentType.ACK
    
    @validator("content")
    def validate_content(cls, v):
        if "received" not in v:
            raise ValueError("Ack intent must include 'received' in content")
        return v


class ErrorMessage(BaseMessage):
    """Error message structure"""
    
    type: str = "error_message"
    error_code: str
    message: str
    original_message_id: Optional[str] = None


def create_intent_message(
    intent: IntentType,
    from_agent: str,
    to_agent: str,
    content: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None,
    context: Optional[Dict[str, Any]] = None,
    attachments: Optional[List[Dict[str, Any]]] = None,
) -> IntentMessage:
    """Factory function to create intent messages"""
    
    intent_classes = {
        IntentType.QUERY: QueryIntent,
        IntentType.PLAN: PlanIntent,
        IntentType.EXECUTE: ExecuteIntent,
        IntentType.ACT: ActIntent,
        IntentType.REFLECT: ReflectIntent,
        IntentType.EVALUATE: EvaluateIntent,
        IntentType.NOTIFY: NotifyIntent,
        IntentType.ACK: AckIntent,  # C: Acknowledgment intent
    }
    
    msg_class = intent_classes.get(intent, IntentMessage)
    
    # Create message - use field names with populate_by_name=True
    # This allows us to use from_agent/to_agent even though aliases are "from"/"to"
    try:
        return msg_class(
            intent=intent,
            from_agent=from_agent,
            to_agent=to_agent,
            content=content,
            metadata=metadata or {},
            context=context,
            attachments=attachments or [],
        )
    except Exception as e:
        # Fallback: try using aliases directly if field names don't work
        try:
            return msg_class(
                intent=intent,
                **{"from": from_agent, "to": to_agent},
                content=content,
                metadata=metadata or {},
                context=context,
                attachments=attachments or [],
            )
        except:
            raise e

