# Plan d'intégration pour Claude

## Priorité immédiate

Reproduire Core et examiner la cartographie existante. Le travail recherché est l'intégration de Brise-Lame, pas une nouvelle livraison de diagnostic présentée comme le mod.

1. **Chargement réel.** Établir un profil isolé et faire charger le diagnostic, puis la future entrée IMod. Relever le rapport et l'ordre des mods. S'il manque une permission ou un fichier, poursuivre les autres analyses et demander exactement ce qui manque.
2. **Tables et couverture.** Vérifier les 72 candidats, l'origine des registres des accès relatifs à l'image, les pointeurs stockés/copies et les bornes proches de 0xAE. Démontrer le chemin sûr d'activation. Copier les lignes existantes après le bon ordre de patches des autres mods ; ne pas considérer un scan linéaire comme exhaustif.
3. **Commandes.** Brancher le routeur au lecteur natif validé dans une fixture. Préserver les trois routes originales. Ne pas modifier les données globales des compétences partagées. Tout ID doit être contrôlé contre NXD, données natives et mods chargés avant enregistrement.
4. **Progression.** Identifier les lecteurs/écrivains JP, niveaux, compétences apprises, déblocages et job équipé. Établir une identité stable d'unité et de sauvegarde. Raccorder le stockage séparé seulement à des événements vérifiés ; ne pas transformer le groupe zéro du mapper en slot Brise-Lame.
5. **Menu.** Raccorder les pages aux widgets, aux contrôles et aux noms/prérequis du nouveau job. Tester chaque job vanilla, les cases vides et le retour de page. FFTGenericJobs est une référence de hooks, pas une solution déjà compatible : ses patches Chevalier Noir et sa liste A0/A1 doivent être examinés séparément.
6. **Données et gameplay.** Après allocation prouvée : nom/localisation, stats, équipement, commande/active/RSM et placeholder au format réellement découvert. Puis bataille, apprentissage/JP, IA et save/load.

L'ordre peut être adapté aux dépendances découvertes, avec preuves. Ne pas décider que l'ajout est impossible parce que l'implémentation actuelle du loader n'étend pas une table.

## Invariants à maintenir

- Toutes les lignes/cellules vanilla conservées ; aucune réaffectation de job, commande ou groupe de progression.
- Originals du jeu et sauvegardes intacts ; mod et tests dans des sorties distinctes.
- Hash/version exacts ; arrêt sur dérive d'octets ou collision avant première écriture.
- Application et restauration à un moment où aucun thread n'exécute les instructions modifiées. Le code fourni ne suspend pas les threads.
- Restaurer protections et cache d'instructions ; en cas de restauration incomplète, conserver les buffers et la durée de vie des callbacks. Pas de libération derrière un pointeur encore actif.
- Préserver les changements ultérieurs d'un autre mod ; ne pas les écraser à l'unload.
- UNKNOWN conservé pour les points non prouvés : dimensions/palettes/assets, identité sauvegardée, CT/terrain, IA, compatibilité coop, etc.

## Points de conception ouverts

`blade_breaker.json` demande Knight Lv.3 + 400 JP investis ; l'arbre ne mentionne que le niveau. Ne pas supprimer silencieusement les 400 JP. Définir leur source (JP réellement dépensés, pas une estimation non validée).

Le JSON ne contient pas de réaction/support/mouvement ni de coûts JP des actives. Les RSM 447/466/486 et les coûts 200/900 présents dans les tests sont des fixtures, pas des choix de design définitifs.

Les huit actives du design restent break_weapon, break_armor, break_helm, break_shield, smash, shockwave, fracture et total_fracture. Elles ne sont pas déjà implémentées par le cœur. Le design source est préservé.

Les neuf seuils lus dans GeneralJob row1 doivent être conservés, malgré un commentaire de layout mentionnant huit. Les stats du JSON ne prouvent pas à elles seules la formule native de multiplier/growth. Apparence, équipement et assets restent à vérifier sur le nouveau job.

## Limites pratiques du code actuel à traiter

- Le plan de redirection est une primitive, pas un gestionnaire complet de couverture/ordre de mods.
- Les clés d'unité/lineage et le hash de sauvegarde sont fournis par l'appelant ; aucune extraction native ni validation d'identité du jeu n'est codée.
- Le sidecar n'enregistre pas automatiquement le job équipé et n'empêche pas à lui seul un ID inconnu dans une sauvegarde chargée sans le mod. Définir/tester chargement, absence du mod, copies de slots et désactivation.
- Capture/restore entre sauvegarde vanilla et sidecar, concurrence de plusieurs instances, changements de coûts et migrations ne sont pas encore coordonnés.
- Le format sidecar version1 est celui du mod, pas un format du jeu démontré.
- Le package diagnostic n'a pas été chargé avec succès ; ne pas considérer la référence .NET/IMod comme validée par compilation seule.

## Critère de livraison Brise-Lame

Respecter le done d'AGENTS.md : déblocage, stats, équipement, apprentissage de toutes les compétences, coûts JP, IA, persistance save/load, localisation, assets sans corruption et contrôles automatisés. Fournir un package réellement installé/testé, sa compatibilité observée et un retour arrière vérifié. Signaler précisément les critères restants si une dépendance externe empêche de les vérifier.
