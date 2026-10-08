from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
design=json.loads((ROOT.parent/'The-Forgotten-Jobs-Equipment-Originality-Revision/items.json').read_text(encoding='utf-8-sig'))
old=[{k:x[k] for k in ('id','name_fr','category','rarity')} for x in design['items'] if x['rarity'] in ('legendary','unique')]
motifs={}
for line in (ROOT/'motifs.txt').read_text(encoding='utf-8-sig').splitlines():
 key,shape,palette,effect=line.split('|');assert key not in motifs
 motifs[key]=(shape,palette,effect)
assert set(motifs)=={x['id'] for x in old} and len(motifs)==68
style=' Match the supplied actual FFT The Ivalice Chronicles Enhanced native inventory icon strictly as a rendering-style and scale reference, do not copy its design. Small delicate hand-painted fantasy equipment icon, softly broken textured edges, subdued mineral colors, restrained low-contrast shading, clear compact masses with a few tiny worn details. No glossy luxury product render, thick cartoon outline, overdecorated gold cathedral filigree, tiny inscriptions, scene, text, frames, pedestals, mannequin or person. Not uniformly rusted: show the materials appropriate to this specific item. Exactly one complete isolated object, or one coherent wearable pair only when explicitly specified. Genuine transparent background with safe margins. Legible at 100x100; do not claim game-ready dimensions or battle sprite readiness. Long weapons shown diagonally upper left tip to lower right grip. Unworn garments have empty neck and arm openings; no head, hands or legs. Visual effects are restrained close to the object, never a full screen aura. Avoid repeating shapes from other categories.'
refs=ROOT/'references'
plan=[]
for item in old:
 shape,palette,effect=motifs[item['id']]
 if item['category'] in ['Armor','Clothing','Robe','Helmet','Hat','Cloak','Shoes','Armguard']:ref='ei_185_uitx.png'
 elif item['category']=='Shield':ref='ei_139_uitx.png'
 elif item['category'] in ['Staff','Rod','Book','Perfume','Item','Ring','Armlet','HairAdornment','Instrument','Bag','Cloth']:ref='ei_066_uitx.png'
 else:ref='ei_029_uitx.png'
 prompt=f"Create a NEW ORIGINAL {item['rarity']} {item['category']} inventory icon for FFT The Ivalice Chronicles: {item['name_fr']}. Individual design: {shape} Specific palette: {palette}. Localized visual effect: {effect}. Make the exceptional identity apparent from silhouette and this material/visual signature, not more random jewelry."+style
 plan.append({**{k:item[k] for k in ['id','name_fr','category','rarity']},'signature_design_en':shape,'palette':palette,'visual_effect':effect,'prompt':prompt,'reference':str((refs/ref).resolve()),'model':'OPENAI_BUILT_IN_IMAGEGEN','runtime_ready':False,'runtime_item_id':None,'combat_representation_status':'NOT_CREATED_BINDING_UNKNOWN'})
(ROOT/'production-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
# Repair the saved source path from output_hint's human-readable text.
for record in (ROOT/'records').glob('*.json'):
 data=json.loads(record.read_text(encoding='utf-8-sig'))
 if ' as ' in data.get('source',''):data['source']=data['source'].split(' as ',1)[1]
 record.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'designs':len(plan),'palette_signatures':len({x['palette'] for x in plan}),'no_runtime_bindings':True}))
