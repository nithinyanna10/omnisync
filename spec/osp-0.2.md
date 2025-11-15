# OmniSync Protocol (OSP) v0.2

## Abstract

This document specifies the OmniSync Protocol (OSP), a JSON-based message specification that enables interoperability between different AI agent frameworks. OSP provides a standardized communication layer for agents built with LangChain, AutoGen, CrewAI, LlamaIndex, and other frameworks, enabling cross-framework collaboration and message routing.

## Status of This Memo

This is an experimental protocol specification. It is published for review and comment.

## 1. Introduction

### 1.1. Purpose

The OmniSync Protocol (OSP) defines a standardized message format for inter-agent communication, enabling:

- Framework-agnostic agent interoperability
- Intent-based message routing
- Session and trace tracking
- Rich metadata for observability
- Protocol-level acknowledgments

### 1.2. Scope

This specification covers:
- Message structure and field definitions
- Intent taxonomy
- Content type definitions
- Metadata schema
- Session and trace tracking
- Schema validation

## 2. Message Structure

### 2.1. Base Message Format

All OSP messages follow this base structure:

```json
{
  "type": "intent_message",
  "version": "0.1",
  "schema_version": "osp-0.2",
  "id": "unique-message-id",
  "timestamp": "2025-11-13T10:00:00Z",
  "intent": "query|plan|act|execute|reflect|evaluate|notify|ack",
  "from": "agent_id",
  "to": "agent_id|broadcast",
  "metadata": {},
  "content": {},
  "context": {},
  "attachments": [],
  "signature": null,
  "response_to": null
}
```

### 2.2. Required Fields

- `type` (string): Must be `"intent_message"` for OSP v0.2
- `version` (string): Protocol version `"0.1"`
- `schema_version` (string): Schema version `"osp-0.2"`
- `id` (string): Unique message identifier (UUID v4 recommended)
- `timestamp` (string): ISO 8601 UTC timestamp
- `intent` (string): One of the supported intent types (see Section 3)
- `from` (string): Source agent identifier
- `to` (string): Target agent identifier or `"broadcast"`

### 2.3. Optional Fields

- `metadata` (object): Framework information and diagnostics (see Section 4)
- `content` (object): Primary message payload (see Section 5)
- `context` (object): Relevant memory, conversation history, or state
- `attachments` (array): Additional data attachments
- `signature` (string): Optional message signature for authentication
- `response_to` (string): ID of message this is responding to

## 3. Intent Taxonomy

OSP defines the following intent types:

### 3.1. Query Intent

Request information from another agent.

**Content Requirements:**
- Must include `query` field

**Example:**
```json
{
  "intent": "query",
  "content": {
    "query": "What is the current status of the data processing pipeline?",
    "type": "text"
  }
}
```

### 3.2. Plan Intent

Request multi-step goal reasoning.

**Content Requirements:**
- Must include `goal` field

**Example:**
```json
{
  "intent": "plan",
  "content": {
    "goal": "Extract and analyze data from PDF documents",
    "steps": []
  }
}
```

### 3.3. Act Intent

Perform a task or action.

**Content Requirements:**
- Must include `action` or `task` field

**Example:**
```json
{
  "intent": "act",
  "content": {
    "action": "process_data_batch",
    "parameters": {
      "batch_id": "batch_001",
      "source": "data_warehouse"
    }
  }
}
```

### 3.4. Execute Intent

Execute a specific task (alias for act, maintained for compatibility).

**Content Requirements:**
- Must include `task` field

### 3.5. Reflect Intent

Self-evaluate reasoning or analysis.

**Content Requirements:**
- Must include `analysis` field

**Example:**
```json
{
  "intent": "reflect",
  "content": {
    "analysis": "The approach was effective but could be optimized",
    "confidence": 0.85
  }
}
```

### 3.6. Evaluate Intent

Judge another agent's output.

**Content Requirements:**
- Must include `target` and `scores` fields

**Example:**
```json
{
  "intent": "evaluate",
  "content": {
    "target": "message_id_123",
    "scores": {
      "quality": 0.9,
      "accuracy": 0.95
    },
    "feedback": "High quality output"
  }
}
```

### 3.7. Notify Intent

Send notifications or status updates.

**Content Requirements:**
- Must include `event` field

**Example:**
```json
{
  "intent": "notify",
  "content": {
    "event": "pipeline_status_update",
    "message": "Data processing completed successfully"
  }
}
```

### 3.8. ACK Intent (v0.2)

Protocol-level acknowledgment.

**Content Requirements:**
- Must include `received` field

**Example:**
```json
{
  "intent": "ack",
  "content": {
    "received": true,
    "response_to": "message_id_123"
  }
}
```

## 4. Metadata Schema

### 4.1. Standard Metadata Fields

```json
{
  "metadata": {
    "framework": "OmniSync",
    "framework_version": "0.1.0",
    "model": "gpt-oss:120b-cloud",
    "capabilities": ["query", "plan", "act"],
    "hop_count": 0,
    "ttl": 3,
    "latency_ms": 45,
    "response_time_ms": 150,
    "token_usage": 123,
    "token_count": 123,
    "cpu_usage": 25.5,
    "mem_usage": 60.2,
    "session_id": "session_20251113_100000",
    "trace_id": "trace_1734172800.123",
    "parent_message_id": "msg_123"
  }
}
```

### 4.2. Field Descriptions

- `framework` (string): Agent framework name
- `framework_version` (string): Framework version (v0.2)
- `model` (string, optional): LLM model identifier
- `capabilities` (array): List of supported intents
- `hop_count` (integer): Number of hops message has taken (anti-loop)
- `ttl` (integer): Time-to-live in hops (default: 3)
- `latency_ms` (integer, optional): Message processing latency
- `response_time_ms` (integer, optional): Response generation time (v0.2)
- `token_usage` (integer, optional): Token count for LLM operations
- `token_count` (integer, optional): Alternative token count field (v0.2)
- `cpu_usage` (number, optional): CPU usage percentage (v0.2)
- `mem_usage` (number, optional): Memory usage percentage (v0.2)
- `session_id` (string, optional): Conversation session identifier (v0.2)
- `trace_id` (string, optional): Request trace identifier for threading (v0.2)
- `parent_message_id` (string, optional): ID of parent message in thread

## 5. Content Types

### 5.1. Supported Content Types

- `text`: Plain text content
- `text_response`: Text response with confidence/sources
- `json_data`: Structured JSON data
- `image`: Image data reference
- `embedding`: Vector embedding data
- `tool_call`: Tool/function call
- `error`: Error information
- `metrics`: Performance metrics (v0.2)

### 5.2. Structured Content Example

```json
{
  "content": {
    "type": "text_response",
    "data": "I am Agent A responding via OmniSync!",
    "confidence": 0.98,
    "sources": ["doc1", "doc2"]
  }
}
```

## 6. Session and Trace Tracking (v0.2)

### 6.1. Session ID

Session IDs group related messages within a conversation. Generated at agent initialization:

```
session_{YYYYMMDD}_{HHMMSS}
```

### 6.2. Trace ID

Trace IDs track request flows across agents:

```
trace_{timestamp}
```

### 6.3. Propagation

Session and trace IDs are:
- Generated at agent initialization
- Automatically propagated through all messages
- Included in message metadata
- Used for conversation threading

## 7. Anti-Loop Mechanism

### 7.1. Hop Count

Messages include a `hop_count` in metadata, incremented on each forward.

### 7.2. TTL (Time-To-Live)

Messages include a `ttl` (default: 3) in metadata. Messages exceeding TTL are dropped.

### 7.3. Implementation

```python
if message.metadata["hop_count"] > message.metadata["ttl"]:
    # Drop message
    return None
```

## 8. Schema Validation

### 8.1. JSON Schema

OSP v0.2 messages must validate against `osp-0.2.json` schema.

### 8.2. Validation Tools

- Python: `omnisync.validation.validate_message()`
- JavaScript: JSON Schema validator

## 9. Security Considerations

### 9.1. Message Signatures

Optional `signature` field for message authentication.

### 9.2. Agent Authentication

Agents must register with the Hub before sending messages.

## 10. IANA Considerations

This document has no IANA actions.

## 11. References

### 11.1. Normative References

- [RFC8259] JSON
- [RFC3339] Date and Time on the Internet

### 11.2. Informative References

- OmniSync Hub: https://github.com/nithinyanna10/omnisync
- JSON Schema: https://json-schema.org/

## 12. Author Information

OmniSync Protocol Specification v0.2

## Appendix A. Example Messages

### A.1. Complete Query Message

```json
{
  "type": "intent_message",
  "version": "0.1",
  "schema_version": "osp-0.2",
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-11-13T10:00:00Z",
  "intent": "query",
  "from": "omnisync_DataAnalyst",
  "to": "omnisync_TaskExecutor",
  "metadata": {
    "framework": "OmniSync",
    "framework_version": "0.1.0",
    "model": "gpt-oss:120b-cloud",
    "capabilities": ["query", "plan", "evaluate"],
    "hop_count": 0,
    "ttl": 3,
    "session_id": "session_20251113_100000",
    "trace_id": "trace_1734172800.123",
    "cpu_usage": 25.5,
    "mem_usage": 60.2
  },
  "content": {
    "type": "text",
    "query": "What is the current status of the data processing pipeline?",
    "context": {
      "requested_metrics": ["throughput", "error_rates"]
    }
  },
  "context": null,
  "attachments": [],
  "signature": null,
  "response_to": null
}
```

### A.2. ACK Message

```json
{
  "type": "intent_message",
  "version": "0.1",
  "schema_version": "osp-0.2",
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "timestamp": "2025-11-13T10:00:05Z",
  "intent": "ack",
  "from": "omnisync_TaskExecutor",
  "to": "omnisync_DataAnalyst",
  "metadata": {
    "framework": "OmniSync",
    "session_id": "session_20251113_100000",
    "trace_id": "trace_1734172800.123"
  },
  "content": {
    "received": true,
    "response_to": "550e8400-e29b-41d4-a716-446655440000"
  },
  "response_to": "550e8400-e29b-41d4-a716-446655440000"
}
```

## Appendix B. Change Log

### v0.2 (2025-11-13)

- Added ACK intent for protocol-level acknowledgments
- Enhanced metadata with CPU/memory usage, response times
- Session and trace ID tracking
- Schema v0.2 validation
- Trace visualization utilities

### v0.1 (2025-11-12)

- Initial protocol specification
- Base intent types (query, plan, execute, reflect, evaluate, notify)
- Anti-loop mechanism
- Basic metadata schema

