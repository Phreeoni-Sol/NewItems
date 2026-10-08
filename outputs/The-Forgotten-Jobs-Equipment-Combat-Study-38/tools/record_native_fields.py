"""Record observed reference values; do not resolve them to atlas rectangles."""
from pathlib import Path
import csv
import hashlib
import json
import xml.etree.ElementTree as ET

root=Path(__file__).resolve().parents[1]
reference=root.parent/'The-Forgotten-Jobs-Equipment-Originality-Revision/references'
table=reference/'baseline-tables/ItemData.xml'
inventory={int(i['id']):i for i in csv.DictReader((reference/'baseline-inventory.csv').open(encoding='utf-8-sig',newline=''))}
items=[]
for item in ET.fromstring(table.read_bytes()).findall('./Entries/Item'):
    key=int(item.findtext('Id'))
    items.append({'reference_item_id':key,'name_en':inventory.get(key,{}).get('name_en'),'category':item.findtext('ItemCategory'),'SpriteID':int(item.findtext('SpriteID')),'Palette':int(item.findtext('Palette')),'runtime_binding':'UNKNOWN','atlas_rectangle':'UNKNOWN','shape_sequence':'UNKNOWN'})
assert len(items)==261 and len({i['reference_item_id'] for i in items})==261
data={'source':str(table.relative_to(root.parents[1])),'source_sha256':hashlib.sha256(table.read_bytes()).hexdigest(),'evidence':'Values read from the local modloader reference XML, not a live engine capture. XML notes that the nex Item table may override properties. Model Item.cs exposes nullable fields; runtime consumer and Enhanced mapping not traced.','new_ids_allocated':False,'items':items}
(root/'native-item-visual-fields.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'reference_rows':len(items),'new_ids_allocated':False}))
