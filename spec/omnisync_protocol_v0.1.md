# OmniSync Protocol (OSP) v0.1

## Overview

The OmniSync Protocol (OSP) is a JSON-based message specification that enables interoperability between different AI agent frameworks. It provides a standardized communication layer for agents built with LangChain, AutoGen, CrewAI, LlamaIndex, and other frameworks.

## Core Principles

1. **Framework Agnostic**: Works with any agent framework
2. **Intent-Based**: Messages express clear intents (query, plan, execute, reflect, evaluate)
3. **Extensible**: Supports custom metadata, attachments, and context
4. **Verifiable**: Optional message signatures for authentication
5. **Observable**: Rich metadata for logging and visualization

## Message Schema

### Base Message Structure

All OSP messages follow this base structure:

```json
{
  "type": "intent_message",
  "version": "0.1",
  "id": "unique-message-id",
  "intent": "query|plan|execute|reflect|evaluate|notify",
  "from": "agent_id",
  "to": "agent_id|broadcast",
  "timestamp": "2025-11-12T18:20:00Z",
  "metadata": {},
  "content": {},
  "context": {},
  "attachments": [],
  "signature": null
}
```

### Field Definitions

#### `type` (string, required)
- Must be `"intent_message"` for OSP v0.1

#### `version` (string, required)
- Protocol version: `"0.1"`

#### `id` (string, required)
- Unique message identifier (UUID v4 recommended)

#### `intent` (string, required)
- One of: `query`, `plan`, `execute`, `reflect`, `evaluate`, `notify`
- Defines the purpose of the message

#### `from` (string, required)
- Source agent identifier
- Format: `{framework}_{agent_name}_{instance_id}` (e.g., `langchain_agent_1`)

#### `to` (string, required)
- Target agent identifier or `"broadcast"` for multi-cast

#### `timestamp` (string, required)
- ISO 8601 UTC timestamp

#### `metadata` (object, required)
- Framework information and capabilities
- Example:
```json
{
  "framework": "LangChain",
  "model": "GPT-4o-mini",
  "capabilities": ["query", "plan"],
  "version": "0.1.0"
}
```

#### `content` (object, required)
- Primary message payload
- Structure varies by intent (see Intent Specifications)

#### `context` (object, optional)
- Relevant memory, conversation history, or state
- Example:
```json
{
  "conversation_id": "conv_123",
  "previous_messages": ["msg_1", "msg_2"],
  "memory": {"key": "value"}
}
```

#### `attachments` (array, optional)
- Additional data: embeddings, files, code snippets
- Example:
```json
[
  {
    "type": "embedding",
    "data": [0.1, 0.2, ...],
    "model": "text-embedding-ada-002"
  },
  {
    "type": "file",
    "url": "https://...",
    "mime_type": "application/pdf"
  }
]
```

#### `signature` (string, optional)
- Cryptographic signature or embedding fingerprint
- Format: `{algorithm}:{hash}` (e.g., `sha256:abc123...`)

## Intent Specifications

### 1. Query Intent

Request information or answer a question.

```json
{
  "intent": "query",
  "content": {
    "query": "Retrieve lease clauses for building X",
    "parameters": {},
    "expected_format": "json|text|structured"
  }
}
```

### 2. Plan Intent

Request or share a plan of action.

```json
{
  "intent": "plan",
  "content": {
    "goal": "Summarize today's financial news",
    "steps": [
      {"action": "fetch_data", "params": {}},
      {"action": "analyze", "params": {}}
    ],
    "priority": "high|medium|low"
  }
}
```

### 3. Execute Intent

Request execution of a task or action.

```json
{
  "intent": "execute",
  "content": {
    "task": "fetch_data",
    "parameters": {"source": "api", "endpoint": "/news"},
    "timeout": 30
  }
}
```

### 4. Reflect Intent

Share analysis, reasoning, or reflection.

```json
{
  "intent": "reflect",
  "content": {
    "analysis": "The plan is sound but may need optimization",
    "reasoning": "...",
    "confidence": 0.85
  }
}
```

### 5. Evaluate Intent

Provide evaluation or feedback.

```json
{
  "intent": "evaluate",
  "content": {
    "target": "plan_id_or_message_id",
    "criteria": ["quality", "feasibility"],
    "scores": {"quality": 0.9, "feasibility": 0.8},
    "feedback": "Plan quality: good, proceed."
  }
}
```

### 6. Notify Intent

Send notifications or status updates.

```json
{
  "intent": "notify",
  "content": {
    "event": "task_completed|error|status_update",
    "message": "Task completed successfully",
    "data": {}
  }
}
```

## Response Messages

Responses follow the same structure but include a `response_to` field:

```json
{
  "type": "intent_message",
  "intent": "query",
  "response_to": "original-message-id",
  "from": "agent_b",
  "to": "agent_a",
  "content": {
    "answer": "Building X has 15 lease clauses...",
    "sources": ["doc_1", "doc_2"]
  }
}
```

## Error Messages

Errors use a special structure:

```json
{
  "type": "error_message",
  "version": "0.1",
  "id": "error-id",
  "error_code": "INVALID_INTENT|AGENT_NOT_FOUND|TIMEOUT",
  "message": "Human-readable error description",
  "original_message_id": "msg-id",
  "timestamp": "2025-11-12T18:20:00Z"
}
```

## Message Routing

- **Direct**: `to` field specifies exact agent ID
- **Broadcast**: `to: "broadcast"` sends to all subscribed agents
- **Topic-based**: Future extension (e.g., `to: "topic:financial_analysis"`)

## Security Considerations

1. **Message Signatures**: Optional but recommended for production
2. **Agent Authentication**: Hub should verify agent identities
3. **Content Validation**: SDKs should validate all message schemas
4. **Rate Limiting**: Hub should enforce rate limits per agent

## Versioning

- Protocol versions follow semantic versioning (MAJOR.MINOR.PATCH)
- Breaking changes increment MAJOR version
- New intents or optional fields increment MINOR version
- Bug fixes increment PATCH version

## Future Extensions

- Topic-based routing
- Message encryption
- Streaming responses
- Multi-hop routing
- Agent discovery protocol

