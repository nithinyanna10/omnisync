'use client'

interface StatsPanelProps {
  stats: any
  agents: any[]
}

export default function StatsPanel({ stats, agents }: StatsPanelProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div className="bg-white rounded-lg shadow p-4">
        <div className="text-sm text-gray-600">Total Messages</div>
        <div className="text-2xl font-bold text-gray-900">{stats.total_messages || 0}</div>
      </div>
      <div className="bg-white rounded-lg shadow p-4">
        <div className="text-sm text-gray-600">Active Agents</div>
        <div className="text-2xl font-bold text-gray-900">{stats.total_agents || 0}</div>
      </div>
      <div className="bg-white rounded-lg shadow p-4">
        <div className="text-sm text-gray-600">Query Messages</div>
        <div className="text-2xl font-bold text-blue-600">
          {stats.intent_counts?.query || 0}
        </div>
      </div>
      <div className="bg-white rounded-lg shadow p-4">
        <div className="text-sm text-gray-600">Execute Messages</div>
        <div className="text-2xl font-bold text-yellow-600">
          {stats.intent_counts?.execute || 0}
        </div>
      </div>
    </div>
  )
}

