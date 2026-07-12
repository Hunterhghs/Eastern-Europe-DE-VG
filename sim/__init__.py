"""
Convergence — Development Economics Simulation Game

A deep systems simulation where you guide a fictional Eastern European
nation across 100 years of development.

Modules:
- d_coefficient: The Medium Coefficient engine
- institutions: Institutional DNA system
- convergence_map: Phase space with attractor basins
- events: Crisis and random event system
- engine: Core simulation orchestrator
"""

from .engine import SimulationEngine, NationState
from .d_coefficient import DCoefficientEngine, DCoefficientInputs
from .institutions import InstitutionalDNA, Institution
from .convergence_map import ConvergenceMap, PhasePosition, AttractorBasin
from .events import EventEngine, Crisis

__version__ = "0.1.0"
