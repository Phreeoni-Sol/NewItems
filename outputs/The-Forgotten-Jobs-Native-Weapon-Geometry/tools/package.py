from pathlib import Path
import hashlib, json, zipfile

root=Path(__file__).resolve().parents[1]
archive=root.with_suffix('.zip')
if archive.exists():
    raise FileExistsError('Preserve sealed delivery; choose a new archive name for a revision.')
manifest={str(p.relative_to(root)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob('*')) if p.is_file() and p.name!='file-manifest.json'}
(root/'file-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(root.rglob('*')):
        if p.is_file(): z.write(p,str(p.relative_to(root)))
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for name,digest in manifest.items():
        assert hashlib.sha256(z.read(name)).hexdigest()==digest
digest=hashlib.sha256(archive.read_bytes()).hexdigest()
archive.with_suffix('.zip.sha256').write_text(f'{digest}  {archive.name}\n',encoding='ascii')
print(json.dumps({'archive':str(archive),'bytes':archive.stat().st_size,'sha256':digest,'verified_files':len(manifest)}))
