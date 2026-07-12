// Crisis & Event System
// Ported from sim/events.py

const CRISIS_TEMPLATES = [
  { key: "financial_panic", name: "Financial Panic", severity: 0.7, duration: 2, gdpImpact: -0.08, instImpact: -0.05, socialImpact: -0.10, dImpact: -3, reformBonus: 2.5, triggers: ["political_instability", "sovereign_debt_crisis"] },
  { key: "sovereign_debt_crisis", name: "Sovereign Debt Crisis", severity: 0.75, duration: 3, gdpImpact: -0.12, instImpact: -0.08, socialImpact: -0.15, dImpact: -5, reformBonus: 3.0, triggers: ["political_instability", "social_unrest"] },
  { key: "hyperinflation", name: "Hyperinflation", severity: 0.85, duration: 2, gdpImpact: -0.15, instImpact: -0.10, socialImpact: -0.20, dImpact: -8, reformBonus: 3.5, triggers: ["political_instability", "social_unrest", "regime_change"] },
  { key: "political_instability", name: "Political Instability", severity: 0.6, duration: 1, gdpImpact: -0.03, instImpact: -0.12, socialImpact: -0.10, dImpact: -2, reformBonus: 4.0, triggers: ["financial_panic", "ethnic_conflict", "regime_change"] },
  { key: "ethnic_conflict", name: "Ethnic Conflict Flare-Up", severity: 0.8, duration: 3, gdpImpact: -0.10, instImpact: -0.15, socialImpact: -0.30, dImpact: -6, reformBonus: 1.5, triggers: ["political_instability", "external_intervention"] },
  { key: "environmental_disaster", name: "Environmental Disaster", severity: 0.5, duration: 1, gdpImpact: -0.05, instImpact: -0.02, socialImpact: -0.05, dImpact: -2, reformBonus: 2.0, triggers: ["social_unrest"] },
  { key: "commodity_price_collapse", name: "Commodity Price Collapse", severity: 0.6, duration: 2, gdpImpact: -0.07, instImpact: -0.03, socialImpact: -0.08, dImpact: -1, reformBonus: 2.5, triggers: ["sovereign_debt_crisis", "political_instability"] },
  { key: "external_intervention", name: "External Intervention", severity: 0.9, duration: 4, gdpImpact: -0.15, instImpact: -0.20, socialImpact: -0.25, dImpact: -10, reformBonus: 2.0, triggers: ["political_instability", "ethnic_conflict", "regime_change"] },
  { key: "demographic_shock", name: "Demographic Shock", severity: 0.4, duration: 5, gdpImpact: -0.04, instImpact: -0.02, socialImpact: -0.10, dImpact: -1, reformBonus: 1.8, triggers: ["social_unrest"] },
  { key: "pandemic", name: "Pandemic", severity: 0.7, duration: 2, gdpImpact: -0.06, instImpact: -0.03, socialImpact: -0.12, dImpact: -2, reformBonus: 2.8, triggers: ["financial_panic", "political_instability"] },
  { key: "social_unrest", name: "Social Unrest", severity: 0.5, duration: 1, gdpImpact: -0.04, instImpact: -0.05, socialImpact: -0.10, dImpact: -2, reformBonus: 3.0, triggers: ["political_instability"] },
  { key: "regime_change", name: "Regime Change", severity: 0.9, duration: 3, gdpImpact: -0.10, instImpact: -0.20, socialImpact: -0.15, dImpact: -8, reformBonus: 5.0, triggers: ["political_instability", "ethnic_conflict", "social_unrest"] },
];

const EVENT_TEMPLATES = [
  { key: "technology_breakthrough", name: "Technology Breakthrough", prob: 0.03, gdpImpact: 0.02, dChange: 2 },
  { key: "foreign_investment_wave", name: "Foreign Investment Wave", prob: 0.04, gdpImpact: 0.03, dChange: 1.5, instChange: 0.02 },
  { key: "diaspora_return", name: "Diaspora Return Wave", prob: 0.03, gdpImpact: 0.02, dChange: 3, instChange: 0.03 },
  { key: "resource_discovery", name: "New Resource Discovery", prob: 0.02, gdpImpact: 0.04, dChange: -1, instChange: -0.02 },
  { key: "cultural_renaissance", name: "Cultural Renaissance", prob: 0.04, dChange: 2, instChange: 0.01, socialChange: 0.05 },
  { key: "trade_agreement", name: "Favorable Trade Agreement", prob: 0.05, gdpImpact: 0.02, dChange: 1 },
  { key: "leader_emergence", name: "Transformational Leader", prob: 0.02, dChange: 1, instChange: 0.05, socialChange: 0.05 },
];

export class EventEngine {
  constructor(seed = null) {
    this.seed = seed || Math.floor(Math.random() * 1000000);
    this.rng = this._createRng(this.seed);
    this.activeCrises = [];
    this.crisisHistory = [];
    this.eventHistory = [];
  }

  _createRng(s) {
    // Simple mulberry32 PRNG
    let state = s;
    return () => {
      state |= 0; state = state + 0x6D2B79F5 | 0;
      var t = Math.imul(state ^ state >>> 15, 1 | state);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
  }

  checkCrisis(state, year, era) {
    const baseProb = 0.015;
    const modifiers = {};
    if (state.institutionalQuality < 0.3) modifiers.political_instability = 2.5;
    else if (state.institutionalQuality < 0.5) modifiers.political_instability = 1.5;
    if (state.ethnicFragmentationIndex > 0.6) modifiers.ethnic_conflict = 2.0;
    else if (state.ethnicFragmentationIndex > 0.4) modifiers.ethnic_conflict = 1.3;
    if (state.ethnicTensionStored > 0.5) modifiers.ethnic_conflict = (modifiers.ethnic_conflict || 1) + 2;
    if (state.resourceDependency > 0.4) modifiers.commodity_price_collapse = 2.5;
    if (state.fiscalHealth < 0.3) modifiers.sovereign_debt_crisis = 2.0;
    if (state.environmentalDamageAccumulated > 0.6) modifiers.environmental_disaster = 3.0;

    for (const ct of CRISIS_TEMPLATES) {
      let prob = baseProb * (modifiers[ct.key] || 1);
      if (era === "era1_nation_building") {
        if (["hyperinflation", "pandemic"].includes(ct.key)) prob *= 0.5;
        if (ct.key === "external_intervention") prob *= 2.0;
      } else if (era === "era2_planned_development") {
        if (ct.key === "financial_panic") prob *= 0.3;
        if (ct.key === "environmental_disaster") prob *= 1.5;
      } else if (era === "era3_convergence") {
        if (ct.key === "financial_panic") prob *= 2.0;
        if (ct.key === "sovereign_debt_crisis") prob *= 1.5;
      }
      if (this.rng() < prob) {
        const crisis = { ...ct, remainingDuration: ct.duration };
        this.activeCrises.push(crisis);
        this.crisisHistory.push({ year, crisis: ct.key, severity: ct.severity });
        return crisis;
      }
    }
    return null;
  }

  checkRandomEvent() {
    for (const et of EVENT_TEMPLATES) {
      if (this.rng() < et.prob) {
        this.eventHistory.push({ event: et.key });
        return { ...et };
      }
    }
    return null;
  }

  cascadeCheck() {
    const newCrises = [];
    for (const active of this.activeCrises) {
      for (const triggerKey of (active.triggers || [])) {
        const template = CRISIS_TEMPLATES.find(c => c.key === triggerKey);
        if (!template) continue;
        if (this.rng() < 0.12) {
          if (!this.activeCrises.find(c => c.key === triggerKey)) {
            const cascade = { ...template, remainingDuration: template.duration };
            this.activeCrises.push(cascade);
            newCrises.push(cascade);
          }
        }
      }
    }
    return newCrises;
  }

  resolveCrises() {
    const resolved = [];
    this.activeCrises = this.activeCrises.filter(c => {
      c.remainingDuration--;
      if (c.remainingDuration <= 0) { resolved.push(c); return false; }
      return true;
    });
    return resolved;
  }

  get reformMultiplier() {
    if (!this.activeCrises.length) return 1.0;
    const totalBonus = this.activeCrises.reduce((s, c) => s + c.reformBonus, 0);
    return 1.0 + Math.sqrt(totalBonus) * 0.5;
  }

  get totalImpact() {
    const impact = { gdp: 0, inst: 0, social: 0, d: 0 };
    for (const c of this.activeCrises) {
      impact.gdp += c.gdpImpact;
      impact.inst += c.instImpact;
      impact.social += c.socialImpact;
      impact.d += c.dImpact;
    }
    return impact;
  }
}
