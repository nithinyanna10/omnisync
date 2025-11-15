'use client'

import { useEffect, useState } from 'react'
import AgentGraph from '../components/AgentGraph'
import GraphView from '../components/GraphView'
import MessageList from '../components/MessageList'
import StatsPanel from '../components/StatsPanel'
import axios from 'axios'

const HUB_URL = process.env.NEXT_PUBLIC_HUB_URL || 'http://localhost:8080'

export default function Home() {
  const [messages, setMessages] = useState<any[]>([])
  const [agents, setAgents] = useState<any[]>([])
  const [stats, setStats] = useState<any>({})
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null)

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 2000) // Refresh every 2 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchData = async () => {
    try {
      const [messagesRes, agentsRes, statsRes] = await Promise.all([
        axios.get(`${HUB_URL}/api/messages?limit=1000`),
        axios.get(`${HUB_URL}/api/agents`),
        axios.get(`${HUB_URL}/api/stats`),
      ])
      setMessages(messagesRes.data.messages || [])
      setAgents(agentsRes.data.agents || [])
      setStats(statsRes.data || {})
    } catch (error) {
      console.error('Error fetching data:', error)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-3xl font-bold text-gray-900">OmniSync Hub</h1>
          <p className="text-sm text-gray-600 mt-1">Agent Communication Visualization</p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">
        <StatsPanel stats={stats} agents={agents} />

        <div className="mt-6">
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Live Conversation Graph (v0.3)</h2>
            <GraphView autoRefresh={true} refreshInterval={5000} />
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Agent Network Graph</h2>
            <AgentGraph messages={messages} agents={agents} />
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Message Timeline</h2>
            <div className="mb-4">
              <select
                value={selectedAgent || ''}
                onChange={(e) => setSelectedAgent(e.target.value || null)}
                className="border rounded px-3 py-2"
              >
                <option value="">All Agents</option>
                {agents.map((agent) => (
                  <option key={agent.agent_id} value={agent.agent_id}>
                    {agent.name} ({agent.framework})
                  </option>
                ))}
              </select>
            </div>
            <MessageList
              messages={selectedAgent ? messages.filter(m => m.from === selectedAgent || m.to === selectedAgent) : messages}
            />
          </div>
        </div>
      </main>
    </div>
  )
}

