import React, { useState } from 'react';
import { NATIONS } from '../engine/nation-data.js';
import KPIDashboard from './KPIDashboard.jsx';
import PolicyPanel from './PolicyPanel.jsx';
import ConvergenceMapViz from './ConvergenceMapViz.jsx';
import EraTransitionOverlay from './EraTransitionOverlay.jsx';
import EventLog from './EventLog.jsx';

export default function GameScreen({
  gameState, nationId, policiesThisTurn, lastTickEvents,
  pendingTransition, onApplyPolicy, onAdvanceYear,
  onDismissTransition, getAvailablePolicies, getEraConfig,
  getScore, getPhasePosition,
}) {
  const [activeTab, setActiveTab] = useState('policies'); // policies | convergence | log
  const nation = NATIONS[nationId];
  const eraConfig = getEraConfig();
  const score = getScore();
  const position = getPhasePosition();

  const eraNames = {
    era1_nation_building: 'Era 1: Nation-Building (1918-1945)',
    era2_planned_development: 'Era 2: Planned Development (1945-1990)',
    era3_convergence: 'Era 3: Convergence or Drift (1990-2025)',
  };

  const maxPoliciesPerTurn = 3;

  return (
    <div className="min-h-screen bg-bg flex flex-col">
      {/* Top Bar */}
      <header className="bg-surface border-b border-border px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-bold">
            <span className="text-accent">{nation.name}</span>
          </h1>
          <span className="text-muted text-sm">|</span>
          <span className="text-sm text-muted">{eraNames[gameState.era]}</span>
        </div>
        <div className="flex items-center gap-6">
          <div className="text-right">
            <div className="text-xs text-muted">Year</div>
            <div className="text-2xl font-bold font-mono text-accent">{gameState.year}</div>
          </div>
          <button
            onClick={onAdvanceYear}
            className="btn-primary text-lg px-6 py-2"
          >
            Advance Year →
          </button>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left: Map + KPI */}
        <div className="flex-1 flex flex-col p-4 gap-4 overflow-y-auto">
          <KPIDashboard state={gameState} nation={nation} />

          {/* Map Placeholder — will be D3 map */}
          <div className="kpi-card flex-1 flex flex-col min-h-[300px]">
            <h3 className="text-sm font-semibold text-muted uppercase tracking-wide mb-3">
              The Carpathian Crescent
            </h3>
            <div className="flex-1 flex items-center justify-center">
              <NationMapDisplay nation={nation} state={gameState} />
            </div>
          </div>
        </div>

        {/* Right: Policy Panel / Convergence Map / Log */}
        <div className="w-[420px] bg-surface border-l border-border flex flex-col">
          {/* Tabs */}
          <div className="flex border-b border-border">
            {['policies', 'convergence', 'log'].map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`flex-1 py-3 text-sm font-semibold transition-colors ${
                  activeTab === tab
                    ? 'text-accent border-b-2 border-accent bg-accent/5'
                    : 'text-muted hover:text-text'
                }`}
              >
                {tab === 'policies' ? '📋 Policies' : tab === 'convergence' ? '🗺️ Convergence' : '📜 Log'}
              </button>
            ))}
          </div>

          <div className="flex-1 overflow-y-auto">
            {activeTab === 'policies' && (
              <PolicyPanel
                policies={getAvailablePolicies()}
                policiesThisTurn={policiesThisTurn}
                maxPolicies={maxPoliciesPerTurn}
                onApply={onApplyPolicy}
              />
            )}
            {activeTab === 'convergence' && (
              <div className="p-4">
                <ConvergenceMapViz position={position} score={score} history={[]} />
              </div>
            )}
            {activeTab === 'log' && (
              <EventLog events={lastTickEvents} />
            )}
          </div>
        </div>
      </div>

      {/* Era Transition Overlay */}
      {pendingTransition && (
        <EraTransitionOverlay
          transition={pendingTransition}
          state={gameState}
          onDismiss={onDismissTransition}
        />
      )}
    </div>
  );
}

// Simple SVG map display (placeholder until D3 map is built)
function NationMapDisplay({ nation, state }) {
  const geo = nation.geography;
  const terrainColors = {
    flat_coastal: '#22c55e33',
    river_plains_uplands: '#f59e0b33',
    fertile_plains: '#22c55e44',
    mountainous: '#94a3b833',
    alpine: '#e2e8f033',
  };
  const terrainBorder = {
    flat_coastal: '#22c55e',
    river_plains_uplands: '#f59e0b',
    fertile_plains: '#22c55e',
    mountainous: '#94a3b8',
    alpine: '#e2e8f0',
  };

  // Generate a unique but deterministic shape for each nation
  const seed = nation.name.charCodeAt(0) + nation.name.charCodeAt(nation.name.length - 1);
  const shapePoints = generateNationShape(seed, nation.areaKm2);

  const pathD = shapePoints.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ') + ' Z';

  return (
    <svg viewBox="0 0 400 300" className="w-full h-full max-w-[400px]">
      {/* Neighboring nations faded */}
      {Object.entries(NATIONS).filter(([id]) => id !== nation.name.toLowerCase().replace(/[^a-z]/g, '_')).slice(0, 3).map(([id, n], i) => {
        const nSeed = n.name.charCodeAt(0) + n.name.charCodeAt(n.name.length - 1);
        const nPoints = generateNationShape(nSeed + i * 10, n.areaKm2, true);
        const nPath = nPoints.map((p, j) => `${j === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ') + ' Z';
        return (
          <path key={id} d={nPath} fill="#33415522" stroke="#33415544" strokeWidth="1" />
        );
      })}

      {/* Main nation */}
      <path
        d={pathD}
        fill={terrainColors[geo.terrain] || '#38bdf833'}
        stroke={terrainBorder[geo.terrain] || '#38bdf8'}
        strokeWidth="2.5"
      />

      {/* Capital marker */}
      <circle cx={shapePoints[0].x} cy={shapePoints[0].y} r="5" fill="#f59e0b" stroke="#0f172a" strokeWidth="2" />
      <text x={shapePoints[0].x + 8} y={shapePoints[0].y + 4} className="text-[10px] fill-text font-semibold">
        {nation.capital}
      </text>

      {/* Nation label */}
      <text x="200" y="270" textAnchor="middle" className="text-sm fill-muted font-semibold">
        {nation.name}
      </text>
      <text x="200" y="288" textAnchor="middle" className="text-xs fill-muted">
        {nation.areaKm2.toLocaleString()} km² · Pop {state.populationMillions.toFixed(1)}M
      </text>
    </svg>
  );
}

function generateNationShape(seed, areaKm2, isNeighbor = false) {
  // Deterministic pseudo-random based on seed
  const rng = (s) => { const x = Math.sin(s * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };

  const scale = Math.sqrt(areaKm2) / 25;
  const cx = isNeighbor ? 100 + rng(seed + 1) * 200 : 200;
  const cy = isNeighbor ? 80 + rng(seed + 2) * 140 : 150;
  const points = [];
  const numPoints = 10 + Math.floor(rng(seed) * 6);

  for (let i = 0; i < numPoints; i++) {
    const angle = (i / numPoints) * Math.PI * 2;
    const radius = (30 + rng(seed + i * 7) * 30) * scale * (isNeighbor ? 0.7 : 1);
    const x = cx + Math.cos(angle) * radius;
    const y = cy + Math.sin(angle) * radius * 0.7;
    points.push({ x: Math.max(10, Math.min(390, x)), y: Math.max(10, Math.min(290, y)) });
  }
  return points;
}
