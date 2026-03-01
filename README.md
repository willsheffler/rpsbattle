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

The graphical app now opens with a start screen before the simulation begins.
Use the buttons to change a few starting variables, then click `Start Simulation`.

Optional examples:
```bash
# Disable loser conversion rule.
uv run python main.py --no-convert

# Disable creature-to-creature bounce.
uv run python main.py --no-bounce

# Spawn random obstacle shapes with average size 36.
uv run python main.py --obstacle-count 5 --obstacle-avg-size 36

# Make winners grow by the loser's mass.
uv run python main.py --grow-on-win

# Faster game with more creatures.
uv run python main.py --fps 12 --count 20

# Customize speed randomization range (base speed * multipliers).
uv run python main.py --speed 50 --min-speed-mult 0.8 --max-speed-mult 1.2

# Speed up all simulation ticks globally.
uv run python main.py --tps-multiplier 2.0

# Headless mode (no window), prints winner.
uv run python main.py --headless --max-ticks 20000
```

You can also run:
```bash
uv run rpsbattle --no-convert
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
