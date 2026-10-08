from pathlib import Path
from html.parser import HTMLParser
import hashlib, json
from PIL import Image
root=Path(__file__).resolve().parents[1]
class Links(HTMLParser):
    count=0
    def handle_starttag(self,tag,attrs):
        for key,value in attrs:
            if key in ('href','src') and value and not value.startswith(('http','#')):
                assert (root/value).exists(),value
                self.count+=1
p=Links();p.feed((root/'index.html').read_text(encoding='utf8'))
rows=json.loads((root/'adaptation-contracts-38.json').read_text(encoding='utf8'))
assert len(rows)==38 and len({r['id'] for r in rows})==38
for row in rows:
    assert not row['runtime_ready']
    assert row['native_sprite_id'] is None and row['native_palette_id'] is None and row['native_sequence_id'] is None
    for pose in row['preview_measurements']:
        path=root/pose['preview']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==pose['sha256']
        im=Image.open(path)
        assert im.mode=='RGBA' and im.size==(36,36)
report=json.loads((root/'validation.json').read_text(encoding='utf8'))
report['local_html_links_verified']=p.count
(root/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('PASS: 38 contracts, 152 unchanged previews, unallocated IDs;',p.count,'local links')
