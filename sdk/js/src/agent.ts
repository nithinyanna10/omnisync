/**
 * OmniSync Agent for JavaScript/TypeScript
 */

import { IntentMessage, IntentType, createIntentMessage } from './protocol';
import { HubClient } from './hub-client';

export type MessageHandler = (message: IntentMessage) => Promise<IntentMessage | Record<string, any>> | IntentMessage | Record<string, any>;

export class Agent {
  private name: string;
  private framework: string;
  private agentId: string;
  private hubClient: HubClient;
  private model?: string;
  private capabilities: string[];
  private handlers: Map<IntentType, MessageHandler>;
  private running: boolean;

  constructor(
    name: string,
    framework: string = 'OmniSync',
    hubUrl: string = 'http://localhost:8080',
    model?: string,
    capabilities: string[] = [],
  ) {
    this.name = name;
    this.framework = framework;
    this.agentId = `${framework.toLowerCase()}_${name}`;
    this.hubClient = new HubClient(hubUrl, this.agentId);
    this.model = model;
    this.capabilities = capabilities;
    this.handlers = new Map();
    this.running = false;
  }

  on(intent: IntentType, handler: MessageHandler): void {
    this.handlers.set(intent, handler);
  }

  async handleMessage(message: IntentMessage): Promise<IntentMessage | null> {
    const handler = this.handlers.get(message.intent);
    if (handler) {
      try {
        const result = await handler(message);
        if (typeof result === 'object' && 'intent' in result) {
          return result as IntentMessage;
        } else {
          // Create response message
          const response = createIntentMessage(
            message.intent,
            this.agentId,
            message.from,
            result as Record<string, any>,
            {
              framework: this.framework,
              model: this.model,
              capabilities: this.capabilities,
            },
          );
          response.response_to = message.id;
          return response;
        }
      } catch (error) {
        console.error(`Error handling message ${message.id}:`, error);
        return null;
      }
    } else {
      console.warn(`No handler for intent ${message.intent}`);
    }
    return null;
  }

  async send(
    intent: IntentType,
    toAgent: string,
    content: Record<string, any>,
    metadata?: Record<string, any>,
    context?: Record<string, any>,
  ): Promise<IntentMessage> {
    const message = createIntentMessage(
      intent,
      this.agentId,
      toAgent,
      content,
      metadata || {
        framework: this.framework,
        model: this.model,
        capabilities: this.capabilities,
      },
      context,
    );
    await this.hubClient.sendMessage(message);
    return message;
  }

  async broadcast(
    intent: IntentType,
    content: Record<string, any>,
    metadata?: Record<string, any>,
  ): Promise<IntentMessage> {
    return this.send(intent, 'broadcast', content, metadata);
  }

  async start(): Promise<void> {
    this.running = true;
    await this.hubClient.connect();
    console.log(`Agent ${this.agentId} started`);

    // Register agent with hub
    await this.hubClient.registerAgent({
      agent_id: this.agentId,
      name: this.name,
      framework: this.framework,
      capabilities: this.capabilities,
      model: this.model,
    });

    // Start message listener
    this.messageLoop();
  }

  private async messageLoop(): Promise<void> {
    while (this.running) {
      try {
        const messages = await this.hubClient.getMessages(this.agentId);
        for (const message of messages) {
          const response = await this.handleMessage(message);
          if (response) {
            await this.hubClient.sendMessage(response);
          }
        }
        await new Promise((resolve) => setTimeout(resolve, 100));
      } catch (error) {
        console.error('Error in message loop:', error);
        await new Promise((resolve) => setTimeout(resolve, 1000));
      }
    }
  }

  async stop(): Promise<void> {
    this.running = false;
    await this.hubClient.disconnect();
    console.log(`Agent ${this.agentId} stopped`);
  }
}

