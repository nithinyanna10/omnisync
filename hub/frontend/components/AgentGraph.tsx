'use client'

import { useEffect, useRef } from 'react'
import * as d3 from 'd3'

interface AgentGraphProps {
  messages: any[]
  agents: any[]
}

export default function AgentGraph({ messages, agents }: AgentGraphProps) {
  const svgRef = useRef<SVGSVGElement>(null)

  useEffect(() => {
    if (!svgRef.current || messages.length === 0) return

    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    const width = 600
    const height = 400
    svg.attr('width', width).attr('height', height)

    // Create nodes from agents
    const nodes = agents.map((agent) => ({
      id: agent.agent_id,
      name: agent.name,
      framework: agent.framework,
    }))

    // Create links from messages
    const linkMap = new Map<string, number>()
    messages.forEach((msg) => {
      if (msg.from && msg.to && msg.to !== 'broadcast') {
        const key = `${msg.from}-${msg.to}`
        linkMap.set(key, (linkMap.get(key) || 0) + 1)
      }
    })

    const links = Array.from(linkMap.entries()).map(([key, value]) => {
      const [source, target] = key.split('-')
      return { source, target, value }
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
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', (d) => Math.sqrt(d.value) * 2)

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

