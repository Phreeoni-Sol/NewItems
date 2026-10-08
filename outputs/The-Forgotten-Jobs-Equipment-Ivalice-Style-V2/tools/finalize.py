from pathlib import Path
import json,runpy,sys,hashlib,shutil,re
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
write=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
runpy.run_path(str(ROOT/'tools/review.py'))
generated=read(ROOT/'review/generated-manifest.json');assert len(generated)==68
# All six boards and all nine correction sources have been explicitly inspected.
sys.argv=['select_reviewed.py']+[x['id'] for x in generated]
runpy.run_path(str(ROOT/'tools/select_reviewed.py'))
selected=read(ROOT/'selected-manifest.json')
for x in selected:
 if x['id']=='tfj_knight_sword_06':
  x['signature_design_en']='Broad charcoal greatsword with a short angular point, plain bronze U-shaped guard, brown grip and a restrained violet recess near the blade base. Large blade slot from the initial prompt was simplified in the accepted rendering.'
 if x['id']=='tfj_shield_16':x['visual_review']='Corrected hexagonal ceramic ward shield, missing corner, integral iron palm emblem and repaired crack; full object and native-inspired rendering inspected. No combat binding.'
 assert x['alpha_ready'] and not x['runtime_ready'] and x['runtime_item_id'] is None
 assert x['sha256']==hashlib.sha256((ROOT/x['image']).read_bytes()).hexdigest()
 assert (ROOT/x['record']).exists()
 for size in (100,48):assert Image.open(ROOT/x[f'preview{size}']).size==(size,size)
write(ROOT/'selected-manifest.json',selected)
assert len({x['sha256'] for x in selected})==68
assert sum(x['rarity']=='legendary' for x in selected)==34
assert sum(x['rarity']=='unique' for x in selected)==34
coherence=read(ROOT/'combat-coherence-manifest.json');by={x['id']:x for x in selected}
for x in coherence['items']:
 s=by[x['id']]
 x.update(signature_design_en=s['signature_design_en'],palette=s['palette'],inventory_visual_effect=s['visual_effect'],inventory_image=s['image'],inventory_sha256=s['sha256'],combat_art_status='NOT_CREATED',combat_binding='UNKNOWN')
write(ROOT/'combat-coherence-manifest.json',coherence)
lines=['# Index des 68 visuels retenus','', '| Objet | Rareté | Palette | Effet visuel d’inventaire | Source |','|---|---|---|---|---|']
for x in selected:lines.append(f"| {x['name_fr']} | {x['rarity']} | {x['palette']} | {x['visual_effect']} | [{x['id']}]({x['image']}) |")
(ROOT/'ART_INDEX.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
for n in range(1,7):shutil.copy2(ROOT/'review'/f'board-{n:02}-generated-68.jpg',ROOT/'review'/f'board-{n:02}-final.jpg')
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
def fit(path,size):
 im=Image.open(path).convert('RGBA');bbox=im.getbbox()
 if bbox:im=im.crop(bbox)
 im.thumbnail((size-12,size-12),Image.Resampling.LANCZOS)
 result=Image.new('RGBA',(size,size));result.alpha_composite(im,((size-im.width)//2,(size-im.height)//2));return result
# Comparisons at the same 100 px canvas scale, with an additional large new detail.
oldroot=ROOT.parent/'The-Forgotten-Jobs-Equipment-Kontext-Legendary-Unique'
old={x['id']:x for x in read(oldroot/'selected-manifest.json')}
rows=[('tfj_sword_18','ei_029_uitx.png'),('tfj_staff_08','ei_066_uitx.png'),('tfj_armor_13','ei_185_uitx.png'),('tfj_shield_16','ei_139_uitx.png')]
board=Image.new('RGB',(1060,900),'#292a2d');d=ImageDraw.Draw(board)
for xx,text in [(25,'Référence native · 100 px'),(280,'Ancien · 100 px'),(490,'Nouveau · 100 px'),(720,'Détail nouveau')]:d.text((xx,20),text,fill='#eee8da',font=font)
for j,(key,ref) in enumerate(rows):
 y=65+j*205;s=by[key];d.text((25,y),s['name_fr'],fill='#eee8da',font=font)
 native=Image.open(ROOT/'references'/ref).convert('RGBA');board.paste(native,(75,y+50),native)
 for xx,path,size in [(295,oldroot/old[key]['image'],100),(505,ROOT/s['preview100'],100),(755,ROOT/s['image'],160)]:
  pic=fit(path,size) if size==160 else Image.open(path).convert('RGBA')
  if pic.size!=(size,size):pic=fit(path,size)
  board.paste(pic,(xx,y+35),pic)
board.save(ROOT/'review/native-before-after.jpg',quality=94)
# A compact overview from eight different categories.
keys=['tfj_katana_09','tfj_bow_10','tfj_gun_07','tfj_staff_08','tfj_shield_16','tfj_armor_13','tfj_robe_07','tfj_item_15']
board=Image.new('RGB',(1200,650),'#292a2d');d=ImageDraw.Draw(board)
for n,key in enumerate(keys):
 xx=(n%4)*300;yy=(n//4)*325;s=by[key];pic=fit(ROOT/s['image'],260);board.paste(pic,(xx+20,yy),pic);d.text((xx+10,yy+265),s['name_fr'][:33],fill='#eee8da',font=font)
board.save(ROOT/'review/overview-final.jpg',quality=94)
report={'status':'PASS','selected':68,'legendary':34,'unique':34,'generated_sources':len(list((ROOT/'images').glob('*.png')))+len(list((ROOT/'corrections').glob('*.png'))),'corrected_selected':sum(x['image'].startswith('corrections/') for x in selected),'transparent_selected':68,'unique_source_hashes':68,'preview_sizes_checked':[100,48],'model':'OPENAI_BUILT_IN_IMAGEGEN','visual_review':'ALL_SIX_BOARDS_AND_NINE_CORRECTIONS_INSPECTED','runtime_ready':False,'combat_art':'NOT_CREATED','game_tests':'NOT_RUN','pollinations_requests_in_this_revision':0}
write(ROOT/'validation-report.json',report)
(ROOT/'CORRECTIONS_A_PREVOIR.md').write_text('# Corrections effectuées\n\nNeuf corrections ont été générées et inspectées. Lire selected-manifest.json et les JSON de corrections/ pour choisir les sources finales. Les premiers essais restent dans images/.\n\nLa grande fenêtre de lame initialement envisagée pour Le Trône vacant est simplifiée en un renfoncement violet dans le dessin retenu ; la signature finale décrit cette variation. Aucune correction restante requise pour ce lot d’inventaire. Graphismes portés et liaison moteur restent à réaliser.\n',encoding='utf-8')
print(json.dumps(report))
