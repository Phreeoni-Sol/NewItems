from pathlib import Path
from html.parser import HTMLParser
import hashlib,json,html,shutil
from PIL import Image
root=Path(__file__).resolve().parents[1]
base=next(p for p in root.parents if (p/'work/upstream').is_dir())
old=base/'outputs/The-Forgotten-Jobs-Equipment-Combat-Study-38'
plan=json.loads((root/'generation-plan.json').read_text(encoding='utf8'))
rows=json.loads((root/'review/measurements.json').read_text(encoding='utf8'))
decisions=json.loads((root/'review/visual-decisions.json').read_text(encoding='utf8'))
assert len(rows)==38 and len({r['id'] for r in rows})==38
assert set(decisions['reviewed_ids'])=={r['id'] for r in rows}
assert not decisions['unresolved_corrections']
old_rows={r['id']:r for r in json.loads((old/'selected-concepts.json').read_text(encoding='utf8'))}
(root/'previous-previews').mkdir(exist_ok=True)
cards=[]
for row in rows:
    item=next(p for p in plan['items'] if p['id']==row['id'])
    assert None not in row['split_xy'] and len(row['poses'])==4
    assert hashlib.sha256((root/'sources'/f"{row['id']}.png").read_bytes()).hexdigest()==row['sha256']
    assert hashlib.sha256((old/old_rows[row['id']]['sheet']).read_bytes()).hexdigest()==old_rows[row['id']]['sha256']
    row.update(category=item['category'],rarity=item['rarity'],signature=item['signature'],palette_intent=item['palette'],status='VISUALLY_REVIEWED_ALTERNATIVE_CONCEPT_ONLY',native_encoding='NOT_CREATED',native_sprite_id=None,native_palette_id=None,hand_anchor='UNKNOWN',runtime_ready=False,review=decisions['notes'].get(row['id'],'Source and miniature inspected: family, dominant palette and main signature recognizable. No diffuse halo visible. Opposed views are author proposals; grid, native palette, hand pivots and frame mapping unvalidated.'))
    before=[];after=[]
    for i,p in enumerate(row['poses']):
        path=root/p['path'];im=Image.open(path);assert im.mode=='RGBA' and im.size==(36,36)
        p['sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
        previous=old/old_rows[row['id']]['poses'][i]
        target=root/'previous-previews'/previous.name;shutil.copy2(previous,target)
        before.append(f'<img class="pixel" src="previous-previews/{previous.name}" alt="Ancienne proposition {i+1}">')
        after.append(f'<img class="pixel" src="{p["path"]}" alt="Nouvelle proposition {i+1}">')
    cards.append(f'<article><h2>{html.escape(row["name_fr"])}</h2><p>{html.escape(item["category"])} · {html.escape(item["rarity"])} · {html.escape(item["palette"])}</p><p>Ancienne étude</p><div>{"".join(before)}</div><p>Nouveau dessin</p><div>{"".join(after)}</div><p><a href="sources/{row["id"]}.png">Nouvelle planche</a></p><small>Étude artistique ; conversion native et prise en main non validées.</small></article>')
    if item['inherited_witness']:
        record={k:v for k,v in item['existing_record'].items() if k!='detail'}
        record.update(generator='OPENAI_BUILT_IN_IMAGEGEN',status=row['status'],inherited_from='The-Forgotten-Jobs-Retouch-Three-Witnesses')
        (root/'sources'/f"{row['id']}.json").write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8')
(root/'selected-alternatives.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
(root/'index.html').write_text('''<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>38 équipements — nouveaux dessins</title><style>body{background:#25231e;color:#eee4ce;font:16px/1.6 system-ui;max-width:1000px;margin:auto;padding:24px}a,h1,h2{color:#dac08d}article{padding:20px;background:#34302a;margin:24px 0}article[hidden]{display:none}.pixel{width:144px;height:144px;image-rendering:pixelated;margin:4px}img{max-width:100%}input{font:inherit;padding:8px}</style><h1>38 équipements exceptionnels — nouveaux dessins</h1><p>36 armes et 2 boucliers, quatre vues proposées par objet. Silhouettes et aplats simplifiés, identités variées, anciens dessins conservés.</p><p>Aperçus à 36 × 36 agrandis sans lissage : taille d’étude, pas format moteur. Aucune capture d’équipement porté. Pour les livres, sacs et boucliers, l’ordre des profils et revers peut différer ; les revers sont des dessins proposés.</p><p><a href="CLAUDE_RETOUCH_HANDOFF.md">Dossier Claude</a> · <a href="selected-alternatives.json">Sélection revue</a> · <a href="generation-plan.json">Prompts et provenance</a></p><label>Rechercher <input id="query" placeholder="Nom ou famille"></label><span id="count">38 / 38</span>'''+''.join(cards)+'''<h2>Référence native de style</h2><img width="512" style="image-rendering:pixelated" src="references/weapon-palette-03.png" alt="Banque native, palette historique 3"><p>Palette indexée, grille finale, poses natives et points de prise restent à valider.</p><script>const q=document.getElementById('query'),cards=[...document.querySelectorAll('article')];q.addEventListener('input',()=>{let n=0;for(const c of cards){c.hidden=!c.textContent.toLowerCase().includes(q.value.toLowerCase());if(!c.hidden)n++}document.getElementById('count').textContent=n+' / 38'});</script></html>''',encoding='utf8')
class Links(HTMLParser):
    count=0
    def handle_starttag(self,tag,attrs):
        for key,value in attrs:
            if key in ('src','href') and value and not value.startswith(('http','#')):
                assert (root/value).exists(),value
                self.count+=1
links=Links();links.feed((root/'index.html').read_text(encoding='utf8'))
validation={'status':'PASS_ART_REVIEW_ONLY','reviewed_equipment':38,'weapons':36,'shields':2,'cut_views':152,'local_links_verified':links.count,'alpha_preserved':True,'original_sources_unchanged':True,'native_encoding':'NOT_CREATED','runtime_ready':False,'game_tests':'NOT_RUN','browser_qa':'BLOCKED_BY_URL_POLICY','pollen_calls':0,'new_ids_allocated':0}
(root/'validation.json').write_text(json.dumps(validation,indent=2),encoding='utf8')
for catalogue in ('The-Forgotten-Jobs-Equipment-Klein-Production','The-Forgotten-Jobs-Equipment-Originality-Revision'):
    destination=base/'outputs'/catalogue/'retouch-38'
    shutil.copytree(root,destination,dirs_exist_ok=True,ignore=shutil.ignore_patterns('tools','file-manifest.json'))
    page=destination.parent/'combat-study/index.html';text=page.read_text(encoding='utf8')
    if 'retouch-38/index.html' not in text:
        page.write_text(text.replace('</h1>','</h1><p><a href="../retouch-38/index.html">38 équipements redessinés — comparer avant / après</a></p>',1),encoding='utf8')
print(json.dumps(validation))
