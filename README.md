# rpsbattle

Learning-first 2D creature simulation project for Jonah and Will.

## Setup (uv)
1. Install dependencies:
```bash
uv sync --dev
```

2. Run the simulation:
```bash
uv run python main.py
```

3. Run tests:
```bash
uv run pytest -q
```

## Project Layout
- `src/sim/`: simulation and rendering code
- `tests/`: pytest tests for simulation logic
- `docs/curriculum.md`: living plan
- `docs/session-logs/`: per-session logs
- `docs/reports/`: school-credit style reports

## Next Milestone
2D board with moving creatures and RPS interactions.
