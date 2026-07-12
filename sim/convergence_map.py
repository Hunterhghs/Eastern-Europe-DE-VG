"""
Convergence Map — Phase Space with Attractor Basins

Every nation exists in a 2D phase space:
- X-axis: Economic Complexity (productive capability diversity)
- Y-axis: Institutional Quality (state capacity, rule of law)

The space contains attractor basins — regions that pull nearby states
toward equilibrium points. Some are desirable (high-development attractors),
others are traps (middle-income trap, extractive equilibrium).

A nation's position drifts based on policies. Near basin boundaries
(saddle points), small policy changes produce large trajectory shifts.
Inside a basin, there is strong inertia.

Based on Hunter Hughes' "Convergence Maps: Who Crosses When" framework.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import math


@dataclass
class AttractorBasin:
    """A region of the phase space with a gravitational pull."""
    name: str
    center_x: float         # economic complexity, 0-100
    center_y: float         # institutional quality, 0-100
    radius: float           # how far the pull extends
    strength: float         # 0-1, how strong the pull
    description: str
    is_trap: bool = False   # traps are hard to escape
    is_desirable: bool = True


@dataclass
class PhasePosition:
    """A nation's position in the convergence phase space."""
    economic_complexity: float  # 0-100
    institutional_quality: float  # 0-100
    year: int = 1918
    
    @property
    def tuple(self) -> Tuple[float, float]:
        return (self.economic_complexity, self.institutional_quality)
    
    def distance_to(self, other: 'PhasePosition') -> float:
        return math.sqrt(
            (self.economic_complexity - other.economic_complexity) ** 2 +
            (self.institutional_quality - other.institutional_quality) ** 2
        )


# Standard attractor basins in the Convergence Map
STANDARD_BASINS = [
    AttractorBasin(
        name="Failed State Repeller",
        center_x=8, center_y=5, radius=18, strength=0.6,
        description="Very low complexity and institutional quality. Nations here are pushed outward — it's a repeller, not an attractor. Escape is possible but requires external intervention or extraordinary leadership.",
        is_trap=True, is_desirable=False,
    ),
    AttractorBasin(
        name="Extractive Growth Trap",
        center_x=35, center_y=15, radius=22, strength=0.55,
        description="Moderate economic complexity built on resource extraction or cheap labor, with extractive institutions. Growth without development. Hard to escape because elites benefit from the status quo.",
        is_trap=True, is_desirable=False,
    ),
    AttractorBasin(
        name="Middle-Income Trap",
        center_x=55, center_y=35, radius=25, strength=0.50,
        description="Moderate complexity and institutional quality. Growth slows as cheap labor advantages fade, but institutions aren't strong enough for innovation-led growth. The most common trap — many nations stall here.",
        is_trap=True, is_desirable=False,
    ),
    AttractorBasin(
        name="Liberal Market Attractor",
        center_x=75, center_y=60, radius=28, strength=0.45,
        description="High economic complexity with adequate institutions. Market-led growth with moderate state capacity. The Anglo-American development model.",
        is_trap=False, is_desirable=True,
    ),
    AttractorBasin(
        name="Coordinated Market Attractor",
        center_x=78, center_y=80, radius=30, strength=0.48,
        description="High complexity with strong institutions. Coordinated capitalism — state, firms, and labor cooperate on long-term investment. The Nordic/Rhine development model.",
        is_trap=False, is_desirable=True,
    ),
    AttractorBasin(
        name="Developmental State Attractor",
        center_x=82, center_y=65, radius=26, strength=0.47,
        description="Very high economic complexity driven by state-led industrial policy. Strong state capacity directs development but political institutions lag. The East Asian model.",
        is_trap=False, is_desirable=True,
    ),
]


class ConvergenceMap:
    """The phase space in which nations navigate.
    
    Manages attractor basins, calculates gravitational pulls, and tracks
    nation trajectories over time.
    """
    
    def __init__(self, basins: Optional[List[AttractorBasin]] = None):
        self.basins = basins or STANDARD_BASINS
        self.trajectories: Dict[str, List[PhasePosition]] = {}  # nation_id -> history
    
    def gravitational_pull(self, position: PhasePosition) -> Tuple[float, float]:
        """Calculate the net force vector on a position from all basins.
        
        Returns (dx, dy) representing the annual drift from attractor pulls.
        Forces are stronger when near a basin boundary, weaker when deep inside.
        """
        total_dx, total_dy = 0.0, 0.0
        
        for basin in self.basins:
            dist = position.distance_to(PhasePosition(basin.center_x, basin.center_y))
            
            if dist < 1.0:
                # At the center — no pull (equilibrium)
                continue
            
            # Force = strength / distance (inverse linear, not squared — 
            # so distant basins still have meaningful influence)
            # Clamp to avoid extreme forces at very close distances
            effective_dist = max(dist, 0.5)
            force_magnitude = basin.strength / effective_dist * basin.radius * 0.3
            
            # Direction from position toward basin center
            dx = (basin.center_x - position.economic_complexity) / effective_dist
            dy = (basin.center_y - position.institutional_quality) / effective_dist
            
            # Repellers push away instead of pull
            if basin.is_trap and basin.name == "Failed State Repeller":
                force_magnitude *= -1.0
            
            total_dx += dx * force_magnitude
            total_dy += dy * force_magnitude
        
        # Clamp annual drift
        max_drift = 5.0
        total_dx = max(-max_drift, min(max_drift, total_dx))
        total_dy = max(-max_drift, min(max_drift, total_dy))
        
        return (total_dx, total_dy)
    
    def dominant_basin(self, position: PhasePosition) -> Optional[AttractorBasin]:
        """Which basin has the strongest pull on this position?"""
        best = None
        best_force = 0.0
        
        for basin in self.basins:
            dist = position.distance_to(PhasePosition(basin.center_x, basin.center_y))
            force = basin.strength / max(dist, 0.5) * basin.radius
            
            if force > best_force:
                best_force = force
                best = basin
        
        return best
    
    def in_basin(self, position: PhasePosition, basin: AttractorBasin) -> bool:
        """Is the position inside this basin's zone of influence?"""
        dist = position.distance_to(PhasePosition(basin.center_x, basin.center_y))
        return dist <= basin.radius
    
    def convergence_distance(self, position: PhasePosition) -> float:
        """Distance to the nearest desirable attractor.
        
        This is the convergence metric — how far a nation has to travel
        to reach a high-development equilibrium.
        """
        desirable = [b for b in self.basins if b.is_desirable]
        if not desirable:
            return 100.0
        
        return min(
            position.distance_to(PhasePosition(b.center_x, b.center_y))
            for b in desirable
        )
    
    def saddle_proximity(self, position: PhasePosition) -> float:
        """How close is this position to a basin boundary (saddle point)?
        
        Near boundaries, small policy changes have large effects.
        Returns 0 (deep in a basin) to 1 (exactly on a boundary).
        """
        if not self.basins:
            return 0.0
        
        # Find the two basins with the strongest pull
        pulls = []
        for basin in self.basins:
            dist = position.distance_to(PhasePosition(basin.center_x, basin.center_y))
            force = basin.strength / max(dist, 0.5) * basin.radius
            pulls.append((force, basin, dist))
        
        pulls.sort(key=lambda x: x[0], reverse=True)
        
        if len(pulls) < 2:
            return 0.0
        
        # If two basins pull with similar strength, we're near a boundary
        force_ratio = pulls[1][0] / max(pulls[0][0], 0.001)
        return min(1.0, force_ratio)
    
    def record_position(self, nation_id: str, position: PhasePosition) -> None:
        """Record a nation's position in its trajectory history."""
        if nation_id not in self.trajectories:
            self.trajectories[nation_id] = []
        self.trajectories[nation_id].append(position)
    
    def trajectory_summary(self, nation_id: str) -> Dict:
        """Summarize a nation's convergence trajectory."""
        if nation_id not in self.trajectories or not self.trajectories[nation_id]:
            return {"error": "No trajectory data"}
        
        traj = self.trajectories[nation_id]
        start = traj[0]
        end = traj[-1]
        
        total_distance = sum(
            traj[i].distance_to(traj[i+1])
            for i in range(len(traj) - 1)
        )
        
        net_progress = PhasePosition(
            end.economic_complexity - start.economic_complexity,
            end.institutional_quality - start.institutional_quality,
        )
        
        return {
            "nation": nation_id,
            "years": f"{start.year}-{end.year}",
            "start_position": (round(start.economic_complexity, 1), round(start.institutional_quality, 1)),
            "end_position": (round(end.economic_complexity, 1), round(end.institutional_quality, 1)),
            "net_progress": (round(net_progress.economic_complexity, 1), round(net_progress.institutional_quality, 1)),
            "total_distance_traveled": round(total_distance, 1),
            "convergence_remaining": round(self.convergence_distance(end), 1),
            "dominant_basin": self.dominant_basin(end).name if self.dominant_basin(end) else "none",
        }


def compute_economic_complexity(gdp_per_capita: float, industrial_share: float,
                                  export_diversity: float, human_capital: float,
                                  innovation_index: float) -> float:
    """Map real economic indicators to the 0-100 phase space X-axis.
    
    Economic complexity goes beyond GDP — it captures the diversity
    and sophistication of productive capabilities.
    """
    # GDP component (log scale — diminishing returns)
    # $500 = ~5, $5000 = ~35, $50000 = ~65
    gdp_component = min(60, math.log10(max(500, gdp_per_capita) / 500) * 25)
    
    # Industrial diversity component
    industrial_component = industrial_share * 30
    
    # Export sophistication
    export_component = export_diversity * 20
    
    # Human capital
    human_component = human_capital * 15
    
    # Innovation
    innovation_component = innovation_index * 15
    
    raw = gdp_component + industrial_component + export_component + human_component + innovation_component
    return max(0.0, min(100.0, raw))


def compute_institutional_quality(property_rights: float, state_capacity: float,
                                    rule_of_law: float, corruption_control: float,
                                    regulatory_quality: float) -> float:
    """Map institutional indicators to the 0-100 phase space Y-axis."""
    return (
        property_rights * 20 +
        state_capacity * 25 +
        rule_of_law * 20 +
        (1.0 - corruption_control) * 20 +  # invert: low corruption = high score
        regulatory_quality * 15
    )
