"""
D-Coefficient Engine — The Medium Coefficient

The master variable of the simulation: how fast capability diffuses from
adoption points (cities, institutions) to the periphery (towns, villages).

D ∈ [0, 100] where:
  0  = Total friction — nothing spreads; investments are point-local
  50 = Moderate diffusion — cities share with towns over years
  100 = Perfect diffusion — any improvement instantly reaches everywhere

The D-coefficient is both a metric and a strategic investment target.
Players can invest directly in diffusion capacity (roads, broadband, trust)
or in point improvements (factories, universities) — the D-coefficient 
determines which investment type has higher marginal returns.

Based on Hunter Hughes' "The Medium Coefficient" framework.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import math


@dataclass
class DCoefficientInputs:
    """Raw inputs that feed into the D-coefficient calculation."""
    
    # Infrastructure (0-1)
    road_density: float = 0.0          # km of paved road per km²
    rail_density: float = 0.0          # km of rail per km²
    electricity_access: float = 0.0    # proportion with electricity
    broadband_penetration: float = 0.0  # internet access proportion
    port_quality: float = 0.0          # 0=landlocked, 1=world-class port
    
    # Institutional (0-1)
    institutional_trust: float = 0.0   # composite: corruption, contract enforcement
    state_capacity: float = 0.0        # tax collection, service delivery
    property_rights: float = 0.0       # registry completeness, enforcement
    
    # Human capital (0-1)
    literacy_rate: float = 0.0
    mean_years_schooling: float = 0.0
    education_gini: float = 1.0        # 0=perfect equality, 1=max inequality
    
    # Information (0-1)
    media_freedom: float = 0.0
    language_fragmentation: float = 1.0  # 0=homogeneous, 1=max fragmented
    
    # Geographic (static or slow-changing)
    terrain_roughness: float = 0.5     # 0=flat, 1=extreme mountains
    landlocked: bool = True
    urban_density: float = 0.0         # urban proportion
    country_area_km2: float = 100000   # larger = more internal friction


@dataclass
class DCoefficientWeights:
    """Configurable weights for each D-coefficient sub-component.
    
    These can be era-adjusted — e.g., infrastructure matters more in early eras,
    information permeability matters more in the digital era.
    """
    infrastructure_weight: float = 0.30
    institutional_weight: float = 0.25
    human_capital_weight: float = 0.20
    information_weight: float = 0.10
    geographic_weight: float = 0.15


class DCoefficientEngine:
    """Calculates and tracks the D-coefficient over time.
    
    The D-coefficient is calculated as a weighted composite of five sub-indices:
    1. Infrastructure Connectivity Index
    2. Institutional Trust Index  
    3. Human Capital Distribution Index
    4. Information Permeability Index
    5. Geographic Friction Factor
    
    Each sub-index ∈ [0, 1]. The final D-coefficient ∈ [0, 100].
    """
    
    def __init__(self, weights: Optional[DCoefficientWeights] = None):
        self.weights = weights or DCoefficientWeights()
        self.history: List[Tuple[int, float]] = []  # (year, d_value)
    
    def infrastructure_index(self, inputs: DCoefficientInputs) -> float:
        """How connected is the physical territory?
        
        Roads, rail, electricity, ports, and broadband form the physical
        substrate through which goods, people, and ideas flow.
        """
        landlock_penalty = 0.6 if inputs.landlocked else 1.0
        
        # Road and rail are the backbone
        transport = (inputs.road_density * 0.4 + inputs.rail_density * 0.3) * landlock_penalty
        
        # Electricity is prerequisite for modern diffusion
        energy = inputs.electricity_access * 0.15
        
        # Port quality amplifies external connectivity
        port = inputs.port_quality * 0.15 * (0.3 if inputs.landlocked else 1.0)
        
        return min(1.0, transport + energy + port)
    
    def institutional_index(self, inputs: DCoefficientInputs) -> float:
        """How much do people trust the systems that transmit capability?
        
        Low trust = capability stops at personal networks.
        High trust = capability flows through formal channels.
        """
        return (
            inputs.institutional_trust * 0.40 +
            inputs.state_capacity * 0.35 +
            inputs.property_rights * 0.25
        )
    
    def human_capital_index(self, inputs: DCoefficientInputs) -> float:
        """Can people absorb and retransmit what reaches them?
        
        Education Gini matters as much as average — a highly educated
        elite with a poorly educated mass creates diffusion bottlenecks.
        """
        avg_quality = (
            inputs.literacy_rate * 0.4 +
            (inputs.mean_years_schooling / 16.0) * 0.3  # 16 years = ceiling
        )
        equality_bonus = (1.0 - inputs.education_gini) * 0.3
        
        return min(1.0, avg_quality + equality_bonus)
    
    def information_index(self, inputs: DCoefficientInputs) -> float:
        """How freely does information move?
        
        Language fragmentation and media freedom determine whether
        knowledge reaches everyone or stops at community boundaries.
        """
        language_penalty = inputs.language_fragmentation  # higher = more friction
        
        return (
            inputs.media_freedom * 0.50 +
            (1.0 - language_penalty) * 0.30 +
            inputs.broadband_penetration * 0.20
        )
    
    def geographic_index(self, inputs: DCoefficientInputs) -> float:
        """The physical terrain's resistance to diffusion.
        
        Mountains, distance, and low urban density create natural friction
        that infrastructure must overcome.
        """
        terrain_factor = 1.0 - inputs.terrain_roughness * 0.7
        
        # Urban density amplifies diffusion (network effects)
        urban_bonus = inputs.urban_density * 0.4
        
        # Size penalty — larger countries have more internal distance
        # 28,000 km² (Karpathia) = small bonus; 128,000 km² (Zaleskia) = penalty
        size_penalty = max(0.0, math.log10(inputs.country_area_km2 / 25000) * 0.15)
        
        raw = terrain_factor + urban_bonus - size_penalty
        return max(0.1, min(1.0, raw))
    
    def calculate(self, inputs: DCoefficientInputs) -> float:
        """Compute the D-coefficient from current inputs.
        
        Returns a value in [0, 100].
        """
        w = self.weights
        
        infra = self.infrastructure_index(inputs)
        inst = self.institutional_index(inputs)
        human = self.human_capital_index(inputs)
        info = self.information_index(inputs)
        geo = self.geographic_index(inputs)
        
        d_raw = (
            w.infrastructure_weight * infra +
            w.institutional_weight * inst +
            w.human_capital_weight * human +
            w.information_weight * info +
            w.geographic_weight * geo
        )
        
        return round(d_raw * 100, 1)
    
    def diffusion_delay(self, d_value: float, distance_tiers: int = 1) -> int:
        """How many years for a capability to diffuse N tiers from source?
        
        Tier 0 = source city
        Tier 1 = secondary cities  
        Tier 2 = towns
        Tier 3 = villages
        
        At D=70: Tier 1 takes ~3 years, Tier 3 takes ~8 years
        At D=25: Tier 1 takes ~12 years, Tier 3 takes ~35 years
        """
        base_delay = 2.0  # years at D=100 per tier
        friction = (100.0 - d_value) / 100.0 * 30.0  # max 30 extra years per tier
        
        return round(base_delay + friction * distance_tiers)
    
    def marginal_return_ratio(self, d_value: float) -> float:
        """Should the player invest in diffusion or point improvements?
        
        Returns the ratio: marginal return of diffusion investment / 
                          marginal return of point investment.
        
        > 1.0 = invest in raising D
        < 1.0 = invest in specific projects
        
        At low D, raising D has enormous returns (unlocks all existing investments).
        At high D, point investments become more attractive.
        """
        if d_value < 20:
            return 4.0
        elif d_value < 40:
            return 2.5
        elif d_value < 60:
            return 1.5
        elif d_value < 80:
            return 0.8
        else:
            return 0.4
    
    def era_adjust_weights(self, era: str) -> None:
        """Adjust sub-index weights based on the era.
        
        Different eras emphasize different diffusion mechanisms:
        - Era 1: Infrastructure is everything (roads, rail)
        - Era 2: Institutions matter more (state capacity for planning)
        - Era 3: Information and human capital dominate (digital economy)
        """
        if era == "era1_nation_building":
            self.weights = DCoefficientWeights(
                infrastructure_weight=0.40,
                institutional_weight=0.25,
                human_capital_weight=0.15,
                information_weight=0.05,
                geographic_weight=0.15,
            )
        elif era == "era2_planned_development":
            self.weights = DCoefficientWeights(
                infrastructure_weight=0.30,
                institutional_weight=0.35,
                human_capital_weight=0.20,
                information_weight=0.05,
                geographic_weight=0.10,
            )
        elif era == "era3_convergence":
            self.weights = DCoefficientWeights(
                infrastructure_weight=0.20,
                institutional_weight=0.25,
                human_capital_weight=0.25,
                information_weight=0.20,
                geographic_weight=0.10,
            )


def create_inputs_from_nation(nation_data: dict) -> DCoefficientInputs:
    """Factory: create DCoefficientInputs from a nation's era1_start data."""
    start = nation_data["era1_start"]
    geo = nation_data["geography"]
    ethnicity = nation_data["ethnic_fragmentation_index"]
    
    max_area = 130000  # approximate max for normalization
    
    return DCoefficientInputs(
        road_density=start["paved_road_km"] / nation_data["area_km2"] * 10,
        rail_density=start["rail_km"] / nation_data["area_km2"] * 10,
        electricity_access=start["electricity_access_pct"],
        broadband_penetration=0.0,  # era 1
        port_quality=0.8 if geo["port_access"] else 0.0,
        institutional_trust=start["institutional_quality"] * 0.7,
        state_capacity=start["institutional_quality"] * 0.6,
        property_rights=start["institutional_quality"] * 0.5,
        literacy_rate=start["literacy_rate"],
        mean_years_schooling=start["literacy_rate"] * 8.0,  # rough mapping
        education_gini=start["gini_coefficient"] * 1.2,  # education inequality tracks income
        media_freedom=0.3,  # era 1 baseline
        language_fragmentation=ethnicity,
        terrain_roughness={
            "flat_coastal": 0.1,
            "river_plains_uplands": 0.35,
            "fertile_plains": 0.15,
            "mountainous": 0.70,
            "alpine": 0.85,
        }.get(geo["terrain"], 0.5),
        landlocked=geo["landlocked"],
        urban_density=start["urbanization_rate"],
        country_area_km2=nation_data["area_km2"],
    )
