# 38 équipements exceptionnels — nouvelles études de retouche

Ce lot cible les 36 armes et 2 boucliers exceptionnels dans 19 familles. Les trois témoins précédents sont repris à l’identique ; les 35 autres dessins repartent de leur signature et de l’atlas natif comme référence de style. Les anciens dessins, icônes, mécaniques et prix restent inchangés. Aucun job, objet ni fichier vanilla modifié.

## Intention artistique

Réduire l’apparence d’illustration et les halos hérités des images initiales : silhouettes plus simples, aplats lisibles, palettes artistiques propres à chaque objet. La rareté repose sur le motif et la forme — feuille de chêne, cloche fendue, garde particulière, engrenage, lanterne, étoffe ou emblème — sans imposer un ornement doré uniforme. Toute brume, particule ou effet animé devra passer par une voie d’effets séparée démontrée.

Chaque planche contient quatre vues proposées, pas quatre poses moteur prouvées. Les revers de boucliers, livres et sacs sont des interprétations artistiques. L’ordre de leurs vues peut différer de celui de l’ancienne étude ; le comparatif examine la lisibilité et l’identité, pas une égalité de pose. Les poignées, cordes et chaînes sont dessinées pour le concept ; leur mouvement et leurs points de prise restent UNKNOWN.

## Autorité et provenance

`selected-alternatives.json` constitue la sélection réellement revue de ce nouveau lot. `review/visual-decisions.json` identifie les planches et miniatures inspectées ainsi que les corrections. Les premières variantes corrigées restent dans `rejected/`, avec leurs prompts et provenance. `generation-plan.json` conserve les demandes initiales ; les JSON associés aux sources/corrections conservent les prompts des itérations. Générateur OpenAI intégré, aucun appel Pollinations.

Ce lot ne remplace pas l’autorité gameplay de `Equipment-Originality-Revision` (271 designs), ni les 68 icônes de `Equipment-Ivalice-Style-V2`. Les nouvelles feuilles sont des alternatives de retouche aux études de `Equipment-Combat-Study-38` ; les originaux restent conservés. Les 107 autres armes/boucliers ne sont pas produits par ce lot.

## Limites concrètes de la livraison

Les 152 vues sont découpées suivant les séparations réellement détectées, puis réduites au plus proche voisin en 36 × 36 pour la comparaison. Le seuil alpha > 16 sert uniquement à trouver les limites géométriques. L’alpha et les couleurs des pixels copiés sont conservés ; aucun détourage destructif, aucune quantification ou conversion native ne sont appliqués. Les grands pixels générés ne garantissent pas une grille logique régulière.

L’absence de halo diffus visible est une conclusion de revue artistique. Elle ne signifie pas alpha binaire : les sources et aperçus gardent des couleurs nombreuses et des pixels semi-transparents. Les compteurs du rapport séparent alpha 0, alpha 255 et alpha 1 à 239 ; une valeur 254 est proche de l’opaque mais reste conservée sans modification. Ces chiffres ne définissent pas une palette du moteur.

Pour le relevé natif, utiliser le complément `Native-Weapon-Geometry` : WEP1/WEP2 SHP/SEQ extraits, comparaison octet pour octet avec les ressources historiques vérifiée dans `Equipment-Adaptation-Handoff`. La voie XML du gestionnaire local ItemData modifie les entrées existantes et ne fournit pas l’ajout de lignes ; ce constat n’est pas une limite moteur. Lier les nouveaux objets sans sacrifier les vanilla demande une voie additive démontrée.

## Suite pour Claude

Relever les poses nécessaires et les points de main sur une unité témoin, tracer Palette/SpriteID et les consommateurs réels, puis retoucher les formes sur une grille et une palette natives vérifiées. Encoder uniquement après cette preuve. Tester attente, marche, attaque, garde, directions et double équipement séparément dans les modes ciblés.

Runtime ready : false. Liaison moteur, pivots et nombre de poses requis : UNKNOWN. Format natif final : NOT_CREATED. Tests en jeu : NOT_RUN. Aucun ID attribué. Armures et accessoires : changement automatique de modèle non démontré.

## Reproduction

Le lecteur `tools/review_witnesses.py` relit les sources présentes, crée les découpes/aperçus et leurs mesures. `tools/make_review_boards.py` compose des contacts fidèles. `tools/finalize.py` exige une décision explicite pour les 38 objets et aucune correction non résolue avant de produire la sélection et le catalogue. `tools/package.py` vérifie tous les SHA de l’archive et refuse d’écraser une livraison scellée. Aucun de ces scripts ne génère d’images ni ne modifie le jeu.

La revue du navigateur reste refusée par la politique d’URL. Les planches, miniatures, liens locaux et empreintes de fichiers sont contrôlés localement sans contourner ce refus.
