# The Forgotten Jobs — rapport initial de reconnaissance

Date : **6 octobre 2026**. Statut : **analyse réelle commencée ; reconnaissance complète non acquise**.

CODEX_START_HERE.md, AGENTS.md et les documents de design/workflow ont été lus avant l'analyse. Travail limité à la Phase 0 : aucun job implémenté, ID alloué ou original du jeu écrasé. Les règles d'équilibrage du handoff ne sont pas des limites moteur.

## 1. Outils utilisés

PowerShell 7.6.5, rg, SHA-256, bibliothèques FF16Tools.Pack/Files déjà présentes dans le loader local 1.7.5. PAC ouverts avec codename `ffto` ; DirectStorage décompresse les échantillons avec les DLL déjà présentes dans le dossier du jeu.

Sources primaires consultées : [guide Nenkai](https://nenkai.github.io/ffxvi-modding/modding/creating_mods_fft/), [FF16Tools](https://github.com/Nenkai/FF16Tools), [loader](https://github.com/Nenkai/fftivc.utility.modloader), [source FFTGenericJobs](https://github.com/cipherxof/FFTGenericJobs/blob/main/GenericJobs/Mod.cs).

Le téléchargement des dépôts via PowerShell/curl a échoué à cause de TLS/Schannel. Aucun dépôt téléchargé. Les bibliothèques locales et la consultation web ont permis de poursuivre. L'ouverture initiale sans codename et l'extraction avant chargement de DirectStorage ont échoué explicitement ; les commandes corrigées ont réussi sans mutation du jeu.

Scripts reproductibles : `tools/extract/recon.ps1`, `tools/extract/sample-tables.ps1`. Tests : `tests/recon-tests.ps1`. Les scripts ont un dry-run et refusent des sorties dans les répertoires source du jeu/loader.

## 2. Fichiers inspectés

Installation : `D:\FINAL-FANTASY-TACTICS-The-Ivalice-Chronicles\FINAL FANTASY TACTICS - The Ivalice Chronicles`.

| Périmètre | Inventaire vérifié |
|---|---|
| Enhanced | 36 PAC ; 38 233 entrées |
| Classic | 25 PAC ; 13 035 entrées |
| Total | **61 PAC ; 51 268 entrées** |
| Exécutables | Enhanced 12 158 720 octets ; Classic 7 900 416 ; hashes conservés |
| Loader | CoopMod/tools/Reloaded-II/Mods/fftivc.utility.modloader ; ModVersion 1.7.5 |

FileVersion des exécutables : 1.0.0.0. Version réelle du patch : **UNKNOWN**, cette ressource seule ne l'établit pas. Loader installé sur disque ; activation runtime **UNKNOWN**.

Les répertoires des 61 archives ont été lus, sans décompression totale. Dix fichiers Enhanced ont été extraits ; sept NXD décodés entièrement. Les données binaires extraites restent dans work/, hors du projet livré.

Preuves dans `../recon-output/` : archives.csv, archive-files.csv, executables.json, environment.json, sample-summary.json, nxd-row-keys.csv, loader-table-evidence.json et validation.txt.

## 3. Formats vérifiés

PAC : signature PACK observée, parsing réussi avec FF16Tools.Pack. Exemple 0000.pac Enhanced : en-tête chiffré et chunks signalés par le parseur. Les flags des autres PAC figurent dans archives.csv.

NXD : signature **NXDF**, version 1, SingleKeyed. Les cinq tables FR ci-dessous sont localisées ; les deux autres ne le sont pas.

| Archive Enhanced | Chemin | Lignes | Taille inline selon layout, octets |
|---|---|---:|---:|
| 0004.fr.pac | nxd/job.fr.nxd | 174 | 64 |
| 0004.fr.pac | nxd/ability.fr.nxd | 512 | 68 |
| 0004.fr.pac | nxd/jobcommand.fr.nxd | 227 | 36 |
| 0004.fr.pac | nxd/item.fr.nxd | 261 | 48 |
| 0004.fr.pac | nxd/uistatuseffect.fr.nxd | 45 | 36 |
| 0004.pac | nxd/generaljob.nxd | 21 | 124 |
| 0004.pac | nxd/overrideabilityactiondata.nxd | 368 | 40 |

Les chaînes/tableaux référencent des données supplémentaires : la taille inline n'est pas une taille totale de ligne dans le fichier.

Clés observées : Job 0–173 ; Ability 0–511 ; JobCommand 0–226 ; GeneralJob 0–20. UiStatusEffect contient des clés discontinues : 45 textes UI ne prouvent pas 45 statuts de combat.

Job expose Name/Description, jobtype, jobcommand, TexturePartsIndex. GeneralJob expose RequiredJobExp, RequiredJobIds, RequiredJobLevels. OverrideAbilityActionData expose Formula, X/Y, InflictStatus, CT, MPCost et paramètres de ciblage. Le décodage ne valide pas leur effet runtime.

Assets extraits : sprite battle_10m_spr.bin (37 377 octets), portrait event_wldface_bin.bin (131 072), fragment UI wldface_001_08_uitx.utexpt (310). g2d.dat localisé dans Enhanced 0007.pac. Dimensions, palettes, frames, codecs graphiques et mapping complet : **UNKNOWN**.

## 4. Limites internes et portée des preuves

**Aucune limite absolue d'extension du moteur n'est démontrée dans cette passe.** Les XML locaux du loader documentent les contraintes suivantes ; leur application à la mémoire de cet exécutable reste à vérifier. Hashes et nombres d'entrées conservés dans loader-table-evidence.json.

| Interface loader 1.7.5 | IDs documentés |
|---|---|
| JobData | 0–175 ; taille annoncée 176 |
| AbilityData | 0–511 ; taille annoncée 512 |
| JobNeedLevelData | 0–21 ; taille annoncée 22 |
| StatusEffectData | 0–39 ; taille annoncée 40 |
| AbilityTypeData | 0–453 ; taille annoncée 454 |
| JobCommandData | 0–175 et 224–226 ; 176–223 dans MonsterJobCommandData |

Ne pas confondre nombre de lignes NXD, table interne, liste des jobs génériques, menus, bits de maîtrise et stockage sauvegardé. Un ID absent/vide n'est pas un ID libre sans audit des références. Un champ byte/uint16 ne prouve pas une capacité utilisable égale à son domaine numérique.

Le source FFTGenericJobs montre des hooks, une pagination et des traitements pour A0/A1, avec un patch du contrôle de déblocage. C'est une piste pour étudier les jobs masqués et les menus ; ce code ne prouve pas l'ajout de 30 jobs arbitraires ni leur persistance. [Source](https://github.com/cipherxof/FFTGenericJobs/blob/main/GenericJobs/Mod.cs).

## 5. Points d'extension candidats

Le mainteneur décrit overrides de fichiers, fusion de cellules NXD et modifications XML sous FFTIVC/tables/<mode>/. Il mentionne aussi les mods de code pour étendre les comportements internes. [Guide](https://nenkai.github.io/ffxvi-modding/modding/creating_mods_fft/).

Candidats : XML minimal pour stats/équipement/commandes ; NXD pour textes et données complémentaires ; overrides d'assets. Ces voies sont identifiées, **pas encore qualifiées de sûres en jeu**.

Détails locaux à respecter : AbilityData.xml indique que JPCost doit venir du NXD Ability ; AbilityActionData.xml est un rappel sans fonctionnalité et renvoie à OverrideAbilityActionData. Ne pas produire le patch dans la mauvaise couche.

## 6. Systèmes risqués / UNKNOWN

| Système | État |
|---|---|
| Append jobs/abilities et collisions d'IDs | UNKNOWN ; extension NXD seule insuffisante comme preuve |
| Coût HP | UNKNOWN ; absence de HPCost dans le layout inspecté ne prouve pas l'impossibilité |
| CT direct | UNKNOWN ; CT d'action distinct de CT d'unité |
| Déplacement forcé | UNKNOWN ; collisions/hauteur/formules à inspecter |
| Pièges dynamiques et terrain persistant | UNKNOWN ; MapTrapFormationData existante ne prouve pas la création par compétence |
| Statuts personnalisés / interception | UNKNOWN au-delà des paramètres déjà exposés |
| Météo/lois globales | UNKNOWN ; weather.tga est seulement un asset localisé |
| IA | Flags exposés ; évaluation des nouvelles mécaniques UNKNOWN |
| Sauvegarde, maîtrise, migration | UNKNOWN ; aucun test save/load |
| Compatibilité coop/autres mods | UNKNOWN ; dossier CoopMod présent |

Les fallbacks du handoff restent des candidats à tester. Ne pas annoncer qu'un statut caché, une AoE ou la vitesse remplacent déjà une mécanique complexe.

## 7. Stratégie recommandée

1. Cibler Enhanced et son SHA-256 exact ; relever le profil des mods de test. Classic seulement inventorié ici.
2. Examiner les signatures des tables sur une copie d'exécutable et les consommateurs de leurs tailles. Ne pas reprendre des offsets historiques.
3. Étudier sauvegarde et structures JP/maîtrise avant allocation. Examiner les hooks existants sans activation à l'aveugle.
4. Lecture → sérialisation → relecture NXD vérifiée depuis ce rapport initial, ainsi que les ajouts de lignes conservant les cellules vanilla. Voir `additive-extension.md`.
5. Tester le diagnostic en lecture seule, puis démontrer une extension additive conservant tous les jobs vanilla ; aucun remplacement temporaire autorisé.
6. Après ces preuves : Brise-Lame, plan de retour arrière, tests bataille et sauvegarde.

## 8. Blocages et limites

Accès au jeu et décompression disponibles. Restent analyse mémoire/signatures, sérialisation, sauvegarde et tests runtime. Aucun jeu lancé ou hook appliqué. FileVersion ne suffit pas à identifier le patch réel, présence du loader ne suffit pas à prouver son activation.

Design à préciser : Knight Lv.3 seul dans l'arbre contre ajout de 400 JP investis dans le JSON ; réaction/support/mouvement et coûts absents du JSON. Ce sont des lacunes de conception, pas des limites moteur. Ne pas modifier le design silencieusement.

## 9. Prochaine étape Brise-Lame

Cartographier sur copies la chaîne **Job ↔ GeneralJob/JobNeedLevel ↔ JobCommand ↔ Ability/OverrideAbilityActionData ↔ maîtrise sauvegardée**. Produire une matrice de références et une justification d'allocation avant de choisir un ID.

Une fois l'extension validée : un job additif, condition clarifiée, stats/équipement, commande Fracture, une active, une réaction, un support, un mouvement, textes FR et assets temporaires au format vérifié. Vérifier battle load, apprentissage/JP, IA, affichage et save/load. Aucun de ces critères de done n'est revendiqué aujourd'hui.

## Validation exécutée

Cinq contrôles réussis dans tests/recon-tests.ps1 : rejet des sorties dans le dossier source ; dry-run sans écriture ; deux exécutions indépendantes donnant cinq rapports identiques par SHA-256 ; décodage des lignes sélectionnées avec tailles, clés uniques et nombre de colonnes contrôlés ; hash de l'exécutable Enhanced inchangé.

Ces tests concernent la reconnaissance, pas la sérialisation, le gameplay ou les sauvegardes.

## Mise à jour — ajout indépendant uniquement

Le choix utilisateur interdit le remplacement temporaire. Les résultats de sérialisation, ajout NXD, audit natif, signatures du menu, recherche de représentation sauvegardée et diagnostic Reloaded compilé sont consolidés dans [additive-extension.md](additive-extension.md). Les sections historiques de ce rapport décrivent la reconnaissance initiale ; la mise à jour fait foi pour l'état du développement.

Collision physique vérifiée sur ce build : Job174/175 tels qu'adressés par le loader recouvrent AbilityData. Ne pas les allouer via XML. Cette collision ne démontre pas de plafond universel ; l'extension runtime reste à implémenter et à tester. Aucun job jouable ou test save/load revendiqué.
