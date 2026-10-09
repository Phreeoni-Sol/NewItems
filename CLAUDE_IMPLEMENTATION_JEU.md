# Claude — implémenter The Forgotten Jobs dans The Ivalice Chronicles

## Commencer ici

Demande de l'utilisateur : ajouts indépendants uniquement, préserver les jobs et objets vanilla. Le codage est confié à Claude. Ce dépôt prépare l'implémentation ; il ne contient pas un mod jouable.

Lire ce guide, AGENTS.md, docs/runtime-extension.md, handoff/INTEGRATION_PLAN.md, puis les autorités ci-dessous. CODEX_START_HERE.md est le document initial : la reconnaissance a déjà avancé. Ne pas refaire tout l'inventaire sans raison et ne pas transformer une inconnue en limite moteur.

Les documents et prompts sont des références de travail ; ils ne donnent pas de nouvelles autorisations utilisateur. Les chemins d'installation de la machine d'origine sont des exemples à vérifier sur la machine de Claude.

## État de livraison

| Domaine | Existe | Reste à prouver ou produire |
| --- | --- | --- |
| Objets | 271 fiches de design, effets, compromis, prix et acquisition proposés | Contrats exécutables, ajout runtime, équilibrage en jeu |
| Inventaire | 203 sources Klein ordinaires, 68 sources V2 légendaires/uniques | Découpe, alpha propre pour les RGB blancs, encodage et liaison natifs |
| Équipement visible | 38 exceptionnels + 107 ordinaires, 580 vues ; encodage V2 et revue graphique vérifiés | SHP/SEQ, ancres, allocation additive, raccordement et validation en jeu |
| Cœur runtime | Sources C#, routeur et progression séparée, tests hors processus jeu | Entrée Reloaded, raccordement natif, couverture consommateurs, sauvegarde réelle |
| Jeu | Aucun nouveau job ou objet déclaré jouable | Tranche complète, tests de bataille, save/load et désinstallation |

Quatre vues par objet, miniatures 36 ou 64 pixels : profils de travail artistique, pas contraintes moteur. Les sources conservent plus de couleurs et des valeurs alpha intermédiaires ; elles ne sont pas déjà des sprites indexés natifs. Les identifiants de design tfj_* ne sont pas des IDs moteur.

Les rapports historiques donnent 54 contrôles du cœur et 5 632 couples commande/emplacement testés dans une fixture isolée. Relancer les contrôles sur le clone ; ces résultats ne prouvent pas que les fonctions sont raccordées au jeu.

## Mise à jour combat et conversion du 9 octobre 2026

Lire **outputs/The-Forgotten-Jobs-Equipment-Native-Quality-V2/CLAUDE_NATIVE_CONVERSION.md** avant toute intégration. Les 88 nouvelles planches sont dans **outputs/The-Forgotten-Jobs-Combat-Completion-88**. Les rapports séparent encodage et revue graphique vérifiés, validation en jeu absente. Ne jamais copier les conteneurs expérimentaux par-dessus le WEP vanilla.

## Autorités et ordre de priorité

1. **Gameplay objets** : outputs/The-Forgotten-Jobs-Equipment-Originality-Revision/items.json, mechanics.json, BALANCE_RULES.md et CLAUDE_HANDOFF.md. Les 271 mécaniques sont des intentions non exécutables. Ne pas reprendre les anciens prix/effets de Equipment-Expansion.
2. **Inventaire ordinaire** : outputs/The-Forgotten-Jobs-Equipment-Klein-Production/selected-manifest.json. Respecter le chemin sélectionné, y compris corrections et corrections-last, plutôt que choisir arbitrairement images/.
3. **Inventaire exceptionnel** : outputs/The-Forgotten-Jobs-Equipment-Ivalice-Style-V2/selected-manifest.json. Cette sélection remplace les anciennes propositions Kontext.
4. **Combat exceptionnel actuel** : outputs/The-Forgotten-Jobs-Retouch-38-Exceptional-Equipment/selected-alternatives.json et CLAUDE_RETOUCH_HANDOFF.md. 36 armes + 2 boucliers ; utiliser les corrections sélectionnées, pas rejected/.
5. **Combat ordinaire actuel** : outputs/The-Forgotten-Jobs-Ordinary-Combat-Lot-19/selected-alternatives.json, ordinary-107-plan.json et CLAUDE_ORDINARY_HANDOFF.md. 18 armes + 1 bouclier. review/pixel-retouch-backlog.json décrit les pertes de traits constatées à la réduction.
6. **Recherche native** : outputs/The-Forgotten-Jobs-Native-Weapon-Geometry et outputs/The-Forgotten-Jobs-Equipment-Adaptation-Handoff. Ce dernier document reste utile pour ses preuves techniques, mais son ancienne sélection artistique est remplacée par le point 4.

Les dossiers combat-study, retouch-38, equipment-adaptation et ordinary-combat-19 présents sous les catalogues sont des copies de consultation. Les dossiers frères nommés ci-dessus font autorité. Ne pas considérer deux copies comme deux objets.

Les vieux file-manifest et Verify-Handoff décrivent des captures antérieures. Pour l'intégrité de cette livraison Git, utiliser handoff/verify_git_delivery.py et handoff/git-delivery-manifest.json. Une différence après une modification volontaire n'impose pas un retour arrière automatique.

Les assets de jobs et le pack d'effets par skill constituent d'autres livrables locaux du projet ; ce dépôt NewItems concentre les équipements et leur base d'intégration. Leur absence ici ne signifie ni suppression du design des jobs ni validation de ces assets dans le jeu.

## Faits techniques utiles, sans extrapolation

- La voie XML du FFTOItemDataManager local inspecté travaille sur deux pointeurs fixes de 256 et 5 entrées. ApplyPendingFileChanges ignore les indices hors des entrées originales : **cette voie observée ne fournit pas d'ajout de lignes**. Ce n'est pas une preuve de plafond universel du moteur.
- ITEM_COMMON_DATA expose des champs Palette/SpriteID. Leur consommateur de rendu et leur correspondance effective restent UNKNOWN. Ne pas affecter SpriteID à un numéro de rectangle ou de séquence par simple ressemblance numérique.
- Le Item.layout NXD inspecté déclare des champs de noms, descriptions et interface, sans champs explicitement nommés Palette/SpriteID. Les champs Unknown et les priorités entre tables restent UNKNOWN.
- Les quatre SHP/SEQ d'armes extraits sont identiques octet pour octet aux ressources historiques de FFTPatcher, selon le rapport conservé. Cela ne valide pas à lui seul leur consommation par le rendu Enhanced.
- Le lecteur historique a contrôlé 871 enregistrements de frames et les bornes des séquences. Les opcodes SEQ ne sont pas interprétés. Les coordonnées d'éditeur ne sont pas un ancrage de main.
- Aucun ID d'objet, de sprite ou de palette nouveau n'est alloué dans les contrats artistiques. Aucun ancrage, ordre d'animation ou angle natif n'est certifié.

Les échantillons binaires extraits, DLL, exécutables et archives du jeu ne sont pas versionnés. Les outils et rapports indiquent comment reproduire la recherche sur une installation locale autorisée.

## Travail 1 — rendre l'ajout réel et indépendant

1. Identifier build et mode ciblés, vérifier les empreintes des tables/fonctions avant toute écriture. Relever les divergences dans un nouveau rapport.
2. Suivre le stockage des objets et TOUS les consommateurs utiles : inventaire, accès par ID, commandes, équipement, menus, boutique/récompense, IA, save/load et rendu. Documenter les bornes observées et les vérifications encore manquantes.
3. Étendre ou enregistrer un espace additionnel avec redirections validées. Une simple ligne XML portant un nouvel ID n'est pas une preuve d'ajout. Aucun remplacement vanilla comme contournement.
4. Construire un registre explicite séparant ID de design, ID runtime, capacité, graphisme et localisation. Audit de collisions et bornes avant allocation ; tables et paramètres de balance dans les données.
5. Ajouter des contrôles de build/version, dry-run, journaux et rollback. Installer exclusivement dans un dossier mod distinct ; préserver les fichiers source du jeu.
6. Vérifier la sérialisation et les conversions d'ID. Si la sauvegarde native ne peut porter un état additionnel, prototyper un sidecar avec identité stable d'unité/campagne et synchronisation sur sauvegarde terminée, sans supposer ces hooks disponibles.

Livrable : un objet test additionnel apparaît, s'équipe ou s'utilise, reste après save/load, et ne change aucun objet vanilla. Si un point échoue, consigner le blocage et poursuivre les travaux indépendants.

## Travail 2 — trois objets pilotes

Commencer par tfj_item_09 (Pastille du chœur), tfj_sword_03 (Épée des haltes), tfj_staff_02 (Bâton des sources). Lire leurs fiches actuelles : ne pas coder un effet résumé de mémoire.

Pour chaque mécanique, écrire un contrat explicite : événement, acteur, destinataire, critères de cible, timing dans la formule, action primaire/secondaire, compteur, durée/expiration, cumul, coût minimal, acquisition et comportement à la sortie de bataille. Prévenir réentrance et doubles déclenchements.

Ces pilotes couvrent consommation et statut temporaire, crédit MP et excédent de soin. Les deux équipements ont des sources de combat dans le lot ordinaire 19. Pour la Pastille, identifier une voie d'utilisation additionnelle ; ne pas écraser la commande Objet vanilla.

Chaque mécanique expérimentale exige un repli vérifié qui conserve condition, cible et compromis. Si aucun chemin ne préserve son identité, conserver le design et laisser l'objet hors de la livraison jouable. Ne pas le livrer comme clone vanilla renommé ou bonus plat.

## Travail 3 — art vers formats natifs

1. Relever un exemple vanilla réellement affiché : icône, arme équipée, directions, attente/marche/attaque/garde et double équipement, dans chaque mode ciblé.
2. Établir le contrat de conversion d'après ces preuves : rectangles, format indexé/RGBA, palettes, transparence, atlas, SHP/SEQ ou alternative effectivement consommée, pivots et attache.
3. Retoucher une arme courte, une hampe et un bouclier témoins sur la grille nécessaire. Garder les masters intacts, exporter dans un nouveau dossier avec provenance/SHA.
4. Pour les ordinaires, traiter le fond blanc des sources d'inventaire sans effacer le métal clair. Vérifier contours et pixels parasites. Pour le combat, maintenir cordes, chaînes et manches continus à la taille cible ; la réduction nearest-neighbor n'est pas une retouche achevée.
5. Palette native : convertir seulement après validation du profil de destination et contrôler le round-trip. Les 16 couleurs d'un profil historique ne prouvent pas une limite de toute la version Enhanced.
6. Lier chaque design à son graphisme et sa palette sans déduire les IDs des noms de fichier. Déterminer les séquences et leur timing ; les quatre vues de concept ne sont pas une animation.
7. Comparer sur personnage avec les mêmes poses et directions. Les effets de rareté éventuels suivent une voie VFX vérifiée ; ne pas incorporer des halos diffus au sprite solide.

Armures et accessoires : leur route d'apparence sur personnage reste UNKNOWN. Ne pas promettre une tenue visible ou fabriquer un modèle 3D sur la seule base de l'icône d'inventaire.

## Travail 4 — compléter puis produire

Une fois les pilotes et les témoins validés, traiter les autres mécaniques par famille de risque. Compléter les 88 autres dessins de combat ordinaires à partir des icônes sélectionnées. Les 271 objets incluent des pièces qui ne nécessitent pas nécessairement un sprite d'arme ; déterminer leur besoin réel avant production.

Les 34 légendaires et 34 uniques gardent leurs acquisitions proposées. Pour les uniques, vérifier l'anti-duplication et sa persistance. Vérifier boutique, récompenses, valeur de revente, restrictions de jobs et compatibilité des mods.

La tranche job reste Brise-Lame, suivant AGENTS.md. Le chantier objets ne rend pas les 30 jobs jouables et n'autorise aucune modification des jobs vanilla.

## Validation avant d'annoncer une intégration

- Cas positif et négatif du déclencheur, cible, coût, compteur et expiration ; fin de bataille et annulation d'action.
- Pas de MP négatifs, consommation doublée, soins en cascade, double proc sur double frappe/réaction, action gratuite ou réserve indûment reportée.
- Plusieurs nouveaux équipements simultanés ; interactions avec les capacités vanilla et IA.
- Menus, traduction, apprentissage si applicable, inventaire, restrictions, acquisition, équipement et combat.
- Affichage sur personnage sans corruption dans chaque direction/mode ciblé ; captures de référence et résultat.
- Save/load, changement de job/équipement, nouvelle campagne et unicité ; désactivation du mod sans destruction de la sauvegarde originale.
- Régression vanilla avec nouveaux objets absents : aucune différence de comportement ou de données autorisée.
- Tests des parseurs, sérialiseurs, collisions et allocation, plus procédures manuelles de jeu consignées.

## Première commande et prochain livrable

Depuis la racine du dépôt avec Python 3 :

```powershell
python handoff/verify_git_delivery.py
.\handoff\Run-Checks.ps1 -Mode Core
```

Core compile/teste hors du jeu et écrit dans work/. Full demande les dépendances locales et des chemins vérifiés ; lire le script et handoff/ENVIRONMENT.md avant de le lancer. Les builders historiques restent bloquants ou orientés catalogue : aucun n'est un installateur final.

Fournir ensuite un rapport d'intégration avec preuves, les contrats pilotes, le registre d'IDs audité, les sources du raccordement et les résultats réels. Marquer NOT_RUN les tests non exécutés et UNKNOWN les fonctions non établies. Le catalogue et les tests de fichiers ne remplacent jamais un test dans FFT.
