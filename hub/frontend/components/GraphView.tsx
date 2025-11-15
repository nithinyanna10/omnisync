'use client'

import { useEffect, useRef, useState } from 'react'
import * as d3 from 'd3'
import axios from 'axios'

const HUB_URL = process.env.NEXT_PUBLIC_HUB_URL || 'http://localhost:8080'

interface GraphViewProps {
  sessionId?: string
  traceId?: string
  autoRefresh?: boolean
  refreshInterval?: number
}

export default function GraphView({ 
  sessionId, 
  traceId, 
  autoRefresh = true,
  refreshInterval = 5000 
}: GraphViewProps) {
  const svgRef = useRef<SVGSVGElement>(null)
  const [metrics, setMetrics] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!svgRef.current) return

    const fetchAndRender = async () => {
      try {
        setLoading(true)
        
        // Fetch conversation graph
        const graphResponse = await axios.get(`${HUB_URL}/api/conversations`)
        const graphData = graphResponse.data

        // Fetch metrics
        const metricsResponse = await axios.get(`${HUB_URL}/api/v1/metrics?time_range=1h`)
        setMetrics(metricsResponse.data)

        // Render graph
        renderGraph(graphData.nodes || [], graphData.edges || [])
        
        setLoading(false)
      } catch (error) {
        console.error('Error fetching graph data:', error)
        setLoading(false)
      }
    }

    fetchAndRender()

    // Auto-refresh
    let interval: NodeJS.Timeout | null = null
    if (autoRefresh) {
      interval = setInterval(fetchAndRender, refreshInterval)
    }

    return () => {
      if (interval) clearInterval(interval)
    }
  }, [sessionId, traceId, autoRefresh, refreshInterval])

  function renderGraph(nodes: any[], edges: any[]) {
    if (!svgRef.current) return

    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    const width = 800
    const height = 600
    svg.attr('width', width).attr('height', height)

    // Create force simulation
    const simulation = d3
      .forceSimulation(nodes as any)
      .force(
        'link',
        d3
          .forceLink(edges)
          .id((d: any) => d.id)
          .distance(150)
      )
      .force('charge', d3.forceManyBody().strength(-500))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(30))

    // Create arrow markers for directed edges
    svg
      .append('defs')
      .selectAll('marker')
      .data(['arrow'])
      .enter()
      .append('marker')
      .attr('id', 'arrow')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 25)
      .attr('refY', 0)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', '#999')

    // Draw links with intent-based colors
    const link = svg
      .append('g')
      .selectAll('line')
      .data(edges)
      .enter()
      .append('line')
      .attr('stroke', (d: any) => {
        const intentColors: Record<string, string> = {
          query: '#3b82f6',
          plan: '#10b981',
          act: '#f59e0b',
          execute: '#f59e0b',
          reflect: '#8b5cf6',
          evaluate: '#ef4444',
          notify: '#6b7280',
          ack: '#94a3b8',
        }
        return intentColors[d.intent] || '#999'
      })
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', (d: any) => Math.sqrt(d.value || 1) * 3)
      .attr('marker-end', 'url(#arrow)')

    // Draw nodes
    const node = svg
      .append('g')
      .selectAll('circle')
      .data(nodes)
      .enter()
      .append('circle')
      .attr('r', 25)
      .attr('fill', (d: any) => {
        const colors: Record<string, string> = {
          LangChain: '#1C3C3C',
          AutoGen: '#4A90E2',
          CrewAI: '#FF6B6B',
          LlamaIndex: '#51CF66',
          OmniSync: '#9775FA',
        }
        return colors[d.framework] || '#999'
      })
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)
      .call(
        d3
          .drag<any, any>()
          .on('start', dragstarted)
          .on('drag', dragged)
          .on('end', dragended)
      )

    // Add labels
    const labels = svg
      .append('g')
      .selectAll('text')
      .data(nodes)
      .enter()
      .append('text')
      .text((d: any) => d.name || d.label)
      .attr('font-size', '14px')
      .attr('font-weight', 'bold')
      .attr('dx', 30)
      .attr('dy', 5)
      .attr('fill', '#333')

    // Update positions on simulation tick
    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y)

      node.attr('cx', (d: any) => d.x).attr('cy', (d: any) => d.y)

      labels.attr('x', (d: any) => d.x).attr('y', (d: any) => d.y)
    })

    function dragstarted(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0.3).restart()
      d.fx = d.x
      d.fy = d.y
    }

    function dragged(event: any, d: any) {
      d.fx = event.x
      d.fy = event.y
    }

    function dragended(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0)
      d.fx = null
      d.fy = null
    }
  }

  return (
    <div className="w-full">
      {loading && (
        <div className="text-center py-4">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
          <p className="mt-2 text-gray-600">Loading graph...</p>
        </div>
      )}
      
      {metrics && (
        <div className="mb-4 grid grid-cols-4 gap-4">
          <div className="bg-blue-50 p-3 rounded">
            <div className="text-sm text-gray-600">Messages</div>
            <div className="text-2xl font-bold">{metrics.total_messages}</div>
          </div>
          <div className="bg-green-50 p-3 rounded">
            <div className="text-sm text-gray-600">Avg Latency</div>
            <div className="text-2xl font-bold">{Math.round(metrics.average_latency_ms)}ms</div>
          </div>
          <div className="bg-yellow-50 p-3 rounded">
            <div className="text-sm text-gray-600">CPU Usage</div>
            <div className="text-2xl font-bold">{Math.round(metrics.average_cpu_usage)}%</div>
          </div>
          <div className="bg-purple-50 p-3 rounded">
            <div className="text-sm text-gray-600">Memory</div>
            <div className="text-2xl font-bold">{Math.round(metrics.average_memory_usage)}%</div>
          </div>
        </div>
      )}
      
      <svg ref={svgRef} className="w-full h-96 border rounded bg-white"></svg>
    </div>
  )
}

