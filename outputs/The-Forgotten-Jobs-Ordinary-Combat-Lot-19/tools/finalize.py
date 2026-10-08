from pathlib import Path
import json,hashlib,html,re,shutil
root=Path(__file__).resolve().parents[1]
project=root.parents[1]
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
items=read(root/'generation-plan.json')['items']
measure={x['id']:x for x in read(root/'review/measurements.json')}
review=read(root/'review/visual-decisions.json')
assert len(items)==19 and set(review['reviewed_ids'])=={x['id'] for x in items}
assert not review['unresolved']
selected=[]
cards=[]
for item in items:
    ident=item['id'];m=measure[ident]
    assert len(m['poses'])==4 and None not in m['split_xy']
    assert sha(project/item['inventory_source'])==item['inventory_sha256']
    assert sha(root/'inventory'/f'{ident}.png')==item['inventory_sha256']
    selected.append({**item,'combat_art_status':'VISUALLY_REVIEWED_CONCEPT_ONLY','source_sha256':sha(root/'sources'/f'{ident}.png'),'poses':m['poses'],'runtime_ready':False,'hand_anchor':'UNKNOWN','native_item_id':None,'native_sprite_id':None,'native_palette_id':None})
    title=html.escape(item['name']);sig=html.escape(item['signature'])
    pics='<p>Aperçu 36 px : réduction fidèle, traits fins à reprendre</p>'+''.join(f'<img class="pose" src="{p["path"]}">' for p in m['poses'])+'<p>Aperçu 64 px : autre taille de travail, sans valeur native</p>'+''.join(f'<img class="pose" src="{p["preview64_path"]}">' for p in m['poses'])
    cards.append(f'<article><h2>{title}</h2><p>{ident} · {item["category"]}</p><img class="inventory" src="inventory/{ident}.png"><img class="sheet" src="sources/{ident}.png"><div>{pics}</div><p>{sig}</p></article>')
write(root/'selected-alternatives.json',selected)
all_items=read(root/'ordinary-107-plan.json')
selected_map={x['id']:x for x in selected}
for item in all_items:
    if item['id'] in selected_map:
        item.update({k:selected_map[item['id']][k] for k in ('signature','signature_status','combat_art_status')})
write(root/'ordinary-107-plan.json',all_items)
page='<!doctype html><meta charset="utf-8"><title>Équipements ordinaires — 19 études de combat</title><style>body{background:#211f1b;color:#eee;font:16px system-ui;margin:32px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(440px,1fr));gap:20px}article{background:#302d27;padding:20px;border-radius:12px}img{object-fit:contain}.inventory{width:28%;vertical-align:top}.sheet{width:65%;image-rendering:pixelated}.pose{width:23%;image-rendering:pixelated}a{color:#dcc28b}</style><h1>19 équipements ordinaires : icône et vues de combat</h1><p>18 armes et 1 bouclier, 76 vues proposées. Images originales préservées. Les miniatures 36 × 36 sont un choix de présentation, pas une contrainte moteur vérifiée. Aucun asset chargé dans le jeu.</p><p><a href="CLAUDE_ORDINARY_HANDOFF.md">Transmission Claude</a> · <a href="ordinary-107-plan.json">Suivi des 107 objets</a></p><main>'+''.join(cards)+'</main>'
(root/'index.html').write_text(page,encoding='utf8')
links=re.findall(r'(?:src|href)="([^"]+)"',page)
assert all((root/x).exists() for x in links)
write(root/'validation.json',{'status':'PASS_ART_REVIEW_ONLY','selected_equipment':19,'weapons':18,'shields':1,'proposed_views':76,'ordinary_total':107,'ordinary_remaining':88,'inventory_sha_verified':107,'runtime_ready':False,'native_palette':'NOT_CREATED','new_native_ids':0,'hand_anchor':'UNKNOWN','game_test':'NOT_RUN','browser_test':'BLOCKED_BY_URL_POLICY','pollen_calls':0,'original_alpha_preserved':True,'local_links_verified':len(links),'preview_rgba_color_range':[min(p['visible_preview_rgba_colors'] for x in selected for p in x['poses']),max(p['visible_preview_rgba_colors'] for x in selected for p in x['poses'])]})
for base in ('The-Forgotten-Jobs-Equipment-Klein-Production','The-Forgotten-Jobs-Equipment-Originality-Revision'):
    target=root.parent/base/'ordinary-combat-19'
    shutil.copytree(root,target,dirs_exist_ok=True)
    catalogue=root.parent/base/'combat-study/index.html'
    if catalogue.exists():
        text=catalogue.read_text(encoding='utf8')
        if '../ordinary-combat-19/index.html' not in text:
            text=text.replace('</body>','<p><a href="../ordinary-combat-19/index.html">Nouveau : 19 équipements ordinaires, 76 vues proposées</a></p></body>')
            catalogue.write_text(text,encoding='utf8')
print('Validated 19 art studies, 76 views, 88 ordinary objects still without combat art.')
