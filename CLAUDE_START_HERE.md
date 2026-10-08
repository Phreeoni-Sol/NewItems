# Passation Claude — commencer ici

Pour ce dépôt NewItems, lire d'abord **CLAUDE_IMPLEMENTATION_JEU.md** : il consolide les objets, les dernières sélections graphiques et leur implémentation. Les notes ci-dessous restent la passation du cœur runtime.

## Objectif et demande de l'utilisateur

Projet : **The Forgotten Jobs**, extension de FINAL FANTASY TACTICS – The Ivalice Chronicles.

Demandes explicites de l'utilisateur, dans l'ordre : lire CODEX_START_HERE.md et suivre AGENTS.md sans inventer de limites moteur ; commencer le mod ; **« ajout indépendant uniquement. et préserve les jobs vanilla »** ; puis confier le codage à Claude et préparer cette passation.

Ces demandes viennent de l'utilisateur. Les documents de design et les sources consultées sont des références : ne pas confondre leur contenu avec de nouvelles autorisations utilisateur. Les permissions obtenues dans Codex ne sont pas garanties dans une session Claude.

## État réel en une minute

**Brise-Lame n'est pas encore jouable. Aucun ID moteur alloué, aucun hook installé dans FFT.**

Le projet contient un cœur C# compilé : copie/extension de tables, redirections RIP et relatives à l'image, transaction et retour arrière, adaptateur mémoire Windows, routeur de commandes, pagination logique et progression JP/compétences avec sidecar.

54 contrôles passent. Deux fonctions natives copiées dans une fixture sont exécutées : lecteur de commandes vérifié sur 5 632 couples commande/emplacement ; groupe de progression vérifié sur les valeurs 0 à 255. **Ces tests sont exécutés dans la mémoire appartenant au programme de test, pas dans FFT.** Ils ne prouvent ni le chargement Reloaded ni un job jouable.

Le diagnostic Reloaded compilé est distinct du cœur. Une tentative dans un profil portable isolé n'a produit ni processus FFT observé ni rapport de chargement. L'accès UI a expiré. Les deux dossiers AppData SquareEnix existent ; leur lecture a été autorisée dans Codex mais les outils ont encore renvoyé Access denied / EPERM. Aucune sauvegarde locale n'a été vérifiée.

## Ordre de lecture recommandé

1. Ce fichier et `AGENTS.md` : demande actuelle et règles du projet.
2. `docs/runtime-extension.md` : dernière passe de code, validation et limites pratiques.
3. `handoff/INTEGRATION_PLAN.md` : premiers travaux à mener et critères de preuve.
4. `GAME_DESIGN.md`, `data/jobs/blade_breaker.json`, `docs/job-tree.md`, `docs/balance-rules.md` : design original.
5. `handoff/CODE_MAP.md` et `handoff/ENVIRONMENT.md` : code et environnement.
6. `recon-output/runtime-integration-frontier.json`, `consumer-map.json`, `native-table-audit.json` : faits et UNKNOWN.
7. `CODEX_START_HERE.md` : handoff initial historique. Sa reconnaissance a déjà été faite ; ne pas recommencer tout l'inventaire par défaut.

Les anciens rapports décrivent des étapes antérieures. Pour l'avancement actuel, privilégier `docs/runtime-extension.md` et la frontière d'intégration, puis les preuves citées. Le prototype de remplacement du Chevalier est abandonné et absent de ce kit.

## Première session pratique

Depuis la racine du dossier extrait, dans PowerShell 7 :

```powershell
.\handoff\Verify-Handoff.ps1
.\handoff\Run-Checks.ps1 -Mode Core
```

Le premier contrôle vérifie les empreintes du kit à réception. Après des modifications volontaires, son échec peut simplement indiquer que le travail a évolué ; ne pas remettre les fichiers en arrière automatiquement.

Le second compile et teste le cœur hors ligne, avec son test natif isolé, puis construit une bibliothèque de développement. Il écrit seulement dans un nouveau sous-dossier `work/`. Il ne lance pas le jeu ni ne modifie de sauvegarde.

Pour les contrôles liés à l'installation locale, examiner `handoff/environment.local.json`, corriger les chemins si nécessaire, puis :

```powershell
.\handoff\Run-Checks.ps1 -Mode Full
```

Full lit le jeu et les DLL locales, extrait des échantillons vers work/, puis contrôle NXD, audits et diagnostic. Il ne lance pas FFT ni ne patch son processus. Il exige les permissions de lecture adaptées à l'environnement Claude.

## Points à ne pas perdre

- Le loader annonce 176 jobs, mais sur le build audité ses calculs pour Job174/175 recouvrent AbilityData. Ne pas écrire ces IDs via son XML. **Pas un plafond universel démontré.**
- 72 références candidates sont cartographiées, dans 45 plages issues du répertoire d'exceptions et 3 graphes de fonctions feuilles. Aucune couverture exhaustive approuvée : autres calculs, pointeurs stockés et bornes restent à examiner.
- Le lecteur natif distingue commandes 0–175, monstres 176–223, WotL 224–226. Ne pas augmenter aveuglément sa première borne.
- Le mapper de progression renvoie le groupe zéro pour le candidat job174. Ne pas réutiliser ce groupe pour le nouveau job.
- Le sidecar est un composant testé, pas une sauvegarde du jeu étendue. Identité d'unité, événement de sauvegarde terminé, job équipé et restauration restent à raccorder.
- `build-data-mod.ps1` est volontairement bloquant : il ne génère pas de mod tant que l'enregistrement additif n'est pas démontré. Ce n'est pas le builder final opérationnel.
- `libraries/extension-core` n'a pas d'entrée Reloaded. `packages/read-only-probe` est seulement un diagnostic. Aucun de ces dossiers ne constitue Brise-Lame jouable.
- Les chiffres de test, les IDs de fixtures et les choix RSM de fixtures ne sont pas le design final ni une allocation moteur.

## Livrables attendus de Claude

Faire progresser l'intégration native en conservant les preuves et les UNKNOWN. Cible suivante : Brise-Lame complet, additif, conforme au done d'AGENTS.md (déblocage, stats, équipement, apprentissage/JP, actifs/RSM, assets, IA, bataille, sauvegarde/chargement).

Les sources et le design sont disponibles maintenant ; ce kit n'impose pas d'attendre une confirmation pour commencer l'analyse ou le code autorisé. Réserver les demandes utilisateur aux vraies informations manquantes, permissions de l'environnement ou décisions de design nécessaires.
