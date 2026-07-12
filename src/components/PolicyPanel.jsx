import React, { useState } from 'react';

export default function PolicyPanel({ policies, policiesThisTurn, maxPolicies, onApply }) {
  const [investmentLevels, setInvestmentLevels] = useState({});

  const canApply = policiesThisTurn < maxPolicies;

  const handleApply = (policyId) => {
    if (!canApply) return;
    const level = investmentLevels[policyId] || 0.7;
    onApply(policyId, level);
  };

  const setLevel = (policyId, level) => {
    setInvestmentLevels(prev => ({ ...prev, [policyId]: level }));
  };

  return (
    <div className="p-4 space-y-3">
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-semibold text-sm">Policy Decisions</h3>
        <span className={`text-xs font-semibold ${canApply ? 'text-accent' : 'text-warn'}`}>
          {policiesThisTurn}/{maxPolicies} used this turn
        </span>
      </div>

      {policies.map(policy => {
        const level = investmentLevels[policy.id] || 0.7;
        return (
          <div key={policy.id} className="bg-bg border border-border rounded-lg p-3 hover:border-muted transition-colors">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-lg">{policy.icon}</span>
              <div className="flex-1">
                <div className="font-semibold text-sm">{policy.name}</div>
                <div className="text-xs text-muted">{policy.desc}</div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-[10px] text-muted w-8 text-right">
                {level < 0.4 ? 'Low' : level < 0.7 ? 'Med' : 'High'}
              </span>
              <input
                type="range"
                min="0.1"
                max="1.0"
                step="0.1"
                value={level}
                onChange={(e) => setLevel(policy.id, parseFloat(e.target.value))}
                className="flex-1 h-1.5 rounded-full appearance-none bg-border cursor-pointer
                  [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3.5 [&::-webkit-slider-thumb]:h-3.5
                  [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-accent"
              />
              <button
                onClick={() => handleApply(policy.id)}
                disabled={!canApply}
                className={`text-xs px-3 py-1.5 rounded-lg font-semibold transition-all ${
                  canApply
                    ? 'bg-accent/20 text-accent hover:bg-accent/30'
                    : 'bg-border/50 text-muted cursor-not-allowed'
                }`}
              >
                Enact
              </button>
            </div>
          </div>
        );
      })}

      {policies.length === 0 && (
        <div className="text-center text-muted py-8 text-sm">
          No policies available in this era.
        </div>
      )}
    </div>
  );
}
