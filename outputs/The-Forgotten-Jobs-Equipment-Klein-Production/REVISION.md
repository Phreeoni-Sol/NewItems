# Révision d’originalité — 271 objets

Cette révision remplace les propositions d’effets et de prix de `The-Forgotten-Jobs-Equipment-Expansion/items.json`. Elle ne modifie aucun objet du jeu et ne constitue pas un mod installé.

## Résultat du travail de conception

- 271 fiches revues : 71 communes, 59 peu communes, 73 rares, 34 légendaires et 34 uniques.
- Chaque fiche possède un effet conditionnel, un rôle tactique, une limite ou une contrepartie, une acquisition proposée et un repli de développement.
- Suppression du principe « même effet vanilla, nouveau nom et meilleures statistiques ». Les 16 consommables ont tous une seconde fonction tactique ou un fonctionnement différent de leur référence.
- Les anciens passifs sont remplacés, pas additionnés. Les anciens bonus permanents de Mouvement, Saut, PA et MA ne sont pas reconduits ; les valeurs de puissance/PV/MP sont réduites pour laisser du budget aux effets.
- Prix des consommables recalculés individuellement ; prix des autres objets disponibles en boutique basés sur leur référence et leur rareté. Ce sont des propositions à équilibrer en bataille.
- Légendaires et uniques : acquisition dédiée, hors boutique et non revendables dans ce design. Leur unicité doit être validée par le code ; elle n’est pas garantie par ces fichiers.
- Les 203 visuels Klein sélectionnés sont conservés. Le lot frère Kontext apporte les 68 nouveaux visuels légendaires/uniques et leurs variantes de correction. Leur transparence et leur liaison au jeu restent à finaliser. La révision de gameplay n’a généré aucune image ; la production visuelle est tracée dans le lot Kontext.

## Exemples avant / après

| Objet | Ancienne proposition | Nouvelle identité |
|---|---|---|
| Pastille du chœur | Retire Silence ; 5 400 gils | Retire Silence et bloque une seule nouvelle application jusqu’à la fin du prochain tour ; 150 gils proposés |
| Baume de route | Soin simple | 25 PV immédiats et une réserve de 15 PV pour compléter un prochain soin |
| Épée des haltes | Profil de progression | Une attente immobile prépare un crédit de 5 MP, perdu si le porteur se déplace avant son sort |
| Bâton des sources | Profil de progression | Une partie de l’excédent d’un soin complet passe à un second allié voisin, avec plafond et sans cascade |
| Panacée du pèlerin | Restauration de PV/MP | Récupération mixte limitée en échange de l’abandon des réserves offensives des nouveaux équipements |

## Ce que l’audit démontre

Couverture exacte des 271 identifiants existants, nouveaux textes pour les 271 effets, absence de doublon textuel après neutralisation des nombres, contrôle des paramètres numériques et des références de fichiers, aucune allocation d’identifiant moteur, conservation du fichier source et des visuels sélectionnés. Les similarités lexicales servent à repérer des fiches à relire ; elles ne prouvent ni ne réfutent l’originalité sémantique.

La référence comprend les 261 lignes inventoriées, dont sentinelles et entrées hors équipement, et sept tables d’objets du modloader. Elle ne comprend pas une analyse exhaustive des compétences vanilla ni de toutes les liaisons `OptionsAbilityId`. Il serait donc faux de garantir que chaque interaction imaginable est absente du jeu. L’objectif du design est de différencier la combinaison déclencheur / cible / résultat / coût des ajouts par rapport aux profils statiques relevés.

## État réel

Conception et catalogue prêts pour revue de Claude. Les points d’accroche, identifiants, règles d’éligibilité, formats d’icônes et comportements en bataille restent `UNKNOWN` tant qu’ils ne sont pas validés. Les fichiers JSON décrivent l’intention ; ils ne sont ni des scripts exécutables ni des patchs de tables à charger tels quels.

Voir `CLAUDE_HANDOFF.md`, `BALANCE_RULES.md`, `originality-audit.json` et `changes.json`.
