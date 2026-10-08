# Extension runtime — code et validation

6 octobre 2026. Ajout indépendant uniquement. Le cœur de l'extension est écrit et compilé, mais il n'est pas encore raccordé au jeu : **Brise-Lame n'est pas jouable**.

## Code disponible

| Composant | Fonction implémentée | État de validation |
|---|---|---|
| Relocation.cs | Copie de table avec préfixe vanilla intact, plans RIP/image-relative, contrôle de portée disp32, transaction, dry-run et retour arrière | Tests et exécution sur mémoire native appartenant au test |
| WindowsMemory.cs | Lecture contrôlée, allocation proche, protection des pages et cache d'instructions | Test natif ; aucun patch du processus FFT |
| CommandRouter.cs | Commandes personnalisées séparées, délégation exacte des commandes existantes | Appel natif → routeur géré → copie du lecteur natif FFT |
| MenuPages.cs | Pagination avec conservation de l'ordre et de toutes les entrées vanilla | Projection testée ; widgets et entrées clavier du jeu non raccordés |
| Progression.cs | JP totaux/disponibles, apprentissage avec coûts configurés, niveaux, prérequis et snapshot séparé par unité/job | Round-trip sidecar testé ; identité d'unité et événements de sauvegarde du jeu non raccordés |

Sources : `runtime/ExtensionCore/`. Bibliothèque : `libraries/extension-core/ForgottenJobs.ExtensionCore.dll`. Ce DLL n'a pas d'entrée Reloaded IMod : ce n'est pas un package de job installable. Aucun ID moteur n'est alloué. Les IDs de tests sont locaux aux fixtures.

Les constantes de coûts, niveaux et prérequis sont passées au composant par les données. Les coûts utilisés par les tests ne sont pas des valeurs de balance finales. Une compétence inconnue ou sans coût configuré est rejetée. Le test de prérequis conserve les deux conditions du JSON Brise-Lame ; la divergence avec l'arbre de design et la source runtime des JP réellement investis restent à résoudre.

## Validation native réelle, dans une fixture isolée

54 contrôles du cœur passent. Un petit consommateur x64 exécuté par le test lit la nouvelle table, accède à une ligne ajoutée et retrouve les valeurs vanilla inchangées. Le retour arrière restaure instructions, pointeurs et protections mémoire. Les échecs partiels, les modifications d'un autre mod et les restaurations incomplètes sont détectés ; si un pointeur peut subsister, le stockage doit rester vivant.

Un second test copie, depuis l'exécutable au SHA-256 audité, deux fonctions natives sans appels externes. Il redirige uniquement leurs références de base vers des copies des tables dans sa propre mémoire. **Il ne lance ni ne modifie FFT.**

Le lecteur de commandes correspond au décodeur indépendant sur **5 632 couples commande/emplacement**. Un appel natif traverse ensuite le routeur géré : toutes les commandes vanilla, monstres et WotL sont conservées ; une commande supplémentaire de fixture renvoie ses propres actives et RSM. Cela vérifie l'ABI utilisée par cette fonction et la logique du routeur ; cela ne vérifie pas un detour Reloaded dans le processus du jeu.

Le mapper de progression natif est également exécuté sur les 256 valeurs de 0 à 255. Le candidat 174 renvoie le groupe zéro. **Il ne dispose donc pas d'un groupe de progression distinct par ce chemin.** Cela ne prouve pas un plafond moteur ; il faut détourner les accès à la progression ajoutée, jamais réaffecter un groupe vanilla.

Preuves : `extension-core-validation.txt`, `native-accessor-validation.txt` dans `recon-output/`.

## Cartographie améliorée

`map-consumers.ps1` exploite le répertoire d'exceptions x64 du PE et les branches directes des fonctions feuilles. Il recense maintenant **72 références candidates dans 48 plages/fonctions examinées** : 40 RIP-relative, 32 accès avec déplacement relatif à l'image. Aucun candidat recensé n'est laissé sans décodage, mais **la couverture totale n'est pas approuvée** : pointeurs stockés, calculs indirects et autres bornes restent à examiner. Une adresse relative à l'image exige de vérifier l'origine du registre de base ou d'index avant patch.

Le lecteur de commandes à RVA 0x275860 possède des branches distinctes : 0–175, monstres 176–223, WotL 224–226 ; à partir de 227 il renvoie zéro. Une augmentation aveugle de la première borne ferait passer les commandes monstres par la mauvaise table. Le routeur prévu ajoute un cas spécifique et conserve l'accès original pour les autres IDs.

Le mapper job → groupe de progression se trouve à RVA 0x2b8f18. La cartographie conserve aussi les instructions de comparaison 0xAE proches des lectures JobData. Ces observations sont spécifiques au SHA-256 audité, pas des limites universelles.

Preuves : `consumer-map.json`, `consumer-disassembly.txt`, `consumer-map-validation.txt`. Le décodeur teste les branches après un premier RET et la récupération de déplacements suivis d'immédiats.

## Intégration restant nécessaire

- Achever les preuves des consommateurs/bornes et établir un point d'activation où aucun thread n'exécute une instruction modifiée. Le composant mémoire ne suspend pas les threads.
- Raccorder le routeur au lecteur natif via un detour Reloaded et assurer sa durée de vie. Le test de passage ABI ne remplace pas ce test en jeu.
- Raccorder les widgets/menu aux pages, avec sélection, noms et retour aux jobs vanilla.
- Trouver une identité stable d'unité et de sauvegarde ; intercepter lectures/écritures JP, apprentissage, déblocage et job équipé. Le sidecar n'étend pas à lui seul les tableaux natifs.
- Valider la capture après sauvegarde réussie et la restauration lors du chargement. Les copies de slots, renommages, suppressions d'unités, versions de coûts et migrations nécessitent des règles explicites.
- Allouer les IDs seulement après ces vérifications, construire les données Brise-Lame, puis tester assets, bataille, IA et save/load.

## Tentative en jeu et accès aux fichiers

Un launcher portable et un profil de diagnostic ont été créés dans `work/runtime-test`, sans les mods habituels. Le hash du profil Reloaded original est conservé. Aucun processus FFT ni rapport de diagnostic n'a été observé. La demande d'accès au launcher via computer-use a expiré. Les processus de launcher isolés créés par cette tâche ont été fermés. **Démarrage en jeu non validé.**

La permission de lecture des deux dossiers AppData SquareEnix a été accordée, mais leur lecture renvoie toujours Access denied / EPERM avec les outils. Aucune sauvegarde n'a été lue, copiée ou modifiée. Le chemin précis d'une sauvegarde reste à fournir ou à rendre accessible pour sa vérification. Ce blocage d'accès ne dit rien des possibilités du moteur.

Le profil portable s'appuie sur la [documentation Reloaded](https://reloaded-project.github.io/Reloaded-II/ExperimentalFeatures/) ; le lancement par --launch est décrit dans sa [FAQ](https://reloaded-project.github.io/Reloaded-II/FAQ/). Il n'a pas été présenté comme un test réussi.

## Reproduire les vérifications

PowerShell 7 et SDK/reference pack .NET 9 locaux :

```powershell
.\tests\extension-core-tests.ps1 -ScratchRoot C:\chemin\hors-jeu\tests-core
.\tests\native-accessor-tests.ps1 -Executable 'D:\chemin\FFT_enhanced.exe' -ScratchRoot C:\chemin\hors-jeu\tests-native
.\tests\consumer-map-tests.ps1 -IcedDll 'D:\chemin\Iced.dll'
.\tools\build\build-extension-core.ps1 -ScratchRoot C:\chemin\hors-jeu\build -OutputRoot C:\chemin\hors-jeu\library
```

Le test des fonctions copiées exige l'empreinte exacte du build audité ; il refuse les autres versions. Aucun exécutable du jeu, fichier NXD extrait ou sauvegarde n'est distribué dans l'archive du projet. Les rapports contiennent les octets et désassemblages des structures examinées pour rendre les audits vérifiables.


