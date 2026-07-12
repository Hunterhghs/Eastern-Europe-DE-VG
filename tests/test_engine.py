"""
Tests for Convergence simulation engine.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sim.engine import SimulationEngine
from sim.d_coefficient import DCoefficientEngine, DCoefficientInputs, create_inputs_from_nation
from sim.institutions import InstitutionalDNA, seed_initial_institutions
from sim.convergence_map import ConvergenceMap, PhasePosition, STANDARD_BASINS


def test_d_coefficient_calculation():
    """D-coefficient should return values in [0, 100]."""
    engine = DCoefficientEngine()
    
    # Load all nations
    data_dir = Path(__file__).parent.parent / "sim" / "data"
    with open(data_dir / "nations.json") as f:
        nations = json.load(f)["nations"]
    
    for nid, nation in nations.items():
        inputs = create_inputs_from_nation(nation)
        d = engine.calculate(inputs)
        assert 0 <= d <= 100, f"{nid}: D={d} out of range"
    
    print("  ✅ D-coefficient calculation: all nations in [0, 100]")


def test_nation_differentiation():
    """Nations should have meaningfully different starting positions."""
    data_dir = Path(__file__).parent.parent / "sim" / "data"
    with open(data_dir / "nations.json") as f:
        nations = json.load(f)["nations"]
    
    d_values = {}
    for nid, nation in nations.items():
        inputs = create_inputs_from_nation(nation)
        engine = DCoefficientEngine()
        d_values[nid] = engine.calculate(inputs)
    
    # Should have meaningful spread
    spread = max(d_values.values()) - min(d_values.values())
    assert spread > 15, f"D-coefficient spread only {spread:.1f} — not enough differentiation"
    
    print(f"  ✅ Nation differentiation: D-coefficient spread {spread:.1f} (max {max(d_values.values()):.1f}, min {min(d_values.values()):.1f})")


def test_era_transitions():
    """Era transitions should occur at correct years."""
    engine = SimulationEngine("moravia_nord", seed=42)
    
    assert engine.state.era == "era1_nation_building"
    assert engine.state.year == 1918
    
    # Run past 1945
    while engine.state.year < 1946:
        engine.tick()
    
    transition = engine.check_era_transition()
    assert transition is not None or engine.state.era == "era2_planned_development", \
        f"Era 1→2 transition failed at year {engine.state.year}, era={engine.state.era}"
    
    print(f"  ✅ Era 1→2 transition at year {engine.state.year}")


def test_policies_have_effect():
    """Applying policies should change state variables."""
    engine = SimulationEngine("moravia_nord", seed=42)
    
    initial_literacy = engine.state.literacy_rate
    engine.apply_policy("education_investment", 1.0)
    assert engine.state.literacy_rate > initial_literacy, "Education policy had no effect"
    
    initial_infra = engine.state.infrastructure_quality
    engine.apply_policy("infrastructure_investment", 1.0)
    assert engine.state.infrastructure_quality > initial_infra, "Infrastructure policy had no effect"
    
    print(f"  ✅ Policies have measurable effects")


def test_institutional_inertia():
    """Deep institutions should resist reform more than shallow ones."""
    dna = seed_initial_institutions("austro_hungarian", 0.45, 40)
    
    # Should have institutions with significant depth
    assert len(dna.institutions) > 0, "No institutions seeded"
    
    # Old institution should have inertia
    old_inst = list(dna.institutions.values())[0]
    assert old_inst.inertia > 0.4, f"40yr institution should have high inertia, got {old_inst.inertia:.2f}"
    
    print(f"  ✅ Institutional inertia: {old_inst.inertia:.2f} for {old_inst.depth_years}yr institution")


def test_convergence_map_basins():
    """Convergence map should have attractor basins that pull positions."""
    cmap = ConvergenceMap(basins=STANDARD_BASINS)
    
    # Test a position near the Failed State Repeller — should be pushed away
    pos = PhasePosition(10, 8)
    dx, dy = cmap.gravitational_pull(pos)
    # Should not have zero pull
    assert abs(dx) + abs(dy) > 0.01, "No gravitational pull detected"
    
    # Test position in Middle-Income Trap
    pos_trap = PhasePosition(55, 35)
    dominant = cmap.dominant_basin(pos_trap)
    assert dominant is not None, "No dominant basin for trap position"
    
    print(f"  ✅ Convergence map: {len(cmap.basins)} basins, gravitational pull active")


def test_simulation_runs():
    """Full simulation should complete without errors."""
    engine = SimulationEngine("moravia_nord", seed=42)
    
    # Run silently
    while engine.state.year <= 2025:
        engine.check_era_transition()
        engine.tick()
    
    # Should have a valid final state
    assert engine.state.gdp_per_capita_ppp > 0, "GDP collapsed to zero"
    assert 0 <= engine.state.d_coefficient <= 100, "D-coefficient out of range"
    assert engine.state.literacy_rate > 0.5, "Literacy unrealistically low"
    assert engine.state.life_expectancy > 40, "Life expectancy unrealistically low"
    
    # Should have tracked history
    assert len(engine.state_history) > 50, f"Only {len(engine.state_history)} history entries"
    
    print(f"  ✅ Full simulation: {len(engine.state_history)} years simulated")
    print(f"     GDP: ${engine.state_history[0].gdp_per_capita_ppp:.0f} → ${engine.state.gdp_per_capita_ppp:.0f}")
    print(f"     D-coefficient: {engine.state_history[0].d_coefficient:.1f} → {engine.state.d_coefficient:.1f}")


if __name__ == "__main__":
    print("═══ Convergence Simulation Tests ═══\n")
    
    tests = [
        test_d_coefficient_calculation,
        test_nation_differentiation,
        test_policies_have_effect,
        test_institutional_inertia,
        test_convergence_map_basins,
        test_simulation_runs,
        test_era_transitions,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  ❌ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"  💥 {test.__name__}: {type(e).__name__}: {e}")
            failed += 1
    
    print(f"\n═══ Results: {passed} passed, {failed} failed ═══")
    
    if failed > 0:
        sys.exit(1)
