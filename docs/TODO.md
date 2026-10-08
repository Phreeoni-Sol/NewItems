# Implementation Backlog

Décision utilisateur : **ajout indépendant uniquement, préserver tous les jobs vanilla**. État à jour : `additive-extension.md`.

## Outillage de l'ajout

- [x] NXD : ajout de lignes et préservation de toutes les cellules vanilla sur fixtures
- [x] Audit natif reproductible, collision Job174/175 avec Ability identifiée sur ce build
- [x] Audit reproductible des 28 signatures de menu
- [x] Diagnostic Reloaded sans patch compilé et tests hors jeu réussis
- [ ] Valider chargement du diagnostic en jeu
- [ ] Cartographier tous les consommateurs et bornes avant extension native
- [ ] Valider progression et sauvegarde sans réaffectation de groupes vanilla

## P0 — Reconnaissance

6 octobre 2026 : inventaire et extraction vérifiés ; détails et UNKNOWN dans `recon-report.md`. Les cases restantes ne sont pas des impossibilités moteur.
- [ ] Identify supported mod loader/toolchain
- [x] Map relevant game archives/files
- [x] Locate job data
- [x] Locate ability data
- [x] Locate localization
- [ ] Locate battle sprites/portraits/icons
- [ ] Determine maximum table sizes
- [ ] Determine save-data implications
- [x] Create extraction script
- [x] Create validation report

## P1 — Brise-Lame vertical slice
- [ ] Allocate safe job ID
- [ ] Add job name/description
- [ ] Add unlock condition
- [ ] Add stat multipliers
- [ ] Add equipment permissions
- [ ] Implement Fracture command
- [ ] Implement 1 active ability
- [ ] Implement reaction
- [ ] Implement support
- [ ] Implement movement ability
- [ ] Add placeholder sprite
- [ ] Verify battle load
- [ ] Verify save/load

## P2 — High-risk mechanics
- [ ] Pyromancien persistent fire/terrain fallback
- [ ] Hémomancien HP costs + Blood Marks
- [ ] Bastion ally interception
- [ ] Artificier trap entity/fallback
- [ ] Graviturge forced movement
- [ ] Chronarque CT changes
- [ ] Arbitre global Law state

## P3 — Asset pipeline
- [ ] Discover sprite dimensions/layout
- [ ] Discover palette restrictions
- [ ] Build sprite validator
- [ ] Build portrait validator
- [ ] Build icon validator
- [ ] Produce 8 prototype job concept sheets
- [ ] Produce final prototype sprites after format verification

## P4 — Production
- [ ] Tier I
- [ ] Tier II
- [ ] Tier III
- [ ] Tier IV
- [ ] Balance pass
- [ ] AI pass
- [ ] Localization pass
- [ ] Regression tests


## Extension runtime : code disponible

Le cœur est écrit et compilé : redirection transactionnelle, routeur de commandes, projection de menu et progression JP/compétences séparée. 54 contrôles du cœur passent ; les fonctions natives copiées sont testées sur 5 632 couples commande/emplacement dans une fixture isolée. Cartographie : 72 références candidates, couverture totale non approuvée. Raccordement au processus du jeu et save/load non validés. Aucun job jouable installé.

État actuel détaillé : `docs/runtime-extension.md` depuis la racine du projet (ou `runtime-extension.md` depuis docs/). Les notes de reconnaissance antérieures restent historiques ; cette mise à jour décrit l'avancement du code.
