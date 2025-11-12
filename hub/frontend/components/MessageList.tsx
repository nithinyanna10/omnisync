'use client'

interface MessageListProps {
  messages: any[]
}

export default function MessageList({ messages }: MessageListProps) {
  const intentColors: Record<string, string> = {
    query: 'bg-blue-100 text-blue-800',
    plan: 'bg-green-100 text-green-800',
    execute: 'bg-yellow-100 text-yellow-800',
    reflect: 'bg-purple-100 text-purple-800',
    evaluate: 'bg-orange-100 text-orange-800',
    notify: 'bg-gray-100 text-gray-800',
  }

  return (
    <div className="space-y-2 max-h-96 overflow-y-auto">
      {messages.length === 0 ? (
        <p className="text-gray-500 text-center py-8">No messages yet</p>
      ) : (
        messages
          .slice()
          .reverse()
          .map((msg) => (
            <div
              key={msg.id}
              className="border rounded-lg p-3 hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center justify-between mb-2">
                <span className={`px-2 py-1 rounded text-xs font-medium ${intentColors[msg.intent] || 'bg-gray-100'}`}>
                  {msg.intent}
                </span>
                <span className="text-xs text-gray-500">
                  {new Date(msg.timestamp).toLocaleTimeString()}
                </span>
              </div>
              <div className="text-sm">
                <span className="font-medium text-blue-600">{msg.from}</span>
                <span className="mx-2 text-gray-400">→</span>
                <span className="font-medium text-green-600">{msg.to}</span>
              </div>
              <div className="mt-2 text-sm text-gray-700">
                {JSON.stringify(msg.content, null, 2).substring(0, 100)}
                {JSON.stringify(msg.content, null, 2).length > 100 && '...'}
              </div>
            </div>
          ))
      )}
    </div>
  )
}

