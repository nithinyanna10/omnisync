"""
Content type definitions for OmniSync Protocol
Structured content semantics for different message types
"""

from enum import Enum
from typing import Any, Dict, Optional, Union
from pydantic import BaseModel, Field


class ContentType(str, Enum):
    """Supported content types"""
    TEXT = "text"
    TEXT_RESPONSE = "text_response"
    JSON_DATA = "json_data"
    IMAGE = "image"
    EMBEDDING = "embedding"
    TOOL_CALL = "tool_call"
    ERROR = "error"


class TextContent(BaseModel):
    """Text content structure"""
    type: str = ContentType.TEXT
    data: str
    confidence: Optional[float] = None
    language: Optional[str] = None


class TextResponseContent(BaseModel):
    """Text response content structure"""
    type: str = ContentType.TEXT_RESPONSE
    data: str
    confidence: Optional[float] = None
    sources: Optional[list] = None


class JsonDataContent(BaseModel):
    """JSON data content structure"""
    type: str = ContentType.JSON_DATA
    data: Dict[str, Any]
    data_schema: Optional[str] = Field(None, alias="schema")  # Use alias to avoid shadowing


class ToolCallContent(BaseModel):
    """Tool call content structure"""
    type: str = ContentType.TOOL_CALL
    tool_name: str
    parameters: Dict[str, Any]
    result: Optional[Any] = None


class ErrorContent(BaseModel):
    """Error content structure"""
    type: str = ContentType.ERROR
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None


def create_content(
    content_type: ContentType,
    data: Any,
    **kwargs
) -> Dict[str, Any]:
    """Factory function to create structured content"""
    
    content_classes = {
        ContentType.TEXT: TextContent,
        ContentType.TEXT_RESPONSE: TextResponseContent,
        ContentType.JSON_DATA: JsonDataContent,
        ContentType.TOOL_CALL: ToolCallContent,
        ContentType.ERROR: ErrorContent,
    }
    
    content_class = content_classes.get(content_type)
    if content_class:
        if content_type == ContentType.TEXT:
            return TextContent(data=str(data), **kwargs).dict()
        elif content_type == ContentType.TEXT_RESPONSE:
            return TextResponseContent(data=str(data), **kwargs).dict()
        elif content_type == ContentType.JSON_DATA:
            return JsonDataContent(data=data if isinstance(data, dict) else {"value": data}, **kwargs).dict()
        elif content_type == ContentType.TOOL_CALL:
            return ToolCallContent(tool_name=kwargs.get("tool_name", ""), parameters=data if isinstance(data, dict) else {}, **kwargs).dict()
        elif content_type == ContentType.ERROR:
            return ErrorContent(error_code=kwargs.get("error_code", "UNKNOWN"), message=str(data), **kwargs).dict()
    
    # Fallback to simple dict
    return {"type": content_type.value, "data": data, **kwargs}


def normalize_content(content: Union[Dict[str, Any], str]) -> Dict[str, Any]:
    """Normalize content to structured format"""
    if isinstance(content, str):
        return create_content(ContentType.TEXT_RESPONSE, content)
    elif isinstance(content, dict):
        if "type" not in content:
            # Assume it's a text response if no type specified
            return create_content(ContentType.TEXT_RESPONSE, content.get("answer") or content.get("data") or str(content))
        return content
    else:
        return create_content(ContentType.TEXT_RESPONSE, str(content))

