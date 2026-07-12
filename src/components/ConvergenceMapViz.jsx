import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { STANDARD_BASINS } from '../engine/convergence-map.js';

export default function ConvergenceMapViz({ position, score, history = [] }) {
  const svgRef = useRef();
  const W = 380, H = 380, M = 40;

  useEffect(() => {
    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const g = svg.append('g').attr('transform', `translate(${M},${M})`);
    const innerW = W - M * 2, innerH = H - M * 2;

    // Scales
    const x = d3.scaleLinear().domain([0, 100]).range([0, innerW]);
    const y = d3.scaleLinear().domain([0, 100]).range([innerH, 0]);

    // Grid
    g.append('g').call(d3.axisLeft(y).ticks(5).tickFormat(d => d)).attr('color', '#334155').selectAll('text').attr('fill', '#64748b').attr('font-size', '9');
    g.append('g').call(d3.axisBottom(x).ticks(5).tickFormat(d => d)).attr('transform', `translate(0,${innerH})`).attr('color', '#334155').selectAll('text').attr('fill', '#64748b').attr('font-size', '9');

    // Labels
    g.append('text').attr('x', innerW / 2).attr('y', innerH + 30).attr('text-anchor', 'middle').attr('fill', '#94a3b8').attr('font-size', '11').text('Economic Complexity →');
    g.append('text').attr('x', -20).attr('y', innerH / 2).attr('text-anchor', 'middle').attr('transform', `rotate(-90, -20, ${innerH/2})`).attr('fill', '#94a3b8').attr('font-size', '11').text('Institutional Quality →');

    // Basins
    for (const basin of STANDARD_BASINS) {
      const fill = basin.isDesirable ? '#22c55e15' : basin.isTrap ? '#ef444415' : '#38bdf815';
      const stroke = basin.isDesirable ? '#22c55e44' : basin.isTrap ? '#ef444444' : '#38bdf844';
      g.append('circle')
        .attr('cx', x(basin.cx)).attr('cy', y(basin.cy)).attr('r', x(basin.radius) - x(0))
        .attr('fill', fill).attr('stroke', stroke).attr('stroke-width', '1')
        .attr('stroke-dasharray', basin.isTrap ? '4,2' : 'none');

      g.append('text')
        .attr('x', x(basin.cx)).attr('y', y(basin.cy) - x(basin.radius) + 12)
        .attr('text-anchor', 'middle').attr('fill', '#64748b').attr('font-size', '7')
        .text(basin.name);
    }

    // Nation position
    const px = x(position.x), py = y(position.y);
    g.append('circle').attr('cx', px).attr('cy', py).attr('r', '6')
      .attr('fill', '#f59e0b').attr('stroke', '#0f172a').attr('stroke-width', '2');
    g.append('circle').attr('cx', px).attr('cy', py).attr('r', '12')
      .attr('fill', 'none').attr('stroke', '#f59e0b').attr('stroke-width', '1').attr('opacity', '0.5');

    // Score badge
    g.append('rect').attr('x', innerW - 90).attr('y', 5).attr('width', 85).attr('height', 28).attr('rx', '6')
      .attr('fill', '#1e293b').attr('stroke', '#334155').attr('stroke-width', '1');
    g.append('text').attr('x', innerW - 47).attr('y', 23).attr('text-anchor', 'middle')
      .attr('fill', score.score > 50 ? '#22c55e' : '#f59e0b').attr('font-size', '11').attr('font-weight', 'bold')
      .text(`Score: ${score.score?.toFixed(0) || '--'}`);

  }, [position, score]);

  return (
    <div>
      <h3 className="text-sm font-semibold text-muted uppercase tracking-wide mb-2">Convergence Map</h3>
      <svg ref={svgRef} viewBox={`0 0 ${W} ${H}`} className="w-full" />
      <div className="mt-3 space-y-2">
        <div className="text-xs text-muted">
          <span className="font-semibold">Dominant Basin: </span>
          <span className={score.dominantBasin?.includes('Trap') ? 'text-warn' : 'text-green'}>
            {score.dominantBasin || 'Unknown'}
          </span>
        </div>
        <div className="text-xs text-muted">
          <span className="font-semibold">Convergence Remaining: </span>
          {score.convergenceRemaining?.toFixed(1) || '--'}
        </div>
        <div className="text-xs text-muted">
          <span className="font-semibold">Verdict: </span>
          {score.verdict}
        </div>
      </div>
    </div>
  );
}
