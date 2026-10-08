# Carte du code et des preuves

| Zone | Fichiers | Lecture conseillée |
|---|---|---|
| Cœur de redirection | runtime/ExtensionCore/Relocation.cs | Plans RIP/image, conservation du préfixe, PatchTransaction |
| Mémoire Windows | runtime/ExtensionCore/WindowsMemory.cs | VirtualQuery/Protect, cache, allocation proche, durée de vie |
| Commandes ajoutées | runtime/ExtensionCore/CommandRouter.cs | Cas personnalisés ; délégation de tous les autres au lecteur original |
| Menu logique | runtime/ExtensionCore/MenuPages.cs | Pages, sélection et identité ; aucun widget natif raccordé |
| Progression séparée | runtime/ExtensionCore/Progression.cs | Registry symbolique, coûts configurés, JP, snapshot lié au hash de sauvegarde |
| Diagnostic Reloaded | runtime/ReadOnlyProbe/Probe.cs | IMod, vérification de hash, observation des lignes ; aucune écriture mémoire |
| Codec NXD | tools/build/nxd.ps1 | Lecture/écriture, clone de ligne, comparaison de toutes les cellules vanilla |
| Extraction | tools/extract/recon.ps1 et sample-tables.ps1 | Inventaire PAC, hashes, extraction hors du jeu |
| Audit natif | tools/extract/audit-native.ps1 et NativeAudit.cs | Signatures, tables, collision et références RIP candidates |
| Cartographie | tools/extract/map-consumers.ps1 et ConsumerDecoder.cs | PE exception directory, graphes feuilles, déplacements |
| Build | tools/build/csharp-offline.ps1, build-extension-core.ps1, build-probe.ps1 | Compilation hors ligne ; source hashes et sorties séparées |

## Vérifications

- extension-core-tests : 54 contrôles, dont exécution d'un consommateur x64 sur mémoire de fixture, conservation des valeurs et retour arrière.
- native-accessor-tests : fonctions natives copiées, lecteur comparé sur 5 632 couples, callback natif/géré, mapper de progression ; exécutable exact obligatoire.
- consumer-map-tests : branches après RET, displacement suivi d'immédiat et cohérence des 72 candidats.
- native-audit-tests : signatures, RIP et collision locale Job/Ability.
- nxd-tests et additive-nxd-tests : round-trips, nouvelles lignes de fixtures et égalité vanilla.
- probe-tests : hors jeu seulement ; ne teste pas un chargement Reloaded.
- recon-tests : extraction/inventaire reproductibles, dry-run et destinations séparées.

Les rapports correspondants sont sous recon-output/. Ils ont été conservés tels qu'à la fin du développement Codex. Run-Checks produit ses nouveaux logs sous work/ et ne remplace pas ces preuves historiques.

## Adresses importantes — build Enhanced épinglé seulement

| Élément | RVA | Remarque |
|---|---:|---|
| JobData | 0x785E30 | 49 octets / entrée ; 174 entrées avant AbilityData |
| AbilityData | 0x787F80 | Commence deux octets après Job173 |
| JobCommand principal | 0x67E210 | Entrées de 25 octets ; commandes 0–175 |
| JobNeedLevel | 0x67F390 | Structure de 12 octets ; extension à analyser |
| Lecteur de commande | 0x275860 | Branches normal/monstre/WotL distinctes |
| Mapper job → groupe JP | 0x2B8F18 | Candidat 174 → zéro ; ne pas détourner un slot vanilla |

Les RVA ne sont pas des adresses absolues. Respecter ASLR, le hash du module, les octets des instructions, la portée signée disp32 et l'origine du registre utilisé. Les offsets fichier figurent dans les JSON d'audit.

## Ce qui est volontairement incomplet

`build-data-mod.ps1` lève une erreur. Il matérialise la décision de ne pas produire un patch de remplacement, pas une implémentation d'enregistrement runtime. `libraries/extension-core` contient une bibliothèque sans IMod. Le diagnostic dans packages/ ne crée aucun job.

Le routeur ne pose pas de detour. La pagination ne manipule pas les pointeurs UI. La progression ne lit pas les unités du jeu ni les sauvegardes. Ces raccordements sont le travail suivant.
