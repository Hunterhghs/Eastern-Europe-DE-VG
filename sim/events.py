"""
Crisis & Event System

Crises are not just bad events — they are the only times when discontinuous
institutional change is possible. During normal times, reform is incremental
(1-3% per year). During a crisis, players can push through 15-30% changes.

Crisis types cascade: a financial crisis can trigger political crisis;
political crisis can trigger ethnic conflict. Smart play involves preparing
for crises (building buffers, diversifying, investing in social cohesion).
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
import random
import math
from enum import Enum


class CrisisCategory(Enum):
    ECONOMIC = "economic"
    POLITICAL = "political"
    SOCIAL = "social"
    ENVIRONMENTAL = "environmental"
    EXTERNAL = "external"


@dataclass
class Crisis:
    """A crisis event that opens a reform window."""
    name: str
    category: CrisisCategory
    severity: float  # 0-1
    description: str
    reform_window_bonus: float  # multiplier on reform effectiveness during crisis
    duration_years: int = 1
    
    # Effects on nation state
    gdp_impact_pct: float = 0.0  # e.g., -0.05 = 5% GDP drop
    institutional_quality_impact: float = 0.0
    social_cohesion_impact: float = 0.0
    d_coefficient_impact: float = 0.0
    
    # Cascade triggers
    can_trigger: List[str] = field(default_factory=list)


@dataclass
class Event:
    """A non-crisis event — beneficial, neutral, or mildly negative."""
    name: str
    description: str
    probability_per_year: float = 0.05
    
    # Effects
    gdp_impact_pct: float = 0.0
    d_coefficient_change: float = 0.0
    institutional_quality_change: float = 0.0
    social_cohesion_change: float = 0.0
    population_change_pct: float = 0.0


# Crisis definitions
CRISIS_TEMPLATES = {
    "financial_panic": Crisis(
        name="Financial Panic",
        category=CrisisCategory.ECONOMIC,
        severity=0.7,
        description="Banking system loses confidence. Credit freezes. Depositors rush to withdraw.",
        reform_window_bonus=2.5,
        duration_years=2,
        gdp_impact_pct=-0.08,
        institutional_quality_impact=-0.05,
        social_cohesion_impact=-0.10,
        d_coefficient_impact=-3.0,
        can_trigger=["political_instability", "sovereign_debt_crisis"],
    ),
    "sovereign_debt_crisis": Crisis(
        name="Sovereign Debt Crisis",
        category=CrisisCategory.ECONOMIC,
        severity=0.75,
        description="Government cannot service its debt. Default looms. International creditors demand austerity.",
        reform_window_bonus=3.0,
        duration_years=3,
        gdp_impact_pct=-0.12,
        institutional_quality_impact=-0.08,
        social_cohesion_impact=-0.15,
        d_coefficient_impact=-5.0,
        can_trigger=["political_instability", "social_unrest"],
    ),
    "hyperinflation": Crisis(
        name="Hyperinflation",
        category=CrisisCategory.ECONOMIC,
        severity=0.85,
        description="Currency collapses. Prices double weekly. Savings evaporate.",
        reform_window_bonus=3.5,
        duration_years=2,
        gdp_impact_pct=-0.15,
        institutional_quality_impact=-0.10,
        social_cohesion_impact=-0.20,
        d_coefficient_impact=-8.0,
        can_trigger=["political_instability", "social_unrest", "regime_change"],
    ),
    "political_instability": Crisis(
        name="Political Instability",
        category=CrisisCategory.POLITICAL,
        severity=0.6,
        description="Government collapses or loses legitimacy. Policy paralysis. Street protests.",
        reform_window_bonus=4.0,
        duration_years=1,
        gdp_impact_pct=-0.03,
        institutional_quality_impact=-0.12,
        social_cohesion_impact=-0.10,
        d_coefficient_impact=-2.0,
        can_trigger=["financial_panic", "ethnic_conflict", "regime_change"],
    ),
    "ethnic_conflict": Crisis(
        name="Ethnic Conflict Flare-Up",
        category=CrisisCategory.SOCIAL,
        severity=0.8,
        description="Long-suppressed ethnic tensions erupt. Violence, displacement, possible separatist movements.",
        reform_window_bonus=1.5,  # Hard to reform during conflict
        duration_years=3,
        gdp_impact_pct=-0.10,
        institutional_quality_impact=-0.15,
        social_cohesion_impact=-0.30,
        d_coefficient_impact=-6.0,
        can_trigger=["political_instability", "external_intervention"],
    ),
    "environmental_disaster": Crisis(
        name="Environmental Disaster",
        category=CrisisCategory.ENVIRONMENTAL,
        severity=0.5,
        description="Major flood, drought, or industrial accident. Infrastructure damaged. Agricultural output collapses.",
        reform_window_bonus=2.0,
        duration_years=1,
        gdp_impact_pct=-0.05,
        institutional_quality_impact=-0.02,
        social_cohesion_impact=-0.05,
        d_coefficient_impact=-2.0,
        can_trigger=["social_unrest"],
    ),
    "commodity_price_collapse": Crisis(
        name="Commodity Price Collapse",
        category=CrisisCategory.ECONOMIC,
        severity=0.6,
        description="The price of your main export commodity crashes. Foreign exchange dries up.",
        reform_window_bonus=2.5,
        duration_years=2,
        gdp_impact_pct=-0.07,
        institutional_quality_impact=-0.03,
        social_cohesion_impact=-0.08,
        d_coefficient_impact=-1.0,
        can_trigger=["sovereign_debt_crisis", "political_instability"],
    ),
    "external_intervention": Crisis(
        name="External Intervention",
        category=CrisisCategory.EXTERNAL,
        severity=0.9,
        description="A great power intervenes militarily or economically. Sovereignty compromised.",
        reform_window_bonus=2.0,
        duration_years=4,
        gdp_impact_pct=-0.15,
        institutional_quality_impact=-0.20,
        social_cohesion_impact=-0.25,
        d_coefficient_impact=-10.0,
        can_trigger=["political_instability", "ethnic_conflict", "regime_change"],
    ),
    "demographic_shock": Crisis(
        name="Demographic Shock",
        category=CrisisCategory.SOCIAL,
        severity=0.4,
        description="Sudden population change — mass emigration wave, baby bust, or mortality crisis. Labor markets disrupted.",
        reform_window_bonus=1.8,
        duration_years=5,
        gdp_impact_pct=-0.04,
        institutional_quality_impact=-0.02,
        social_cohesion_impact=-0.10,
        d_coefficient_impact=-1.0,
        can_trigger=["social_unrest"],
    ),
    "pandemic": Crisis(
        name="Pandemic",
        category=CrisisCategory.SOCIAL,
        severity=0.7,
        description="Infectious disease sweeps through the population. Death, economic disruption, and social distancing.",
        reform_window_bonus=2.8,
        duration_years=2,
        gdp_impact_pct=-0.06,
        institutional_quality_impact=-0.03,
        social_cohesion_impact=-0.12,
        d_coefficient_impact=-2.0,
        can_trigger=["financial_panic", "political_instability"],
    ),
    "social_unrest": Crisis(
        name="Social Unrest",
        category=CrisisCategory.SOCIAL,
        severity=0.5,
        description="Widespread protests, strikes, and civil disobedience. The social contract frays.",
        reform_window_bonus=3.0,
        duration_years=1,
        gdp_impact_pct=-0.04,
        institutional_quality_impact=-0.05,
        social_cohesion_impact=-0.10,
        d_coefficient_impact=-2.0,
        can_trigger=["political_instability"],
    ),
    "regime_change": Crisis(
        name="Regime Change",
        category=CrisisCategory.POLITICAL,
        severity=0.9,
        description="The entire political order is overthrown. New rules, new players, uncertain outcomes.",
        reform_window_bonus=5.0,
        duration_years=3,
        gdp_impact_pct=-0.10,
        institutional_quality_impact=-0.20,
        social_cohesion_impact=-0.15,
        d_coefficient_impact=-8.0,
        can_trigger=["political_instability", "ethnic_conflict", "social_unrest"],
    ),
}

# Positive and neutral events
EVENT_TEMPLATES = {
    "technology_breakthrough": Event(
        name="Technology Breakthrough",
        description="A domestic innovation or technology transfer creates new productive capabilities.",
        probability_per_year=0.03,
        gdp_impact_pct=0.02,
        d_coefficient_change=2.0,
    ),
    "foreign_investment_wave": Event(
        name="Foreign Investment Wave",
        description="International investors discover your market. Capital and expertise flow in.",
        probability_per_year=0.04,
        gdp_impact_pct=0.03,
        d_coefficient_change=1.5,
        institutional_quality_change=0.02,
    ),
    "diaspora_return": Event(
        name="Diaspora Return Wave",
        description="Emigrants return with capital, skills, and international networks.",
        probability_per_year=0.03,
        gdp_impact_pct=0.02,
        d_coefficient_change=3.0,
        institutional_quality_change=0.03,
    ),
    "resource_discovery": Event(
        name="New Resource Discovery",
        description="Significant new mineral or energy deposits found. Wealth — but dependency risk.",
        probability_per_year=0.02,
        gdp_impact_pct=0.04,
        d_coefficient_change=-1.0,  # resource curse
        institutional_quality_change=-0.02,  # temptation of easy money
    ),
    "cultural_renaissance": Event(
        name="Cultural Renaissance",
        description="A flourishing of arts, sciences, and public discourse. Soft power and social cohesion rise.",
        probability_per_year=0.04,
        social_cohesion_change=0.05,
        d_coefficient_change=2.0,
        institutional_quality_change=0.01,
    ),
    "trade_agreement": Event(
        name="Favorable Trade Agreement",
        description="A new trade deal opens major export markets. Economic integration deepens.",
        probability_per_year=0.05,
        gdp_impact_pct=0.02,
        d_coefficient_change=1.0,
    ),
    "leader_emergence": Event(
        name="Transformational Leader Emerges",
        description="A leader of exceptional vision and competence rises to power. Reform capacity increases.",
        probability_per_year=0.02,
        d_coefficient_change=1.0,
        institutional_quality_change=0.05,
        social_cohesion_change=0.05,
    ),
}


class EventEngine:
    """Manages random events and crisis generation/propagation."""
    
    def __init__(self, seed: Optional[int] = None):
        self.rng = random.Random(seed)
        self.active_crises: List[Crisis] = []
        self.crisis_history: List[Dict] = []
        self.event_history: List[Dict] = []
    
    def check_crisis(self, nation_state: Dict, year: int, era: str) -> Optional[Crisis]:
        """Determine if a crisis triggers this year based on nation vulnerabilities.
        
        Different eras have different crisis likelihoods:
        - Era 1: Financial panics, ethnic conflict, external intervention
        - Era 2: Commodity shocks, environmental disaster (industrial)
        - Era 3: Financial crises (market transition), sovereign debt, demographic shock
        """
        # Base crisis probability per year
        base_prob = 0.015  # ~1.5% per crisis type per year
        
        # Vulnerability modifiers
        modifiers = {}
        
        # Low institutional quality increases political crisis risk
        inst_quality = nation_state.get("institutional_quality", 0.5)
        if inst_quality < 0.3:
            modifiers["political_instability"] = 2.5
        elif inst_quality < 0.5:
            modifiers["political_instability"] = 1.5
        
        # High ethnic fragmentation increases ethnic conflict risk
        ethnic_frag = nation_state.get("ethnic_fragmentation_index", 0.3)
        if ethnic_frag > 0.6:
            modifiers["ethnic_conflict"] = 2.0
        elif ethnic_frag > 0.4:
            modifiers["ethnic_conflict"] = 1.3
        
        # Stored ethnic tension (from era transitions) increases risk
        stored_tension = nation_state.get("ethnic_tension_stored", 0.0)
        if stored_tension > 0.5:
            modifiers["ethnic_conflict"] = modifiers.get("ethnic_conflict", 1.0) + 2.0
        
        # Resource dependency increases commodity crisis risk
        resource_dependency = nation_state.get("resource_dependency", 0.0)
        if resource_dependency > 0.4:
            modifiers["commodity_price_collapse"] = 2.5
        
        # Low fiscal health increases sovereign debt crisis risk
        fiscal_health = nation_state.get("fiscal_health", 0.5)
        if fiscal_health < 0.3:
            modifiers["sovereign_debt_crisis"] = 2.0
        
        # Environmental damage accumulated increases environmental crisis risk
        env_damage = nation_state.get("environmental_damage_accumulated", 0.0)
        if env_damage > 0.6:
            modifiers["environmental_disaster"] = 3.0
        
        # Check each crisis type
        for crisis_key, crisis in CRISIS_TEMPLATES.items():
            prob = base_prob * modifiers.get(crisis_key, 1.0)
            
            # Era-specific adjustments
            if era == "era1_nation_building":
                if crisis_key in ("hyperinflation", "pandemic"):
                    prob *= 0.5  # less common in early 20th c
                if crisis_key == "external_intervention":
                    prob *= 2.0
            elif era == "era2_planned_development":
                if crisis_key == "financial_panic":
                    prob *= 0.3  # planned economy
                if crisis_key == "environmental_disaster":
                    prob *= 1.5  # rapid industrialization
            elif era == "era3_convergence":
                if crisis_key == "financial_panic":
                    prob *= 2.0  # market transition
                if crisis_key == "sovereign_debt_crisis":
                    prob *= 1.5
            
            if self.rng.random() < prob:
                self.active_crises.append(crisis)
                self.crisis_history.append({
                    "year": year,
                    "crisis": crisis_key,
                    "severity": crisis.severity,
                })
                return crisis
        
        return None
    
    def check_random_event(self, year: int) -> Optional[Event]:
        """Check for random non-crisis events."""
        for event_key, event in EVENT_TEMPLATES.items():
            if self.rng.random() < event.probability_per_year:
                self.event_history.append({
                    "year": year,
                    "event": event_key,
                })
                return event
        return None
    
    def cascade_check(self) -> List[Crisis]:
        """Check if any active crises trigger cascading crises."""
        new_crises = []
        for active in self.active_crises:
            for trigger_key in active.can_trigger:
                if trigger_key not in CRISIS_TEMPLATES:
                    continue  # skip unknown cascade triggers
                if self.rng.random() < 0.12:  # 12% cascade chance (was 30%)
                    cascade = CRISIS_TEMPLATES[trigger_key]
                    if cascade not in self.active_crises:
                        new_crises.append(cascade)
                        self.active_crises.append(cascade)
        return new_crises
    
    def resolve_crises(self, year: int) -> List[Crisis]:
        """Decrement crisis durations and resolve expired ones."""
        resolved = []
        surviving = []
        for crisis in self.active_crises:
            crisis.duration_years -= 1
            if crisis.duration_years <= 0:
                resolved.append(crisis)
            else:
                surviving.append(crisis)
        self.active_crises = surviving
        return resolved
    
    @property
    def reform_window_multiplier(self) -> float:
        """How much do active crises boost reform capacity?
        
        Multiple crises stack but with diminishing returns.
        """
        if not self.active_crises:
            return 1.0
        
        total_bonus = sum(c.reform_window_bonus for c in self.active_crises)
        # Diminishing returns: sqrt so 2 crises = 1.4x not 2x
        return 1.0 + math.sqrt(total_bonus) * 0.5
    
    @property
    def total_crisis_impact(self) -> Dict[str, float]:
        """Aggregate all active crisis effects on the nation."""
        impact = {
            "gdp_impact_pct": 0.0,
            "institutional_quality_impact": 0.0,
            "social_cohesion_impact": 0.0,
            "d_coefficient_impact": 0.0,
        }
        
        for crisis in self.active_crises:
            impact["gdp_impact_pct"] += crisis.gdp_impact_pct
            impact["institutional_quality_impact"] += crisis.institutional_quality_impact
            impact["social_cohesion_impact"] += crisis.social_cohesion_impact
            impact["d_coefficient_impact"] += crisis.d_coefficient_impact
        
        return impact
