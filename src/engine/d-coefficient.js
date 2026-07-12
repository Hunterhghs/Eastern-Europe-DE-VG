// D-Coefficient Engine — The Medium Coefficient
// Ported from sim/d_coefficient.py

const TERRAIN_ROUGHNESS = {
  flat_coastal: 0.1,
  river_plains_uplands: 0.35,
  fertile_plains: 0.15,
  mountainous: 0.70,
  alpine: 0.85,
};

const ERA_WEIGHTS = {
  era1_nation_building: {
    infrastructure: 0.40, institutional: 0.25, humanCapital: 0.15,
    information: 0.05, geographic: 0.15,
  },
  era2_planned_development: {
    infrastructure: 0.30, institutional: 0.35, humanCapital: 0.20,
    information: 0.05, geographic: 0.10,
  },
  era3_convergence: {
    infrastructure: 0.20, institutional: 0.25, humanCapital: 0.25,
    information: 0.20, geographic: 0.10,
  },
};

export function calculateDCoefficient(state, geography, era) {
  const weights = ERA_WEIGHTS[era] || ERA_WEIGHTS.era1_nation_building;
  const d = state.dCoefficient / 100;

  // Infrastructure Index
  const landlockPenalty = geography.landlocked ? 0.6 : 1.0;
  const transport = (state.roadDensity * 0.4 + state.railDensity * 0.3) * landlockPenalty;
  const energy = state.electricityAccess * 0.15;
  const port = (geography.portAccess ? 0.8 : 0) * 0.15 * (geography.landlocked ? 0.3 : 1.0);
  const infra = Math.min(1, transport + energy + port);

  // Institutional Index
  const inst = state.institutionalTrust * 0.40 + state.stateCapacity * 0.35 + state.propertyRights * 0.25;

  // Human Capital Index
  const avgQuality = state.literacyRate * 0.4 + (state.meanYearsSchooling / 16) * 0.3;
  const equalityBonus = (1 - state.educationGini) * 0.3;
  const human = Math.min(1, avgQuality + equalityBonus);

  // Information Index
  const languagePenalty = state.ethnicFragmentationIndex;
  const info = state.mediaFreedom * 0.50 + (1 - languagePenalty) * 0.30 + state.broadbandPenetration * 0.20;

  // Geographic Index
  const terrainFactor = 1 - (TERRAIN_ROUGHNESS[geography.terrain] || 0.5) * 0.7;
  const urbanBonus = state.urbanizationRate * 0.4;
  const sizePenalty = Math.max(0, Math.log10(state.countryAreaKm2 / 25000) * 0.15);
  const geo = Math.max(0.1, Math.min(1, terrainFactor + urbanBonus - sizePenalty));

  const raw = weights.infrastructure * infra + weights.institutional * inst +
              weights.humanCapital * human + weights.information * info +
              weights.geographic * geo;

  return Math.round(raw * 1000) / 10; // one decimal
}

export function diffusionDelay(dValue, distanceTiers = 1) {
  const baseDelay = 2;
  const friction = ((100 - dValue) / 100) * 30;
  return Math.round(baseDelay + friction * distanceTiers);
}
