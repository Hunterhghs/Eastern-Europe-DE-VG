import React from 'react';

export default function EraTransitionOverlay({ transition, state, onDismiss }) {
  const eraLabels = {
    era2_planned_development: { name: 'Planned Development', years: '1945–1990', role: 'Planning Ministry (Constrained Autonomy)', color: 'text-gold', icon: '🏭' },
    era3_convergence: { name: 'Convergence or Drift', years: '1990–2025', role: 'Democratic Government (Full Autonomy)', color: 'text-green', icon: '🏛️' },
  };

  const era = eraLabels[transition.to];
  if (!era) return null;

  return (
    <div className="fixed inset-0 bg-bg/95 flex items-center justify-center z-50 animate-fade-in">
      <div className="max-w-lg w-full mx-4 bg-surface border-2 border-accent rounded-2xl p-8 text-center">
        <div className="text-5xl mb-4">{era.icon}</div>
        <h2 className={`text-3xl font-extrabold mb-2 ${era.color}`}>
          {era.name}
        </h2>
        <p className="text-muted mb-1">{era.years}</p>
        <p className="text-sm text-muted mb-6">{era.role}</p>

        <div className="bg-bg rounded-xl p-4 mb-6 text-left space-y-2">
          {transition.details.map((d, i) => (
            <div key={i} className="text-sm">
              {d.startsWith('⚠') ? (
                <span className="text-warn">{d}</span>
              ) : (
                <span className="text-muted">• {d}</span>
              )}
            </div>
          ))}
        </div>

        <div className="grid grid-cols-3 gap-3 mb-6">
          <div className="kpi-card py-2">
            <div className="text-[10px] text-muted">GDP/cap</div>
            <div className="text-lg font-bold text-accent">${state.gdpPerCapitaPPP.toFixed(0)}</div>
          </div>
          <div className="kpi-card py-2">
            <div className="text-[10px] text-muted">D-Coefficient</div>
            <div className="text-lg font-bold">{state.dCoefficient.toFixed(1)}</div>
          </div>
          <div className="kpi-card py-2">
            <div className="text-[10px] text-muted">Inst. Quality</div>
            <div className="text-lg font-bold">{state.institutionalQuality.toFixed(2)}</div>
          </div>
        </div>

        <button
          onClick={onDismiss}
          className="btn-primary text-lg px-8 py-3 animate-pulse-glow"
        >
          Enter {era.name} →
        </button>
      </div>
    </div>
  );
}
