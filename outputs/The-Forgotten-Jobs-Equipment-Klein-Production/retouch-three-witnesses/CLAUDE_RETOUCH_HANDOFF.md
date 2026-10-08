# Trois témoins redessinés depuis la référence native

Ce lot expérimente une autre méthode de retouche artistique : repartir d’un dessin neuf, décrit par sa signature, avec l’atlas natif comme référence de style. Les essais précédents d’édition de Dernier aveu conservaient le halo de leur source. Ils restent archivés et ne sont pas remplacés.

## Objets concernés

- Dernier aveu : lame courte cuivrée en feuille, dos ébréché, poignée noire, petit sceau rouge.
- Mémoire du premier soin : bois d’if rouge, fourche asymétrique, petit galet rose, lin sauge.
- Le Refus : bouclier céramique ocre asymétrique, coin manquant, bande indigo, paume de fer, fissure réparée.

Les nouveaux dessins restent des propositions artistiques en quatre vues. Aucune correspondance avec une pose native n’est attribuée. Les vues arrière du bouclier sont inventées pour le design, pas observées dans le moteur. Les originaux des 38 études et leurs icônes sont conservés. Les mécaniques et prix des 271 objets ne changent pas.

## Contrôle

Les sources sont inspectées à grande taille, puis les 12 aperçus à 36 × 36. Cette taille sert à examiner la lisibilité et ne constitue pas un format du jeu. `tools/review_witnesses.py` détecte des séparations réellement vides au-dessus d’alpha 16, découpe les vues et fait une réduction fidèle au plus proche voisin. Il ne modifie ni les couleurs ni l’alpha des pixels copiés. Le rapport compte les couleurs et les pixels selon leur alpha ; il ne certifie pas une palette native ni un encodage.

Les prompts exacts et les références sont conservés dans `generation-plan.json`. Générateur : outil OpenAI intégré. Aucun appel Pollinations. Le manifeste de sélection décrit le résultat de la revue ; l’existence d’une source seule ne signifie pas acceptation.

## Suite

Ne pas transposer directement les quatre vues à une animation. Relever les poses nécessaires, les points de prise, inversions et palettes sur une unité témoin avant conversion. La silhouette et les grands aplats constituent le guide de retouche ; grille native régulière, palette indexée et format final restent à produire et valider. Les ajouts doivent préserver tous les items et jobs vanilla.

Tests en jeu : NOT_RUN. Liaison moteur et pivots : UNKNOWN. Runtime ready : false. Le contrôle navigateur reste refusé par sa politique d’URL ; les images et fichiers sont contrôlés localement.
