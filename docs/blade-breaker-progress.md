# Brise-Lame — développement additif

6 octobre 2026. **Ajout indépendant uniquement, tous les jobs vanilla préservés. Aucun job jouable installé ou validé.**

Le remplacement temporaire du Chevalier est abandonné. Son plan généré a été retiré ; le builder refuse les plans de remplacement. Les fichiers de design originaux restent intacts.

Travail validé : extraction locale, sérialisation NXD, ajout de lignes dans des fixtures avec comparaison de toutes les cellules vanilla, audit natif des tables, recherche des signatures du menu et compilation d'un diagnostic Reloaded sans patch. Les tests détectent collisions, changements vanilla, chevauchements, empreinte inconnue et snapshots incomplets.

Constat : les jobs 174/175 déclarés par le loader recouvrent AbilityData sur ce build. Nous ne les utilisons pas. Il faut investiguer et implémenter une extension des accès aux structures, du menu et de la progression sauvegardée. Aucun plafond moteur général n'est démontré.

`packages/read-only-probe` est **uniquement un diagnostic**, compilé et testé hors jeu. Il ne crée ni job ni compétence et ne touche aucune sauvegarde. Chargement en jeu à vérifier.

État détaillé et prochaines étapes : [additive-extension.md](additive-extension.md). Aucun ID moteur alloué. Déblocage, équipement, actives personnalisées, réaction/support/mouvement, assets, IA et sauvegarde restent nécessaires pour satisfaire AGENTS.md.

## Extension runtime : code disponible

Le cœur est écrit et compilé : redirection transactionnelle, routeur de commandes, projection de menu et progression JP/compétences séparée. 54 contrôles du cœur passent ; les fonctions natives copiées sont testées sur 5 632 couples commande/emplacement dans une fixture isolée. Cartographie : 72 références candidates, couverture totale non approuvée. Raccordement au processus du jeu et save/load non validés. Aucun job jouable installé.

État actuel détaillé : `docs/runtime-extension.md` depuis la racine du projet (ou `runtime-extension.md` depuis docs/). Les notes de reconnaissance antérieures restent historiques ; cette mise à jour décrit l'avancement du code.
