from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,html,textwrap
root=Path('outputs/The-Forgotten-Jobs-Equipment-Klein-Production');plan=json.loads((root/'production-plan.json').read_text(encoding='utf-8'));reserved=json.loads((root/'reserved-legendary-unique.json').read_text(encoding='utf-8'));records={}
selection={r['id']:r for r in json.loads((root/'selected-manifest.json').read_text(encoding='utf-8'))} if (root/'selected-manifest.json').exists() else {}
for p in (root/'records').glob('*.json'):
 try:records[p.stem]=json.loads(p.read_text(encoding='utf-8'))
 except json.JSONDecodeError:continue
ready=[p for p in plan if (root/'previews100'/(p['id']+'.png')).is_file()];(root/'contact-sheets').mkdir(exist_ok=True)
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',n)
for start in range(0,len(ready),24):
 group=ready[start:start+24];board=Image.new('RGB',(1000,((len(group)+3)//4)*275+50),(30,34,42));d=ImageDraw.Draw(board);d.text((20,10),f'Klein — icônes {start+1} à {start+len(group)} / {len(ready)}',font=font(22),fill='white')
 for n,item in enumerate(group):
  x=(n%4)*250+20;y=(n//4)*275+55;im=Image.open(root/selection.get(item['id'],{}).get('preview100','previews100/'+item['id']+'.png')).convert('RGB');board.paste(im.resize((200,200),Image.Resampling.NEAREST),(x,y))
  lines=textwrap.wrap(item['name_fr'],width=25)[:2];d.text((x,y+205),'\n'.join(lines),font=font(15),fill='white');d.text((x,y+245),item['id'],font=font(12),fill=(175,190,212))
 board.save(root/'contact-sheets'/f'page-{start//24+1:02}.png')
summary={'planned':len(plan),'generated':len(ready),'reserved_other_model':len(reserved),'failed':[r['id'] for r in records.values() if r['status']=='FAILED'],'expected_generated_cost_pollen':round(len(ready)*.005,3),'runtime_ready':False,'alpha_ready':sum(r.get('alpha_ready',False) for r in records.values())}
variant_count=len(list((root/'images').glob('*.png')))+len(list((root/'corrections/images').glob('*.png')))+len(list((root/'corrections-last/images').glob('*.png')))
summary.update(generated_variants=variant_count,corrected_objects=len(selection) and sum(i.get('image','').startswith('corrections') for i in selection.values()),selected_objects=len(selection),expected_generated_cost_pollen=round(variant_count*.005,3),actual_account_debit='NOT_VERIFIED')
(root/'production-status.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
parts=['<!doctype html><html lang="fr"><meta charset="utf-8"><title>FFT — production Klein</title><style>body{font:16px system-ui;background:#191c24;color:#e3e6ed;margin:25px auto;max-width:1300px;padding:20px}h1,h2{color:#e0c28c}a{color:#a6cffe}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(255px,1fr));gap:15px}.card{background:#272e3a;border-radius:10px;padding:15px}.pair{display:flex;gap:12px}.icon{width:100px;height:100px;object-fit:contain;background:white}.big{max-width:100%}.pending{color:#b7bfcc}.badge{color:#e3c58b}input,select{padding:10px;font-size:16px;background:#272e3a;color:white;border:1px solid #586577;margin:6px}small{color:#c5ccd8}</style><h1>Équipements — production Klein</h1>']
parts.append(f'<p><strong>{len(ready)} / 203</strong> objets générés · <strong>68 légendaires et uniques réservés à un autre modèle</strong>.</p><p>Les références du jeu sont à gauche, nos nouvelles propositions à droite. Les sorties sont des essais artistiques ; transparence et intégration restent à finaliser.</p><p><a href="production-status.json">État du lot</a> · <a href="reserved-legendary-unique.json">Objets réservés</a></p><input id="search" placeholder="Rechercher un objet"><select id="category"><option value="">Toutes les familles</option>')
for cat in sorted({i['category'] for i in plan}):parts.append('<option>'+html.escape(cat)+'</option>')
parts.append('</select><div class="grid">')
for item in plan:
 id=item['id'];image_url=selection.get(id,{}).get('image','images/'+id+'.png');preview_url=selection.get(id,{}).get('preview100','previews100/'+id+'.png');generated=(root/'previews100'/(id+'.png')).is_file();ref='references/'+Path(item['reference']).name;label=html.escape(item['name_fr']);parts.append(f'<article class="card" data-category="{item["category"]}" data-search="{html.escape((item["name_fr"]+" "+id).lower(),quote=True)}"><h2>{label}</h2><p class="badge">{item["rarity"]} · {item["category"]}</p><div class="pair"><div><img class="icon" src="{ref}"><p><small>Référence native</small></p></div>')
 if generated:parts.append(f'<div><a href="{image_url}"><img class="icon" src="{preview_url}"></a><p><small>Nouvelle proposition</small></p></div></div><p><a href="{image_url}">Image originale</a> · <a href="prompts/{id}.txt">Consigne</a></p>')
 else:parts.append('<div><p class="pending">À générer</p></div></div>')
 parts.append('</article>')
parts.append('''</div><h2>Réservés pour un autre modèle</h2><p>34 légendaires et 34 uniques : aucune génération Klein dans ce lot.</p><script>const search=document.getElementById('search'),category=document.getElementById('category');function filter(){const q=search.value.toLowerCase();document.querySelectorAll('.card').forEach(c=>c.hidden=!(c.dataset.search.includes(q)&&(!category.value||c.dataset.category===category.value)))}search.addEventListener('input',filter);category.addEventListener('change',filter)</script></html>''')
(root/'catalogue.html').write_text(''.join(parts),encoding='utf-8');print(summary)
