from pathlib import Path
import json,hashlib,zipfile,sys
sys.stdout.reconfigure(encoding='utf-8')
r=Path(__file__).resolve().parents[1];dest=r.parent/'The-Forgotten-Jobs-Equipment-271-Originality-Revision.zip'
manifest=[]
for p in sorted(r.rglob('*')):
 if not p.is_file() or '__pycache__' in p.parts or p.name=='file-manifest.json':continue
 manifest.append({'path':p.relative_to(r).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(r/'file-manifest.json').write_text(json.dumps({'files':manifest,'scope':'design handoff and existing small previews; full source images in sibling Klein pack','runtime_ready':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(r.rglob('*')):
  if p.is_file() and '__pycache__' not in p.parts:z.write(p,(Path(r.name)/p.relative_to(r)).as_posix())
with zipfile.ZipFile(dest) as z:
 assert z.testzip() is None
 for entry in manifest:assert hashlib.sha256(z.read(r.name+'/'+entry['path'])).hexdigest()==entry['sha256']
 count=len(z.infolist())
sha=hashlib.sha256(dest.read_bytes()).hexdigest();dest.with_suffix('.zip.sha256').write_text(sha+'  '+dest.name+'\n',encoding='ascii')
print(json.dumps({'path':str(dest.resolve()),'bytes':dest.stat().st_size,'entries':count,'sha256':sha,'verified':True},ensure_ascii=False))
