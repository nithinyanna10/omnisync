"""
OmniSync Python SDK - Interoperability layer for AI agent frameworks
"""

from .protocol import (
    IntentMessage,
    QueryIntent,
    PlanIntent,
    ExecuteIntent,
    ReflectIntent,
    EvaluateIntent,
    NotifyIntent,
    ErrorMessage,
    IntentType,
)
from .agent import Agent, send_intent, broadcast_intent
from .hub_client import HubClient
from .adapters import (
    LangChainAdapter,
    AutoGenAdapter,
    CrewAIAdapter,
    LlamaIndexAdapter,
)

__version__ = "0.1.0"
__all__ = [
    "IntentMessage",
    "QueryIntent",
    "PlanIntent",
    "ExecuteIntent",
    "ReflectIntent",
    "EvaluateIntent",
    "NotifyIntent",
    "ErrorMessage",
    "IntentType",
    "Agent",
    "send_intent",
    "broadcast_intent",
    "HubClient",
    "LangChainAdapter",
    "AutoGenAdapter",
    "CrewAIAdapter",
    "LlamaIndexAdapter",
]

