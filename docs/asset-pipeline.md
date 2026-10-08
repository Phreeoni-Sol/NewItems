# Asset Pipeline

## Principle

Do not generate final production sprites before the actual sprite specification is discovered.

## Temporary workflow

1. Create concept art and silhouette references.
2. Store them under `assets/reference/` if added later.
3. Determine exact in-game sprite/portrait format.
4. Build conversion/validation tools.
5. Produce final pixel assets at the verified dimensions/palette.
6. Validate every output automatically.

## Naming

Use stable machine names:

- `blade_breaker_male`
- `blade_breaker_female`
- `pyromancer_male`
- `pyromancer_female`

Suggested files once format is known:

- `<job>_<gender>_battle.<ext>`
- `<job>_<gender>_portrait.<ext>`
- `<job>_icon.<ext>`

## Sprite art direction

Target:
- FFT/Ivalice silhouette readability
- strong job-specific headgear / weapon silhouette
- restrained detail
- color separation readable at battle scale
- male/female variants should share the same job identity

Avoid:
- overly modern armor
- photorealism
- tiny unreadable accessories
- palette choices that blend into common maps

## First concepts

Produce concept sheets first for:
1. Brise-Lame
2. Pyromancien
3. Hémomancien
4. Bastion
5. Artificier
6. Graviturge
7. Chronarque
8. Arbitre
