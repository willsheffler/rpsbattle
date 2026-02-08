# AGENTS.md

## 1) Purpose and Audience
This is a learning project for Jonah (15, basic Python) and his father Will (professional software engineer).
Primary goals:
- Teach core programming and simulation concepts.
- Have fun building evolving creature simulations together.
- Maintain school-credit-friendly documentation of progress.

## 2) Project Direction
- Build creature simulations in a 2D world (Primer-style experiments).
- Start simple and layer complexity gradually.
- First milestone: a 2D board where creatures move and interact via rock-paper-scissors.

## 3) Teaching-First Engineering Rules
- Prefer clarity over cleverness.
- Keep code beginner-readable: small functions, clear names, minimal indirection.
- Introduce one major concept per change when possible.
- Explain tradeoffs in plain language.
- Use short teaching comments only when intent is not obvious.

## 4) Code and Design Standards
- Use Python and follow PEP 8.
- Avoid premature abstractions and deep class hierarchies.
- Preserve existing behavior unless change is requested.
- Prefer deterministic setups first (seed/config) before heavy randomness.
- Keep simulation parameters easy to tweak (board size, creature count, movement, encounter rules).

## 5) Validation and Scope
- Run relevant checks/tests after changes.
- If no tests exist, run a smoke check and report it.
- If something cannot be verified, state that explicitly.
- Do not delete files unless explicitly requested.
- Avoid unrelated refactors and unrelated file edits.

## 6) Chat-First Session Workflow (Default)
Use chat as the primary workflow for planning, logging, and reporting.

### Session Start Protocol
When the user says `Start session`, do all of the following:
1. Ask for:
   - Participants
   - Planned duration
   - Primary goal
   - Stretch goal
   - Expected evidence (commits/screenshots/notes)
2. Create a dated session log in `docs/session-logs/`.
3. Add an initial `Next Session Draft` or current-session focus update in `docs/curriculum.md`.

### During Session Protocol
When the user says `log this: ...`:
- Append concise notes to the active session log.
- Capture learning moments, blockers, and notable decisions.

### Reminder Protocol
If the workflow is not being followed, provide gentle reminders.
Examples:
- If coding starts before `Start session`: remind user to start the session log.
- Mid-session (after substantial work): remind user to capture evidence.
- Before wrapping up: remind user to run `End session` for documentation closure.

### Session End Protocol
When the user says `End session`, do all of the following:
1. Ask for a brief recap if needed.
2. Finalize the current session log.
3. Update `docs/curriculum.md`:
   - Move completed items to milestones.
   - Refresh `Next Session Draft`.
4. Update monthly report data in `docs/reports/`.
5. Provide a print-ready summary for school-credit records.

## 7) Documentation Outputs
Maintain these files:
- Living plan: `docs/curriculum.md`
- Per-session logs: `docs/session-logs/YYYY-MM-DD-<slug>.md`
- Monthly report: `docs/reports/<YYYY-MM>.md` (or template-derived equivalent)

## 8) Communication Expectations
In coding summaries, include:
- What changed
- Why it changed
- How it was verified
- What Jonah should learn from this step (brief)
- Suggested next incremental step
