# GAME_DESIGN.md

# The Forgotten Jobs

## Design pillars

The mod adds **30 jobs** in four tiers.

### Tier I
1. Brise-Lame — anti-armure
2. Traqueur — chasse / cible prioritaire
3. Pyromancien — feu / terrain
4. Chirurgien de Guerre — soins physiques
5. Exorciste — purification / anti-undead
6. Saboteur — debuffs
7. Alchimiste de Combat — mélanges / explosifs
8. Marche-Vent — mobilité / déplacement forcé
9. Dresseur de Guerre — monstres
10. Hémomancien — sacrifice de PV

### Tier II
11. Bastion — tank / contrôle de zone
12. Duelliste — combat 1v1
13. Conducteur d’Orage — foudre en chaîne
14. Pestifère — maladies
15. Sanguelame — berserker
16. Sylvestre — terrain / nature
17. Artificier — pièges
18. Spirite — âmes / unités KO
19. Graviturge — gravité / positionnement
20. Occultiste — magie interdite

### Tier III
21. Chronarque — CT / ordre des tours
22. Maître d’Armes — arsenal
23. Miméomancien — capture de techniques
24. Maréchal — commandement
25. Seigneur des Tempêtes — météo
26. Marche-Néant — téléportation
27. Arbitre — lois de combat
28. Chimériste — traits monstrueux

### Tier IV
29. Astromancien — magie céleste
30. Parangon d’Ivalice — personnalisation ultime

## Global balance rules

- CT changes from custom systems: max +40 / -40 CT per round per unit.
- Same-category stat buffs do not stack; strongest value wins.
- Hard control grants temporary control resistance.
- Bosses resist but are not universally immune to debuffs.
- Hémomancien: max 3 blood marks per target.
- Sanguelame: self-inflicted HP loss does not generate Fury.
- Artificier: max 4 active traps.
- Conducteur d’Orage: chain damage loses ~20% per bounce.
- Spirite: max 5 souls consumed by one skill.
- Arbitre: one global law active per Arbitre.
- Seigneur des Tempêtes: one major weather state active.
- Astromancien: major astral cast-time reduction capped at 25%.
- Parangon inherited skills are weaker than originals.

## Prototype jobs

Priority order:
1. Brise-Lame
2. Pyromancien
3. Hémomancien
4. Bastion
5. Artificier
6. Graviturge
7. Chronarque
8. Arbitre

## Unlock tree

See `docs/job-tree.md`.

## Balance targets

See `docs/balance-rules.md`.

## Implementation policy

The design is aspirational until verified against the actual game engine.
Any unsupported mechanic must be adapted rather than forcing an unsafe or fragile implementation.
