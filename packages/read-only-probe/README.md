# The Forgotten Jobs — diagnostic seulement

Ce package ne rend pas Brise-Lame jouable. Il observe les tables natives au démarrage, sans hook, patch, changement de job ni accès aux sauvegardes. Compilé pour .NET 9 et l'interface Reloaded 2.5.0, sur l'installation locale Reloaded-II utilisant .NET 9. Chargement en jeu non testé.

Exécutable autorisé : FFT_enhanced.exe, SHA-256 `937233F7FE76182A665C487C8802F5CEC6662DDD09967E87CD09FB146FC6B5D5`. Tout autre hash arrête le diagnostic avant lecture mémoire.

Pour un futur test : ajouter ce dossier comme mod dans un profil Reloaded de test isolé, puis lancer Enhanced. Le journal indiquera le chemin du rapport `read-only-probe.json`, dans le dossier de configuration du mod. L'emplacement dépend du launcher. Aucune installation automatique ni copie dans le jeu effectuée.

Une égalité des lignes observées ne valide pas l'ajout de jobs. Les différences peuvent venir d'autres mods et ne désignent pas leur auteur. Retrait : désactiver le diagnostic dans Reloaded.

Sources/build : `runtime/ReadOnlyProbe/`, `tools/build/build-probe.ps1`, `tools/build/csharp-offline.ps1`. Détails : `docs/additive-extension.md` dans le projet livré.
