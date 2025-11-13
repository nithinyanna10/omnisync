"""
JSON Schema validation for OmniSync Protocol messages
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import jsonschema
from jsonschema import validate, ValidationError


def load_schema(version: str = "0.1") -> Dict[str, Any]:
    """Load JSON schema for OSP"""
    schema_path = Path(__file__).parent.parent.parent.parent / "spec" / "schema" / f"osp-{version}.json"
    
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    
    with open(schema_path, 'r') as f:
        return json.load(f)


def validate_message(message: Dict[str, Any], schema_version: str = "0.1") -> tuple[bool, Optional[str]]:
    """
    Validate a message against OSP schema
    
    Returns:
        (is_valid, error_message)
    """
    try:
        schema = load_schema(schema_version)
        # Convert message dict to use "from" and "to" aliases if needed
        validated_msg = message.copy()
        if "from_agent" in validated_msg and "from" not in validated_msg:
            validated_msg["from"] = validated_msg.pop("from_agent")
        if "to_agent" in validated_msg and "to" not in validated_msg:
            validated_msg["to"] = validated_msg.pop("to_agent")
        
        validate(instance=validated_msg, schema=schema)
        return True, None
    except ValidationError as e:
        return False, f"Validation error: {e.message} at {'.'.join(str(p) for p in e.path)}"
    except Exception as e:
        return False, f"Error loading schema: {str(e)}"


def validate_message_dict(message_dict: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """Validate message dict, auto-detecting schema version"""
    schema_version = message_dict.get("schema_version", "osp-0.1")
    if schema_version.startswith("osp-"):
        version = schema_version.replace("osp-", "")
    else:
        version = "0.1"
    
    return validate_message(message_dict, version)

