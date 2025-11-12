/**
 * OmniSync Hub Client for JavaScript/TypeScript
 */

import axios, { AxiosInstance } from 'axios';
import WebSocket from 'ws';
import { IntentMessage } from './protocol';

export class HubClient {
  private hubUrl: string;
  private agentId: string;
  private axiosInstance: AxiosInstance;
  private ws?: WebSocket;

  constructor(hubUrl: string = 'http://localhost:8080', agentId: string = 'default') {
    this.hubUrl = hubUrl.replace(/\/$/, '');
    this.agentId = agentId;
    this.axiosInstance = axios.create({
      baseURL: this.hubUrl,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  async connect(): Promise<void> {
    // HTTP connection is always available
    // WebSocket can be added for real-time updates
    console.log(`Connected to hub at ${this.hubUrl}`);
  }

  async disconnect(): Promise<void> {
    if (this.ws) {
      this.ws.close();
      this.ws = undefined;
    }
  }

  async sendMessage(message: IntentMessage): Promise<boolean> {
    try {
      const response = await this.axiosInstance.post('/api/messages', message);
      return response.status === 200;
    } catch (error) {
      console.error('Error sending message:', error);
      return false;
    }
  }

  async getMessages(agentId?: string): Promise<IntentMessage[]> {
    const targetId = agentId || this.agentId;
    try {
      const response = await this.axiosInstance.get(`/api/messages/${targetId}`);
      return response.data.messages || [];
    } catch (error) {
      console.error('Error getting messages:', error);
      return [];
    }
  }

  async registerAgent(agentInfo: Record<string, any>): Promise<boolean> {
    try {
      const response = await this.axiosInstance.post('/api/agents/register', agentInfo);
      return response.status === 200;
    } catch (error) {
      console.error('Error registering agent:', error);
      return false;
    }
  }

  async getAgents(): Promise<Array<Record<string, any>>> {
    try {
      const response = await this.axiosInstance.get('/api/agents');
      return response.data.agents || [];
    } catch (error) {
      console.error('Error getting agents:', error);
      return [];
    }
  }
}

