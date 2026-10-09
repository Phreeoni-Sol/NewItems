from pathlib import Path
import hashlib,json,re
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'handoff/git-delivery-manifest.json').read_text(encoding='utf8'))
errors=[]
for name,digest in manifest.items():
    path=root/name
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:errors.append(name)
assert not errors, f'Files changed or missing: {errors[:20]}'
def read(path):return json.loads((root/path).read_text(encoding='utf8'))
design=read('outputs/The-Forgotten-Jobs-Equipment-Originality-Revision/items.json')
records=design['items'];assert len(records)==271
for prefix,count in [('The-Forgotten-Jobs-Retouch-38-Exceptional-Equipment',38),('The-Forgotten-Jobs-Ordinary-Combat-Lot-19',19)]:
    folder='outputs/'+prefix
    selected=read(folder+'/selected-alternatives.json');assert len(selected)==count
    assert len({x['id'] for x in selected})==count
    assert all(x['runtime_ready'] is False and x.get('native_item_id') is None and x['native_sprite_id'] is None and x['native_palette_id'] is None and len(x['poses'])==4 for x in selected)
    for item in selected:
        assert hashlib.sha256((root/folder/'sources'/f"{item['id']}.png").read_bytes()).hexdigest()==item.get('source_sha256',item.get('sha256'))
        assert all((root/folder/p['path']).is_file() for p in item['poses'])
print(json.dumps({'integrity_files':len(manifest),'equipment_designs':271,'combat_designs':145,'proposed_views':580,'runtime_ready':False,'game_tests':'NOT_RUN'}))

completion=read('outputs/The-Forgotten-Jobs-Combat-Completion-88/review/measurements.json')
assert len(completion)==88 and all(len(x['poses'])==4 for x in completion)
converted=read('outputs/The-Forgotten-Jobs-Equipment-Native-Quality-V2/conversion-manifest.json')
assert len(converted)==145 and all(x['runtime_ready'] is False for x in converted)
