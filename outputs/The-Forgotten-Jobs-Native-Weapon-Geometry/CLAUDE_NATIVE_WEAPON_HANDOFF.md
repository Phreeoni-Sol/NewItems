# Formes et séquences d’armes — relevé local

Ce complément accompagne les 38 études graphiques (36 armes et 2 boucliers), soit 152 vues proposées. Il ne convertit pas ces vues en ressources chargeables. Préserver les jobs, objets et fichiers vanilla. Aucun ID attribué.

## Fichiers réellement extraits

Archive installée `data/enhanced/0002.pac`, chemins `fftpack/unit/` :

| Ressource | Octets | Diagnostic suivant le lecteur historique |
|---|---:|---|
| battle_wep1_shp.bin | 5 218 | 422 entrées, 67 rectangles distincts |
| battle_wep2_shp.bin | 5 436 | 449 entrées, 70 rectangles distincts |
| battle_wep1_seq.bin | 2 607 | 94 offsets, intervalles dans le fichier |
| battle_wep2_seq.bin | 2 657 | 94 offsets, intervalles dans le fichier |
| battle_wep_spr.bin | 85 504 | copie identique à la référence déjà décodée |

Les tailles décompressées sont vérifiées via FF16Tools.Pack ; les SHA et en-têtes figurent dans `reports/sample-summary.json`. Les scripts lisent l’installation et écrivent exclusivement dans ce dossier. Ils emploient les DLL déjà présentes du jeu et du loader.

## Ce que montre le diagnostic

Le code local de FFTPatcher (`ShishiSpriteEditor/DataTypes/Shape.cs`, `Frame.cs`, `Tile.cs`, `Sequence.cs`) fournit une hypothèse de lecture historique. Appliquée aux copies extraites, la table de formes commence à 0x48, les données de formes à 0x846. Chaque entrée lue contient six octets : un mot brut, deux coordonnées signées, un mot de flags. Les offsets et les 871 entrées tiennent dans les fichiers. La réécriture des champs décodés reproduit exactement les six octets de chaque entrée ; cela vérifie la lecture des champs, pas leur sens dans le moteur.

Selon cette lecture, le mot de flags contient les coordonnées d’atlas par pas de 8, un code de taille et deux inversions. Les 137 rectangles relevés par banque (avec recouvrements entre banques) tiennent tous dans 256 × 256. Plusieurs rectangles partagent des pixels : leur compte n’est pas un nombre d’objets ou d’images indépendantes. Les planches `review/wep1-atlas-crops.png` et `wep2-atlas-crops.png` montrent uniquement les découpes avec la première palette historique. Elles ont été inspectées visuellement : armes, boucliers, livres et autres silhouettes sont reconnaissables. Les couleurs par objet restent à résoudre.

Les tailles observées sont des propriétés de ces ressources vanilla ; elles ne sont pas des limites imposées aux futurs ajouts. Les aperçus 36 × 36 des études restent un choix de présentation.

Le lecteur historique interprète le premier mot comme rotation et calcule des positions d’éditeur par ajout de 53 et 118. Ces valeurs ne prouvent ni le pivot de la main ni les angles du moteur. Son rendu de Frame.cs ne suffit pas à démontrer l’application de cette rotation. Le rapport conserve donc `rotation_raw`, les coordonnées signées et les positions historiques séparément. Aucune fausse animation sur personnage n’est produite.

Pour les séquences, les offsets commencent à 4 et la base historique est 0x406. Les 94 offsets de chaque fichier produisent des intervalles bornés valides. Les octets sont conservés en hexadécimal dans `geometry.json`. Les opcodes ne sont pas interprétés : ni les branchements, ni les délais, ni le rapport entre index de séquence et objet ne sont validés. La présence de ces ressources dans l’archive Enhanced ne démontre pas quels chemins le rendu Enhanced exécute.

## Suite concrète

1. Tracer les consommateurs de Palette/SpriteID, puis relier quelques objets vanilla à leurs rectangles et séquences. Les valeurs de référence de 261 objets figurent dans le lot des 38 études.
2. Comparer l’arme portée et l’icône sur une unité témoin, dans chaque mode ciblé ; documenter main, pivot, direction, inversions et superposition.
3. Déterminer une extension additive avec contrôle des collisions. Aucun remplacement vanilla ni allocation depuis une borne supposée.
4. Retoucher les 38 études sur les grilles et palettes effectivement requises ; produire les poses nécessaires après cette vérification. Les quatre propositions par objet ne constituent pas un contrat d’animation natif.
5. Tester attente, marche, attaque, garde et double équipement en jeu. `runtime_ready: false`, tests en jeu non exécutés.

## Reproduction

Lancer `tools/extract-weapons.ps1` avec GameRoot, LoaderRoot, SampleRoot et ReportRoot explicites. L’option DryRun affiche la sélection sans extraire. Puis lancer `tools/inspect_geometry.py` avec Python et Pillow. Le diagnostic n’effectue aucune modification binaire. Les sources historiques sont identifiées et hachées dans `reports/validation.json` ; elles ne sont pas copiées dans ce complément.

La vérification automatique du navigateur a été refusée par sa politique d’URL. Les contrôles de ce complément portent sur les fichiers locaux et les planches inspectées, sans contournement du refus.
