# Équipements ordinaires — premier lot de combat

Extension artistique indépendante de The Forgotten Jobs. Préserver tous les jobs et objets vanilla. Aucun fichier du jeu, aucune donnée de gameplay ni allocation native ne sont modifiés.

## Portée

107 armes et boucliers ordinaires ont des icônes d'inventaire sélectionnées, vérifiées par SHA-256. Ce lot propose 19 études de combat, une par famille : 18 armes et 1 bouclier, quatre vues artistiques par objet. L'Épée des haltes et le Bâton des sources couvrent deux priorités du prototype.

Les signatures sont relevées sur les images réellement sélectionnées, plutôt que reprises aveuglément des anciens prompts. Exemple : le Bâton des sources a quatre pointes et une gemme bleue près de sa base. Les nouveaux dessins utilisent le générateur OpenAI intégré ; aucun appel Pollinations.

## Fichiers

- generation-plan.json : prompts, références, signatures vérifiées visuellement.
- inventory/ : copies fidèles des 19 icônes existantes, SHA inchangés.
- sources/ : feuilles RGBA et provenance de génération.
- poses/ : découpes fidèles et miniatures de présentation.
- review/ : mesures et décisions de contrôle visuel.
- selected-alternatives.json : concepts sélectionnés, sans identifiants natifs.
- ordinary-107-plan.json : suivi complet, dont objets encore sans dessin de combat.
- index.html : comparaison icône / propositions de combat.

## Limites établies

Quatre vues et miniatures 36 × 36 sont des choix d'étude artistique. Ce ne sont pas des dimensions ni un nombre d'images imposés par le moteur. Les couleurs et l'alpha générés sont conservés ; aucune quantification native ni normalisation de transparence n'est effectuée.

Les identifiants d'objet, de sprite et de palette sont null. Les ancrages de main sont UNKNOWN. Les variantes arrière du bouclier et des objets asymétriques sont des propositions. Aucune pose sur personnage ou séquence de combat n'est validée dans le jeu.

La revue valide uniquement les silhouettes et identités des feuilles sources. À 36 px, certaines cordes, chaînes et manches perdent leur continuité au rééchantillonnage. Des aperçus fidèles 64 px sont aussi fournis pour comparaison ; ils ne constituent pas une solution native. Reprendre ces traits au pixel seulement après identification des rectangles de destination. Voir review/pixel-retouch-backlog.json. Aucun lot n'est marqué prêt à charger.

Consulter les dossiers voisins The-Forgotten-Jobs-Native-Weapon-Geometry et The-Forgotten-Jobs-Equipment-Adaptation-Handoff pour les observations binaires documentées. La voie de patch XML locale observée modifie des entrées existantes et n'ajoute pas de lignes ; ce constat ne prouve pas une limite globale du moteur.

Avant intégration : vérifier la voie d'ajout indépendante, le consommateur des champs visuels, les palettes, les rectangles et les séquences, puis établir les ancrages et tester sur personnage. Ne remplacer aucun objet vanilla pour contourner une inconnue.

## Reproduction

Python avec Pillow : tools/prepare.py vérifie les sources et prépare les contacts ; tools/review_witnesses.py découpe et mesure ; tools/make_review_boards.py produit les contacts ; tools/finalize.py exige la revue visuelle explicite ; tools/package.py scelle une nouvelle archive et vérifie sa relecture.

Ne pas relancer prepare.py après validation sans préserver les décisions : il réinitialise le suivi artistique. Les générations elles-mêmes ne sont pas déterministes ; les prompts et sources sélectionnées sont archivés.

Contrôles locaux de fichiers et d'images uniquement. Le contrôle du catalogue dans le navigateur a été refusé par la politique d'URL. Les tests en jeu restent à faire.
