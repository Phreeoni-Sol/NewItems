from pathlib import Path
from PIL import Image
import json,hashlib,re
root=Path('outputs/The-Forgotten-Jobs-Equipment-Klein-Production');plan=json.loads((root/'production-plan.json').read_text(encoding='utf-8'));pilot=set(json.loads((root/'pilot-ids.json').read_text()));issues=json.loads((root/'visual-issues.json').read_text(encoding='utf-8-sig'));fixids={i['id'] for i in issues};selected=[]
for item in plan:
 id=item['id'];folder='corrections-last' if id=='tfj_polearm_01' else ('corrections' if id in fixids else '')
 prefix=folder+'/' if folder else '';img=prefix+'images/'+id+'.png';record_path=root/(prefix+'records/'+id+'.json');r=json.loads(record_path.read_text(encoding='utf-8'))
 with Image.open(root/img) as im:im.load();assert min(im.size)>0;size=list(im.size);mode=im.mode
 assert hashlib.sha256((root/img).read_bytes()).hexdigest()==r['sha256'];assert item['rarity'] not in ['legendary','unique']
 selected.append(dict(id=id,name_fr=item['name_fr'],category=item['category'],rarity=item['rarity'],image=img,preview100=prefix+'previews100/'+id+'.png',preview48=prefix+'previews48/'+id+'.png',record=prefix+'records/'+id+'.json',sha256=r['sha256'],size=size,mode=mode,alpha_ready=False,runtime_ready=False,runtime_item_id=None,status='SELECTED_AUTHORING_PROPOSAL',visual_review='Contact-sheet inspection at 100 px; major duplicated/incomplete shapes corrected. Full style fidelity and in-game review remain pending.'))
 # Preserve the actual first-pass prompt used before the blade instruction was strengthened.
 original_record=root/'records'/(id+'.json');original=json.loads(original_record.read_text(encoding='utf-8'));actual=item['prompt']
 if id in pilot and item['category'] in ['Knife','Sword','KnightSword','Katana','NinjaBlade']:actual=actual.replace(' Show only ONE unsheathed weapon: absolutely no scabbard, sheath, carrying case, second grip, second blade, floating extra handle or crossed objects.','')
 original['prompt']=actual;original_record.write_text(json.dumps(original,ensure_ascii=False,indent=2),encoding='utf-8')
assert len(selected)==203
(root/'selected-manifest.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2),encoding='utf-8')
for issue in issues:issue['status']='MAJOR_SHAPE_CORRECTED_IN_SELECTED_VARIANT';issue['selected_image']=next(i['image'] for i in selected if i['id']==issue['id'])
(root/'visual-issues.json').write_text(json.dumps(issues,ensure_ascii=False,indent=2),encoding='utf-8')
p=root/'tools/make_catalogue.py';s=p.read_text(encoding='utf-8-sig');s=s.replace('records={}','records={}\nselection={r[\'id\']:r for r in json.loads((root/\'selected-manifest.json\').read_text(encoding=\'utf-8\'))} if (root/\'selected-manifest.json\').exists() else {}')
s=s.replace("Image.open(root/'previews100'/(item['id']+'.png'))","Image.open(root/selection.get(item['id'],{}).get('preview100','previews100/'+item['id']+'.png'))")
s=s.replace("id=item['id'];generated=", "id=item['id'];image_url=selection.get(id,{}).get('image','images/'+id+'.png');preview_url=selection.get(id,{}).get('preview100','previews100/'+id+'.png');generated=")
s=s.replace('images/{id}.png','{image_url}').replace('previews100/{id}.png','{preview_url}')
p.write_text(s,encoding='utf-8')
# Copy extraction provenance for all native reference files used in this batch.
source=Path('outputs/The-Forgotten-Jobs-Equipment-Enhanced-Revision/references/extraction-provenance.json');refs=json.loads(source.read_text(encoding='utf-8-sig'));nativeids={int(Path(i['reference']).name.split('_')[1]) for i in plan};(root/'references/native-provenance.json').write_text(json.dumps([r for r in refs if r['item_id_reference'] in nativeids],indent=2),encoding='utf-8')
print('Selected',len(selected),'objects;',len(fixids),'corrected objects; reserved excluded; PNG checks and SHA256 verified.')
