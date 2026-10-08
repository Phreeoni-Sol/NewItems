# Environnement et dépendances

Le kit est autonome pour le code et les preuves, pas pour les fichiers du jeu ni les runtimes installés. `environment.local.json` contient les chemins du PC d'origine et peut être adapté. Ce fichier ne transfère pas de permissions.

## Installation observée

- Windows x64, PowerShell 7.6.5, .NET SDK 9.0.318 / reference pack 9.0.20 lors des tests.
- Enhanced : FFT_enhanced.exe, SHA-256 `937233F7FE76182A665C487C8802F5CEC6662DDD09967E87CD09FB146FC6B5D5`.
- Classic : inventorié seulement ; ne pas appliquer les offsets Enhanced à Classic.
- Loader fftivc.utility.modloader installé : 1.7.5.
- Launcher Reloaded-II local : runtime .NET 9 ; liaison du diagnostic en jeu non validée.
- Source du loader : commit c74047dc1b36bfe1bf6a466cf3645f1fe9815425.
- Les ressources FileVersion 1.0.0.0 ne permettent pas d'identifier le patch commercial réel ; utiliser les hashes.

`local-dependencies.json` relève SHA-256 et version d'assembly des bibliothèques nécessaires à NXD. Le helper de compilation utilise directement Roslyn et le reference pack local .NET 9 ; il n'a pas besoin d'une restauration NuGet. Une tentative dotnet restore classique a buté sur l'accès à AppData/NuGet.Config dans le sandbox Codex. Ce problème n'est pas une limite de .NET ou du jeu.

Le diagnostic référence Reloaded.Mod.Interfaces 2.5.0. Son avertissement CS1701 est documenté ; tests hors jeu réussis, chargement dans Reloaded inconnu. Iced.dll est fourni par le mod sharedlib.hooks local, pas par le kit.

## Archives et extraction

61 PAC inventoriés : Enhanced 36 / 38 233 entrées ; Classic 25 / 13 035 entrées. Codename FF16Tools : **ffto**. La décompression a nécessité le chargement des DLL dstoragecore.dll puis dstorage.dll du jeu. Le script d'extraction contient ce chemin.

Les dix échantillons ne sont pas livrés. Les régénérer avec `sample-tables.ps1` ou Run-Checks Full. Les JSON d'audit contiennent les octets et observations des structures inspectées ; ils ne remplacent pas l'installation réelle.

## Sources épinglées livrées

`references/upstream/` contient deux archives git archive des sources MIT, sans .git : loader et FFTGenericJobs, licences incluses. Elles sont consultables hors ligne et extractibles vers work/.

Les extraits Ivalice Companion sont des copies source non modifiées, avec licence GPL-3.0-only et notices. Ce sous-dossier est une référence séparée, pas une dépendance du cœur et pas un checkout compilable. Ne pas mélanger son code GPL dans le cœur sans traiter les obligations de licence ; les faits observés peuvent orienter l'investigation.

Les hashes et commits figurent dans provenance.json et le manifeste du kit. Si un checkout Git complet est nécessaire : cloner l'URL déclarée et sélectionner le commit exact, avec les permissions réseau propres à Claude. Ne pas supposer que le HEAD actuel du dépôt distant est la version auditée.

Un problème Git « dubious ownership » est apparu lors d'un changement de compte sandbox. Pour ce dossier de sources connu uniquement, un `git -c safe.directory=<chemin exact> -C <chemin exact> ...` fonctionne ; ne pas modifier la configuration globale ni utiliser un joker.

## Sauvegardes et lancement

Dossiers candidats : AppData/Local/SquareEnix et AppData/Roaming/SquareEnix. Ils existent ; le chemin précis d'un fichier FFT est inconnu. Permission de lecture accordée dans Codex, lecture toujours refusée (Access denied/EPERM). Ne pas attribuer ce refus à l'utilisateur et ne pas en déduire un fait moteur. Obtenir un chemin accessible ou une copie de sauvegarde si nécessaire.

Le profil Reloaded original avait les mods hooks, sigscan, framework, modloader et coop activés. Aucun n'a été modifié. Un profil portable indépendant, diagnostic seul, a été tenté sous work/runtime-test dans l'ancien workspace, puis ses processus ont été fermés. Aucun démarrage FFT ni rapport diagnostic observé. Ne pas activer la coop pendant le premier test additif sans validation de compatibilité.

Le launcher et les DLL tierces ne sont pas redistribués dans le kit. Les réutiliser depuis l'installation locale ou les obtenir depuis leurs sources officielles selon le besoin. Éviter d'hériter du profil de mods habituel pour un premier test ; relever exactement les versions et l'ordre de chargement.
