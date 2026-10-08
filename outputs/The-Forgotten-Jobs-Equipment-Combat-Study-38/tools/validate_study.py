from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote
import hashlib
import json
from PIL import Image

root=Path(__file__).resolve().parents[1]
art=root.parent/'The-Forgotten-Jobs-Equipment-Ivalice-Style-V2'
originality=root.parent/'The-Forgotten-Jobs-Equipment-Originality-Revision'
inventory={i['id']:i for i in json.loads((art/'selected-manifest.json').read_text(encoding='utf-8'))}
selected=json.loads((root/'selected-concepts.json').read_text(encoding='utf-8'))
assert len(selected)==38 and len({i['id'] for i in selected})==38
assert sum(i['category']=='Shield' for i in selected)==2
assert sum(i['rarity']=='legendary' for i in selected)==19
assert sum(i['rarity']=='unique' for i in selected)==19
assert len({i['category'] for i in selected})==19
poses=0
for i in selected:
    assert not i['runtime_ready'] and i['binding']=='UNKNOWN' and i['status']=='VISUALLY_REVIEWED_CONCEPT_ONLY'
    assert hashlib.sha256((root/i['sheet']).read_bytes()).hexdigest()==i['sha256']
    assert hashlib.sha256((art/inventory[i['id']]['image']).read_bytes()).hexdigest()==i['inventory_sha256']
    assert hashlib.sha256((root/'inventory'/f'{i["id"]}.png').read_bytes()).hexdigest()==i['inventory_sha256']
    assert len(i['poses'])==4
    for p in i['poses']:
        im=Image.open(root/p);assert im.mode=='RGBA' and im.size==(36,36);poses+=1
    assert i['original_alpha_preserved'] and i['crop_detection_alpha_threshold']==16
    assert (root/i['record']).is_file()
contracts=json.loads((root/'combat-production-plan.json').read_text(encoding='utf-8'))['items']
assert len(contracts)==271 and len({i['id'] for i in contracts})==271
assert sum(i['combat_art_status']=='CONCEPT_ONLY' for i in contracts)==38
assert all(i['runtime_item_id'] is None and i['native_sprite_id'] is None and i['native_palette_id'] is None for i in contracts)
class Links(HTMLParser):
    def __init__(self):super().__init__();self.paths=[]
    def handle_starttag(self,tag,attrs):
        for k,v in attrs:
            if k in ('href','src') and v and not v.startswith(('http:','https:','#')):self.paths.append(v)
links_checked=0
for folder,file in ((root,'index.html'),(originality/'combat-study','index.html'),(root.parent/'The-Forgotten-Jobs-Equipment-Klein-Production'/'combat-study','index.html')):
    parser=Links();parser.feed((folder/file).read_text(encoding='utf-8'))
    for p in parser.paths:assert (folder/unquote(p)).exists(),str(folder/p);links_checked+=1
source=root.parents[1]/'work/effects-reference/0002.pac_battle_wep_spr.bin'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='7a4c733e1654f9f1ff41e1281fd26fce894bd608bc1c95e1e4713aecdc0eff0a'
report=json.loads((root/'validation-report.json').read_text(encoding='utf-8'))
report.update({'selected_hashes_checked':38,'inventory_hashes_unchanged_checked':38,'preview_images_checked':poses,'legendary':19,'unique':19,'families':19,'local_links_checked':links_checked,'all_ids_unallocated':True,'native_source_unchanged':True})
(root/'validation-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report))
