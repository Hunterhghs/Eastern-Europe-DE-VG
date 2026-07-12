import React, { useState } from 'react';
import { NATIONS } from '../engine/nation-data.js';

const nationList = Object.entries(NATIONS).map(([id, n]) => ({
  id,
  ...n,
  d: n.era1Start.dCoefficient,
  gdp: n.era1Start.gdpPerCapitaPPP,
  literacy: n.era1Start.literacyRate,
  legacy: n.era1Start.institutionalLegacy.replace(/_/g, ' '),
}));

export default function NationSelect({ onSelect }) {
  const [selected, setSelected] = useState(null);

  const difficulty = (n) => {
    if (n.d >= 35) return { label: 'Easier', color: 'text-green' };
    if (n.d >= 20) return { label: 'Moderate', color: 'text-gold' };
    return { label: 'Harder', color: 'text-warn' };
  };

  return (
    <div className="min-h-screen bg-bg flex flex-col items-center justify-center p-8">
      <div className="text-center mb-12 animate-slide-up">
        <h1 className="text-5xl font-extrabold tracking-tight mb-3">
          <span className="text-accent">The Carpathian</span> Crescent
        </h1>
        <p className="text-muted text-lg max-w-xl mx-auto">
          Guide a nation across 100 years of development. Build institutions,
          navigate crises, and shape the convergence trajectory of your people.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-w-5xl w-full">
        {nationList.map((n) => {
          const diff = difficulty(n);
          const isSelected = selected === n.id;
          return (
            <button
              key={n.id}
              onClick={() => setSelected(n.id)}
              className={`text-left p-5 rounded-xl border transition-all duration-200 ${
                isSelected
                  ? 'border-accent bg-accent/10 scale-[1.02]'
                  : 'border-border bg-surface hover:border-muted'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-lg font-bold">{n.name}</h3>
                <span className={`text-xs font-semibold uppercase ${diff.color}`}>
                  {diff.label}
                </span>
              </div>
              <p className="text-muted text-sm mb-3">{n.geography.description}</p>
              <div className="grid grid-cols-3 gap-2 text-sm">
                <div>
                  <div className="text-muted text-xs">Population</div>
                  <div className="font-semibold">{n.population1918M}M</div>
                </div>
                <div>
                  <div className="text-muted text-xs">D-Coefficient</div>
                  <div className="font-semibold text-accent">{n.d}</div>
                </div>
                <div>
                  <div className="text-muted text-xs">GDP/cap</div>
                  <div className="font-semibold">${n.gdp.toLocaleString()}</div>
                </div>
              </div>
              <div className="mt-2 text-xs text-muted capitalize">
                Legacy: {n.legacy}
              </div>
            </button>
          );
        })}
      </div>

      <button
        disabled={!selected}
        onClick={() => selected && onSelect(selected)}
        className={`mt-8 px-8 py-3 rounded-xl font-bold text-lg transition-all ${
          selected
            ? 'bg-accent text-bg hover:brightness-110 animate-pulse-glow'
            : 'bg-surface text-muted cursor-not-allowed'
        }`}
      >
        {selected ? `Begin as ${NATIONS[selected].name}` : 'Choose a Nation'}
      </button>
    </div>
  );
}
