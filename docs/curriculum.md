# Living Curriculum

Purpose: This is the project learning roadmap and pacing document.
Use it as the single source of truth across sessions.

Update cadence:
- Update after each session.
- Keep changes short and concrete.

Last updated: 2026-02-14

## Program Goals
- Teach Jonah core Python and simulation thinking through playful experiments.
- Build a 2D creature world where interactions are based on rock-paper-scissors.
- Keep progress visible for learning reflection and possible school credit.

## Current Focus
- Phase: Foundations
- Current target: Continuous 2D arena simulation with configurable encounter rules.
- Current session update (2026-02-08): Built a working continuous arena game with headless winner reporting and image sprites.
- Definition of done for this phase:
  - Arena renders consistently.
  - Creatures move each tick with delta-time updates.
  - Creature encounters resolve via RPS rules in both convert and elimination modes.

## Next Session Draft
- Primary goal: Use headless mode to run repeated simulations and measure win-rate patterns.
- Stretch goal: Add `--headless-runs N` and print aggregate rock/paper/scissors wins.
- Student challenge: Form a hypothesis, change one parameter (`--tps-multiplier`, speed range, or count), and explain how outcomes changed.
- Next-session task list:
  - Add `--headless-runs N` and aggregate win summary output.
  - Add reproducibility reporting with explicit seed in outputs.
  - Tighten win detection and end-of-run reporting.
  - Add one focused stats display improvement.
  - Set exact creature amounts and starting positions.
  - Make creatures bounce off each other.
  - Add sound.
  - Explore pathfinding/AI.
  - Improve stats display.
  - Add arena features/walls.

## Backlog
Choose from this list each session based on interest and momentum.

### Ready Now
- Add headless batch runs and aggregate results.
- Add explicit seed/config echo in CLI output.
- Add a small regression test for winner resolution behavior.
- Create fixed-size board render.
- Add simulation loop and tick counter.
- Add creature state (x, y, type).
- Add random movement with boundary rules.
- Add encounter detection on shared tile.
- Add RPS winner/loser resolution.

### Next
- Improve HUD stats (counts, rates, and run summary).
- Add one controlled experiment preset.
- Add config file for board size and spawn count.
- Add pause/step controls.

### Later
- Add creature behavior variants (aggressive, avoidant, random).
- Add food/resource mechanics.
- Add reproduction and mutation experiments.
- Add experiment preset comparison utilities.

## Completed Milestones
| Date | Milestone | Notes |
|---|---|---|
| 2026-02-08 | First playable continuous arena build | Added movement smoothing, image sprites, screenshot key, speed controls, headless mode, and no-convert elimination behavior. |

For update procedure, see:
- `shared/sheffler_standards/docs/playbooks/session-management.md`
