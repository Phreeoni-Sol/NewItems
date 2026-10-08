# Contexte projet pour Claude

Commencer par **CLAUDE_IMPLEMENTATION_JEU.md**, puis **AGENTS.md** et **docs/runtime-extension.md**. **CLAUDE_START_HERE.md** conserve la passation initiale du cœur runtime ; le nouveau guide décrit aussi les 271 objets et les derniers assets.

Demande utilisateur actuelle : Claude prend en charge le codage de The Forgotten Jobs. Ajouts indépendants uniquement ; préserver tous les jobs vanilla et leur progression. Ne pas inventer de limites moteur.

La reconnaissance et un cœur d'extension testé existent déjà. Le job n'est pas encore jouable ; aucun hook du jeu ni ID moteur n'est alloué. Les tests natifs portent sur des fixtures isolées, pas sur FFT. Ne pas présenter les bibliothèques ou le diagnostic comme le mod final.

Consulter `handoff/` pour les chemins locaux, les commandes de validation, le plan d'intégration et les pièges connus. Travailler avec les outils et permissions réellement disponibles dans la session ; les outils Codex ne sont pas requis ni garantis.

Conserver les sources originales du jeu et les sauvegardes ; utiliser work/ pour les copies, extractions et tests. Ne pas activer de remplacement du Chevalier ou de slot vanilla. L'ancien CODEX_START_HERE.md décrit la mission initiale ; l'état actuel figure dans ce handoff.
