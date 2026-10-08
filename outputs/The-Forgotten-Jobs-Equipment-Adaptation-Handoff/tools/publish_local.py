"""Copy the review bundle to the existing local catalogue; no browser access."""
from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[1]
base=next(p for p in root.parents if (p/'work/upstream').is_dir())
page=root/'index.html'
text=page.read_text(encoding='utf8')
if 'retouch-pilot/tfj_knife_10-v2.png' not in text:
    section='<h2>Essais de retouche non retenus — Dernier aveu</h2><p>Ombrages simplifiés, mais halo résiduel : aucun remplacement de la version sélectionnée.</p><details><summary>Voir les deux essais rejetés</summary><img class="native" src="retouch-pilot/tfj_knife_10-v2.png" alt="Premier essai, halo non corrigé"><img class="native" src="retouch-pilot/tfj_knife_10-v3.png" alt="Correction ciblée, halo toujours présent"><p><a href="retouch-pilot/tfj_knife_10-v2.json">Prompt initial</a> · <a href="retouch-pilot/tfj_knife_10-v3.json">Prompt de correction</a></p></details>'
    page.write_text(text.replace('</html>',section+'</html>'),encoding='utf8')
for catalogue in ('The-Forgotten-Jobs-Equipment-Klein-Production','The-Forgotten-Jobs-Equipment-Originality-Revision'):
    destination=base/'outputs'/catalogue/'equipment-adaptation'
    shutil.copytree(root,destination,dirs_exist_ok=True,ignore=shutil.ignore_patterns('tools','file-manifest.json'))
    study=destination.parent/'combat-study/index.html'
    text=study.read_text(encoding='utf8')
    if 'equipment-adaptation/index.html' not in text:
        study.write_text(text.replace('</h1>','</h1><p><a href="../equipment-adaptation/index.html">Fiches de retouche et repères natifs — 38 équipements</a></p>',1),encoding='utf8')
    assert destination.joinpath('index.html').is_file()
print('Updated both local catalogues; no browser navigation or game writes.')
