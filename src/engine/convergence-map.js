// Convergence Map — Phase Space with Attractor Basins
// Ported from sim/convergence_map.py

export const STANDARD_BASINS = [
  { name: "Failed State Repeller", cx: 8, cy: 5, radius: 18, strength: 0.6, isTrap: true, isDesirable: false,
    desc: "Very low complexity and institutional quality. A repeller — escape requires extraordinary effort." },
  { name: "Extractive Growth Trap", cx: 35, cy: 15, radius: 22, strength: 0.55, isTrap: true, isDesirable: false,
    desc: "Growth without development. Hard to escape because elites benefit from the status quo." },
  { name: "Middle-Income Trap", cx: 55, cy: 35, radius: 25, strength: 0.50, isTrap: true, isDesirable: false,
    desc: "Growth slows as cheap labor advantages fade, but institutions aren't strong enough for innovation-led growth." },
  { name: "Liberal Market Attractor", cx: 75, cy: 60, radius: 28, strength: 0.45, isTrap: false, isDesirable: true,
    desc: "High economic complexity with adequate institutions. Market-led growth. The Anglo-American model." },
  { name: "Coordinated Market Attractor", cx: 78, cy: 80, radius: 30, strength: 0.48, isTrap: false, isDesirable: true,
    desc: "High complexity with strong institutions. The Nordic/Rhine development model." },
  { name: "Developmental State Attractor", cx: 82, cy: 65, radius: 26, strength: 0.47, isTrap: false, isDesirable: true,
    desc: "Very high economic complexity driven by state-led industrial policy. The East Asian model." },
];

export function distance(a, b) {
  return Math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2);
}

export function gravitationalPull(position, basins = STANDARD_BASINS) {
  let dx = 0, dy = 0;
  for (const basin of basins) {
    const dist = distance(position, { x: basin.cx, y: basin.cy });
    if (dist < 0.5) continue;
    const effectiveDist = Math.max(dist, 0.5);
    let force = basin.strength / effectiveDist * basin.radius * 0.3;
    if (basin.name === "Failed State Repeller") force *= -1;
    dx += (basin.cx - position.x) / effectiveDist * force;
    dy += (basin.cy - position.y) / effectiveDist * force;
  }
  const maxDrift = 5;
  return {
    dx: Math.max(-maxDrift, Math.min(maxDrift, dx)),
    dy: Math.max(-maxDrift, Math.min(maxDrift, dy)),
  };
}

export function dominantBasin(position, basins = STANDARD_BASINS) {
  let best = null, bestForce = 0;
  for (const basin of basins) {
    const dist = distance(position, { x: basin.cx, y: basin.cy });
    const force = basin.strength / Math.max(dist, 0.5) * basin.radius;
    if (force > bestForce) { bestForce = force; best = basin; }
  }
  return best;
}

export function convergenceDistance(position, basins = STANDARD_BASINS) {
  const desirable = basins.filter(b => b.isDesirable);
  if (!desirable.length) return 100;
  return Math.min(...desirable.map(b => distance(position, { x: b.cx, y: b.cy })));
}

export function computeEconomicComplexity(state) {
  const gdpComp = Math.min(60, Math.log10(Math.max(500, state.gdpPerCapitaPPP) / 500) * 25);
  const indComp = state.industrialLaborShare * 30;
  const exportComp = state.exportDiversity * 20;
  const humanComp = state.literacyRate * 15;
  const innovComp = (0.05 + state.dCoefficient / 200) * 15;
  return Math.max(0, Math.min(100, gdpComp + indComp + exportComp + humanComp + innovComp));
}

export function computeInstitutionalQuality(state) {
  return state.propertyRights * 20 + state.stateCapacity * 25 +
         state.ruleOfLaw * 20 + (1 - state.corruptionControl) * 20 +
         state.regulatoryQuality * 15;
}
