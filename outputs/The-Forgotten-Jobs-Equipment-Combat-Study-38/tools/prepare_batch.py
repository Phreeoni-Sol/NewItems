from pathlib import Path
import json
from PIL import Image, ImageDraw

root=Path(__file__).resolve().parents[1]
art=root.parent/'The-Forgotten-Jobs-Equipment-Ivalice-Style-V2'
design=json.loads((root.parent/'The-Forgotten-Jobs-Equipment-Originality-Revision/items.json').read_text(encoding='utf-8'))['items']
ids={i['id'] for i in design if i['family']=='weapon' or i['category']=='Shield'}
selected=[i for i in json.loads((art/'selected-manifest.json').read_text(encoding='utf-8')) if i['id'] in ids]
assert len(selected)==38
original={'tfj_sword_18':'tfj_sword_18.png','tfj_bow_10':'tfj_bow_10-v2.png','tfj_gun_07':'tfj_gun_07-v3.png'}
choices={i['id']:original.get(i['id'],i['id']+'.png') for i in selected}
(root/'choices.json').write_text(json.dumps(choices,indent=2)+'\n',encoding='utf-8')
plans=[]
for i in selected:
    if i['id'] in original:continue
    category=i['category']
    layout='top left up-left profile, top right opposite up-right profile, bottom left horizontal toward left, bottom right horizontal toward right'
    rules='Keep exactly the same design and proportions in each pose. No sheath, hand, extra weapon or disconnected ornaments.'
    if category=='Shield':
        layout='top left front face, top right back face with functional hand grip and straps, bottom left front face angled slightly left, bottom right front face angled slightly right'
        rules='Preserve the unique front emblem, crack or missing corner; reverse shows plausible straps as author design, not a native layout claim.'
    elif category=='Bow':
        layout='top left upright bow leaning left, top right upright bow leaning right, bottom left oblique leaning left, bottom right oblique leaning right'
        rules='This is a TRUE longbow, no stock/crossbar/arrow. One straight continuous bowstring with a thick readable pixel line (roughly 20 source pixels on a 1254-pixel sheet), clear gap to wood. Preserve upper/lower limb asymmetry.'
    elif category=='Crossbow':rules='This is a medieval CROSSBOW with recognizable stock, transverse limbs and ONE taut string. No loose bolt or modern rifle. String must survive miniature reduction.'
    elif category=='Instrument':rules='Preserve instrument silhouette and a few thick readable straight string clusters; no sword, harp strings not floating decoration.'
    elif category=='Book':rules='One CLOSED book per pose, preserve cover motif, spine, clasp and bookmark, no open pages or floating paper.'
    elif category=='Bag':rules='One bag per pose, preserve flap, clasp and carrying loop. No duplicate strap object or weapon.'
    elif category=='Cloth':rules='One physically continuous textile per pose. Preserve color/border/seam, coherent folded form, no detached scraps or particle ribbons.'
    elif category=='Flail':rules='One connected flail per pose, one striking head, short thick readable chain and one handle. Never change the head into a mace ball.'
    prompt=('Use-case: game-asset. Generate a TRANSPARENT authoring concept sheet for ONE new FFT equipment design, in a clean 2 by 2 grid of four separated views with generous fully empty gutters (at least 12 percent horizontal and vertical). First reference is the inventory icon: preserve this object signature and colors. Second reference is the extracted native FFT pixel weapon bank: use its restrained readable chunky pixel clusters, not its layout or whole atlas. Equipment family '+category+'. Signature: '+i['signature_design_en']+' Palette: '+i['palette']+'. Proposed view layout: '+layout+'. '+rules+' Redraw as small classic FFT battle equipment sprites enlarged with nearest-neighbour appearance; coarse clearly stepped edges, sparse muted color clusters, simplified ornament and strong silhouette. Opaque equipment pixels within, alpha zero everywhere outside. No painterly texture, smooth detailed illustration, text, grid lines, labels, checkerboard backdrop, diffuse lighting, shadows, haze, halo or glow. Even if the icon has a magical effect, OMIT every effect cloud/particle; effects need separate validated layers. Four proposals of SAME item, not four different items. This is authoring study only, NOT a native atlas or proven animation. Keep all views away from canvas edges and each other.')
    plans.append({'id':i['id'],'name_fr':i['name_fr'],'category':category,'image':str((art/i['image']).resolve()),'native_ref':str((root/'references/weapon-palette-03.png').resolve()),'prompt':prompt})
(root/'production-plan.json').write_text(json.dumps(plans,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(root/'review').mkdir(exist_ok=True)
for page in range(0,len(plans),12):
    board=Image.new('RGB',(1000,750),(35,37,42));d=ImageDraw.Draw(board)
    for n,i in enumerate(plans[page:page+12]):
        x,y=(n%4)*250,(n//4)*250
        im=Image.open(i['image']).convert('RGBA');im.thumbnail((200,190))
        board.paste(im,(x+20,y+12),im);d.text((x+8,y+205),i['id'],fill='white');d.text((x+8,y+224),i['name_fr'],fill='#dfca9b')
    board.save(root/'review'/f'inventory-inputs-{page//12+1:02}.jpg')
print(json.dumps({'target':len(selected),'existing':len(original),'new':len(plans)}))
