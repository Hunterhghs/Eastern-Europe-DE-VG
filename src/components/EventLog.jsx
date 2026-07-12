import React from 'react';

export default function EventLog({ events }) {
  if (!events || events.length === 0) {
    return (
      <div className="p-4 text-center text-muted text-sm py-12">
        No events this year. The nation is stable.
      </div>
    );
  }

  const typeConfig = {
    crisis: { bg: 'bg-warn/10', border: 'border-warn/30', text: 'text-warn', icon: '🔥' },
    event: { bg: 'bg-green/10', border: 'border-green/30', text: 'text-green', icon: '✨' },
    resolved: { bg: 'bg-accent/10', border: 'border-accent/30', text: 'text-accent', icon: '✅' },
    cascade: { bg: 'bg-gold/10', border: 'border-gold/30', text: 'text-gold', icon: '⛓️' },
  };

  return (
    <div className="p-4 space-y-2">
      <h3 className="text-sm font-semibold text-muted uppercase tracking-wide mb-3">Events This Year</h3>
      {events.map((evt, i) => {
        const config = typeConfig[evt.type] || typeConfig.event;
        return (
          <div key={i} className={`${config.bg} border ${config.border} rounded-lg px-3 py-2`}>
            <span className="mr-2">{config.icon}</span>
            <span className={`text-sm font-semibold ${config.text}`}>
              {evt.type === 'crisis' ? `CRISIS: ${evt.name}` :
               evt.type === 'resolved' ? `Resolved: ${evt.name}` :
               evt.type === 'cascade' ? `Cascade: ${evt.name}` :
               evt.name}
            </span>
            {evt.severity !== undefined && (
              <span className="text-xs text-muted ml-2">
                severity: {(evt.severity * 100).toFixed(0)}%
              </span>
            )}
          </div>
        );
      })}
    </div>
  );
}
