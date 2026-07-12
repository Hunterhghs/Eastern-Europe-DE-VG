import React from 'react';
import { NATIONS } from '../engine/nation-data.js';

export default function GameOver({ sim, onRestart }) {
  const score = sim.getScore();
  const state = sim.state;
  const start = sim.history[0];
  const nation = NATIONS[state.nationId];

  const verdictColor = score.score > 80 ? 'text-green' : score.score > 50 ? 'text-gold' : score.score > 25 ? 'text-warn' : 'text-warn';

  return (
    <div className="min-h-screen bg-bg flex items-center justify-center p-8 animate-fade-in">
      <div className="max-w-2xl w-full">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-extrabold mb-2">
            The Story of <span className="text-accent">{nation.name}</span>
          </h1>
          <p className="text-muted">1918 – 2025 · {sim.history.length} years of history</p>
        </div>

        {/* Convergence Score */}
        <div className="bg-surface border-2 border-accent rounded-2xl p-8 text-center mb-6">
          <div className="text-sm text-muted uppercase tracking-wide mb-2">Convergence Score</div>
          <div className={`text-6xl font-extrabold ${verdictColor}`}>
            {score.score.toFixed(0)}<span className="text-2xl text-muted">/100</span>
          </div>
          <div className={`mt-3 text-lg font-semibold ${verdictColor}`}>{score.verdict}</div>
          <div className="text-sm text-muted mt-1">Dominant basin: {score.dominantBasin}</div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
          {[
            ['GDP/capita', `$${start.gdpPerCapitaPPP.toFixed(0)} → $${state.gdpPerCapitaPPP.toFixed(0)}`],
            ['Life Expectancy', `${start.lifeExpectancy.toFixed(0)} → ${state.lifeExpectancy.toFixed(0)} yr`],
            ['Literacy', `${(start.literacyRate * 100).toFixed(0)}% → ${(state.literacyRate * 100).toFixed(0)}%`],
            ['Urbanization', `${(start.urbanizationRate * 100).toFixed(0)}% → ${(state.urbanizationRate * 100).toFixed(0)}%`],
            ['D-Coefficient', `${start.dCoefficient.toFixed(1)} → ${state.dCoefficient.toFixed(1)}`],
            ['Gini', `${start.giniCoefficient.toFixed(2)} → ${state.giniCoefficient.toFixed(2)}`],
            ['Inst. Quality', `${start.institutionalQuality.toFixed(2)} → ${state.institutionalQuality.toFixed(2)}`],
            ['Crises', `${sim.events.crisisHistory.length} survived`],
          ].map(([label, value]) => (
            <div key={label} className="kpi-card py-3">
              <div className="text-[10px] text-muted uppercase">{label}</div>
              <div className="text-sm font-bold mt-1">{value}</div>
            </div>
          ))}
        </div>

        {/* Phase Position */}
        <div className="bg-surface rounded-xl p-4 mb-6 text-center">
          <div className="text-sm text-muted mb-2">Final Phase Position</div>
          <div className="flex items-center justify-center gap-8">
            <div>
              <div className="text-xs text-muted">Economic Complexity</div>
              <div className="text-2xl font-bold text-accent">{state.economicComplexity.toFixed(1)}</div>
            </div>
            <div className="text-muted">×</div>
            <div>
              <div className="text-xs text-muted">Institutional Quality</div>
              <div className="text-2xl font-bold text-accent">{state.institutionalQualityPhase.toFixed(1)}</div>
            </div>
          </div>
        </div>

        <div className="text-center">
          <button onClick={onRestart} className="btn-primary text-lg px-8 py-3">
            Play Again
          </button>
        </div>
      </div>
    </div>
  );
}
