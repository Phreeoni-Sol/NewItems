# 38 équipements — adaptation et intégration additive

Ce dossier prépare la retouche des 36 armes et 2 boucliers exceptionnels. Il contient 38 fiches individualisées, la signature à conserver, les priorités de retouche par famille et 152 aperçus copiés sans modification. `index.html` permet de les comparer hors ligne avec des découpes vanilla séparées. Aucun visuel n’est présenté comme équipé sur personnage.

## Résultats nouveaux

- Les quatre fichiers WEP1/WEP2 SHP/SEQ extraits de l’installation sont identiques octet pour octet aux ressources de FFTPatcher. Le rapprochement historique est maintenant vérifié par comparaison complète et SHA, pas seulement par des tailles compatibles. Cela ne valide pas leur consommation par le rendu Enhanced.
- Le gestionnaire local `FFTOItemDataManager.cs` expose deux pointeurs fixes, de 256 et 5 entrées, et un total de 261. `FFTOTableManagerBase.ApplyPendingFileChanges` ignore les indices au-delà des entrées originales. Cette voie de patch XML modifie des lignes existantes et ne fournit pas d’ajout de lignes. Il s’agit d’une propriété du code inspecté, pas d’une limite du moteur. Ne pas remplacer des objets vanilla pour contourner ce problème.
- Le `Item.layout` installé déclare des champs de noms, descriptions et interface ; aucun champ explicitement nommé Palette ou SpriteID. Les champs Unknown restent UNKNOWN. La priorité éventuelle de cette table sur les champs d’apparence n’est pas établie.
- Les 152 aperçus comptent entre 68 et 695 couleurs RGBA visibles (alpha > 16), chacun au-delà de 16. Ce nombre mesure les aperçus, pas la palette moteur. Les sources restent des études ; il faut une retouche sur une grille régulière et un encodage indexé validé. Le diagnostic ne quantifie pas automatiquement les couleurs et ne modifie pas l’alpha.

## Autorités des données

`Equipment-Originality-Revision` reste l’autorité des 271 designs et mécaniques. `Equipment-Ivalice-Style-V2` reste celle des 68 icônes exceptionnelles. `Equipment-Combat-Study-38/selected-concepts.json` reste la sélection graphique des 38 études. Le présent dossier ajoute des mesures et instructions, sans remplacer ces autorités. Les 107 autres armes/boucliers n’ont pas reçu de planches de combat dans ce lot.

## Travaux à réaliser

Chaque fiche dans `adaptation-contracts-38.json` conserve la signature, la palette artistique, les SHA et les mesures des quatre vues. Commencer par trois témoins : une arme courte, une hampe et un bouclier. Relever d’abord les poses, points de prise et palettes d’un exemple vanilla en jeu. Ne pas affecter SpriteID à un index de rectangle ou de séquence sur la seule base de sa valeur numérique.

Pour les silhouettes, préserver le motif principal de chaque objet à la petite taille réellement requise. Pour les fléaux et tissus, relever le mouvement avant de décider comment la chaîne ou l’étoffe se déforme. Les brumes et lueurs éventuelles doivent suivre une voie d’effets séparée vérifiée ; ne pas les incorporer à la transparence du sprite d’arme. Le nombre de poses nécessaires est UNKNOWN.

Pour l’ajout indépendant : identifier le stockage extensible, ses consommateurs, la correspondance catégories/tables supplémentaires et les implications de sauvegarde. La simple écriture d’un ItemData.xml avec de nouveaux IDs ne démontre pas un ajout fonctionnel. Aucun nouveau numéro n’est alloué ici.

Conserver une capture native de référence, puis comparer attente, marche, attaque, garde, directions et double équipement sur la même unité. Valider séparément les modes ciblés. La route d’apparence des armures/accessoires reste UNKNOWN.

## Vérification et reproduction

Deux essais de retouche OpenAI intégrée sur Dernier aveu sont conservés sous `retouch-pilot`, avec prompts exacts et provenance. Les ombrages ont été simplifiés mais le halo diffus persiste malgré une correction ciblée. Les deux essais sont rejetés pour la production à alpha propre ; aucun ne remplace la sélection des 38. L’essai v3 a aussi saturé davantage le sceau rouge. Ne pas déployer cette méthode sur tout le lot sans résoudre ce défaut. Aucun appel Pollinations.

`validation.json` certifie les comptes et la provenance des copies. Les 152 fichiers RGBA sont en 36 × 36, choix d’aperçu. Le générateur `tools/build_adaptation_handoff.py` se trouve aussi dans le dossier des 38 études ; il relit les sources et vérifie leurs SHA avant copie. Il ne génère ni n’encode d’assets natifs et n’appelle aucune API.

Les copies natives et le lecteur de formes sont dans le complément `The-Forgotten-Jobs-Native-Weapon-Geometry`. Les sources historiques ne sont pas reproduites ici. `integration-evidence.json` fournit les chemins et SHA des fichiers de code inspectés.

Tests en jeu : NOT_RUN. Consommateur de rendu : UNKNOWN. Allocation de nouveaux IDs : aucune. Fichiers installés modifiés : aucun. Vérification du navigateur : refusée par la politique d’URL ; les contrôles portent sur les fichiers locaux.
