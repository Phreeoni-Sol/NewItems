# Conversion native expérimentale — V2

État publié le 9 octobre 2026 : 77 équipements, 308 vues. 38 exceptionnels et 39 ordinaires.
Le lot complémentaire fournit 20/88 planches ; 68 restent à produire.

## Ce qui est vérifié
Encodage du conteneur WEP SPR observé : 85 504 octets, trois banques,
palettes RGB555, pixels 4 bits avec demi-octet bas en premier.
Relecture indépendante des pixels exportés ; aller-retour exact de la fixture native locale.
Une même échelle de rééchantillonnage est appliquée aux quatre vues d'un équipement.
Cette échelle conserve les proportions de la source ; elle n'établit pas sa taille dans le jeu.

## Ne pas installer directement
Ces fichiers sont des propositions d'atlas indépendants. Les deux banques suivantes
sont vides. Remplacer le WEP vanilla avec ces fichiers effacerait ses autres données.
Aucun ID moteur n'est alloué. SHP, SEQ, points de prise en main et raccordement runtime
restent à déterminer. Aucun test de bataille n'a été réalisé. Tous les runtime_ready restent false.

## Qualité encore ouverte
reports/quality-gate.json relève huit vues avec plusieurs composantes opaques :
crossbow_06 (2), bow_10 (1,2), crossbow_01 (1), sword_02 (3,4), sword_08 (1,2).
Ce signal est un diagnostic à examiner, pas une réparation automatique.
staff_02 et instrument_01 nécessitent aussi une revue de lisibilité des dents/cordes.
La retouche bow_10 attempt-01 est rejetée (halo). attempt-02 est un candidat nettoyé,
non sélectionné, non converti : le manifeste emploie encore la source précédente.
Les autres images nouvelles attendent une revue visuelle complète après réduction.
pixel_retouched reste false : le rééchantillonnage n'est pas une retouche manuelle.

## Reproduire depuis la racine du dépôt
1. python outputs/The-Forgotten-Jobs-Combat-Completion-88/tools/cut_sheets.py
2. python outputs/The-Forgotten-Jobs-Equipment-Native-Quality-V2/tools/build_conversion.py
3. python outputs/The-Forgotten-Jobs-Equipment-Native-Quality-V2/tools/verify_conversion.py
4. python outputs/The-Forgotten-Jobs-Equipment-Native-Quality-V2/tools/quality_gate.py

La fixture propriétaire native n'est pas distribuée. Sur un clone, sa vérification
indiquera NOT_PRESENT ; la relecture indépendante des fichiers générés reste disponible.
Les rapports publiés conservent les résultats obtenus localement avant publication.
Les anciens dossiers et archives demeurent des captures historiques.
