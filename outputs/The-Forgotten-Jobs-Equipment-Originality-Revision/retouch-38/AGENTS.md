# AGENTS.md — The Forgotten Jobs

## Mission

Implement **The Forgotten Jobs** as a safe, reversible expansion mod for
FINAL FANTASY TACTICS – The Ivalice Chronicles.

## Non-negotiable rules

1. **Never invent engine facts.**
   If a file format, enum, table limit, sprite layout, script hook or runtime behavior is unknown,
   mark it `UNKNOWN` and investigate it before implementing dependent features.

2. **Do not overwrite source game files.**
   Build into a separate output/mod directory.

3. **Keep extraction and build reproducible.**
   Any manual binary edit should be replaced by a documented script when possible.

4. **Preserve vanilla behavior by default.**
   New jobs must be additive unless a deliberate rebalance is documented.

5. **Every experimental mechanic needs a fallback.**
   Example:
   - custom trap entity unavailable -> emulate using status/targeted AoE;
   - global weather unavailable -> emulate as battle-wide hidden status;
   - custom CT hook unavailable -> use supported speed/charge-time mechanics.

6. **Validate IDs and table bounds.**
   Never allocate new IDs without checking collisions and maximum table sizes.

7. **Assets must follow discovered game constraints.**
   Do not assume sprite dimensions, palette format, frame count or atlas layout.

8. **All balance values belong in data where possible.**
   Avoid hardcoding numbers in scripts.

## Workflow

### Phase 0 — Reconnaissance
- Identify install layout and moddable archives.
- Identify job, ability, status, equipment and localization tables.
- Identify sprite/portrait/icon formats.
- Determine whether new rows can be appended or only existing rows replaced.
- Document toolchain and findings.

### Phase 1 — Vertical slice
Implement one complete playable job: **Brise-Lame**.
Required:
- unlock condition
- job stats
- equipment permissions
- command set
- one active skill
- one reaction
- one support
- one movement ability
- localization
- sprite/portrait placeholder
- save/load test

### Phase 2 — Risk prototypes
Prototype:
- Pyromancien terrain effect
- Hémomancien HP-cost skill
- Bastion interception/protection
- Artificier trap
- Graviturge forced movement
- Chronarque CT manipulation
- Arbitre global rule

### Phase 3 — Production
Only after Phase 2 is validated:
- implement remaining Tier I
- Tier II
- Tier III
- Tier IV
- final art integration
- balancing pass
- compatibility pass

## Coding expectations

- Prefer small tools with clear CLI arguments.
- Log every modified/generated file.
- Fail loudly on unknown IDs, duplicate IDs or invalid data.
- Add dry-run mode to binary patchers.
- Keep generated artifacts out of source folders.
- Add tests for parsers, serializers and ID allocation.

## Naming

Project: `The Forgotten Jobs`

Machine-friendly identifiers use English snake_case:
- `blade_breaker`
- `tracker`
- `pyromancer`
- `war_surgeon`
- `exorcist`

Display/localized names may remain French during design.

## Definition of done for a job

A job is not complete until:
- unlock works
- stats are correct
- equipment restrictions work
- every ability is learnable
- JP costs are correct
- AI does not obviously break
- save/load preserves state
- localization is present
- assets display without corruption
- automated validation passes
