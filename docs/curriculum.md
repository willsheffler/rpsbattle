# Living Curriculum

Purpose: This is the project learning roadmap and pacing document.
Use it as the single source of truth across sessions.

Update cadence:
- Update after each session.
- Keep changes short and concrete.

Last updated: 2026-03-01

## Program Goals
- Teach Jonah core Python and simulation thinking through playful experiments.
- Build a 2D creature world where interactions are based on rock-paper-scissors.
- Keep progress visible for learning reflection and possible school credit.

## Current Focus
- Phase: Foundations
- Current target: Continuous 2D arena simulation with configurable encounter rules, obstacle variation, and clearer in-app controls.
- Current session update (2026-02-28): Completed a 1-hour exploratory build with Will and Jonah. The sim now has a settings menu, restart flow, screenshots from menu and gameplay, random non-overlapping obstacles, mass-based growth and bounce, and a working win screen.
- Current session update (2026-02-08): Built a working continuous arena game with headless winner reporting and image sprites.
- Definition of done for this phase:
  - Arena renders consistently.
  - Creatures move each tick with delta-time updates.
  - Creature encounters resolve via RPS rules in both convert and elimination modes.

## Next Session Draft
- Primary goal: Add one polish feature that improves repeat play or observation without changing the core simulation too much.
- Stretch goal: Add one measurable experiment or stats improvement after the first polish feature works.
- Student challenge: Make a prediction before changing the simulation, then explain whether the result matched the prediction.
- Next-session task list:
  - Add a `Play Again` button on the win screen.
  - Add a scoreboard across rounds.
  - Add better HUD/debug labels for mass and current settings.
  - Add `--headless-runs N` and aggregate win summary output.
  - Add reproducibility reporting with explicit seed in outputs.
  - Add one focused stats display improvement.
  - Add sound.
  - Explore pathfinding/AI.

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
| 2026-02-28 | Exploratory controls and obstacle upgrade session | Added menu controls, restart flow, random obstacle variations, mass-based growth and bounce, screenshot capture in menu/game, and a live win screen. |

For update procedure, see:
- `shared/sheffler_standards/docs/playbooks/session-management.md`
