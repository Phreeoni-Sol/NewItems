from pathlib import Path
import json,hashlib,shutil
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[1];project=root.parents[1]
old=project/'outputs/The-Forgotten-Jobs-Ordinary-Combat-Lot-19'
all_items=json.loads((old/'ordinary-107-plan.json').read_text(encoding='utf8'))
items=[x for x in all_items if x['combat_art_status']=='NOT_CREATED'];assert len(items)==88
for folder in ('inventory','sources','records','review','references','corrections','rejected'):(root/folder).mkdir(exist_ok=True)
for item in items:
    source=project/item['inventory_source']
    assert hashlib.sha256(source.read_bytes()).hexdigest()==item['inventory_sha256']
    shutil.copy2(source,root/'inventory'/f"{item['id']}.png")
    item['prompt']=f"""Create a new original combat equipment pixel-art sheet for The Forgotten Jobs / Final Fantasy Tactics: {item['name']} ({item['category']}). Image 1 is the selected inventory design: faithfully preserve its physical silhouette, materials, color accents, ornament placement and distinguishing features. Image 2 is a native historical FFT weapon atlas, for style only, not a source of replacement objects.
Make FOUR consistent views of this SAME object in a clean 2x2 grid with generous EMPTY transparent center gutters and margins: diagonal left, diagonal right, near-front, near-back or side. Back-facing structure can be a conservative design proposal. Design each sprite for legibility around 56 logical pixels in height or width, with chunky square pixel clusters and hard opaque interiors. These are authoring sizes, not assertions about engine limits. Small muted palette, two or three shades per material, strong continuous silhouette. Keep slender shafts and handles robust; bow strings and crossbow strings must be solid continuous lines; flail chains must connect handle to weight. Keep all parts physically attached. Preserve exactly the inventory identity, do not copy the white background or painterly texture. No labels, frames, text, hands, characters, particles, glowing haze, detached sparks, shadows, gradients, checkerboard, antialiased illustration or glossy 3D. Real transparent exterior. Four artistic views, not a claimed native animation."""
for start in range(0,88,8):
    board=Image.new('RGB',(1600,900),(34,32,28));draw=ImageDraw.Draw(board)
    for j,item in enumerate(items[start:start+8]):
        x=(j%4)*400;y=(j//4)*450
        draw.text((x+8,y+8),item['id']+' / '+item['name'],fill='white')
        im=Image.open(root/'inventory'/f"{item['id']}.png").convert('RGB');im.thumbnail((380,390))
        board.paste(im,(x+10,y+42))
    board.save(root/f'review/inventory-{start//8+1:02d}.jpg')
shutil.copy2(old/'references/weapon-palette-03.png',root/'references/weapon-palette-03.png')
(root/'generation-plan.json').write_text(json.dumps({'tool':'OpenAI built-in imagegen','runtime_ready':False,'items':items},ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'remaining':len(items),'inventory_sha_verified':len(items),'boards':11}))
