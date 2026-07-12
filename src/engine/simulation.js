// The Carpathian Crescent — Core Simulation Engine
// Ported from sim/engine.py

import { NATIONS } from './nation-data.js';
import { calculateDCoefficient } from './d-coefficient.js';
import {
  STANDARD_BASINS, gravitationalPull, dominantBasin, convergenceDistance,
  computeEconomicComplexity, computeInstitutionalQuality,
} from './convergence-map.js';
import { EventEngine } from './events.js';

const ERA_CONFIG = {
  era1_nation_building: { name: "Nation-Building", years: [1918, 1945], policyAutonomy: 1.0, reformCapacity: 0.03 },
  era2_planned_development: { name: "Planned Development", years: [1945, 1990], policyAutonomy: 0.3, reformCapacity: 0.02 },
  era3_convergence: { name: "Convergence or Drift", years: [1990, 2025], policyAutonomy: 1.0, reformCapacity: 0.04 },
};

const TERRAIN_MAP = {
  flat_coastal: 0.1, river_plains_uplands: 0.35, fertile_plains: 0.15, mountainous: 0.70, alpine: 0.85,
};

export const POLICIES = {
  era1_nation_building: [
    { id: "education_investment", name: "Education Investment", desc: "Build schools and train teachers.", icon: "📚" },
    { id: "infrastructure_investment", name: "Infrastructure", desc: "Roads, rail, and electricity.", icon: "🏗️" },
    { id: "institution_building", name: "Institution Building", desc: "Found courts, registries, civil service.", icon: "🏛️" },
    { id: "land_reform", name: "Land Reform", desc: "Redistribute agricultural land.", icon: "🌾" },
    { id: "health_investment", name: "Public Health", desc: "Sanitation, hospitals, vaccination.", icon: "🏥" },
    { id: "social_cohesion", name: "Social Cohesion", desc: "Bridge ethnic and class divisions.", icon: "🤝" },
  ],
  era2_planned_development: [
    { id: "industrial_policy", name: "Industrial Policy", desc: "Build factories and heavy industry.", icon: "🏭" },
    { id: "infrastructure_investment", name: "Infrastructure", desc: "Expand power grid and transport.", icon: "🏗️" },
    { id: "education_investment", name: "Technical Education", desc: "Vocational training and engineering.", icon: "🔧" },
    { id: "health_investment", name: "Public Health", desc: "Expand healthcare access.", icon: "🏥" },
    { id: "institution_building", name: "State Capacity", desc: "Strengthen planning and administration.", icon: "🏛️" },
    { id: "social_cohesion", name: "Social Management", desc: "Manage suppressed tensions.", icon: "🤝" },
  ],
  era3_convergence: [
    { id: "eu_accession_prep", name: "EU Accession Prep", desc: "Align institutions with European standards.", icon: "🇪🇺" },
    { id: "institution_building", name: "Institutional Reform", desc: "Rule of law, anti-corruption.", icon: "⚖️" },
    { id: "anti_corruption", name: "Anti-Corruption Drive", desc: "Prosecute graft, build transparency.", icon: "🔍" },
    { id: "digital_infrastructure", name: "Digital Infrastructure", desc: "Broadband, e-government, tech hubs.", icon: "💻" },
    { id: "environmental_cleanup", name: "Environmental Cleanup", desc: "Remediate industrial pollution.", icon: "🌿" },
    { id: "education_investment", name: "Higher Education", desc: "Universities and research capacity.", icon: "🎓" },
    { id: "social_cohesion", name: "Social Integration", desc: "Heal divisions, build civil society.", icon: "🤝" },
  ],
};

export function createInitialState(nationId) {
  const nation = NATIONS[nationId];
  if (!nation) throw new Error(`Unknown nation: ${nationId}`);
  const s = nation.era1Start;
  const g = nation.geography;

  const state = {
    nationId,
    year: 1918,
    era: "era1_nation_building",
    // Demographics
    populationMillions: nation.population1918M,
    urbanizationRate: s.urbanizationRate,
    literacyRate: s.literacyRate,
    lifeExpectancy: s.lifeExpectancy,
    meanYearsSchooling: s.literacyRate * 6,
    // Economy
    gdpPerCapitaPPP: s.gdpPerCapitaPPP,
    giniCoefficient: s.giniCoefficient,
    agriculturalLaborShare: s.agriculturalLaborShare,
    industrialLaborShare: s.industrialLaborShare,
    serviceLaborShare: 1 - s.agriculturalLaborShare - s.industrialLaborShare,
    exportDiversity: 0.15,
    resourceDependency: g.naturalResources.some(r => r.includes("oil")) ? 0.3 : 0.1,
    fiscalHealth: s.institutionalQuality * 0.5,
    // Infrastructure
    infrastructureQuality: s.infrastructureQuality,
    electricityAccess: s.electricityAccessPct,
    broadbandPenetration: 0,
    roadDensity: s.pavedRoadKm / nation.areaKm2 * 10,
    railDensity: s.railKm / nation.areaKm2 * 10,
    // Institutional
    institutionalQuality: s.institutionalQuality,
    propertyRights: s.institutionalQuality * 0.5,
    stateCapacity: s.institutionalQuality * 0.6,
    corruptionControl: s.institutionalQuality * 0.3,
    regulatoryQuality: s.institutionalQuality * 0.2,
    ruleOfLaw: s.institutionalQuality * 0.4,
    institutionalTrust: s.institutionalQuality * 0.7,
    // Social
    socialCohesion: 0.55 - s.giniCoefficient * 0.5,
    ethnicFragmentationIndex: nation.ethnicFragmentation,
    ethnicTensionStored: 0,
    mediaFreedom: 0.35,
    // Environment
    environmentalDamageAccumulated: 0.05,
    renewableEnergyShare: 0.02,
    // Meta
    dCoefficient: s.dCoefficient,
    economicComplexity: computeEconomicComplexity({
      gdpPerCapitaPPP: s.gdpPerCapitaPPP, industrialLaborShare: s.industrialLaborShare,
      exportDiversity: 0.15, literacyRate: s.literacyRate, dCoefficient: s.dCoefficient,
    }),
    institutionalQualityPhase: computeInstitutionalQuality({
      propertyRights: s.institutionalQuality * 0.5, stateCapacity: s.institutionalQuality * 0.6,
      ruleOfLaw: s.institutionalQuality * 0.4, corruptionControl: s.institutionalQuality * 0.3,
      regulatoryQuality: s.institutionalQuality * 0.2,
    }),
    policyAutonomy: 1.0,
    reformCapacity: 0.03,
    inCrisis: false,
    crisisReformMultiplier: 1.0,
    // Derived
    countryAreaKm2: nation.areaKm2,
    educationGini: s.giniCoefficient * 1.2,
    institutions: s.institutionalDepth, // simplified depth tracker
    legacy: s.institutionalLegacy,
  };
  return state;
}

export function createSimulation(nationId, seed = null) {
  const state = createInitialState(nationId);
  const nation = NATIONS[nationId];
  const events = new EventEngine(seed);
  let history = [{ ...state }];
  let log = [];
  let policyCycle = 0;
  let transitionJustHappened = null;

  function applyPolicy(policyId, investmentLevel = 0.5) {
    const s = state;
    const eraConfig = ERA_CONFIG[s.era];
    const effective = investmentLevel * eraConfig.reformCapacity * (s.inCrisis ? events.reformMultiplier : 1.0);
    const eff = Math.min(0.3, Math.max(0.005, effective));

    const actions = {
      education_investment: () => {
        s.literacyRate = Math.min(0.99, s.literacyRate + eff * 0.15);
        s.meanYearsSchooling += eff * 3;
        return `Education: literacy ${(s.literacyRate * 100).toFixed(0)}%`;
      },
      infrastructure_investment: () => {
        s.infrastructureQuality = Math.min(1, s.infrastructureQuality + eff * 0.2);
        s.roadDensity += eff * 0.5;
        s.railDensity += eff * 0.3;
        s.electricityAccess = Math.min(1, s.electricityAccess + eff * 0.25);
        return `Infrastructure: quality ${s.infrastructureQuality.toFixed(2)}`;
      },
      institution_building: () => {
        s.stateCapacity = Math.min(1, s.stateCapacity + eff * 0.2);
        s.propertyRights = Math.min(1, s.propertyRights + eff * 0.15);
        s.ruleOfLaw = Math.min(1, s.ruleOfLaw + eff * 0.12);
        s.corruptionControl = Math.min(1, s.corruptionControl + eff * 0.10);
        return `Institutions: state capacity ${s.stateCapacity.toFixed(2)}`;
      },
      land_reform: () => {
        s.giniCoefficient = Math.max(0.20, s.giniCoefficient - eff * 0.3);
        s.agriculturalLaborShare *= (1 - eff * 0.1);
        return `Land reform: Gini ${s.giniCoefficient.toFixed(3)}`;
      },
      industrial_policy: () => {
        s.industrialLaborShare = Math.min(0.55, s.industrialLaborShare + eff * 0.15);
        s.exportDiversity = Math.min(1, s.exportDiversity + eff * 0.1);
        s.environmentalDamageAccumulated += eff * 0.05;
        return `Industry: share ${(s.industrialLaborShare * 100).toFixed(0)}%`;
      },
      health_investment: () => {
        s.lifeExpectancy = Math.min(85, s.lifeExpectancy + eff * 8);
        return `Health: life expectancy ${s.lifeExpectancy.toFixed(0)}`;
      },
      anti_corruption: () => {
        s.corruptionControl = Math.min(1, s.corruptionControl + eff * 0.25);
        s.institutionalQuality = Math.min(1, s.institutionalQuality + eff * 0.2);
        return `Anti-corruption: control ${s.corruptionControl.toFixed(2)}`;
      },
      digital_infrastructure: () => {
        s.broadbandPenetration = Math.min(0.98, s.broadbandPenetration + eff * 0.3);
        s.dCoefficient += eff * 5;
        return `Digital: broadband ${(s.broadbandPenetration * 100).toFixed(0)}%`;
      },
      environmental_cleanup: () => {
        s.environmentalDamageAccumulated = Math.max(0, s.environmentalDamageAccumulated - eff * 0.2);
        s.renewableEnergyShare = Math.min(1, s.renewableEnergyShare + eff * 0.15);
        return `Environment: damage ${s.environmentalDamageAccumulated.toFixed(2)}`;
      },
      social_cohesion: () => {
        s.socialCohesion = Math.min(1, s.socialCohesion + eff * 0.2);
        s.ethnicTensionStored = Math.max(0, s.ethnicTensionStored - eff * 0.15);
        return `Social: cohesion ${s.socialCohesion.toFixed(2)}`;
      },
      eu_accession_prep: () => {
        if (s.era === "era3_convergence") {
          s.institutionalQuality = Math.min(1, s.institutionalQuality + eff * 0.3);
          s.regulatoryQuality = Math.min(1, s.regulatoryQuality + eff * 0.35);
          s.propertyRights = Math.min(1, s.propertyRights + eff * 0.25);
          s.exportDiversity = Math.min(1, s.exportDiversity + eff * 0.2);
          return `EU prep: regulatory quality ${s.regulatoryQuality.toFixed(2)}`;
        }
        return "EU accession prep not available in this era.";
      },
    };

    const result = actions[policyId] ? actions[policyId]() : `Unknown policy: ${policyId}`;
    s.dCoefficient = calculateDCoefficient(s, nation.geography, s.era);
    s.economicComplexity = computeEconomicComplexity(s);
    s.institutionalQualityPhase = computeInstitutionalQuality(s);
    return result;
  }

  function tick() {
    const s = state;
    const yearLog = { year: s.year, events: [] };

    // 1. Crisis check
    const crisis = events.checkCrisis(s, s.year, s.era);
    if (crisis) {
      s.inCrisis = true;
      s.crisisReformMultiplier = events.reformMultiplier;
      yearLog.events.push({ type: "crisis", name: crisis.name, severity: crisis.severity });
    } else {
      s.crisisReformMultiplier = 1.0;
    }

    // 2. Random events
    const event = events.checkRandomEvent();
    if (event) {
      if (event.gdpImpact) s.gdpPerCapitaPPP = Math.max(100, s.gdpPerCapitaPPP * (1 + event.gdpImpact));
      if (event.dChange) s.dCoefficient += event.dChange;
      if (event.instChange) s.institutionalQuality = Math.max(0, Math.min(1, s.institutionalQuality + event.instChange));
      if (event.socialChange) s.socialCohesion = Math.max(0, Math.min(1, s.socialCohesion + event.socialChange));
      yearLog.events.push({ type: "event", name: event.name });
    }

    // 3. Crisis effects
    if (s.inCrisis) {
      const impact = events.totalImpact;
      const gdpImpact = Math.max(-0.20, impact.gdp);
      s.gdpPerCapitaPPP = Math.max(100, s.gdpPerCapitaPPP * (1 + gdpImpact));
      s.institutionalQuality = Math.max(0, Math.min(1, s.institutionalQuality + impact.inst));
      s.socialCohesion = Math.max(0, Math.min(1, s.socialCohesion + impact.social));
      s.dCoefficient = Math.max(0, s.dCoefficient + impact.d);
    }

    // 4. Resolve crises
    const resolved = events.resolveCrises();
    for (const c of resolved) yearLog.events.push({ type: "resolved", name: c.name });

    if (!events.activeCrises.length) {
      s.inCrisis = false;
      s.crisisReformMultiplier = 1.0;
    }

    // 5. Cascades
    const cascades = events.cascadeCheck();
    for (const c of cascades) yearLog.events.push({ type: "cascade", name: c.name });

    // 6. Passive changes
    applyPassiveChanges();

    // 7. Update computed
    s.dCoefficient = calculateDCoefficient(s, nation.geography, s.era);
    s.economicComplexity = computeEconomicComplexity(s);
    s.institutionalQualityPhase = computeInstitutionalQuality(s);

    // 8. Gravitational drift
    const pull = gravitationalPull({ x: s.economicComplexity, y: s.institutionalQualityPhase });
    s.economicComplexity = Math.max(0, Math.min(100, s.economicComplexity + pull.dx));
    s.institutionalQualityPhase = Math.max(0, Math.min(100, s.institutionalQualityPhase + pull.dy));

    // 9. Advance year
    s.year++;
    s.institutions++; // depth grows

    // 10. Record history
    history.push({ ...s });

    return yearLog;
  }

  function applyPassiveChanges() {
    const s = state;
    const d = s.dCoefficient / 100;

    // Population
    let popGrowth = s.year < 1950 ? 0.012 : s.year < 1990 ? 0.008 : 0.002;
    s.populationMillions *= (1 + popGrowth);

    // Urbanization
    s.urbanizationRate = Math.min(0.85, s.urbanizationRate + (s.industrialLaborShare * 0.02 + s.serviceLaborShare * 0.015) * d);

    // Literacy
    const litGain = (0.02 + s.dCoefficient * 0.001) * (1 - s.literacyRate);
    s.literacyRate = Math.min(0.99, s.literacyRate + litGain);
    s.meanYearsSchooling = Math.min(16, s.meanYearsSchooling + litGain * 8);

    // Life expectancy
    s.lifeExpectancy = Math.min(85, s.lifeExpectancy + 0.15 + s.dCoefficient * 0.003);

    // Infrastructure
    s.infrastructureQuality = Math.min(1, s.infrastructureQuality + 0.003 * d);
    s.electricityAccess = Math.min(1, s.electricityAccess + 0.02 * d);
    if (s.year > 1995) s.broadbandPenetration = Math.min(0.98, s.broadbandPenetration + 0.04 * d);

    // Environment
    if (s.era === "era2_planned_development") {
      s.environmentalDamageAccumulated = Math.min(1, s.environmentalDamageAccumulated + s.industrialLaborShare * 0.008);
    }

    // Structural change
    const svcGrowth = 0.003 + d * 0.004;
    s.serviceLaborShare = Math.min(0.80, s.serviceLaborShare + svcGrowth);
    s.agriculturalLaborShare = Math.max(0.02, s.agriculturalLaborShare - svcGrowth * 0.6);

    // Institutional decay
    s.institutionalQuality = Math.max(0, s.institutionalQuality - 0.001 * (1 - s.stateCapacity));

    // GDP growth
    s.gdpPerCapitaPPP *= (1 + 0.02 + d * 0.03);
  }

  function checkEraTransition() {
    const s = state;
    if (s.era === "era1_nation_building" && s.year >= 1945) return transitionToEra2();
    if (s.era === "era2_planned_development" && s.year >= 1990) return transitionToEra3();
    return null;
  }

  function transitionToEra2() {
    const s = state;
    s.era = "era2_planned_development";
    s.policyAutonomy = 0.3;
    s.reformCapacity = 0.02;
    s.ethnicTensionStored = Math.max(0, 0.5 - s.socialCohesion) * s.ethnicFragmentationIndex;
    s.exportDiversity = Math.max(0.1, s.exportDiversity * 0.4);
    return { from: "era1_nation_building", to: "era2_planned_development", eraName: "Planned Development",
      details: [`Ethnic tension stored: ${s.ethnicTensionStored.toFixed(2)}`, "Trade network realigned"] };
  }

  function transitionToEra3() {
    const s = state;
    s.era = "era3_convergence";
    s.policyAutonomy = 1.0;
    s.reformCapacity = 0.04;
    const industrialPenalty = s.industrialLaborShare * 0.4;
    const gdpShock = 0.15 + industrialPenalty;
    s.gdpPerCapitaPPP = Math.max(100, s.gdpPerCapitaPPP * (1 - gdpShock));
    s.agriculturalLaborShare += s.industrialLaborShare * 0.3;
    s.industrialLaborShare *= 0.5;
    const details = [`GDP shock: -${(gdpShock * 100).toFixed(0)}%`, "EU accession track available"];
    if (s.ethnicTensionStored > 0.3) {
      s.socialCohesion = Math.max(0.1, s.socialCohesion - s.ethnicTensionStored * 0.7);
      details.push(`⚠ Ethnic tensions releasing! Social cohesion: ${s.socialCohesion.toFixed(2)}`);
      s.ethnicTensionStored *= 0.3;
    }
    if (s.environmentalDamageAccumulated > 0.5) {
      details.push(`⚠ Environmental damage: ${s.environmentalDamageAccumulated.toFixed(2)}`);
    }
    s.mediaFreedom = Math.min(1, s.mediaFreedom + 0.4);
    return { from: "era2_planned_development", to: "era3_convergence", eraName: "Convergence or Drift", details };
  }

  function getScore() {
    const s = state;
    const convRemaining = convergenceDistance({ x: s.economicComplexity, y: s.institutionalQualityPhase });
    const score = Math.max(0, 100 - convRemaining);
    let verdict;
    if (score > 80) verdict = "Strong convergence — on track for high-development equilibrium";
    else if (score > 50) verdict = "Partial convergence — making progress but trajectory uncertain";
    else if (score > 25) verdict = "Slow convergence — structural barriers remain significant";
    else verdict = "Divergence — fundamental transformation needed";
    const basin = dominantBasin({ x: s.economicComplexity, y: s.institutionalQualityPhase });
    return { score, verdict, converenceRemaining: convRemaining, dominantBasin: basin?.name || "none",
      position: { x: s.economicComplexity, y: s.institutionalQualityPhase } };
  }

  return {
    get state() { return state; },
    get nation() { return nation; },
    get history() { return history; },
    get log() { return log; },
    get events() { return events; },
    tick, applyPolicy, checkEraTransition, getScore,
    getAvailablePolicies: () => POLICIES[state.era] || [],
    getEraConfig: () => ERA_CONFIG[state.era],
    getPhasePosition: () => ({ x: state.economicComplexity, y: state.institutionalQualityPhase }),
    isGameOver: () => state.year > 2025,
    reset: () => { throw new Error("Create a new simulation instead"); },
  };
}
