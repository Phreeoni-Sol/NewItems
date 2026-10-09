from pathlib import Path
import json, html
root=Path(__file__).resolve().parents[1]
rows=json.loads((root/'conversion-manifest.json').read_text(encoding='utf8'))
cards=[]
for row in rows:
    frames=''.join(f'<figure><img src="{html.escape(f["readback_png"])}" width="{f["rectangle"][2]*4}" height="{f["rectangle"][3]*4}"><figcaption>Vue {f["view"]} · {f["rectangle"][2]} × {f["rectangle"][3]} px</figcaption></figure>' for f in row['frames'])
    alert='Pixels détachés à examiner' if any(f['has_multiple_components'] for f in row['frames']) else ('Planche native inspectée · essais en jeu à faire' if row['visual_review'].startswith('INSPECTED') else 'Revue artistique requise')
    cards.append(f'<article data-search="{html.escape((row["id"]+" "+row["name"]+" "+row["category"]).lower())}"><h2>{html.escape(row["name"])}</h2><p>{row["id"]} · {row["category"]}</p><div class="frames">{frames}</div><p class="state">{alert}</p><a href="items/{row["id"]}/layout.json">Données et provenance</a></article>')
page='''<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Équipements — conversion et revue</title><style>body{background:#22201c;color:#eee8db;font:16px system-ui;margin:32px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(480px,1fr));gap:20px}article{border:1px solid #665740;padding:20px;border-radius:8px}h2{font-size:20px}.frames{display:flex;align-items:center;gap:14px;min-height:150px}figure{margin:0;text-align:center;flex:1}img{image-rendering:pixelated;max-width:100%;object-fit:contain}figcaption{font-size:12px;margin-top:10px}.state{color:#dfbf76}a{color:#b6cfea}input{padding:12px;margin:16px 0;width:min(600px,90%)}[hidden]{display:none}</style>'''
page+=f'<h1>{len(rows)} équipements · {4*len(rows)} vues converties</h1><p>Propositions artistiques, encodage expérimental. La présentation à ×4 permet la revue des pixels ; la taille affichée dans le jeu reste à confirmer.</p><p>Ancres, IDs et animations à raccorder. Aucun équipement déclaré jouable.</p><input id="search" placeholder="Rechercher un nom, une famille ou un identifiant"><main>'+''.join(cards)+'</main><script>search.addEventListener("input",()=>{let q=search.value.toLowerCase();document.querySelectorAll("article").forEach(a=>a.hidden=!a.dataset.search.includes(q))})</script></html>'
(root/'index.html').write_text(page,encoding='utf8')
for row in rows:
    for f in row['frames']:assert (root/f['readback_png']).is_file()
print(json.dumps({'cards':len(rows),'image_links_verified':4*len(rows),'browser_review':'NOT_RUN'}))
