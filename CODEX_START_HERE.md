# CODEX_START_HERE.md

# The Forgotten Jobs — Codex Handoff

You are taking over implementation of **The Forgotten Jobs**, an expansion mod project for
**FINAL FANTASY TACTICS – The Ivalice Chronicles**.

## Read first

1. `AGENTS.md`
2. `GAME_DESIGN.md`
3. `docs/implementation-notes.md`
4. `docs/job-tree.md`
5. `docs/balance-rules.md`
6. `docs/asset-pipeline.md`
7. `docs/TODO.md`

A visual concept board is available at:

`assets/reference/the_forgotten_jobs_concept_board.png`

## First mission: reconnaissance only

Do **not** begin implementing all 30 jobs.

Your first task is to determine what is technically possible in the actual game/modding environment.

Investigate and document:

- game data/archive structure
- job table format and limits
- ability table format and limits
- unlock-condition representation
- localization format
- sprite, portrait, icon and effect formats
- whether rows can be appended or only replaced
- custom status-effect feasibility
- HP-cost ability feasibility
- direct CT manipulation feasibility
- forced movement feasibility
- persistent tile/trap feasibility
- battle-wide state feasibility (weather/laws)
- AI behavior with new jobs/abilities
- save-data implications of adding new job mastery state

Record verified findings in:

`docs/implementation-notes.md`

Do not replace `UNKNOWN` with assumptions.

## Deliverable for reconnaissance

Create:

`docs/recon-report.md`

It should contain:

1. tools used
2. files inspected
3. verified formats
4. hard engine limits
5. safe extension points
6. risky/unknown systems
7. recommended implementation strategy
8. blockers
9. next-step recommendation for the Brise-Lame vertical slice

## After reconnaissance

Only after the report is complete and evidence-backed:

Implement **Brise-Lame** as the first vertical slice.

Definition of done is in `AGENTS.md`.

## Safety / preservation

- Never overwrite original game files.
- Work from copies or mod output directories.
- Make every patch reproducible.
- Add dry-run validation for binary/data patchers.
- Log all changed/generated files.
