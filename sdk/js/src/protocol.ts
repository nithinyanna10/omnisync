/**
 * OmniSync Protocol message definitions using Zod
 */

import { z } from 'zod';

export enum IntentType {
  QUERY = 'query',
  PLAN = 'plan',
  EXECUTE = 'execute',
  REFLECT = 'reflect',
  EVALUATE = 'evaluate',
  NOTIFY = 'notify',
}

const BaseMessageSchema = z.object({
  type: z.literal('intent_message').default('intent_message'),
  version: z.literal('0.1').default('0.1'),
  id: z.string().uuid(),
  timestamp: z.string().datetime(),
});

export const IntentMessageSchema = BaseMessageSchema.extend({
  intent: z.nativeEnum(IntentType),
  from: z.string(),
  to: z.string(),
  metadata: z.record(z.any()).default({}),
  content: z.record(z.any()).default({}),
  context: z.record(z.any()).optional(),
  attachments: z.array(z.record(z.any())).default([]),
  signature: z.string().optional(),
  response_to: z.string().optional(),
});

export const QueryIntentSchema = IntentMessageSchema.extend({
  intent: z.literal(IntentType.QUERY),
  content: z.object({
    query: z.string(),
    parameters: z.record(z.any()).optional(),
    expected_format: z.enum(['json', 'text', 'structured']).optional(),
  }),
});

export const PlanIntentSchema = IntentMessageSchema.extend({
  intent: z.literal(IntentType.PLAN),
  content: z.object({
    goal: z.string(),
    steps: z.array(z.record(z.any())).optional(),
    priority: z.enum(['high', 'medium', 'low']).optional(),
  }),
});

export const ExecuteIntentSchema = IntentMessageSchema.extend({
  intent: z.literal(IntentType.EXECUTE),
  content: z.object({
    task: z.string(),
    parameters: z.record(z.any()).optional(),
    timeout: z.number().optional(),
  }),
});

export const ReflectIntentSchema = IntentMessageSchema.extend({
  intent: z.literal(IntentType.REFLECT),
  content: z.object({
    analysis: z.string(),
    reasoning: z.string().optional(),
    confidence: z.number().min(0).max(1).optional(),
  }),
});

export const EvaluateIntentSchema = IntentMessageSchema.extend({
  intent: z.literal(IntentType.EVALUATE),
  content: z.object({
    target: z.string(),
    criteria: z.array(z.string()).optional(),
    scores: z.record(z.number()),
    feedback: z.string().optional(),
  }),
});

export const NotifyIntentSchema = IntentMessageSchema.extend({
  intent: z.literal(IntentType.NOTIFY),
  content: z.object({
    event: z.enum(['task_completed', 'error', 'status_update']),
    message: z.string(),
    data: z.record(z.any()).optional(),
  }),
});

export const ErrorMessageSchema = BaseMessageSchema.extend({
  type: z.literal('error_message'),
  error_code: z.string(),
  message: z.string(),
  original_message_id: z.string().optional(),
});

export type IntentMessage = z.infer<typeof IntentMessageSchema>;
export type QueryIntent = z.infer<typeof QueryIntentSchema>;
export type PlanIntent = z.infer<typeof PlanIntentSchema>;
export type ExecuteIntent = z.infer<typeof ExecuteIntentSchema>;
export type ReflectIntent = z.infer<typeof ReflectIntentSchema>;
export type EvaluateIntent = z.infer<typeof EvaluateIntentSchema>;
export type NotifyIntent = z.infer<typeof NotifyIntentSchema>;
export type ErrorMessage = z.infer<typeof ErrorMessageSchema>;

export function createIntentMessage(
  intent: IntentType,
  fromAgent: string,
  toAgent: string,
  content: Record<string, any>,
  metadata?: Record<string, any>,
  context?: Record<string, any>,
  attachments?: Array<Record<string, any>>,
): IntentMessage {
  const message: IntentMessage = {
    type: 'intent_message',
    version: '0.1',
    id: crypto.randomUUID(),
    timestamp: new Date().toISOString(),
    intent,
    from: fromAgent,
    to: toAgent,
    metadata: metadata || {},
    content,
    context,
    attachments: attachments || [],
  };

  // Validate based on intent type
  const schemas = {
    [IntentType.QUERY]: QueryIntentSchema,
    [IntentType.PLAN]: PlanIntentSchema,
    [IntentType.EXECUTE]: ExecuteIntentSchema,
    [IntentType.REFLECT]: ReflectIntentSchema,
    [IntentType.EVALUATE]: EvaluateIntentSchema,
    [IntentType.NOTIFY]: NotifyIntentSchema,
  };

  const schema = schemas[intent] || IntentMessageSchema;
  return schema.parse(message);
}

