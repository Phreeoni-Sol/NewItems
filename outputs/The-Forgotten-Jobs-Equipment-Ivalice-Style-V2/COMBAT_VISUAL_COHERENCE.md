# Cohérence entre icônes et équipements portés — pour Claude

## Réponse actuelle

Les grandes icônes d’inventaire ne deviennent pas automatiquement les petites armes dessinées sur les combattants. Nos 271 propositions d’objet n’ont pas encore de liaison graphique validée en combat. Une icône réussie ne démontre donc pas la cohérence d’une arme équipée.

La recherche locale a identifié une ressource native distincte, `0002.pac` / `fftpack/unit/battle_wep_spr.bin` : 85 504 octets, SHA256 `7a4c733e1654f9f1ff41e1281fd26fce894bd608bc1c95e1e4713aecdc0eff0a` (le SHA exact sans espaces est dans le manifeste joint). Le code amont FFTPatcher contient `WEPSprite`, `WepSprite` et des formes WEP. Il concerne les variantes historiques de FFT ; cela n’autorise pas à attribuer arbitrairement ses dimensions et indices au rendu Enhanced de The Ivalice Chronicles. Le chemin de résolution objet -> graphisme en combat, les palettes/poses effectivement utilisées et la possibilité d’ajout restent `UNKNOWN`.

Le pack de nouveaux jobs déjà livré contient des armes dessinées directement dans certaines poses de personnage. Il faut auditer ces poses avant d’y ajouter un overlay : sinon une arme peut rester fixe indépendamment de l’inventaire ou deux armes peuvent s’afficher. Une substitution globale d’overlay toucherait potentiellement le vanilla et ne respecte pas la demande.

## Contrat visuel à respecter

Pour chaque arme exceptionnelle, garder les mêmes trois repères entre l’icône et la représentation en combat : silhouette, palette principale et motif signature. Les gravures, petites pierres et ajours trop fins doivent être simplifiés dans le petit sprite ; les proportions doivent rester compatibles avec la main et les poses. Les références de prestige ont volontairement des signatures assez fortes pour survivre à cette simplification.

Exemple de L’Absent : garder la lame grise en feuille, la petite garde asymétrique, la poignée et le ruban vert mousse. Le souffle vert pâle est une signature d’inventaire ; son éventuel rendu en combat exige une voie vérifiée. Ne pas remplacer arbitrairement cette arme par une lame vanilla sans l’indiquer.

Les PNG 48×48 et 100×100 du catalogue sont des tests d’auteur de lisibilité, pas des textures, sprites ou modèles prêts à charger sur les unités. Ne pas les utiliser directement comme sprites de combat.

## Travail à réaliser avant intégration

1. Trouver et documenter la résolution effective des nouveaux IDs d’objet vers les ressources et animations d’armes, pour les modes réellement ciblés. Examiner banque, forme, séquence, palette, pivot et points d’attache ; ne pas supposer de format commun Classic/Enhanced.
2. Produire une arme témoin et vérifier en jeu les quatre orientations, déplacement, attente, frappe, garde, main gauche/droite et double équipement. Vérifier aussi les unités vanilla équipées de la nouvelle arme.
3. Auditer les nouveaux sprites de jobs dont l’arme est intégrée aux pixels. Choisir une voie validée : poses compatibles avec arme séparée, variante de pose spécifique, ou autre raccordement additif réellement démontré. Ne pas effacer globalement l’arme vanilla.
4. Après découverte des contraintes, dessiner les petits sprites de combat correspondants à chaque pièce visible, avec les signatures du manifeste. Créer les nouveaux assets et liaisons sans écraser les ressources existantes.
5. Capturer côte à côte l’icône, l’arme sur le personnage et le mouvement d’attaque. Le design n’est validé pour le combat que si les trois restent cohérents et sans doublon, clipping ou mauvais pivot.

Pour les armures, robes, chapeaux et accessoires, aucune modification automatique de l’apparence du personnage n’est démontrée par ce travail. Ne pas promettre des modèles portés interchangeables tant que le chemin d’affichage n’est pas prouvé. Il peut être nécessaire de garder l’apparence du job ou de créer des variantes adaptées, sous réserve d’une solution additive validée.

## État et repli

Tous les graphismes portés nouveaux : `NOT_CREATED`. Tous les bindings de combat : `UNKNOWN`. Pas de mockup annoncé comme capture du jeu.

Si un raccordement distinct est impossible avec le chemin testé, préserver les assets et rechercher une autre voie additive. Une arme prototype utilisant temporairement un visuel vanilla doit être explicitement marquée comme proxy dans le catalogue et les tests ; elle ne peut pas être présentée comme visuellement terminée. Ne pas inventer une impossibilité moteur à partir de cet échec.

