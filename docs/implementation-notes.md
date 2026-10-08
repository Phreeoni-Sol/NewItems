# Implementation Notes

Statut au 6 octobre 2026 : **RECONNAISSANCE EN COURS — inventaire et extraction vérifiés ; extension et runtime UNKNOWN**.

Voir `recon-report.md` et `../recon-output/` pour les preuves. Les plafonds CT/pièges du design ne sont pas des limites moteur.

## Game build

- Plateforme observée : Windows, modes Enhanced et Classic présents.
- Installation : `D:\FINAL-FANTASY-TACTICS-The-Ivalice-Chronicles\FINAL FANTASY TACTICS - The Ivalice Chronicles`.
- Exécutables : `FFT_enhanced.exe`, `FFT_classic.exe`, empreintes dans `executables.json`.
- FileVersion : `1.0.0.0` pour les deux. Version commerciale / patch réel : **UNKNOWN** ; cette ressource seule ne l'établit pas.
- Loader présent : `fftivc.utility.modloader` 1.7.5, sous `CoopMod/tools/Reloaded-II/Mods/`. Activation et compatibilité runtime : **UNKNOWN**.
- Aucun jeu lancé, aucun ID alloué, aucun patch appliqué.

## Data formats

| Table extraite | Archive Enhanced | Lignes observées | État |
|---|---|---:|---|
| nxd/job.fr.nxd | 0004.fr.pac | 174 | NXDF v1 décodé, noms et références disponibles |
| nxd/ability.fr.nxd | 0004.fr.pac | 512 | NXDF v1 décodé |
| nxd/jobcommand.fr.nxd | 0004.fr.pac | 227 | NXDF v1 décodé |
| nxd/item.fr.nxd | 0004.fr.pac | 261 | NXDF v1 décodé |
| nxd/uistatuseffect.fr.nxd | 0004.fr.pac | 45 | Textes UI ; pas une preuve de 45 statuts de combat |
| nxd/generaljob.nxd | 0004.pac | 21 | Déblocage : IDs, niveaux et expérience exposés par le layout |
| nxd/overrideabilityactiondata.nxd | 0004.pac | 368 | Paramètres d'action : Formula, CT, MPCost, portée, flags, statut |

Toutes sont SingleKeyed. Les cinq FR sont localisées. Les nombres de lignes sont des observations de cette installation, pas des plafonds.

Les interfaces XML du loader documentent JobData 0–175, AbilityData 0–511, JobNeedLevelData 0–21, StatusEffectData 0–39, AbilityTypeData 0–453. JobCommandData : 0–175 et 224–226 ; 176–223 relèvent de MonsterJobCommandData. Preuves et SHA-256 dans `loader-table-evidence.json`. Leur application exacte à la mémoire du jeu local reste à vérifier. Elles ne démontrent ni des slots libres ni une impossibilité d'extension par hooks.

Le loader expose des masques d'équipement et des flags IA. Ses structures donnent JobCommandId en byte et InnateAbilityId en uint16 ; les références Job NXD sont int/uint. Aucun type universel d'ID n'est établi.

AbilityData.xml indique que son JPCost n'est pas la source utilisée, et renvoie au NXD Ability. AbilityActionData.xml est un rappel sans fonctionnalité : il renvoie à OverrideAbilityActionData. Effet runtime de ces couches : **UNKNOWN**.

## Asset formats

- Sprite extrait : `0002.pac:fftpack/unit/battle_10m_spr.bin`, 37 377 octets.
- Portrait extrait : `0002.pac:fftpack/event_wldface_bin.bin`, 131 072 octets.
- Fragment UI extrait : `0008.pac:ui/ffto/common/face/textureparts/wldface_001_08_uitx.utexpt`, 310 octets.
- Conteneur localisé : `0007.pac:system/ffto/g2d.dat`.
- Dimensions, frames, palettes, atlas, conversion et rendu sprite/portrait/icône/VFX : **UNKNOWN**.
- Présence d'un fichier et taille connue ne valident pas une spécification graphique.

## Engine questions

| Question | Résultat |
|---|---|
| Append jobs / abilities | **UNKNOWN** ; distinguer NXD, table interne, menus, IA et sauvegarde |
| Déblocage additif | **UNKNOWN** ; GeneralJob et JobNeedLevelData identifiés, logique restante à inspecter |
| Coût HP | **UNKNOWN** ; aucun HPCost dans le layout d'action examiné, ce qui ne prouve aucune impossibilité |
| CT direct d'unité | **UNKNOWN** ; CT d'action ne démontre pas CT d'unité modifiable |
| Déplacement forcé | **UNKNOWN** ; formule, position, hauteur et collisions à étudier |
| Pièges/terrain persistant | **UNKNOWN** ; MapTrapFormationData existante, création dynamique non démontrée |
| Météo/lois globales | **UNKNOWN** ; weather.tga existe, sans preuve d'état global scriptable |
| Nouveaux statuts | **UNKNOWN** au-delà de l'édition des paramètres exposés |
| IA | Flags exposés ; comportement des nouvelles mécaniques **UNKNOWN** |
| Indexation des sprites | **UNKNOWN** ; TexturePartsIndex identifié pour portraits UI seulement |
| Online / coop | Dossier CoopMod présent ; compatibilité **UNKNOWN** |
| Sauvegarde / maîtrise | **UNKNOWN** ; aucune sauvegarde modifiée ni structure élargie démontrée |

## Design et prochaine étape

- L'arbre demande Knight Lv.3 ; blade_breaker.json ajoute « 400 JP investis en Knight ». Clarifier le design et la signification de JP investis avant implémentation.
- Le JSON ne fournit pas la réaction, le support, le mouvement ou leurs coûts JP nécessaires au done.
- Stats : valeurs de design ; conversion vers multipliers/growth à vérifier.
- Dresseur / Dresseur de Guerre : identifiants à normaliser dans la préparation des données.
- Prochaine expérience : cartographier Job → déblocage → commandes/abilities → maîtrise sauvegardée, avant allocation d'un ID.

## Fallback policy

Développement additif uniquement, conformément au choix utilisateur. Voir `additive-extension.md` et `blade-breaker-progress.md`. Ajouts NXD avec préservation vanilla et diagnostic Reloaded compilé ; aucune allocation runtime ni installation. Le prototype de remplacement est retiré. Runtime et save/load restent UNKNOWN.

Préserver l'intention si une expérience démontre un obstacle. Documenter puis tester l'alternative ; les fallbacks du handoff sont des candidats, pas des fonctions déjà disponibles. Ne pas abandonner une mécanique sur la seule base d'un UNKNOWN. Modifier le design explicitement selon la politique du handoff.

## Audit natif et décision additive — 6 octobre 2026

Les templates du loader ne prouvent pas des slots libres. Sur le SHA-256 Enhanced audité, JobData commence à l'offset 7881264, avec des entrées de 49 octets ; AbilityData commence à 7889792. Cela laisse 174 entrées Job complètes et deux octets, puis la table Ability. La déclaration de 176 jobs du loader recouvre 96 octets d'AbilityData. IDs 174/175 interdits via ce calcul sur ce build. Aucun plafond général du moteur déduit.

L'ajout de lignes NXD avec préservation de toutes les cellules originales est testé. Il ne valide pas l'extension native. Les références natives candidates et les 28 signatures du menu sont consignées dans `recon-output/`. Un diagnostic sans écriture mémoire est compilé et testé hors jeu, non installé. Structures de sauvegarde décrites par une source communautaire, non vérifiées sur une sauvegarde locale. Détails/provenance : `additive-extension.md`.

## Extension runtime : code disponible

Le cœur est écrit et compilé : redirection transactionnelle, routeur de commandes, projection de menu et progression JP/compétences séparée. 54 contrôles du cœur passent ; les fonctions natives copiées sont testées sur 5 632 couples commande/emplacement dans une fixture isolée. Cartographie : 72 références candidates, couverture totale non approuvée. Raccordement au processus du jeu et save/load non validés. Aucun job jouable installé.

État actuel détaillé : `docs/runtime-extension.md` depuis la racine du projet (ou `runtime-extension.md` depuis docs/). Les notes de reconnaissance antérieures restent historiques ; cette mise à jour décrit l'avancement du code.
