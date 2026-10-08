# Contrôle avant transmission

Le 6 octobre 2026, Run-Checks Full a été exécuté sur une copie du projet avec
des répertoires de travail extérieurs au kit. Ses dix étapes ont réussi :
54 contrôles du cœur, compilation, extraction séparée, codec NXD, additions
NXD sans modification des lignes originales, audit natif, graphe de consommateurs,
deux accesseurs natifs isolés, diagnostic hors jeu, garde-fous de reconnaissance.

Les résultats et logs exacts sont sous `validation/`. Les chemins absolus dans
les logs désignent la machine d'origine ; les fixtures ne sont pas redistribuées.
Le diagnostic produit un avertissement CS1701 conservé dans son log.
Cela ne valide pas un chargement Reloaded/FFT : aucun jeu n'a été lancé pour
cette vérification, et aucune sauvegarde réelle n'a été lue ou modifiée.

`integrity-manifest.json` couvre les fichiers livrés, y compris les archives de
sources épinglées, sauf lui-même et les futurs fichiers de travail. Il vérifie
l'intégrité de la copie reçue, sans signature d'authenticité. Le SHA256 de
l'archive complète est fourni à côté du ZIP. Les fichiers de design, AGENTS.md
et CODEX_START_HERE.md ont été comparés à l'archive initiale et conservés.
