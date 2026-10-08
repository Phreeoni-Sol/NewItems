# Passation Claude — objets originaux

## Mandat

Implémentation additive uniquement. Préserver tous les jobs et objets vanilla. Lire le `CODEX_START_HERE.md` et le `AGENTS.md` du projet ; ce document décrit le design demandé, sans certifier les possibilités du moteur.

Ce dossier est l’autorité pour les **effets, prix et budgets proposés des 271 nouveaux objets**. Il remplace les propositions de gameplay du dossier `The-Forgotten-Jobs-Equipment-Expansion`. Les ZIP historiques restent des captures anciennes. Ne pas reprendre leur ancien effet « profil de progression » ou leurs anciens prix de consommables.

## Entrées et provenance

- `items.json` : 271 fiches, identifiants de design stables, référence native, nouvelle description, effet, contrepartie, acquisition, stats, prix et vérifications requises.
- `mechanics.json` : 271 intentions de mécanique. **Non exécutable** ; les conditions/cibles sont décrites en français. Les gabarits et paramètres numériques sont contrôlés mais ne sont pas un AST moteur.
- `changes.json` : avant/après de chaque effet, prix et budget.
- `BALANCE_RULES.md` : durées par défaut, coût minimal, réentrance, cumul, classification et compromis.
- `originality-audit.json` : couverture et contrôles statiques, limites de la comparaison vanilla.
- `references/` : inventaire et sept tables de référence inchangées, issues de la révision modloader d3123d2eaf4beabbe0edb21e76f9e745758fa539. Ce sont des **références**, pas des patchs à installer.
- `art/provenance.json` et `art/previews100/` : 271 aperçus choisis et chemin/SHA des grandes images : 203 du dossier frère `The-Forgotten-Jobs-Equipment-Klein-Production`, 68 du dossier frère `The-Forgotten-Jobs-Equipment-Ivalice-Style-V2`. Les copies des 68 sources choisies sont dans `art/full/`. Le manifeste V2 remplace entièrement la sélection Kontext pour les légendaires et uniques ; les anciens dossiers restent historiques.
- `catalogue.html` : toutes les fiches, filtres et comparaison avant/après. Les légendaires/uniques sont visibles même sans image.

Les aperçus 100 pixels sont destinés au catalogue. Cette taille n’est pas une exigence native. Les 203 sources Klein restent RGB sur fond blanc. Les 68 sources V2 ont une transparence alpha vérifiée ; leur conversion et liaison native ne sont pas terminées. Lire aussi `The-Forgotten-Jobs-Equipment-Ivalice-Style-V2/CLAUDE_ART_HANDOFF.md` et `COMBAT_VISUAL_COHERENCE.md` : les icônes d’inventaire ne constituent pas les sprites des armes équipées, qui restent à créer et à tester en jeu.

La reprise artistique `The-Forgotten-Jobs-Equipment-Combat-Study-38` fournit désormais **38 études** (36 armes et 2 boucliers légendaires/uniques), 152 vues proposées, leurs prompts et une piste Palette/SpriteID documentée. Lire son `CLAUDE_COMBAT_HANDOFF.md` et `selected-concepts.json`. Le catalogue expose ces études sous `combat-study/index.html`. Elles ne sont pas des séquences natives ni des assets validés sur personnage ; aucun ID moteur n’est alloué. Cette reprise remplace les trois études précédentes dans la vue courante, sans changer les 271 mécaniques proposées.

## Ordre de réalisation proposé

1. Vérifier réellement l’ajout d’entrées, les collisions, les sauvegardes et les restrictions d’équipement. Aucun ID moteur n’est attribué dans cette livraison.
2. Faire une tranche jouable avec `tfj_item_09` (Pastille du chœur), `tfj_sword_03` (Épée des haltes) et `tfj_staff_02` (Bâton des sources). Ces trois objets couvrent consommation/statut temporaire, crédit MP et excédent de soin sans produire de modification globale vanilla.
3. Pour chacun, transformer l’intention en contrat explicite : événement exact, destinataire, filtrage des actions secondaires, durée, compteur, paramètres nommés et point d’application dans la formule. Marquer les points non validés `UNKNOWN`.
4. Valider une mécanique représentative pour chaque risque : terrain, orientation, séquences, attribution d’agresseur/KO, classification de sort/contrôle, réserve inter-unités, annulation de marque nouvelle, promesse après réanimation, statut temporaire et persistance en sauvegarde.
5. Ensuite seulement, implémenter les autres fiches et tester leur équilibre/acquisition. Les 34 uniques nécessitent un garde anti-duplication de campagne validé ; aucune supposition sur sa persistance.

## Repli obligatoire pour les mécanismes expérimentaux

Chaque fiche prévoit une voie alternative : action dédiée ou médiation validée conservant la condition, la cible et le compromis. La disponibilité de cette voie est elle-même `UNKNOWN`. Si aucun chemin ne conserve le comportement distinct, **retirer l’objet de la livraison jouable en attente d’une solution**. Ne pas remplacer son effet par un bonus plat ou un consommable vanilla renommé et ne pas annoncer l’objet comme intégré. Le dossier de conception reste intact pour une version future.

Les nouveaux consommables n’accordent pas automatiquement leurs usages à la commande Objet vanilla. Le chemin d’utilisation additionnel doit être découvert et prototypé ; ne pas écraser les anciennes entrées de commande pour leur faire une place.

## Critères de validation

- Cas positif et cas négatif pour chaque déclencheur ; cible et départage corrects ; fenêtres de tour ; sortie/rentrée terrain et orientation réelle.
- Consommation correcte d’un exemplaire ; pas de dupes, MP négatifs, soins en cascade, double proc sur double frappe ou réactions, gratuité involontaire de sort, action supplémentaire ou report de réserve entre batailles.
- Le rôle distinct doit être perceptible en bataille. Même résultat avec un déclencheur différent doit avoir un usage tactique réellement différent, faute de quoi revoir le design.
- Tests simultanés avec plusieurs nouveaux équipements : maximum et expiration conformes, réactions de jobs vanilla conservées.
- Boutique, récompenses, sauvegarde/chargement, unicité, inventaire et désinstallation réversible.
- Comparaison du comportement et des données vanilla avant/après avec les nouveaux objets absents ; aucune différence autorisée.
- Revue des 271 différences avec les capacités vanilla pertinentes, en dépassant les sept tables statiques de ce dossier. L’audit textuel ne remplace pas ce travail.

## Reproduction

Depuis le dossier projet, exécuter `tools/build_revision.py` avec Python 3.12 (bibliothèque standard seulement) (le générateur utilise les aperçus existants ; aucun appel API). Il nécessite les dossiers frères de design et d’art et réécrit les fiches, audits et catalogues. Puis exécuter `tools/validate_revision.py`. Le catalogue de production du port 8852 est actualisé ; son ancienne version artistique est conservée sous `catalogue-art-before-originality.html`.

Ne pas relancer l’ancien `Equipment-Expansion/tools/build_design.py` ni l’ancien générateur du catalogue Klein pour préparer la version revue : ces outils historiques ignorent les nouvelles mécaniques. Utiliser ce générateur de révision pour reconstruire les vues. Aucun outil de ce dossier ne doit être interprété comme un patcher du jeu.
