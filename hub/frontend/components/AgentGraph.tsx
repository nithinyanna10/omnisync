'use client'

import { useEffect, useRef } from 'react'
import * as d3 from 'd3'
import axios from 'axios'

const HUB_URL = process.env.NEXT_PUBLIC_HUB_URL || 'http://localhost:8080'

interface AgentGraphProps {
  messages: any[]
  agents: any[]
}

export default function AgentGraph({ messages, agents }: AgentGraphProps) {
  const svgRef = useRef<SVGSVGElement>(null)

  useEffect(() => {
    if (!svgRef.current) return

    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    const width = 600
    const height = 400
    svg.attr('width', width).attr('height', height)

    // Fetch conversation graph from API
    axios.get(`${HUB_URL}/api/conversations`)
      .then((response) => {
        const graphData = response.data
        renderGraph(graphData.nodes || agents, graphData.edges || [], svg, width, height)
      })
      .catch(() => {
        // Fallback to local data
        renderGraph(agents, messages, svg, width, height)
      })
  }, [messages, agents])

  function renderGraph(nodesData: any[], edgesData: any[], svg: any, width: number, height: number) {
    // Create nodes from agents/graph data
    const nodes = nodesData.map((agent) => ({
      id: agent.agent_id || agent.id,
      name: agent.name || agent.label,
      framework: agent.framework || 'Unknown',
    }))

    // Create links from messages/edges
    const linkMap = new Map<string, { count: number; intents: Set<string> }>()
    
    if (edgesData.length > 0 && edgesData[0].from) {
      // Use graph API format
      edgesData.forEach((edge: any) => {
        const key = `${edge.from}-${edge.to}`
        if (!linkMap.has(key)) {
          linkMap.set(key, { count: 0, intents: new Set() })
        }
        const link = linkMap.get(key)!
        link.count += 1
        link.intents.add(edge.intent)
      })
    } else {
      // Use message format
      edgesData.forEach((msg: any) => {
        if (msg.from && msg.to && msg.to !== 'broadcast') {
          const key = `${msg.from}-${msg.to}`
          if (!linkMap.has(key)) {
            linkMap.set(key, { count: 0, intents: new Set() })
          }
          const link = linkMap.get(key)!
          link.count += 1
          if (msg.intent) link.intents.add(msg.intent)
        }
      })
    }

    const links = Array.from(linkMap.entries()).map(([key, data]) => {
      const [source, target] = key.split('-')
      return { source, target, value: data.count, intents: Array.from(data.intents) }
    })

    // Create force simulation
    const simulation = d3
      .forceSimulation(nodes as any)
      .force(
        'link',
        d3
          .forceLink(links)
          .id((d: any) => d.id)
          .distance(100)
      )
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))

    // Draw links
    const link = svg
      .append('g')
      .selectAll('line')
      .data(links)
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
        }
        const primaryIntent = d.intents?.[0] || 'notify'
        return intentColors[primaryIntent] || '#999'
      })
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', (d: any) => Math.sqrt(d.value) * 2)

    // Draw nodes
    const node = svg
      .append('g')
      .selectAll('circle')
      .data(nodes)
      .enter()
      .append('circle')
      .attr('r', 20)
      .attr('fill', (d) => {
        const colors: Record<string, string> = {
          LangChain: '#1C3C3C',
          AutoGen: '#4A90E2',
          CrewAI: '#FF6B6B',
          LlamaIndex: '#51CF66',
          OmniSync: '#9775FA',
        }
        return colors[d.framework] || '#999'
      })
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
      .text((d) => d.name)
      .attr('font-size', '12px')
      .attr('dx', 25)
      .attr('dy', 5)

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
  }, [messages, agents])

  return (
    <div className="w-full">
      <svg ref={svgRef} className="w-full h-96 border rounded"></svg>
    </div>
  )
}

