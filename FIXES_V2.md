# Pydantic v2 Compatibility Fixes

## Issue
Pydantic v2 validation errors when creating messages - `from` and `to` fields were required but missing.

## Root Cause
- Pydantic v2 changed how field aliases work
- The `allow_population_by_field_name` config option was deprecated
- Need to use `validate_by_name = True` instead

## Fixes Applied

### 1. Updated Config Class
Changed from:
```python
class Config:
    allow_population_by_field_name = True
```

To:
```python
class Config:
    validate_by_name = True  # Pydantic v2
    populate_by_name = True  # Alias
```

### 2. Added Fallback in create_intent_message()
If field names don't work, try using aliases directly:
```python
try:
    return msg_class(from_agent=..., to_agent=...)
except:
    return msg_class(**{"from": ..., "to": ...})
```

### 3. Improved Agent Cleanup
- Added delay before disconnecting to let message loop finish
- Better error handling for session cleanup

## Testing

The fix has been tested and works:
```bash
cd sdk/python
source venv/bin/activate
python3 -c "from omnisync.protocol import create_intent_message, IntentType; msg = create_intent_message(IntentType.QUERY, 'agent1', 'agent2', {'query': 'test'}); print('✅ Success!')"
```

## Files Modified
- `sdk/python/omnisync/protocol.py` - Fixed Pydantic v2 compatibility
- `sdk/python/omnisync/agent.py` - Improved cleanup

