from pathlib import Path
import hashlib
import json
import re
import zipfile

root=Path(__file__).resolve().parents[1]
report=json.loads((root/'validation-report.json').read_text(encoding='utf-8'))
assert report['concept_equipment']==38 and report['concept_weapons']==36 and report['concept_shields']==2 and report['cut_poses']==152 and not report['runtime_ready']
entries=[]
for p in sorted(root.rglob('*')):
    if not p.is_file() or '__pycache__' in p.parts or p.name=='file-manifest.json':continue
    data=p.read_bytes()
    if p.suffix in ('.json','.py','.html','.md','.txt'):
        assert not re.search(rb'sk_[A-Za-z0-9]{20,}',data)
    entries.append({'path':p.relative_to(root).as_posix(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
(root/'file-manifest.json').write_text(json.dumps({'runtime_ready':False,'files':entries},indent=2)+'\n',encoding='utf-8')
out=root.parent/'The-Forgotten-Jobs-Combat-Study-38-Exceptional-Equipment.zip'
files=[p for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts]
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in files:z.write(p,p.relative_to(root).as_posix())
    z.write(root.parents[1]/'work/handoff/The-Forgotten-Jobs/AGENTS.md','AGENTS.md')
    z.writestr('README.md','Lire CLAUDE_COMBAT_HANDOFF.md et ouvrir index.html. 38 etudes graphiques (36 armes, 2 boucliers), 152 vues proposees. Aucun asset valide en jeu. Le retour au catalogue exige le dossier frere Originality-Revision. Les prompts sont dans concepts/*.json. Les anciens ZIP restent historiques.\n')
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
    for p in files:assert hashlib.sha256(z.read(p.relative_to(root).as_posix())).digest()==hashlib.sha256(p.read_bytes()).digest()
sha=hashlib.sha256(out.read_bytes()).hexdigest()
out.with_suffix('.zip.sha256').write_text(sha+'  '+out.name+'\n',encoding='ascii')
print(json.dumps({'path':str(out),'bytes':out.stat().st_size,'sha256':sha,'verified':True}))
