from pathlib import Path
from collections import Counter
import json,hashlib,shutil
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[1]
base=next(p for p in root.parents if (p/'work/upstream').is_dir())
klein=base/'outputs/The-Forgotten-Jobs-Equipment-Klein-Production'
selected=json.loads((klein/'selected-manifest.json').read_text(encoding='utf8'))
intent={x['id']:x['visual_intent'] for x in json.loads((klein/'production-plan.json').read_text(encoding='utf8'))}
families={x['category'] for x in json.loads((base/'outputs/The-Forgotten-Jobs-Retouch-38-Exceptional-Equipment/selected-alternatives.json').read_text(encoding='utf8'))}
ordinary=[x for x in selected if x['category'] in families]
assert len(ordinary)==107
(root/'inventory').mkdir(exist_ok=True)
(root/'review').mkdir(exist_ok=True)
(root/'references').mkdir(exist_ok=True)
plan=[]
for item in ordinary:
    source=klein/item['image'];assert hashlib.sha256(source.read_bytes()).hexdigest()==item['sha256']
    im=Image.open(source).convert('RGB')
    # Analysis only. Ignore near-white backdrop and tally rough RGB bins without editing the asset.
    colors=Counter(tuple((c//16)*16 for c in p) for p in im.get_flattened_data() if min(p)<220)
    plan.append(dict(id=item['id'],name=item['name_fr'],category=item['category'],rarity=item['rarity'],inventory_source=str(source.relative_to(base)),inventory_sha256=item['sha256'],design_intent_from_existing_plan=intent[item['id']],diagnostic_dominant_rgb_bins=[list(c) for c,n in colors.most_common(6)],rgb_bins_are_native_palette=False,signature_status='TO_VERIFY_ON_SELECTED_ICON',combat_art_status='NOT_CREATED',runtime_ready=False,native_item_id=None,native_sprite_id=None,native_palette_id=None,hand_anchor='UNKNOWN'))
chosen=[];seen=set()
for item in plan:
    if item['category'] in seen:continue
    preferred={'Sword':'tfj_sword_03','Staff':'tfj_staff_02'}.get(item['category'])
    pick=next((x for x in plan if x['id']==preferred),item)
    chosen.append(pick);seen.add(item['category'])
assert len(chosen)==19
for item in chosen:
    shutil.copy2(base/item['inventory_source'],root/'inventory'/f"{item['id']}.png")
for start in range(0,len(chosen),4):
    board=Image.new('RGB',(1080,1160),(36,34,30));draw=ImageDraw.Draw(board)
    for i,item in enumerate(chosen[start:start+4]):
        x=(i%2)*540;y=(i//2)*580
        draw.text((x+14,y+10),item['id']+' / '+item['name'],fill='white')
        im=Image.open(root/'inventory'/f"{item['id']}.png").convert('RGB');im.thumbnail((500,500),Image.Resampling.LANCZOS)
        board.paste(im,(x+18,y+44))
    board.save(root/f'review/inventory-{start//4+1:02d}.jpg')
shutil.copy2(base/'outputs/The-Forgotten-Jobs-Retouch-38-Exceptional-Equipment/references/weapon-palette-03.png',root/'references/weapon-palette-03.png')
(root/'ordinary-107-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf8')
(root/'production-plan.json').write_text(json.dumps(chosen,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'ordinary_inventory_sha_verified':107,'pilot_families':19,'source_contacts':5}))
