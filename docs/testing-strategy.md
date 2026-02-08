# Testing Strategy for Pygame Project

## Core Principle
Test simulation logic heavily, keep graphics tests lightweight.

## What To Unit Test (pytest)
- RPS rules (`rps_winner`)
- Board boundaries and clamping
- Simulation step behavior (tick updates, encounter outcomes, counts)
- Deterministic behavior with seeded/stub RNG

## What Not To Over-Test Early
- Pixel-perfect rendering
- Pygame internals
- Window event loop details

## Practical Graphics Testing Options
1. Smoke test only (recommended first)
- Run app and confirm window opens, updates, and closes cleanly.

2. Headless render check (optional)
- Set `SDL_VIDEODRIVER=dummy` in CI.
- Render one frame to a surface.
- Assert no exceptions and expected surface size.

3. Snapshot image tests (later)
- Save a frame image.
- Compare against a baseline with tolerance.
- Use only after visuals become important and stable.

## Suggested Test Pyramid For This Repo
- 80% pure logic unit tests
- 15% integration tests (simulate a few ticks)
- 5% manual visual smoke checks

## Commands (uv)
- Install deps: `uv sync --dev`
- Run tests: `uv run pytest -q`
- Run app: `uv run python main.py`
