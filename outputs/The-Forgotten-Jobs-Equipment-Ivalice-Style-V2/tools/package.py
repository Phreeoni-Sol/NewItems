from pathlib import Path
import hashlib
import json
import re
import sys
import zipfile

sys.stdout.reconfigure(encoding='utf-8')
root = Path(__file__).resolve().parents[1]
revision = root.parent / 'The-Forgotten-Jobs-Equipment-Originality-Revision'
out = root.parent / 'The-Forgotten-Jobs-Ivalice-V2-68-Visuals-and-Combat-Handoff.zip'
selected = json.loads((root / 'selected-manifest.json').read_text(encoding='utf-8'))
assert len(selected) == 68
assert all(i['alpha_ready'] and not i['runtime_ready'] and i['status'] == 'SELECTED_VISUALLY_REVIEWED_AUTHORING' for i in selected)
assert json.loads((root / 'validation-report.json').read_text(encoding='utf-8'))['status'] == 'PASS'
files = []
for directory in (root, revision):
    manifest = []
    for p in sorted(directory.rglob('*')):
        if not p.is_file() or '__pycache__' in p.parts or p.name == 'file-manifest.json':
            continue
        data = p.read_bytes()
        if p.suffix in ('.py', '.json', '.md', '.txt', '.html'):
            assert not re.search(rb'sk_[A-Za-z0-9]{20,}', data), 'Credential-like token found'
        manifest.append({'path': p.relative_to(directory).as_posix(), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
    (directory / 'file-manifest.json').write_text(json.dumps({'files': manifest, 'runtime_ready': False}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for p in sorted(directory.rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts:
            files.append((p, (Path(directory.name) / p.relative_to(directory)).as_posix()))
start = '''# Claude — livraison Ivalice V2

Lire AGENTS.md. The-Forgotten-Jobs-Equipment-Ivalice-Style-V2 est l’autorité artistique pour les 68 légendaires et uniques : selected-manifest.json, CLAUDE_ART_HANDOFF.md, COMBAT_VISUAL_COHERENCE.md, références natives, prompts, neuf corrections retenues et comparatifs. Les anciens lots Kontext et Prestige sont historiques.

The-Forgotten-Jobs-Equipment-Originality-Revision est l’autorité de design pour les 271 propositions : effets, prix, contreparties et acquisition. Son catalogue portable contient 271 aperçus et les 68 grandes sources V2. Les 203 grandes sources ordinaires Klein restent dans le lot Klein précédent ; leurs aperçus sont inclus ici.

Les 68 icônes V2 ont une transparence alpha vérifiée. Les aperçus 100/48 pixels sont des outils de revue, pas une spécification moteur. Les sprites des armes équipées restent à créer ; leur liaison est UNKNOWN. Aucun test en jeu, aucun ID moteur attribué, aucun patch à installer. Préserver tous les objets et jobs vanilla par des ajouts indépendants uniquement.
'''
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    z.writestr('CLAUDE_START_ART.md', start.encode('utf-8'))
    project = root.parents[1]
    z.write(project / 'work/handoff/The-Forgotten-Jobs/AGENTS.md', 'AGENTS.md')
    for p, name in files:
        z.write(p, name)
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
    for p, name in files:
        assert hashlib.sha256(z.read(name)).digest() == hashlib.sha256(p.read_bytes()).digest(), name
    entries = len(z.infolist())
sha = hashlib.sha256(out.read_bytes()).hexdigest()
out.with_suffix('.zip.sha256').write_text(sha + '  ' + out.name + '\n', encoding='ascii')
print(json.dumps({'path': str(out.resolve()), 'bytes': out.stat().st_size, 'entries': entries, 'sha256': sha, 'verified': True}, ensure_ascii=False))
