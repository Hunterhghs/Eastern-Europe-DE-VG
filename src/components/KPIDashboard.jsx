import React from 'react';

export default function KPIDashboard({ state, nation }) {
  const kpis = [
    { label: 'GDP per capita', value: `$${state.gdpPerCapitaPPP.toLocaleString(undefined, { maximumFractionDigits: 0 })}`, sub: 'PPP', color: 'text-accent' },
    { label: 'D-Coefficient', value: state.dCoefficient.toFixed(1), sub: '/ 100', color: state.dCoefficient > 50 ? 'text-green' : state.dCoefficient > 30 ? 'text-gold' : 'text-warn' },
    { label: 'Life Expectancy', value: `${state.lifeExpectancy.toFixed(0)}`, sub: 'years', color: state.lifeExpectancy > 70 ? 'text-green' : 'text-gold' },
    { label: 'Literacy', value: `${(state.literacyRate * 100).toFixed(0)}%`, sub: '', color: state.literacyRate > 0.8 ? 'text-green' : 'text-gold' },
    { label: 'Urbanization', value: `${(state.urbanizationRate * 100).toFixed(0)}%`, sub: '', color: 'text-muted' },
    { label: 'Gini', value: state.giniCoefficient.toFixed(2), sub: 'inequality', color: state.giniCoefficient < 0.4 ? 'text-green' : 'text-warn' },
    { label: 'Social Cohesion', value: (state.socialCohesion * 100).toFixed(0) + '%', sub: '', color: state.socialCohesion > 0.5 ? 'text-green' : 'text-warn' },
    { label: 'Population', value: `${state.populationMillions.toFixed(1)}M`, sub: '', color: 'text-muted' },
    { label: 'Inst. Quality', value: state.institutionalQuality.toFixed(2), sub: '/ 1.0', color: state.institutionalQuality > 0.5 ? 'text-green' : 'text-warn' },
    { label: 'Industry', value: `${(state.industrialLaborShare * 100).toFixed(0)}%`, sub: 'labor share', color: 'text-muted' },
    { label: 'Environment', value: (state.environmentalDamageAccumulated * 100).toFixed(0) + '%', sub: 'damage', color: state.environmentalDamageAccumulated < 0.3 ? 'text-green' : state.environmentalDamageAccumulated < 0.6 ? 'text-gold' : 'text-warn' },
    { label: 'Crisis', value: state.inCrisis ? '⚠ ACTIVE' : 'Stable', sub: '', color: state.inCrisis ? 'text-warn' : 'text-green' },
  ];

  return (
    <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2">
      {kpis.map(kpi => (
        <div key={kpi.label} className="kpi-card py-3 px-3">
          <div className="text-[10px] text-muted uppercase tracking-wide">{kpi.label}</div>
          <div className={`text-lg font-bold ${kpi.color}`}>{kpi.value}</div>
          {kpi.sub && <div className="text-[10px] text-muted">{kpi.sub}</div>}
        </div>
      ))}
    </div>
  );
}
