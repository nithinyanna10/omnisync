"""
OmniSync Protocol (OSP) message definitions using Pydantic
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime
from uuid import uuid4
try:
    from pydantic import BaseModel, Field, validator
    PYDANTIC_V2 = False
except ImportError:
    from pydantic import BaseModel, Field
    from pydantic import field_validator as validator
    PYDANTIC_V2 = True


class IntentType(str, Enum):
    """Supported intent types"""
    QUERY = "query"
    PLAN = "plan"
    EXECUTE = "execute"
    REFLECT = "reflect"
    EVALUATE = "evaluate"
    NOTIFY = "notify"


class BaseMessage(BaseModel):
    """Base message structure for OSP"""
    
    type: str = "intent_message"
    version: str = "0.1"
    id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    
    class Config:
        use_enum_values = True


class IntentMessage(BaseMessage):
    """Core OSP intent message"""
    
    intent: IntentType
    from_agent: str = Field(..., alias="from")
    to_agent: str = Field(..., alias="to")
    metadata: Dict[str, Any] = {}
    content: Dict[str, Any] = {}
    context: Optional[Dict[str, Any]] = None
    attachments: List[Dict[str, Any]] = []
    signature: Optional[str] = None
    response_to: Optional[str] = None
    
    @validator("to_agent")
    def validate_to_agent(cls, v):
        if v not in ["broadcast"] and not isinstance(v, str):
            raise ValueError("to_agent must be a string or 'broadcast'")
        return v
    
    class Config:
        allow_population_by_field_name = True


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
        IntentType.REFLECT: ReflectIntent,
        IntentType.EVALUATE: EvaluateIntent,
        IntentType.NOTIFY: NotifyIntent,
    }
    
    msg_class = intent_classes.get(intent, IntentMessage)
    
    # Create message using field names (Pydantic will handle aliases)
    return msg_class(
        intent=intent,
        from_agent=from_agent,  # Use field name, alias is handled automatically
        to_agent=to_agent,
        content=content,
        metadata=metadata or {},
        context=context,
        attachments=attachments or [],
    )

