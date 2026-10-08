# Ajout indépendant — décision et preuves

6 octobre 2026. Instruction utilisateur : **« ajout indépendant uniquement. et préserve les jobs vanilla »**.

Brise-Lame doit avoir une identité propre. Aucun remplacement du Chevalier, aucun recyclage des jobs 160/161, aucune modification des compétences vanilla partagées. Le prototype de remplacement et son générateur ont été retirés. `build-data-mod.ps1` refuse de produire un mod tant que l'enregistrement additif runtime n'est pas validé.

## Preuves vérifiées

Le codec NXD peut ajouter une ligne et la relire. Les tests comparent toutes les cellules originales : 174 jobs, 227 commandes et 21 GeneralJob sont conservés. Ils rejettent une collision d'ID et une modification du Chevalier. Les IDs des fixtures servent uniquement à la sérialisation ; **ils ne sont pas alloués au moteur**.

SHA-256 de l'exécutable Enhanced audité :
`937233F7FE76182A665C487C8802F5CEC6662DDD09967E87CD09FB146FC6B5D5`.

Les quatre signatures de tables provenant du loader 1.7.5 ont chacune une correspondance unique. Les adresses sont des offsets fichier et des RVA, pas des adresses absolues à réutiliser après ASLR.

| Table | Offset fichier | RVA | Octets / entrée | Nombre déclaré par le loader |
|---|---:|---:|---:|---:|
| JobData | 7 881 264 | 7 888 432 | 49 | 176 |
| JobCommand | 6 803 984 | 6 808 080 | 25 | 176 |
| JobNeedLevel | 6 808 464 | 6 812 560 | 12 | 22 |
| AbilityData | 7 889 792 | 7 896 960 | 8 | 512 |

**Collision locale :** `7 881 264 + 174 × 49 + 2 = 7 889 792`. Après 174 enregistrements Job complets et deux octets de séparation commence AbilityData. La plage de 176 jobs déclarée par le loader dépasse de 96 octets dans cette table. Un patch de job 174/175 utilisant ce calcul ne constitue donc pas un ajout sûr sur ce build.

Ce constat ne démontre pas un plafond universel de 174 jobs. Il démontre qu'il faut étendre ou détourner l'accès à la structure plutôt qu'écrire au-delà de cette zone. Les 35 références RIP candidates dans la plage Job sans chevauchement donnent des points à analyser. Le désassemblage linéaire n'est pas exhaustif : accès indirects, pointeurs copiés, bornes de boucles et constantes restent à examiner. Zéro référence directe pour JobCommand ne signifie pas zéro consommateur.

## Menu

Les 28 signatures relevées dans FFTGenericJobs correspondent chacune une seule fois dans cet exécutable. Elles incluent construction de liste, remplissage des cases, sélection et popup des prérequis. Cette correspondance statique ne valide ni la convention d'appel ni les hooks en jeu.

Ce mod expose deux jobs déjà présents, A0/A1, et contient des patches spécifiques au Chevalier Noir. Il ne prouve pas l'ajout d'une nouvelle identité. Nous ne l'activons pas comme solution pour Brise-Lame : ses changements vanilla et ses hypothèses de liste doivent être dissociés et vérifiés.

## Sauvegarde : extension UNKNOWN

Le code communautaire Ivalice Companion décrit des enregistrements d'unité de 600 octets et les champs suivants. **Observations de ce code, pas validation sur une sauvegarde locale.** Aucun fichier de sauvegarde utilisateur n'a été modifié.

| Champ décrit par la source | Représentation |
|---|---|
| Job courant | u8, offset 0x02 |
| Jobs débloqués | 24 bits, offset 0x2f |
| Compétences apprises | 22 groupes de trois octets, offset 0x32 |
| Niveaux de jobs | 24 demi-octets dans 12 octets, offset 0x74 |
| JP / JP totaux | 23 u16 chacun, offsets 0x80 / 0xae |

Le mapping publié associe 22 groupes aux jobs 0x4a–0x5d et 0xa0/0xa1. Le 23e champ JP ne prouve pas un emplacement additif disponible : compétences et mapping doivent également fonctionner. Il est interdit de réaffecter un groupe vanilla.

Deux voies à investiguer : extension coordonnée des structures et de leur sérialisation, ou stockage complémentaire avec interception des accès JP/maîtrise. La seconde nécessite une identité fiable d'unité et de sauvegarde, un traitement des copies/suppressions et une restauration du job équipé. Aucun de ces mécanismes n'est validé ; aucun sidecar n'est présenté comme opérationnel.

## Diagnostic compilé

`runtime/ReadOnlyProbe/Probe.cs` implémente une entrée Reloaded IMod. Le package est dans `packages/read-only-probe/`. Il ne crée pas Brise-Lame.

Au démarrage, il vérifie le hash de l'exécutable, les bornes du module et les plages mémoire lisibles, puis compare les hashes des lignes observées. JobData est limité aux 174 enregistrements non chevauchants. Il écrit uniquement un rapport dans le dossier de configuration géré par Reloaded et dans son journal. Aucun hook, patch, écriture mémoire ou accès aux sauvegardes.

Compilation et sept contrôles hors jeu réussis. Le chargement du DLL dans Reloaded et VirtualQuery dans le jeu restent **UNKNOWN**. Le snapshot se produit à l'entrée du diagnostic ; son ordre par rapport aux autres mods n'est pas établi. Une différence ne désigne pas son auteur, et une égalité ne valide pas l'extension.

Build reproductible : `tools/build/build-probe.ps1`. Prérequis locaux : PowerShell 7, SDK et reference pack .NET 9, DLL Reloaded.Mod.Interfaces 2.5.0 et exécutable audité. Compilation directe Roslyn sans téléchargement NuGet. Avertissement CS1701 lié aux références .NET anciennes de l'interface : tests hors jeu réussis, liaison dans Reloaded à tester.

## Suite pour un job jouable

1. Charger le diagnostic dans un profil de test isolé et recueillir son rapport.
2. Cartographier les consommateurs et leurs bornes ; implémenter une extension transactionnelle conservant les lignes vanilla et permettant le retour arrière.
3. Vérifier menu, progression et sauvegarde avant allocation d'ID. Vérifier les nouvelles compétences de la même manière.
4. Construire Brise-Lame à partir du design, puis tester déblocage, apprentissage, bataille, IA, assets et save/load.

Design initial intact : statistiques et huit actives non remplacées par les techniques du Chevalier. Divergence Knight Lv.3 / 400 JP investis et choix réaction/support/mouvement à résoudre avant implémentation. Le job n'est pas terminé.

## Provenance

- [Loader, commit c74047d](https://github.com/Nenkai/fftivc.utility.modloader/tree/c74047dc1b36bfe1bf6a466cf3645f1fe9815425) : signatures et structures ; installation locale 1.7.5.
- [FFTGenericJobs, commit 129931e](https://github.com/cipherxof/FFTGenericJobs/tree/129931e09064577c33a59a9108d60e8c81e7e388) : signatures du menu, source MIT consultée ; code de hooks non incorporé.
- [Ivalice Companion, commit 4b18c5d](https://github.com/sam-derby/Ivalice-Companion/tree/4b18c5dde0c1bfc51bef6da99422a6cc26b05568/crates/save-format/src/manual) : description des sauvegardes, source GPL consultée ; implémentation non copiée.

Preuves : `recon-output/native-table-audit.json`, `menu-signature-audit.json`, `native-validation.txt`, `additive-nxd-validation.txt`, `probe-validation.txt`.

## Extension runtime : code disponible

Le cœur est écrit et compilé : redirection transactionnelle, routeur de commandes, projection de menu et progression JP/compétences séparée. 54 contrôles du cœur passent ; les fonctions natives copiées sont testées sur 5 632 couples commande/emplacement dans une fixture isolée. Cartographie : 72 références candidates, couverture totale non approuvée. Raccordement au processus du jeu et save/load non validés. Aucun job jouable installé.

État actuel détaillé : `docs/runtime-extension.md` depuis la racine du projet (ou `runtime-extension.md` depuis docs/). Les notes de reconnaissance antérieures restent historiques ; cette mise à jour décrit l'avancement du code.
