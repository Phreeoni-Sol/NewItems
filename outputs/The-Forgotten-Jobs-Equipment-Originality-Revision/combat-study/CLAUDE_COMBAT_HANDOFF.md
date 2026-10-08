# Armes et boucliers — lot de 38 études graphiques

Lire le CODEX_START_HERE.md et AGENTS.md du projet. Travail additif uniquement : aucun fichier du jeu ni objet vanilla modifié. Le dossier Ivalice-Style-V2 reste l’autorité des 68 icônes ; Originality-Revision reste l’autorité des 271 designs de gameplay.

## Livré

- Décodage de la copie locale de `0002.pac / fftpack/unit/battle_wep_spr.bin`, 85 504 octets. SHA source et aller-retour indices/palettes vérifiés. Trois banques historiques : arme (offset 0, 33 280 octets), effet (33 280, 33 280), piège (66 560, 18 944). Les PNG utilisent une interprétation RGB555 historique et ne prouvent pas les règles d’alpha du runtime.
- Le lot cible les 36 armes et 2 boucliers légendaires/uniques, soit 38 études dans 19 familles. Les trois témoins précédents sont conservés. `selected-concepts.json` est la sélection réellement revue, avec SHA et provenance ; `production-plan.json` contient les 35 nouvelles demandes initiales. Seules les images retenues comptent comme études livrées.
- Quatre vues proposées par objet, à découper après vérification des espaces réels entre vues. Alpha et gouttières sont contrôlées ; la recherche des séparations ignore uniquement les résidus alpha <= 16 pour détecter les contours, sans modifier l’alpha original des images découpées. Les vues opposées sont des propositions de profils, pas quatre orientations natives démontrées. Le revers des boucliers est une proposition de dessin pour les poignées et sangles, pas une observation du modèle moteur.
- Aperçus 36 × 36 pour comparer la lisibilité, choisis pour cette étude. Ce ne sont pas des limites du moteur ni des sprites convertis. Les gros pixels générés ne forment pas nécessairement une grille régulière ou une palette native ; compter les couleurs dans selected-concepts.json ne certifie pas une conversion.
- Contrat de production pour les 271 objets : les 38 armes/boucliers exceptionnels restent CONCEPT_ONLY, les autres graphismes portés restent NOT_CREATED. Les 203 icônes Klein et les 30 autres icônes exceptionnelles V2 ne sont pas retouchées par ce lot. Pour les objets ordinaires, signature/palette à relever sur les sources Klein ; ne pas les inventer depuis leur nom.

## Nouvelle piste de liaison vérifiée dans le code

Le code local du modloader expose `ITEM_COMMON_DATA.Palette` et `ITEM_COMMON_DATA.SpriteID` (deux champs byte dans `Tables/Structures/ITEM_COMMON_DATA.cs`). Cela fournit une piste concrète distincte des statistiques de ITEM_WEAPON_DATA. Il ne démontre pas quel rendu consomme ces champs, comment les indices correspondent aux formes ni comment ajouter une banque. Ne pas transformer leur type byte en une limite absolue du moteur.

`native-item-visual-fields.json` relève les valeurs Palette/SpriteID des 261 lignes du XML de référence, avec noms et SHA source. Ce sont des entrées vanilla de référence, pas de nouveaux IDs. `Tables/Models/Item.cs` expose également ces propriétés comme champs nullable suivis par le système de différences. Le commentaire XML signale une possible priorité de la table nex Item : ces seules valeurs ne prouvent donc pas le résultat Enhanced. Les commentaires historiques sur les bornes divergent entre fichiers ; aucune borne absolue ni allocation nouvelle n’est déduite ici.

Le décodeur suit les dispositions observées dans FFTPatcher : `AbstractSprite.cs` (16 palettes de 32 octets avant les pixels), `ShortSprite.cs` (nibble bas puis haut), `WEPSprite.cs` (hauteur 256), `AllSprites.cs` (offsets des trois banques). Ce code historique cible PSX/PSP. Le rendu Enhanced et ses éventuelles autres ressources restent UNKNOWN.

## Suite pour l’intégration par Claude

1. Tracer les consommateurs réels de Palette/SpriteID et comparer quelques objets vanilla avec les banques/formes. Faire séparément Classic et Enhanced ; conserver preuve et SHA.
2. Identifier formes WEP, séquences, pivots, palettes et règles de superposition. Aucune allocation d’ID ici. Vérifier qu’une voie additive préserve toutes les apparences vanilla.
3. Définir les poses nécessaires et les points de main sur une unité témoin. Auditer les sprites de nouveaux jobs ayant déjà une arme dans leurs pixels.
4. Redessiner/retoucher les propositions sur la grille native réellement observée, puis encoder. Le motif principal doit survivre ; le souffle vert et violet exigent un effet séparé démontré, pas une brume collée au sprite.
5. Tester attente, marche, attaque, garde, directions, mains et double équipement. Capturer l’icône et l’arme réellement portée. Ces tests n’ont pas été exécutés.

Les armures/accessoires n’ont pas de changement automatique de modèle prouvé. Leurs contrats sont explicitement marqués CHARACTER_APPEARANCE_ROUTE_UNKNOWN.

## Reproduction

Depuis la racine du projet, lancer `tools/inspect_weapon_bank.py`, `tools/review_batch.py` puis `tools/build_study.py` de ce dossier avec Python et Pillow. Le premier exige la copie extraite sous work/effects-reference ; le dernier exige les dossiers frères V2, Originality et Klein et le manifeste `choices-reviewed.json` issu de la revue visuelle. Ces scripts ne font aucun appel API. `prepare_batch.py` prépare les prompts et les références sans générer les images. Les prompts exacts des générations OpenAI intégrées sont dans concepts/*.json. Les anciens essais du canon avec brume et la première corde trop fine de l’arc restent historiques ; seuls canon v3 et arc v2 sont retenus parmi ces témoins. Le générateur de catalogue Originality peut supprimer le lien de cette étude : relancer build_study.py après ce générateur pour le rétablir.
