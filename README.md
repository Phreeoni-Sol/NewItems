# NewItems — The Forgotten Jobs

Commencer par [CLAUDE_IMPLEMENTATION_JEU.md](CLAUDE_IMPLEMENTATION_JEU.md).

271 nouveaux objets conçus ; 57 équipements avec des propositions de combat, soit 228 vues. Ce dépôt prépare une extension additive : aucun mod jouable validé et aucun remplacement vanilla.

Les assets, mécaniques et recherches actuels se trouvent dans outputs/. Les documents historiques ci-dessous décrivent le cœur runtime. Les binaires du jeu, builds et clés API sont exclus. Pour contrôler cette livraison Git : python handoff/verify_git_delivery.py.

# The Forgotten Jobs

**Reprise Claude : commencer par [CLAUDE_START_HERE.md](CLAUDE_START_HERE.md).**
Le prompt prêt à coller est `CLAUDE_PROMPT.txt`. Vérification du kit et tests :
`handoff/Verify-Handoff.ps1`, puis `handoff/Run-Checks.ps1 -Mode Core`.
L'état technique le plus récent est [runtime-extension.md](docs/runtime-extension.md).
Les rapports ci-dessous conservent l'historique des étapes précédentes.

**Ajout indépendant uniquement ; jobs et compétences vanilla préservés.**

Le développement de Brise-Lame est commencé. [État actuel et preuves](docs/additive-extension.md) : ajouts NXD avec conservation des cellules originales, audit des tables natives et du menu, diagnostic Reloaded compilé. **Brise-Lame n'est pas encore jouable.** Aucun ID moteur alloué, aucun patch appliqué au jeu, aucune sauvegarde modifiée.

Le package `packages/read-only-probe` est un diagnostic en lecture seule, pas le mod final. Le builder de données refuse tout remplacement et bloque la production tant que l'ajout runtime n'est pas validé. Les anciens prototypes de remplacement sont abandonnés.
## Reconnaissance — 6 octobre 2026

Voir [le rapport initial](docs/recon-report.md), [les observations techniques](docs/implementation-notes.md) et `recon-output/`.
61 archives locales inventoriées ; dix fichiers extraits hors du projet ; sept tables NXD décodées. Aucun mod appliqué. Extension des jobs et tests runtime restent UNKNOWN.

Depuis ce dossier, avec PowerShell 7 et les bibliothèques du loader local :

```powershell
$game = 'D:\FINAL-FANTASY-TACTICS-The-Ivalice-Chronicles\FINAL FANTASY TACTICS - The Ivalice Chronicles'
$loader = 'D:\FINAL-FANTASY-TACTICS-The-Ivalice-Chronicles\CoopMod\tools\Reloaded-II\Mods\fftivc.utility.modloader'
# Choisir un dossier hors du jeu/loader pour conserver les binaires extraits.
$scratch = Join-Path $env:TEMP 'forgotten-jobs-recon'
.\tools\extract\recon.ps1 -GameRoot $game -LoaderRoot $loader -OutputRoot .\recon-output -DryRun
.\tools\extract\recon.ps1 -GameRoot $game -LoaderRoot $loader -OutputRoot .\recon-output
.\tools\extract\sample-tables.ps1 -GameRoot $game -LoaderRoot $loader -SampleRoot (Join-Path $scratch 'samples') -ReportRoot .\recon-output
.\tests\recon-tests.ps1 -GameRoot $game -LoaderRoot $loader -ScratchRoot (Join-Path $scratch 'tests')
```

Les scripts chargent les bibliothèques existantes et ne lancent pas le jeu. Le diagnostic est compilé ; aucun patcher runtime additif validé, aucun ID alloué. Les échantillons du jeu ne sont pas inclus dans ce livrable.

Expansion mod project for **FINAL FANTASY TACTICS – The Ivalice Chronicles**.

## Goal

Add 30 new jobs while preserving the value of the original job system.

Core design principles:

- New jobs should create new playstyles, not simply stronger versions of vanilla jobs.
- Existing jobs remain relevant as prerequisites and as secondary skill sets.
- Terrain, CT, positioning, height, status effects and equipment choices remain important.
- Tier III and IV jobs are more specialized or flexible, not automatically superior.
- Any engine limitation discovered during implementation takes precedence over speculative design.

## First implementation milestone

Prototype these 8 jobs first:

1. Brise-Lame
2. Pyromancien
3. Hémomancien
4. Bastion
5. Artificier
6. Graviturge
7. Chronarque
8. Arbitre

These cover the riskiest systems: stat breaks, terrain effects, HP-based resources, interception, traps,
forced movement, CT manipulation and global combat rules.

## Repository layout

- `GAME_DESIGN.md` — current source of truth for game design.
- `AGENTS.md` — instructions for Codex/agents.
- `docs/` — job tree, balance, asset pipeline, implementation notes.
- `data/` — structured job/ability/equipment definitions.
- `assets/` — sprites, portraits, icons and effects.
- `tools/` — extraction, conversion, validation and build tooling.
- `tests/` — automated validation and regression checks.

## Rule

Do not invent undocumented game formats, table limits, sprite dimensions or engine capabilities.
Inspect the real game/modding data first and record findings in `docs/implementation-notes.md`.


## Extension runtime : code disponible

Le cœur est écrit et compilé : redirection transactionnelle, routeur de commandes, projection de menu et progression JP/compétences séparée. 54 contrôles du cœur passent ; les fonctions natives copiées sont testées sur 5 632 couples commande/emplacement dans une fixture isolée. Cartographie : 72 références candidates, couverture totale non approuvée. Raccordement au processus du jeu et save/load non validés. Aucun job jouable installé.

État actuel détaillé : `docs/runtime-extension.md` depuis la racine du projet (ou `runtime-extension.md` depuis docs/). Les notes de reconnaissance antérieures restent historiques ; cette mise à jour décrit l'avancement du code.
