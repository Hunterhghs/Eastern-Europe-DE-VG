#!/usr/bin/env python3
"""
Run a Convergence simulation from the command line.

Usage:
    python3 -m sim.run --nation moravia_nord
    python3 -m sim.run --nation zaleskia --no-auto
    python3 -m sim.run --nation all --output json
    python3 -m sim.run --list-nations
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent to path for direct execution
sys.path.insert(0, str(Path(__file__).parent.parent))

from sim.engine import SimulationEngine


def list_nations():
    """Print all available nations."""
    with open(Path(__file__).parent / "data" / "nations.json") as f:
        data = json.load(f)
    
    print("\nAvailable Nations in the Carpathian Crescent:\n")
    for nid, nation in data["nations"].items():
        geo = nation["geography"]
        start = nation["era1_start"]
        print(f"  {nation['name']} ({nid})")
        print(f"    Pop 1918: {nation['population_1918_millions']}M | Area: {nation['area_km2']:,} km²")
        print(f"    Geography: {geo['terrain'].replace('_', ' ').title()}")
        print(f"    Legacy: {start['institutional_legacy'].replace('_', ' ').title()}")
        print(f"    D-Coefficient (1918): {start['d_coefficient']}")
        print(f"    GDP/cap: ${start['gdp_per_capita_ppp']} | Literacy: {start['literacy_rate']:.0%}")
        print()


def run_simulation(nation_id: str, auto_policy: bool = True, output_json: bool = False):
    """Run a single simulation and print results."""
    engine = SimulationEngine(nation_id)
    
    if output_json:
        # Run silently and output JSON
        while engine.state.year <= 2025:
            engine.check_era_transition()
            if auto_policy:
                _auto_policy_cycle(engine)
            engine.tick()
        print(json.dumps(engine.to_dict(), indent=2, default=str))
    else:
        # Run with logging
        result = engine.run(auto_policy=auto_policy)
        print(result)


def _auto_policy_cycle(engine):
    """Replicate the auto-policy logic from engine.run() for JSON mode."""
    s = engine.state
    era = s.era
    year_mod = s.year % 3
    
    if year_mod == 0:
        if era == "era1_nation_building":
            engine.apply_policy("education_investment", 0.6)
            engine.apply_policy("infrastructure_investment", 0.4)
            if s.year % 9 == 0:
                engine.apply_policy("institution_building", 0.5)
        elif era == "era2_planned_development":
            engine.apply_policy("industrial_policy", 0.7)
            engine.apply_policy("infrastructure_investment", 0.5)
            if s.year % 9 == 0:
                engine.apply_policy("health_investment", 0.4)
        elif era == "era3_convergence":
            engine.apply_policy("institution_building", 0.5)
            engine.apply_policy("eu_accession_prep", 0.6)
            engine.apply_policy("digital_infrastructure", 0.4)
            if s.environmental_damage_accumulated > 0.4:
                engine.apply_policy("environmental_cleanup", 0.5)


def main():
    parser = argparse.ArgumentParser(
        description="Convergence — Development Economics Simulation"
    )
    parser.add_argument("--nation", "-n", default="moravia_nord",
                       help="Nation ID to simulate (or 'all')")
    parser.add_argument("--no-auto", action="store_true",
                       help="Disable auto-policy (passive simulation only)")
    parser.add_argument("--output", "-o", choices=["text", "json"], default="text",
                       help="Output format")
    parser.add_argument("--list-nations", action="store_true",
                       help="List all available nations and exit")
    
    args = parser.parse_args()
    
    if args.list_nations:
        list_nations()
        return
    
    if args.nation == "all":
        with open(Path(__file__).parent / "data" / "nations.json") as f:
            data = json.load(f)
        
        for nid in data["nations"]:
            print(f"\n{'='*60}")
            run_simulation(nid, auto_policy=not args.no_auto, 
                          output_json=(args.output == "json"))
    else:
        run_simulation(args.nation, auto_policy=not args.no_auto,
                      output_json=(args.output == "json"))


if __name__ == "__main__":
    main()
