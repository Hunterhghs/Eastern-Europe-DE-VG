"""
The Carpathian Crescent — Core Simulation Engine

Orchestrates the full multi-era simulation: nation state, D-coefficient,
convergence map, institutional DNA, events, and era transitions.

Usage:
    engine = SimulationEngine("moravia_nord")
    engine.run()
    print(engine.summary())
"""

import json
import math
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from .d_coefficient import (
    DCoefficientEngine, DCoefficientInputs, DCoefficientWeights,
    create_inputs_from_nation,
)
from .institutions import (
    InstitutionalDNA, Institution, seed_initial_institutions,
)
from .convergence_map import (
    ConvergenceMap, PhasePosition, AttractorBasin,
    compute_economic_complexity, compute_institutional_quality,
    STANDARD_BASINS,
)
from .events import EventEngine, Crisis


DATA_DIR = Path(__file__).parent / "data"


@dataclass
class NationState:
    """The complete state of a nation at a point in time."""
    nation_id: str
    year: int
    era: str
    
    # Demographics
    population_millions: float
    urbanization_rate: float  # 0-1
    literacy_rate: float  # 0-1
    life_expectancy: float
    mean_years_schooling: float
    
    # Economy
    gdp_per_capita_ppp: float
    gini_coefficient: float  # 0-1
    agricultural_labor_share: float
    industrial_labor_share: float
    service_labor_share: float
    export_diversity: float  # 0-1
    resource_dependency: float  # 0-1
    fiscal_health: float  # 0-1
    
    # Infrastructure
    infrastructure_quality: float
    electricity_access: float
    broadband_penetration: float
    road_density: float
    rail_density: float
    
    # Institutional
    institutional_quality: float
    property_rights: float
    state_capacity: float
    corruption_control: float
    regulatory_quality: float
    rule_of_law: float
    
    # Social
    social_cohesion: float  # 0-1
    ethnic_fragmentation_index: float
    ethnic_tension_stored: float  # suppressed tension, releases in era 3
    media_freedom: float
    
    # Environment
    environmental_damage_accumulated: float  # 0-1
    renewable_energy_share: float
    
    # D-Coefficient
    d_coefficient: float  # 0-100
    
    # Phase space
    economic_complexity: float  # 0-100
    institutional_quality_phase: float  # 0-100
    
    # Meta
    policy_autonomy: float  # 0-1, how much control the player has
    reform_capacity: float  # base reform speed
    in_crisis: bool = False
    crisis_reform_multiplier: float = 1.0


class SimulationEngine:
    """Core simulation orchestrator."""
    
    def __init__(self, nation_id: str, seed: Optional[int] = None):
        self.nation_id = nation_id
        
        # Load data
        with open(DATA_DIR / "nations.json") as f:
            nations_data = json.load(f)
        with open(DATA_DIR / "eras.json") as f:
            eras_data = json.load(f)
        
        self.nation_data = nations_data["nations"][nation_id]
        self.eras_data = eras_data
        self.geography = self.nation_data["geography"]
        
        # Initialize subsystems
        self.d_engine = DCoefficientEngine()
        self.convergence_map = ConvergenceMap(basins=STANDARD_BASINS)
        self.event_engine = EventEngine(seed=seed)
        self.rng = random.Random(seed)
        
        # Initialize institutional DNA from legacy
        start = self.nation_data["era1_start"]
        self.institutions = seed_initial_institutions(
            legacy_type=start["institutional_legacy"],
            quality=start["institutional_quality"],
            depth=start["institutional_depth"],
        )
        
        # Create initial state
        self.state = self._create_initial_state()
        
        # History
        self.state_history: List[NationState] = [
            NationState(**{k: v for k, v in self.state.__dict__.items()})
        ]
        self.turn_log: List[str] = []
    
    def _create_initial_state(self) -> NationState:
        """Build the initial NationState from nation data."""
        start = self.nation_data["era1_start"]
        geo = self.geography
        
        # Compute initial D-coefficient
        d_inputs = create_inputs_from_nation(self.nation_data)
        d_value = self.d_engine.calculate(d_inputs)
        
        # Compute phase space position
        econ_complexity = compute_economic_complexity(
            gdp_per_capita=start["gdp_per_capita_ppp"],
            industrial_share=start["industrial_labor_share"],
            export_diversity=0.15,  # era 1 baseline
            human_capital=start["literacy_rate"],
            innovation_index=0.05,  # era 1 baseline
        )
        
        inst_quality_phase = compute_institutional_quality(
            property_rights=start["institutional_quality"] * 0.5,
            state_capacity=start["institutional_quality"] * 0.6,
            rule_of_law=start["institutional_quality"] * 0.4,
            corruption_control=start["institutional_quality"] * 0.3,
            regulatory_quality=start["institutional_quality"] * 0.2,
        )
        
        port_bonus = 0.1 if geo["port_access"] else 0.0
        
        return NationState(
            nation_id=self.nation_id,
            year=1918,
            era="era1_nation_building",
            population_millions=self.nation_data["population_1918_millions"],
            urbanization_rate=start["urbanization_rate"],
            literacy_rate=start["literacy_rate"],
            life_expectancy=start["life_expectancy"],
            mean_years_schooling=start["literacy_rate"] * 6.0,
            gdp_per_capita_ppp=start["gdp_per_capita_ppp"],
            gini_coefficient=start["gini_coefficient"],
            agricultural_labor_share=start["agricultural_labor_share"],
            industrial_labor_share=start["industrial_labor_share"],
            service_labor_share=1.0 - start["agricultural_labor_share"] - start["industrial_labor_share"],
            export_diversity=0.15,
            resource_dependency=0.3 if geo["natural_resources"] and "oil" in str(geo["natural_resources"]).lower() else 0.1,
            fiscal_health=start["institutional_quality"] * 0.5,
            infrastructure_quality=start["infrastructure_quality"],
            electricity_access=start["electricity_access_pct"],
            broadband_penetration=0.0,
            road_density=start["paved_road_km"] / self.nation_data["area_km2"] * 10,
            rail_density=start["rail_km"] / self.nation_data["area_km2"] * 10,
            institutional_quality=start["institutional_quality"],
            property_rights=start["institutional_quality"] * 0.5,
            state_capacity=start["institutional_quality"] * 0.6,
            corruption_control=start["institutional_quality"] * 0.3,
            regulatory_quality=start["institutional_quality"] * 0.2,
            rule_of_law=start["institutional_quality"] * 0.4,
            social_cohesion=0.55 - start["gini_coefficient"] * 0.5,
            ethnic_fragmentation_index=self.nation_data["ethnic_fragmentation_index"],
            ethnic_tension_stored=0.0,
            media_freedom=0.35,
            environmental_damage_accumulated=0.05,
            renewable_energy_share=0.02,
            d_coefficient=d_value,
            economic_complexity=econ_complexity,
            institutional_quality_phase=inst_quality_phase,
            policy_autonomy=1.0,
            reform_capacity=0.03,  # 3% base reform per year
        )
    
    def _update_d_coefficient(self) -> None:
        """Recalculate D-coefficient from current state."""
        d_inputs = DCoefficientInputs(
            road_density=self.state.road_density,
            rail_density=self.state.rail_density,
            electricity_access=self.state.electricity_access,
            broadband_penetration=self.state.broadband_penetration,
            port_quality=0.8 if self.geography["port_access"] else 0.0,
            institutional_trust=self.state.institutional_quality * 0.7,
            state_capacity=self.state.state_capacity,
            property_rights=self.state.property_rights,
            literacy_rate=self.state.literacy_rate,
            mean_years_schooling=self.state.mean_years_schooling,
            education_gini=self.state.gini_coefficient * 1.2,
            media_freedom=self.state.media_freedom,
            language_fragmentation=self.state.ethnic_fragmentation_index,
            terrain_roughness={
                "flat_coastal": 0.1, "river_plains_uplands": 0.35,
                "fertile_plains": 0.15, "mountainous": 0.70, "alpine": 0.85,
            }.get(self.geography["terrain"], 0.5),
            landlocked=self.geography["landlocked"],
            urban_density=self.state.urbanization_rate,
            country_area_km2=self.nation_data["area_km2"],
        )
        self.state.d_coefficient = self.d_engine.calculate(d_inputs)
    
    def _update_phase_position(self) -> None:
        """Update position in the convergence phase space."""
        self.state.economic_complexity = compute_economic_complexity(
            gdp_per_capita=self.state.gdp_per_capita_ppp,
            industrial_share=self.state.industrial_labor_share,
            export_diversity=self.state.export_diversity,
            human_capital=self.state.literacy_rate,
            innovation_index=0.05 + self.state.d_coefficient / 200,
        )
        
        self.state.institutional_quality_phase = compute_institutional_quality(
            property_rights=self.state.property_rights,
            state_capacity=self.state.state_capacity,
            rule_of_law=self.state.rule_of_law,
            corruption_control=self.state.corruption_control,
            regulatory_quality=self.state.regulatory_quality,
        )
    
    def _apply_natural_drift(self) -> None:
        """Apply attractor basin gravitational pull."""
        position = PhasePosition(
            self.state.economic_complexity,
            self.state.institutional_quality_phase,
            self.state.year,
        )
        
        dx, dy = self.convergence_map.gravitational_pull(position)
        
        self.state.economic_complexity = max(0, min(100, self.state.economic_complexity + dx))
        self.state.institutional_quality_phase = max(0, min(100, self.state.institutional_quality_phase + dy))
        
        # Record trajectory
        self.convergence_map.record_position(
            self.nation_id,
            PhasePosition(self.state.economic_complexity, self.state.institutional_quality_phase, self.state.year),
        )
    
    def _apply_passive_changes(self) -> None:
        """Apply gradual, automatic changes each year."""
        s = self.state
        d = s.d_coefficient / 100.0
        
        # Population growth (declining over eras)
        if s.year < 1950:
            pop_growth = 0.012
        elif s.year < 1990:
            pop_growth = 0.008
        else:
            pop_growth = 0.002
        
        s.population_millions *= (1 + pop_growth)
        
        # Urbanization (driven by industrialization)
        urbanization_pull = s.industrial_labor_share * 0.02 + s.service_labor_share * 0.015
        s.urbanization_rate = min(0.85, s.urbanization_rate + urbanization_pull * d)
        
        # Literacy improvement (slow, compounded)
        literacy_gain = (0.02 + s.d_coefficient * 0.001) * (1 - s.literacy_rate)
        s.literacy_rate = min(0.99, s.literacy_rate + literacy_gain)
        s.mean_years_schooling = min(16, s.mean_years_schooling + literacy_gain * 8)
        
        # Life expectancy improvement
        life_gain = 0.15 + s.d_coefficient * 0.003
        s.life_expectancy = min(85, s.life_expectancy + life_gain)
        
        # Infrastructure gradual improvement
        s.infrastructure_quality = min(1.0, s.infrastructure_quality + 0.003 * d)
        s.electricity_access = min(1.0, s.electricity_access + 0.02 * d)
        
        if s.year > 1995:
            s.broadband_penetration = min(0.98, s.broadband_penetration + 0.04 * d)
        
        # Environmental damage accumulates with industrialization
        if s.era == "era2_planned_development":
            s.environmental_damage_accumulated = min(1.0, s.environmental_damage_accumulated + 
                s.industrial_labor_share * 0.008)
        elif s.era == "era3_convergence":
            # Cleanup possible with policy
            pass
        
        # Service sector naturally grows
        service_growth = 0.003 + d * 0.004
        s.service_labor_share = min(0.80, s.service_labor_share + service_growth)
        s.agricultural_labor_share = max(0.02, s.agricultural_labor_share - service_growth * 0.6)
        
        # Institutions age
        self.institutions.advance_year()
        
        # Institutional quality decays slowly without maintenance
        inst_decay = 0.001 * (1 - s.state_capacity)
        s.institutional_quality = max(0.0, s.institutional_quality - inst_decay)
        
        # Natural GDP growth (productivity, technology, capital accumulation)
        base_growth = 0.02 + d * 0.03
        s.gdp_per_capita_ppp *= (1 + base_growth)
    
    def tick(self) -> Dict:
        """Advance the simulation by one year.
        
        Returns a summary of what happened this year.
        """
        s = self.state
        year_log = {"year": s.year, "events": []}
        
        # 1. Check for crisis
        crisis = self.event_engine.check_crisis(
            nation_state={
                "institutional_quality": s.institutional_quality,
                "ethnic_fragmentation_index": s.ethnic_fragmentation_index,
                "ethnic_tension_stored": s.ethnic_tension_stored,
                "resource_dependency": s.resource_dependency,
                "fiscal_health": s.fiscal_health,
                "environmental_damage_accumulated": s.environmental_damage_accumulated,
            },
            year=s.year,
            era=s.era,
        )
        
        if crisis:
            s.in_crisis = True
            s.crisis_reform_multiplier = self.event_engine.reform_window_multiplier
            year_log["events"].append(f"CRISIS: {crisis.name} (severity: {crisis.severity:.2f})")
        else:
            s.crisis_reform_multiplier = 1.0
        
        # 2. Check for random events
        event = self.event_engine.check_random_event(s.year)
        if event:
            s.gdp_per_capita_ppp = max(100, s.gdp_per_capita_ppp * (1 + event.gdp_impact_pct))
            s.d_coefficient += event.d_coefficient_change
            s.institutional_quality = max(0, min(1, s.institutional_quality + event.institutional_quality_change))
            s.social_cohesion = max(0, min(1, s.social_cohesion + event.social_cohesion_change))
            year_log["events"].append(f"EVENT: {event.name}")
        
        # 3. Apply crisis effects
        if s.in_crisis:
            crisis_impact = self.event_engine.total_crisis_impact
            # Cap total GDP impact at -20% per year to prevent collapse
            gdp_impact = max(-0.20, crisis_impact["gdp_impact_pct"])
            s.gdp_per_capita_ppp = max(100, s.gdp_per_capita_ppp * (1 + gdp_impact))
            s.institutional_quality = max(0, min(1, s.institutional_quality + crisis_impact["institutional_quality_impact"]))
            s.social_cohesion = max(0, min(1, s.social_cohesion + crisis_impact["social_cohesion_impact"]))
            s.d_coefficient = max(0, s.d_coefficient + crisis_impact["d_coefficient_impact"])
        
        # 4. Resolve aging crises
        resolved = self.event_engine.resolve_crises(s.year)
        for c in resolved:
            year_log["events"].append(f"CRISIS RESOLVED: {c.name}")
        
        if not self.event_engine.active_crises:
            s.in_crisis = False
            s.crisis_reform_multiplier = 1.0
        
        # 5. Cascade check
        new_cascades = self.event_engine.cascade_check()
        for c in new_cascades:
            year_log["events"].append(f"CASCADE: {c.name}")
        
        # 6. Apply passive changes
        self._apply_passive_changes()
        
        # 7. Update computed metrics
        self._update_d_coefficient()
        self._update_phase_position()
        self._apply_natural_drift()
        
        # 8. Advance year
        s.year += 1
        
        # 9. Record
        self.state_history.append(NationState(
            **{k: v for k, v in s.__dict__.items()}
        ))
        
        return year_log
    
    def apply_policy(self, policy_id: str, investment_level: float = 0.5) -> str:
        """Apply a policy decision for the current year.
        
        investment_level: 0.0-1.0, how much resource committed
        
        Returns a description of what happened.
        """
        s = self.state
        effective_investment = investment_level * s.reform_capacity * s.crisis_reform_multiplier
        
        # Clip to reasonable bounds
        effective_investment = min(0.3, max(0.005, effective_investment))
        
        result = ""
        
        if policy_id == "land_reform":
            # Reduces gini, may reduce short-term agricultural output
            s.gini_coefficient = max(0.20, s.gini_coefficient - effective_investment * 0.3)
            s.agricultural_labor_share *= (1 - effective_investment * 0.1)
            result = f"Land reform: Gini {s.gini_coefficient:.3f}"
        
        elif policy_id == "education_investment":
            s.literacy_rate = min(0.99, s.literacy_rate + effective_investment * 0.15)
            s.mean_years_schooling += effective_investment * 3
            result = f"Education: literacy {s.literacy_rate:.1%}"
        
        elif policy_id == "infrastructure_investment":
            s.infrastructure_quality = min(1.0, s.infrastructure_quality + effective_investment * 0.2)
            s.road_density += effective_investment * 0.5
            s.rail_density += effective_investment * 0.3
            s.electricity_access = min(1.0, s.electricity_access + effective_investment * 0.25)
            result = f"Infrastructure: quality {s.infrastructure_quality:.2f}"
        
        elif policy_id == "institution_building":
            # Found or improve institutions
            s.state_capacity = min(1.0, s.state_capacity + effective_investment * 0.2)
            s.property_rights = min(1.0, s.property_rights + effective_investment * 0.15)
            s.rule_of_law = min(1.0, s.rule_of_law + effective_investment * 0.12)
            s.corruption_control = min(1.0, s.corruption_control + effective_investment * 0.10)
            result = f"Institutions: state capacity {s.state_capacity:.2f}"
        
        elif policy_id == "industrial_policy":
            s.industrial_labor_share = min(0.55, s.industrial_labor_share + effective_investment * 0.15)
            s.export_diversity = min(1.0, s.export_diversity + effective_investment * 0.1)
            # Industrialization increases environmental damage
            s.environmental_damage_accumulated += effective_investment * 0.05
            result = f"Industry: share {s.industrial_labor_share:.1%}"
        
        elif policy_id == "health_investment":
            s.life_expectancy = min(85, s.life_expectancy + effective_investment * 8)
            result = f"Health: life expectancy {s.life_expectancy:.0f}"
        
        elif policy_id == "anti_corruption":
            s.corruption_control = min(1.0, s.corruption_control + effective_investment * 0.25)
            s.institutional_quality = min(1.0, s.institutional_quality + effective_investment * 0.2)
            result = f"Anti-corruption: control {s.corruption_control:.2f}"
        
        elif policy_id == "digital_infrastructure":
            s.broadband_penetration = min(0.98, s.broadband_penetration + effective_investment * 0.3)
            s.d_coefficient += effective_investment * 5
            result = f"Digital: broadband {s.broadband_penetration:.1%}"
        
        elif policy_id == "environmental_cleanup":
            s.environmental_damage_accumulated = max(0, s.environmental_damage_accumulated - effective_investment * 0.2)
            s.renewable_energy_share = min(1.0, s.renewable_energy_share + effective_investment * 0.15)
            result = f"Environment: damage {s.environmental_damage_accumulated:.2f}"
        
        elif policy_id == "social_cohesion":
            s.social_cohesion = min(1.0, s.social_cohesion + effective_investment * 0.2)
            s.ethnic_tension_stored = max(0, s.ethnic_tension_stored - effective_investment * 0.15)
            result = f"Social: cohesion {s.social_cohesion:.2f}"
        
        elif policy_id == "eu_accession_prep":
            # Only available in era 3
            if s.era == "era3_convergence":
                s.institutional_quality = min(1.0, s.institutional_quality + effective_investment * 0.3)
                s.regulatory_quality = min(1.0, s.regulatory_quality + effective_investment * 0.35)
                s.property_rights = min(1.0, s.property_rights + effective_investment * 0.25)
                s.export_diversity = min(1.0, s.export_diversity + effective_investment * 0.2)
                result = f"EU accession prep: regulatory quality {s.regulatory_quality:.2f}"
        
        else:
            result = f"Unknown policy: {policy_id}"
        
        self._update_d_coefficient()
        self._update_phase_position()
        
        return result
    
    def check_era_transition(self) -> Optional[str]:
        """Check if we need to transition eras and apply transition logic."""
        s = self.state
        
        # Era 1 → Era 2
        if s.era == "era1_nation_building" and s.year >= 1945:
            return self._transition_to_era2()
        
        # Era 2 → Era 3
        if s.era == "era2_planned_development" and s.year >= 1990:
            return self._transition_to_era3()
        
        return None
    
    def _transition_to_era2(self) -> str:
        """Execute Era 1 → Era 2 transition."""
        s = self.state
        log_lines = ["═══ ERA TRANSITION: Nation-Building → Planned Development ═══"]
        
        # Store era 1 legacies
        s.era = "era2_planned_development"
        s.policy_autonomy = 0.3
        s.reform_capacity = 0.02  # reduced reform capacity under constraint
        
        # Store ethnic tensions — they go underground
        s.ethnic_tension_stored = max(0, 0.5 - s.social_cohesion) * s.ethnic_fragmentation_index
        log_lines.append(f"Ethnic tension stored: {s.ethnic_tension_stored:.2f}")
        
        # Trade network forcibly realigned
        s.export_diversity = max(0.1, s.export_diversity * 0.4)
        log_lines.append(f"Trade network realigned; export diversity reset to {s.export_diversity:.2f}")
        
        # Institutional DNA persists
        inst_depth = self.institutions.aggregate_depth()
        inst_quality = self.institutions.aggregate_quality()
        log_lines.append(f"Institutions persist: {len(self.institutions.institutions)} institutions, avg depth {inst_depth:.0f}yr, quality {inst_quality:.2f}")
        
        # D-coefficient era weight adjustment
        self.d_engine.era_adjust_weights("era2_planned_development")
        self._update_d_coefficient()
        
        log_lines.append(f"D-coefficient (era-adjusted): {s.d_coefficient:.1f}")
        log_lines.append("═" * 60)
        
        return "\n".join(log_lines)
    
    def _transition_to_era3(self) -> str:
        """Execute Era 2 → Era 3 transition."""
        s = self.state
        log_lines = ["═══ ERA TRANSITION: Planned Development → Convergence or Drift ═══"]
        
        s.era = "era3_convergence"
        s.policy_autonomy = 1.0
        s.reform_capacity = 0.04  # higher reform capacity in open system
        
        # Industrial structure shock — heavy industry is now a liability
        industrial_penalty = s.industrial_labor_share * 0.4  # more industry = harder transition
        gdp_shock = 0.15 + industrial_penalty
        s.gdp_per_capita_ppp = max(100, s.gdp_per_capita_ppp * (1 - gdp_shock))
        log_lines.append(f"Transition GDP shock: -{gdp_shock:.0%} ({s.gdp_per_capita_ppp:.0f} PPP)")
        
        # Unemployment spike as state enterprises collapse
        s.agricultural_labor_share += s.industrial_labor_share * 0.3
        s.industrial_labor_share *= 0.5
        
        # Stored ethnic tensions release
        if s.ethnic_tension_stored > 0.3:
            tension_release = s.ethnic_tension_stored * 0.7
            s.social_cohesion = max(0.1, s.social_cohesion - tension_release)
            log_lines.append(f"⚠️  Stored ethnic tensions releasing! Social cohesion: {s.social_cohesion:.2f}")
            s.ethnic_tension_stored *= 0.3
        
        # Environmental damage now visible (was hidden in era 2)
        if s.environmental_damage_accumulated > 0.5:
            log_lines.append(f"⚠️  Environmental damage revealed: {s.environmental_damage_accumulated:.2f}")
        
        # EU accession track becomes available
        log_lines.append("EU accession track now available (apply policy 'eu_accession_prep')")
        
        # Media freedom opens
        s.media_freedom = min(1.0, s.media_freedom + 0.4)
        
        # D-coefficient era weight adjustment
        self.d_engine.era_adjust_weights("era3_convergence")
        self._update_d_coefficient()
        
        log_lines.append(f"D-coefficient (era-adjusted): {s.d_coefficient:.1f}")
        log_lines.append("═" * 60)
        
        return "\n".join(log_lines)
    
    def run(self, auto_policy: bool = True) -> str:
        """Run the full simulation from 1918 to 2025.
        
        If auto_policy=True, applies a basic policy mix automatically 
        (for testing/balancing). Otherwise, only passive changes occur.
        """
        log_lines = [f"═══ THE CARPATHIAN CRESCENT: {self.nation_data['name']} ═══"]
        log_lines.append(f"Starting year: 1918 | D-coefficient: {self.state.d_coefficient:.1f}")
        log_lines.append(f"Legacy: {self.nation_data['era1_start']['institutional_legacy']}")
        log_lines.append("")
        
        policy_cycle = 0
        
        while self.state.year <= 2025:
            # Era transition check
            transition = self.check_era_transition()
            if transition:
                log_lines.append(transition)
                log_lines.append("")
            
            # Auto-policy: simulate reasonable governance
            if auto_policy:
                era = self.state.era
                if policy_cycle % 3 == 0:
                    if era == "era1_nation_building":
                        self.apply_policy("education_investment", 0.6)
                        self.apply_policy("infrastructure_investment", 0.4)
                        if policy_cycle % 9 == 0:
                            self.apply_policy("institution_building", 0.5)
                    elif era == "era2_planned_development":
                        self.apply_policy("industrial_policy", 0.7)
                        self.apply_policy("infrastructure_investment", 0.5)
                        if policy_cycle % 9 == 0:
                            self.apply_policy("health_investment", 0.4)
                    elif era == "era3_convergence":
                        self.apply_policy("institution_building", 0.5)
                        self.apply_policy("eu_accession_prep", 0.6)
                        self.apply_policy("digital_infrastructure", 0.4)
                        if self.state.environmental_damage_accumulated > 0.4:
                            self.apply_policy("environmental_cleanup", 0.5)
            
            # Tick
            year_log = self.tick()
            policy_cycle += 1
            
            # Log significant years
            if year_log["events"]:
                log_lines.append(f"  {year_log['year']}: {'; '.join(year_log['events'])}")
            
            # Log every 20 years for progress
            if self.state.year % 20 == 0:
                log_lines.append(
                    f"  [{self.state.year}] GDP: ${self.state.gdp_per_capita_ppp:.0f} | "
                    f"D: {self.state.d_coefficient:.1f} | "
                    f"Literacy: {self.state.literacy_rate:.1%} | "
                    f"Life exp: {self.state.life_expectancy:.0f} | "
                    f"Phase: ({self.state.economic_complexity:.1f}, {self.state.institutional_quality_phase:.1f})"
                )
        
        log_lines.append("")
        log_lines.append(self.summary())
        
        self.turn_log = log_lines
        return "\n".join(log_lines)
    
    def summary(self) -> str:
        """Generate a final summary of the simulation."""
        s = self.state
        start = self.state_history[0]
        
        lines = [
            f"═══ FINAL SUMMARY: {self.nation_data['name']} ({s.year}) ═══",
            "",
            f"  GDP per capita (PPP):  ${start.gdp_per_capita_ppp:.0f} → ${s.gdp_per_capita_ppp:.0f}",
            f"  Population:             {start.population_millions:.1f}M → {s.population_millions:.1f}M",
            f"  Life expectancy:        {start.life_expectancy:.0f} → {s.life_expectancy:.0f} years",
            f"  Literacy:               {start.literacy_rate:.1%} → {s.literacy_rate:.1%}",
            f"  Urbanization:           {start.urbanization_rate:.1%} → {s.urbanization_rate:.1%}",
            f"  Gini coefficient:       {start.gini_coefficient:.2f} → {s.gini_coefficient:.2f}",
            "",
            f"  D-Coefficient:          {start.d_coefficient:.1f} → {s.d_coefficient:.1f}",
            f"  Convergence remaining:  {self.convergence_map.convergence_distance(PhasePosition(s.economic_complexity, s.institutional_quality_phase)):.1f}",
            f"  Phase position:         ({s.economic_complexity:.1f}, {s.institutional_quality_phase:.1f})",
            f"  Dominant basin:         {self.convergence_map.dominant_basin(PhasePosition(s.economic_complexity, s.institutional_quality_phase)).name if self.convergence_map.dominant_basin(PhasePosition(s.economic_complexity, s.institutional_quality_phase)) else 'none'}",
            "",
            f"  Institutional quality:  {s.institutional_quality:.2f}",
            f"  State capacity:         {s.state_capacity:.2f}",
            f"  Rule of law:            {s.rule_of_law:.2f}",
            f"  Corruption control:     {s.corruption_control:.2f}",
            f"  Social cohesion:        {s.social_cohesion:.2f}",
            f"  Environmental damage:   {s.environmental_damage_accumulated:.2f}",
            "",
            f"  Crises experienced:     {len(self.event_engine.crisis_history)}",
            f"  Institutions founded:   {len(self.institutions.institutions)}",
            f"  Institutional avg depth: {self.institutions.aggregate_depth():.0f} years",
            "",
            f"═══ CONVERGENCE SCORE ═══",
        ]
        
        # Compute convergence score
        conv_remaining = self.convergence_map.convergence_distance(
            PhasePosition(s.economic_complexity, s.institutional_quality_phase)
        )
        convergence_score = max(0, 100 - conv_remaining)
        
        lines.append(f"  Overall: {convergence_score:.1f}/100")
        
        if convergence_score > 80:
            lines.append("  VERDICT: Strong convergence — on track for high-development equilibrium")
        elif convergence_score > 50:
            lines.append("  VERDICT: Partial convergence — making progress but trajectory uncertain")
        elif convergence_score > 25:
            lines.append("  VERDICT: Slow convergence — structural barriers remain significant")
        else:
            lines.append("  VERDICT: Divergence — fundamental transformation needed")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        """Serialize the full simulation state for export/UI."""
        s = self.state
        return {
            "nation_id": self.nation_id,
            "nation_name": self.nation_data["name"],
            "year": s.year,
            "era": s.era,
            "state": {k: v for k, v in s.__dict__.items()},
            "institutions": self.institutions.summary(),
            "d_coefficient_history": self.d_engine.history,
            "convergence_trajectory": self.convergence_map.trajectory_summary(self.nation_id),
            "crisis_history": self.event_engine.crisis_history,
            "event_history": self.event_engine.event_history,
        }
