# Icônes FFT / Ivalice V2 — transmission artistique

Les 34 légendaires et 34 uniques ont été redessinés à partir des références natives Enhanced. Lire `DIRECTION_ARTISTIQUE.md` et `selected-manifest.json` : ce dernier choisit les 68 sources effectivement inspectées, avec leur hash, leur palette, leur motif, leur alpha et leur provenance. Les styles Kontext et Prestige précédents sont conservés comme historique ; l'utilisateur les a écartés.

Le plan du premier passage est `production-plan.json`. Les prompts et références exacts sont dans `records/`. Neuf retouches ciblées sont conservées dans `corrections/` avec leurs propres JSON : clef, lanterne, bouclier, casque, coiffe, robe, grenade de grésil, shuriken unique et larme sacrée. Leurs signatures remplacent les intentions initiales lorsque le manifeste les sélectionne. `references/` contient les petites images natives utilisées pour le style.

Les sources RGBA sont des PNG d'auteur. Les dimensions réellement produites et les SHA256 sont contrôlés. Les aperçus 100 et 48 pixels sont des tests de lisibilité d'inventaire ; ils ne définissent pas un nouveau format moteur supposé. Le générateur utilisé est l'outil OpenAI intégré, sans appels Pollinations pour ce lot.

Le dossier frère `The-Forgotten-Jobs-Equipment-Originality-Revision` conserve les 271 propositions de gameplay et leur catalogue. Leurs effets, statistiques, prix et acquisitions sont inchangés par cette révision artistique. Les 203 grandes sources ordinaires Klein restent dans leur livraison précédente ; leurs aperçus sont présents dans le catalogue des 271 objets. Tous les IDs moteur sont non attribués.

Lire `COMBAT_VISUAL_COHERENCE.md` et `combat-coherence-manifest.json`. Les icônes ne deviennent pas automatiquement les graphismes d'armes portées. Découvrir les liaisons, formats, palettes, poses et pivots réels, puis produire les petits sprites correspondants. Certains nouveaux sprites de jobs ont déjà une arme intégrée à leur pose : auditer ce point pour éviter un double affichage ou une arme fixe. Aucune modification automatique de l'apparence par armure ou accessoire n'est confirmée.

Les lumières et particules des icônes sont des choix artistiques ; elles n'ajoutent ni propriété élémentaire ni animation de combat confirmée. Préserver tous les objets et jobs vanilla, ajouter indépendamment et ne pas remplacer leurs ressources graphiques globales.

Graphismes portés : NOT_CREATED. Liaison moteur : UNKNOWN. Tests en jeu : NOT_RUN. Aucun patch à installer dans ce lot.
