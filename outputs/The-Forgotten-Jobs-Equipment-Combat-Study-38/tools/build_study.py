from pathlib import Path
import hashlib
import html
import json
import shutil
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT.parent
ART = OUTPUTS / 'The-Forgotten-Jobs-Equipment-Ivalice-Style-V2'
REVISION = OUTPUTS / 'The-Forgotten-Jobs-Equipment-Originality-Revision'
GALLERY = OUTPUTS / 'The-Forgotten-Jobs-Equipment-Klein-Production'
selected = {i['id']:i for i in json.loads((ART/'selected-manifest.json').read_text(encoding='utf-8'))}
items = json.loads((REVISION/'items.json').read_text(encoding='utf-8'))['items']
choices = json.loads((ROOT/'choices-reviewed.json').read_text(encoding='utf-8'))
assert len(choices)==38, 'Complete visual review required before publishing this lot'
for folder in ('inventory','poses','review'):
    (ROOT/folder).mkdir(exist_ok=True)
manifest=[]
parts=['''<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FFT — études des armes équipées</title><style>body{background:#23252a;color:#eee9df;font:16px/1.5 system-ui;max-width:1150px;margin:auto;padding:20px}a{color:#b6d4ef}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:18px}.card{background:#303239;border:1px solid #646670;border-radius:8px;padding:15px}img{max-width:100%}.inventory{width:100px;height:100px;object-fit:contain}.pixel{image-rendering:pixelated;width:144px;height:144px}.poses{display:grid;grid-template-columns:1fr 1fr;gap:6px}h1,h2{color:#dbbe87}small{color:#b9c1cf}summary{cursor:pointer}</style></head><body><h1>Armes équipées — trois études</h1><p>Silhouette et palette des nouvelles icônes, simplifiées pour examiner leur lisibilité en combat. Les quatre vues sont des propositions graphiques, pas des orientations ou animations natives validées.</p><p><a href="../catalogue.html">Retour au catalogue</a> · <a href="CLAUDE_COMBAT_HANDOFF.md">Dossier Claude</a> · <a href="combat-production-plan.json">Plan des 271 objets</a></p><p>Aperçus d’auteur à 36 × 36 pixels, agrandis sans lissage. Taille choisie pour cette étude ; format moteur et pivots encore UNKNOWN. Aucun test en jeu.</p><div class="grid">''']
overview=Image.new('RGB',(1280,3000),(35,37,42)); draw=ImageDraw.Draw(overview)
for n,(key,filename) in enumerate(choices.items()):
    info=selected[key]
    source=ROOT/'concepts'/filename
    image=Image.open(source).convert('RGBA')
    alpha_extrema=image.getchannel('A').getextrema()
    assert alpha_extrema[0]==0 and alpha_extrema[1]>=240,filename
    # Locate actual clear gutters; the generator does not guarantee equal cells.
    # Threshold is for geometry detection only, original alpha is preserved.
    w,h=image.size
    mask=image.getchannel('A').point(lambda a:255 if a>16 else 0)
    split_x=min(range(w*35//100,w*65//100),key=lambda x:sum(mask.crop((x,0,x+1,h)).get_flattened_data()))
    split_y=min(range(h*35//100,h*65//100),key=lambda y:sum(mask.crop((0,y,w,y+1)).get_flattened_data()))
    assert mask.crop((split_x,0,split_x+1,h)).getbbox() is None,filename+' x gutter'
    assert mask.crop((0,split_y,w,split_y+1)).getbbox() is None,filename+' y gutter'
    shutil.copy2(ART/info['image'],ROOT/'inventory'/f'{key}.png')
    record=source.with_suffix('.json')
    meta=json.loads(record.read_text(encoding='utf-8'))
    meta['status']='VISUALLY_REVIEWED_CONCEPT_ONLY'
    meta['review']='Source and miniature previews inspected against the inventory icon: separated views, recognizable family, dominant palette and main signature retained. Fine details simplified. Mirrored profiles are author proposals, not proven native directions. Shield backs are author designs. Hand anchors, indexed palette and timing are not validated.'
    if key=='tfj_bow_09':meta['review']+=' v2 selected after lightening the string for contrast on dark backgrounds.'
    record.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    pose_paths=[]
    for p,(left,top,right,bottom) in enumerate(((0,0,split_x,split_y),(split_x,0,w,split_y),(0,split_y,split_x,h),(split_x,split_y,w,h))):
        cell=image.crop((left,top,right,bottom));box=cell.getchannel('A').point(lambda a:255 if a>16 else 0).getbbox();assert box
        crop=cell.crop(box);crop.save(ROOT/'poses'/f'{key}-{p+1}-source.png')
        small=crop.copy();small.thumbnail((32,32),Image.Resampling.NEAREST)
        canvas=Image.new('RGBA',(36,36));canvas.alpha_composite(small,((36-small.width)//2,(36-small.height)//2))
        path=ROOT/'poses'/f'{key}-{p+1}-preview36.png';canvas.save(path);pose_paths.append(path.relative_to(ROOT).as_posix())
    colors=len(image.getcolors(w*h) or [])
    manifest.append({'id':key,'name_fr':info['name_fr'],'category':info['category'],'rarity':info['rarity'],'sheet':source.relative_to(ROOT).as_posix(),'record':record.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'inventory_sha256':info['sha256'],'signature':info['signature_design_en'],'palette':info['palette'],'poses':pose_paths,'sheet_size':image.size,'split_xy':[split_x,split_y],'crop_detection_alpha_threshold':16,'original_alpha_preserved':True,'distinct_rgba_colors':colors,'alpha_extrema':alpha_extrema,'status':'VISUALLY_REVIEWED_CONCEPT_ONLY','runtime_ready':False,'binding':'UNKNOWN','anchor':'UNKNOWN','native_frame_mapping':'UNKNOWN','effects_layer':'NOT_CREATED'})
    parts.append(f'<article class="card"><h2>{html.escape(info["name_fr"])}</h2><img class="inventory" src="inventory/{key}.png" alt="Icône {html.escape(info["name_fr"])}"><p>{html.escape(info["palette"])}</p><div class="poses">'+''.join(f'<div><img class="pixel" src="{p}" alt="Vue proposée {i+1}"><br><small>Vue proposée {i+1}</small></div>' for i,p in enumerate(pose_paths))+'</div>'+f'<p><a href="{source.relative_to(ROOT).as_posix()}">Planche complète</a> · <a href="{record.relative_to(ROOT).as_posix()}">Prompt et provenance</a></p><small>Étude contrôlée visuellement. Palette indexée, points d’attache et liaison moteur à valider.</small></article>')
    x=(n%4)*320;y=(n//4)*300
    draw.text((x+12,y+8),info['name_fr'],fill='white')
    icon=Image.open(ROOT/'inventory'/f'{key}.png').convert('RGBA');icon.thumbnail((100,100))
    overview.paste(icon,(x+8,y+35),icon)
    for p,path in enumerate(pose_paths):
        small=Image.open(ROOT/path).resize((90,90),Image.Resampling.NEAREST)
        overview.paste(small,(x+116+(p%2)*96,y+45+(p//2)*100),small)
draw.text((10,2980),'ETUDES / 36 px auteur / aucun test en jeu / format natif UNKNOWN',fill='#d5bf91')
overview.save(ROOT/'review/all-38-equipment-studies.jpg')
parts.append('''</div><h2>Référence extraite du jeu</h2><p>Banque d’armes décodée avec l’interprétation historique FFT : 256 × 256, 16 palettes. Les octets et la taille passent un aller-retour exact. Cela ne prouve ni le rendu Enhanced ni la liaison des nouveaux objets.</p><a href="references/weapon-palette-board.jpg"><img width="512" src="references/weapon-palette-03.png" style="image-rendering:pixelated" alt="Banque native, interprétation historique palette 3"></a><p><a href="weapon-bank-report.json">Rapport de décodage</a></p></body></html>''')
page=''.join(parts).replace('Armes équipées — trois études','Armes et boucliers — 38 études').replace('href="../catalogue.html"','href="../The-Forgotten-Jobs-Equipment-Originality-Revision/catalogue.html"')
page=page.replace('<div class="grid">','<label>Rechercher une pièce : <input id="query" placeholder="Nom de l’arme ou du bouclier…" style="font:inherit;padding:8px;margin:12px"></label><span id="count">38 / 38</span><div class="grid">',1)
page=page.replace('</body>','<script>const cards=[...document.querySelectorAll(".card")],q=document.getElementById("query");q.addEventListener("input",()=>{let n=0;for(const c of cards){c.hidden=!c.querySelector("h2").textContent.toLowerCase().includes(q.value.toLowerCase());if(!c.hidden)n++}document.getElementById("count").textContent=n+" / 38"});</script></body>')
page=page.replace('.card{','.card[hidden]{display:none}.card{',1)
(ROOT/'index.html').write_text(page,encoding='utf-8')
(ROOT/'selected-concepts.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
contracts=[]
for i in items:
    weapon=i['family']=='weapon' or i['category']=='Shield'
    s=selected.get(i['id'])
    contracts.append({'id':i['id'],'name_fr':i['name_fr'],'category':i['category'],'rarity':i['rarity'],'runtime_item_id':None,'appearance_route':'WEAPON_OR_SHIELD_PROBE' if weapon else 'CHARACTER_APPEARANCE_ROUTE_UNKNOWN','inventory_art_authority':'Ivalice-Style-V2' if s else 'Klein-Production','signature':s['signature_design_en'] if s else 'TO_EXTRACT_FROM_SELECTED_KLEIN_ICON','palette':s['palette'] if s else 'TO_SAMPLE_FROM_SELECTED_KLEIN_ICON','combat_art_status':'CONCEPT_ONLY' if i['id'] in choices else 'NOT_CREATED','binding':'UNKNOWN','native_sprite_id':None,'native_palette_id':None,'orientation_frames':'UNKNOWN','anchor':'UNKNOWN','tests':['readable_with_unit_at_native_scale','idle_move_attack_guard','all_verified_directions','left_right_and_dual_equip','no_baked_in_weapon_duplicate','vanilla_unchanged']})
(ROOT/'combat-production-plan.json').write_text(json.dumps({'runtime_ready':False,'items':contracts},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert len(contracts)==271 and len({i['id'] for i in contracts})==271
report={'status':'PASS_AUTHORING_CHECKS_ONLY','concept_equipment':len(choices),'concept_weapons':sum(i['category']!='Shield' for i in manifest),'concept_shields':sum(i['category']=='Shield' for i in manifest),'cut_poses':len(choices)*4,'preview_size_author_choice':[36,36],'all_selected_have_transparent_alpha':True,'clear_gutters_checked_above_alpha_16':True,'original_alpha_preserved':True,'contract_items':len(contracts),'native_bank_roundtrip':'PASS','visual_review':'ALL_38_SOURCE_SHEETS_AND_MINIATURES_INSPECTED','generated_source_pngs':len(list((ROOT/'concepts').glob('*.png'))),'game_tests':'NOT_RUN','runtime_ready':False,'pollinations_calls':0}
(ROOT/'validation-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
# Make the study accessible beside the live and portable catalogue without altering their designs.
for gallery in (GALLERY,REVISION):
    destination=gallery/'combat-study'
    shutil.copytree(ROOT,destination,dirs_exist_ok=True,ignore=shutil.ignore_patterns('tools','review','file-manifest.json','__pycache__'))
    copied=destination/'index.html'
    copied.write_text(copied.read_text(encoding='utf-8').replace('../The-Forgotten-Jobs-Equipment-Originality-Revision/catalogue.html','../catalogue.html'),encoding='utf-8')
    page=gallery/'catalogue.html'
    text=page.read_text(encoding='utf-8')
    if 'combat-study/index.html' not in text:
        text=text.replace('<a href="native-before-after.jpg">','<a href="combat-study/index.html">Armes équipées — trois études</a> · <a href="native-before-after.jpg">',1)
        page.write_text(text,encoding='utf-8')
    else:
        page.write_text(text.replace('Armes équipées — trois études','Armes et boucliers — 38 études'),encoding='utf-8')
print(json.dumps(report))
