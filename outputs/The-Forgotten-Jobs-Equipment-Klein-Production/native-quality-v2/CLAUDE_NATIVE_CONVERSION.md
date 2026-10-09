# Livraison graphique et conversion — 9 octobre 2026

145 équipements visibles : 107 ordinaires et 38 exceptionnels, 580 vues.
Les 88 planches complémentaires sont produites et découpées. Les 19 planches
natives actuelles ont été inspectées ; les preuves et empreintes sont dans
reports/visual-review.json. Sept révisions génératives de sources sont sélectionnées.
Aucune retouche manuelle peinte au pixel n'est revendiquée : pixel_retouched=false.

## Résultats vérifiés
Relecture indépendante des 145 conteneurs et 580 vues ; aucune silhouette native
fragmentée détectée. Les 26 contrôles ciblés (cordes d'arcs, quatre dents et gemme
bleue du bâton) passent. La palette déterministe préserve les accents rares.
Une même échelle est appliquée aux quatre vues d'un équipement, avec sélection
de phase documentée et pixels source préservés lors de la découpe.
RGB555, 4 bits, demi-octet bas en premier ; conteneur observé de 85 504 octets.
Les rectangles employés proviennent de l'observation, sans prétendre limiter le moteur.

## Travail d'implémentation pour Claude
1. Lire equipment-integration-contract.json : 271 designs, 145 visuels de combat,
   références de mécanique et inventaire ; tous les raccordements natifs restent nuls.
2. Démontrer l'allocation additive d'IDs et les consommateurs ItemPalette/SpriteID.
   Préserver les entrées, jobs, objets et palettes vanilla ; ne pas deviner de plafond.
3. Construire les SHP/SEQ adaptés, déterminer les prises en main, orientations,
   animations et liens aux personnages à partir de preuves natives.
4. Intégrer les mécaniques originales, statistiques, prix, obtention et restrictions
   conformément aux designs et règles d'équilibrage. Aucun effet n'est exécuté ici.
5. Tester en bataille chaque famille, puis chaque équipement : attaque, mouvement,
   animations, transparence, contraste, taille et prise en main. Tester menus,
   sauvegardes et absence de régression des équipements/jobs vanilla.
6. Livrer un installateur réversible et un rapport de tests avant déclaration jouable.

## Installation et limites de validation
Ces conteneurs sont des atlas d'auteur indépendants : les deux banques suivantes
sont vides. Ne jamais remplacer le WEP vanilla par ces fichiers.
SHP/SEQ, IDs, ancres et raccordement runtime restent UNKNOWN ; tests en jeu NOT_RUN.
La continuité des silhouettes et la revue d'auteur ne prouvent pas leur placement
ou leur rendu animé en bataille. runtime_ready reste false partout.

## Reproduction
Depuis la racine du projet : exécuter les outils cut_sheets.py du dossier
Combat-Completion-88, puis build_conversion.py, verify_conversion.py,
test_palette_quantizer.py, verify_signatures.py, quality_gate.py, build_catalogue.py
et build_integration_contract.py du dossier Native-Quality-V2, dans cet ordre.
Toute reconstruction qui modifie les pixels exige une nouvelle inspection des planches.
finalize_authoring_review.py consigne une revue humaine effectivement réalisée ;
ne pas l'utiliser comme substitut de cette inspection.
La fixture propriétaire n'est pas distribuée : son contrôle sur un clone indiquera
NOT_PRESENT, sans empêcher la relecture indépendante des fichiers produits.
Les anciens dossiers et ZIP sont des captures historiques, conservées intactes.
