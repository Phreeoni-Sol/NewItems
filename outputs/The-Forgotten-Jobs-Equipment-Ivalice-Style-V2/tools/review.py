"""Build faithful previews and review sheets; never claims engine readiness."""
import json, hashlib, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT.parent
plan=json.loads((ROOT/'production-plan.json').read_text(encoding='utf-8-sig'))
oldroot=OUT/'The-Forgotten-Jobs-Equipment-Kontext-Legendary-Unique'
old={x['id']:x for x in json.loads((oldroot/'selected-manifest.json').read_text(encoding='utf-8-sig'))}
for folder in ('previews100','previews48','review'):(ROOT/folder).mkdir(exist_ok=True)
try:font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
except OSError:font=ImageFont.load_default()
manifest=[]
def fit(path,size):
 im=Image.open(path).convert('RGBA');box=im.getbbox()
 if box:im=im.crop(box)
 im.thumbnail((size-12,size-12),Image.Resampling.LANCZOS)
 result=Image.new('RGBA',(size,size));result.alpha_composite(im,((size-im.width)//2,(size-im.height)//2))
 return result
for item in plan:
 path=ROOT/'images'/f"{item['id']}.png"
 correction=ROOT/'corrections'/path.name
 if correction.exists():
  path=correction
  record=json.loads(path.with_suffix('.json').read_text(encoding='utf-8-sig'))
  item={**item,**{k:record[k] for k in ('signature_design_en','palette','visual_effect') if k in record}}
 if not path.exists():continue
 im=Image.open(path); alpha=im.getextrema()[-1] if im.mode=='RGBA' else None
 for size in (100,48):fit(path,size).save(ROOT/f'previews{size}'/path.name)
 manifest.append({**{k:item[k] for k in ('id','name_fr','category','rarity','model','signature_design_en','palette','visual_effect')},
  'source_pack':ROOT.name,'image':path.relative_to(ROOT).as_posix(),'preview100':f'previews100/{path.name}',
  'preview48':f'previews48/{path.name}','record':f"{'corrections' if correction.exists() else 'records'}/{item['id']}.json",
  'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'mode':im.mode,'size':list(im.size),
  'alpha_ready':bool(alpha and alpha[0]==0 and alpha[1]==255),'runtime_ready':False,
  'runtime_item_id':None,'status':'GENERATED_AUTHORING_REQUIRES_VISUAL_REVIEW'})
# Only write a selected manifest after the complete set has been reviewed manually.
(ROOT/'review/generated-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
for start in range(0,len(manifest),12):
 batch=manifest[start:start+12]; board=Image.new('RGB',(1200,math.ceil(len(batch)/4)*310),(242,237,225));draw=ImageDraw.Draw(board)
 for j,item in enumerate(batch):
  x=(j%4)*300;y=(j//4)*310
  board.paste(fit(ROOT/item['image'],260),(x+20,y),fit(ROOT/item['image'],260))
  draw.text((x+10,y+260),item['name_fr'][:34],fill='#251e1c',font=font)
  draw.text((x+10,y+285),item['id']+' · '+item['rarity'],fill='#64513b',font=font)
 board.save(ROOT/'review'/f'board-{start//12+1:02}-generated-{len(manifest):02}.jpg',quality=93)
# Side-by-side originals and redesigns, with an actual 48 px readability sample.
keys=['tfj_sword_18','tfj_knife_09','tfj_armor_14','tfj_shield_16','tfj_bow_10','tfj_ring_07']
shown=[x for x in manifest if x['id'] in keys]
if shown:
 board=Image.new('RGB',(900,len(shown)*260),(242,237,225));draw=ImageDraw.Draw(board)
 for j,item in enumerate(shown):
  y=j*260; key=item['id']; before=oldroot/old[key]['image']
  draw.text((10,y+8),item['name_fr'],fill='#251e1c',font=font)
  for x,path,label in [(20,before,'Ancien'),(330,ROOT/item['image'],'Prestige')]:
   im=fit(path,220);board.paste(im,(x,y+35),im);draw.text((x+220,y+100),label,fill='#64513b',font=font)
  small=Image.open(ROOT/item['preview48']);board.paste(small,(790,y+95),small)
  draw.text((735,y+155),'48 px : inventaire',fill='#64513b',font=font)
 board.save(ROOT/'review/comparison.jpg',quality=94)
print(json.dumps({'generated':len(manifest),'planned':len(plan),'transparent':sum(x['alpha_ready'] for x in manifest)}))
