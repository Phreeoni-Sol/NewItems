# Production des équipements avec Klein

## Périmètre autorisé

203 objets courants, peu communs et rares du catalogue The Forgotten Jobs. Les 34 légendaires et 34 uniques sont réservés pour un autre modèle : voir reserved-legendary-unique.json. Tous les objets sont des ajouts proposés ; aucun objet ou job vanilla n'est remplacé. Aucun ID runtime alloué et aucun fichier du jeu modifié.

## Méthode

Modèle black-forest-labs/flux.2-klein-4b, via l'API Pollinations /v1/images/edits. Une référence native Enhanced par objet, la description propre à l'objet et les consignes de rendu peint, couleurs sobres, contours doux, orientation et absence de texte. Deux générations indépendantes au maximum en parallèle ; les requêtes 401/402/403 interrompent l'envoi du reste du lot. Une relance est permise pour une erreur serveur ou de débit.

Tarif annoncé lors du lancement : 0,005 pollen par génération. Coût théorique du lot initial de 203 images : 1,015 pollen, hors corrections et débits éventuels d'erreurs. Ce chiffre n'est pas un relevé du compte.

Les huit premiers cas pilotes ont servi au contrôle des consignes. Les armes à lame du lot suivant ajoutent une interdiction explicite des fourreaux et objets croisés. La dague pilote doit être reprise pour supprimer son élément supplémentaire.

## Livrables

- images/ : images de génération originales, enregistrées en PNG.
- previews100/ et previews48/ : aperçus redimensionnés avec conservation des proportions et fond de présentation blanc.
- prompts/ et production-plan.json : consignes et références.
- records/ : paramètres, tentatives, dimensions et SHA256 des fichiers de sortie.
- contact-sheets/ : planches de revue.
- catalogue.html : vue par famille avec référence native et nouvelle proposition.
- production-status.json : couverture du lot, erreurs et état d'intégration.

## Limites réelles

La génération ne vaut pas validation artistique. Des variations de silhouettes, reflets, détails ou cohérence restent possibles ; elles doivent être recensées dans la revue du lot. Les sorties RGB sur fond blanc n'ont pas de transparence. Les aperçus à 100 et 48 px sont des tailles de contrôle, pas des limites moteur prouvées. L'extraction de la silhouette, le binding de texture, les nouvelles tables, l'acquisition et le rendu en jeu restent à faire et vérifier. Le lot ne constitue pas un mod jouable.

Les textes, caractéristiques et effets proposés des 271 objets demeurent dans le catalogue d'équipements d'origine. Le présent dossier ne modifie que leur production artistique. Claude reste chargé de l'intégration additive.

## Reprise

Utiliser Python + Pillow, depuis la racine du workspace. La clé Pollinations doit être disponible dans l'environnement du processus sous POLLINATIONS_API_KEY ; ne pas la sauvegarder dans les scripts, manifestes ou archives. generate_production.py all reprend uniquement les images manquantes et conserve celles déjà générées. make_catalogue.py actualise le catalogue et les planches à partir des fichiers existants. Les images et métadonnées sont conservées pour assurer la traçabilité des sorties stochastiques.

Les références natives restent des matériaux de travail locaux, propriété de leurs ayants droit. Le lien entre le numéro de texture et l'objet est une association de référence, pas un binding testé dans le jeu.

## Lot terminé — état des livrables artistiques

203 objets avec une variante sélectionnée dans selected-manifest.json : 71 courants, 59 peu communs et 73 rares. Les 34 légendaires et 34 uniques restent réservés, sans génération Klein dans ce lot.

203 images initiales, 12 images de correction et une deuxième correction de la lance du gué : **216 générations réussies**, soit **1,080 pollen au tarif annoncé**, débit du compte non vérifié. Les 203 images sélectionnées et leurs SHA256 ont été contrôlés. Les neuf planches du lot et les planches de correction ont été inspectées ; les doublons d’objets, arcs incomplets, lances mal formées, rondache anguleuse et capuche transformée en chapeau ont fait l’objet d’une correction de forme. Ce contrôle n’affirme pas que tous les détails et matériaux sont parfaitement conformes aux références. La lance de la nef a notamment une silhouette simplifiée et ses crochets décoratifs restent à affiner.

Les anciennes variantes sont conservées pour comparaison. Le catalogue et les planches finales affichent les images choisies par selected-manifest.json, sans écraser les générations originales. Les 203 choix restent des propositions d’atelier, tous sans transparence et sans binding runtime validé.

Pour Claude : utiliser selected-manifest.json comme point d’entrée graphique, le catalogue d’équipement historique pour les caractéristiques et effets, et reserved-legendary-unique.json pour la suite artistique. Ne pas insérer les variantes historiques ou les objets réservés à la place d’objets vanilla. L’allocation additive des IDs, la conversion/binding de textures et la vérification en jeu restent UNKNOWN jusqu’à validation.


## Révision de gameplay : autorité actuelle

Les effets, prix et budgets des 271 objets ont été revus dans le dossier frère `The-Forgotten-Jobs-Equipment-Originality-Revision`. Lire son `CLAUDE_HANDOFF.md` et son `items.json` ; les propositions de gameplay du dossier Equipment-Expansion sont historiques. Les images de ce dossier restent les sources artistiques sélectionnées. Aucun effet nouveau n’est encore intégré au jeu.


## Visuels légendaires et uniques disponibles

Le dossier frère `The-Forgotten-Jobs-Equipment-Kontext-Legendary-Unique` contient désormais les 68 visuels sélectionnés, leurs variantes et leur passation. Le catalogue du port 8852 affiche les 271 objets. Lire le manifeste de sélection, puis la révision de gameplay pour l’autorité sur les effets. Les sources restent à détourer et intégrer.
