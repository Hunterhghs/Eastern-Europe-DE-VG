# The Carpathian Crescent

**A deep systems simulation of development economics set in a fictional Eastern Europe across 100 years.**

Guide a nation from the rubble of empire (1918) through industrialization to market transition (1990-2025). Every road you build, institution you found, and compromise you make echoes across generations. The game is a playable laboratory for Hunter Hughes' Convergence Maps framework — the D-coefficient, attractor basins, and institutional legacy are the controls the player touches.

---

## The Carpathian Crescent

Five composite nations embodying real Eastern European development archetypes:

| Nation | Pop. | Geography | Starting Legacy |
|--------|------|-----------|-----------------|
| **Moravia-Nord** | 2.8M | Coastal, flat, small | Austro-Hungarian admin, high literacy, port access |
| **Zaleskia** | 8.2M | Landlocked, coal-rich, rivers | Mixed imperial legacy, industrial potential, multi-ethnic |
| **Livonia-Podolia** | 5.1M | Fertile plains, no minerals | Ottoman legacy, low literacy, landed elite |
| **Vynahrad Republic** | 3.4M | Mountainous, oil reserves | Resource wealth, weak institutions, contested borders |
| **Karpathia** | 1.6M | Alpine, transit corridors | Small, multi-ethnic, strategic geography |

## Three Eras, One Map

- **Era 1: Nation-Building (1918-1945)** — Found institutions, build infrastructure, manage ethnic tensions
- **Era 2: Planned Development (1945-1990)** — Industrialize under constraint, manage urbanization
- **Era 3: Convergence or Drift (1990-2025)** — Full policy autonomy, EU accession track, inherited legacies come due

## Core Systems

- **D-Coefficient Engine** — How fast capability diffuses from cores to peripheries
- **Convergence Map** — Phase space with attractor basins, saddle points, and traps
- **Institutional DNA** — Depth × Quality matrix; institutions persist across eras
- **Legacy Cascade** — Era 1 decisions constrain Era 2; Era 1+2 legacies determine Era 3
- **Crisis Windows** — Discontinuous reform only possible during crises

## Technical Architecture

| Layer | Technology |
|-------|-----------|
| Simulation Engine | Python (NumPy/Pandas) |
| Frontend | React + Tailwind + D3.js |
| State | JSON/CSV serializable game state |
| Deployment | Static site + Streamlit backend |

## Development

```bash
# Run simulation tests
cd sim && python3 -m pytest ../tests/

# Run a sample game (100 years, Moravia-Nord)
python3 -m sim.run --nation moravia_nord --eras all

# Veles quality audit
python3 ../veles verify .
```

## Framework Origins

Built from Hunter Hughes' original intellectual frameworks:
- **The Medium Coefficient (D-coefficient)** — metric for diffusion capacity
- **Convergence Maps** — conditional catch-up with attractors and basin-crossing
- **Diffusion, Not Invention** — the century's bottleneck is deployment, not discovery
- **Grammar of the Century** — structure, diffusion, and constraint
