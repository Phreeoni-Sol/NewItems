from pathlib import Path
import json,re,copy,hashlib,html,shutil,csv,collections,difflib,sys,zipfile
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[1]; OUTPUTS=ROOT.parent
SOURCE=OUTPUTS/'The-Forgotten-Jobs-Equipment-Expansion'; ART=OUTPUTS/'The-Forgotten-Jobs-Equipment-Klein-Production'
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
J=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def write_json(name,obj):
 (ROOT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
old=J(SOURCE/'items.json'); source_sha=SHA(SOURCE/'items.json'); items=copy.deepcopy(old['items']); selected={i['id']:i for i in J(ART/'selected-manifest.json')}
NEWART=OUTPUTS/'The-Forgotten-Jobs-Equipment-Kontext-Legendary-Unique'
extra={i['id']:i for i in J(NEWART/'selected-manifest.json')} if (NEWART/'selected-manifest.json').exists() else {}
selected.update(extra)
PRESTIGE=OUTPUTS/'The-Forgotten-Jobs-Equipment-Prestige-Revision'
prestige={i['id']:i for i in J(PRESTIGE/'selected-manifest.json')} if (PRESTIGE/'selected-manifest.json').exists() else {}
extra.update(prestige)
selected.update(prestige)
IVALICE_V2=OUTPUTS/'The-Forgotten-Jobs-Equipment-Ivalice-Style-V2'
ivalice_v2={i['id']:i for i in J(IVALICE_V2/'selected-manifest.json')} if (IVALICE_V2/'selected-manifest.json').exists() else {}
prestige.update(ivalice_v2)
extra.update(ivalice_v2)
selected.update(ivalice_v2)
def artroot(s):return OUTPUTS/s.get('source_pack',ART.name)
mechanics={}; category=None; index=0
for n,line in enumerate((ROOT/'tools/original-mechanics.txt').read_text(encoding='utf-8-sig').splitlines(),1):
 if not line.strip():continue
 if line.startswith('@'):category=line[1:];index=0;continue
 fields=line.split('|');assert len(fields)==4,(n,fields)
 index+=1;item_id=f'tfj_{category}_{index:02}'
 assert item_id not in mechanics
 mechanics[item_id]=dict(zip(('mechanic_id','effect_fr','tradeoff_fr','role_fr'),fields))
assert set(mechanics)=={i['id'] for i in items}, {'missing':list({i['id'] for i in items}-set(mechanics)),'extra':list(set(mechanics)-{i['id'] for i in items})}
assert len(items)==271 and len({v['mechanic_id'] for v in mechanics.values()})==271
fallback='Prototyper un déclenchement dédié préservant la condition, la cible et la contrepartie de cet effet, seulement si ce chemin est validé. Si aucun chemin ne préserve cette identité, exclure ce nouvel objet de la version jouable ; ne pas livrer un clone vanilla. Ne modifier aucun objet existant.'
policy='Règles proposées du mod, pas des limites moteur : au plus un déclenchement par objet et par action ; aucun effet secondaire ne redéclenche un équipement. Réductions de dégâts concurrentes : retenir le maximum. Bonus de même nature : retenir le maximum, jamais additionner les réserves. Une réserve est consommée à la première tentative éligible, réussie ou non. Pas d’action supplémentaire. Durée par défaut d’une réserve non datée : fin du prochain tour du porteur. Compteurs effacés à la fin de la bataille ; perte des réserves à la mise hors combat. Arrondi des gains et réductions vers le bas, coût MP payé minimal de 1 ; aucune précision ne peut garantir une réussite. Une limite plus restrictive indiquée dans la fiche prime.'
prices=[50,150,400,150,350,900,100,150,150,150,250,250,350,500,0,0]
changes=[]; specifications=[]
for item,prior in zip(items,old['items']):
 key=item['id']; m=mechanics[key]; b=item['balance_proposal']; old_stats=copy.deepcopy(b['stats']); old_price=b['price_gil']; rarity=item['rarity']
 # Remove inherited flat bonuses so the new mechanic owns the identity.
 for k in ('MoveBonus','JumpBonus','PABonus','MABonus','SpeedBonus'):b['stats'].pop(k,None)
 budget={'common':.95,'uncommon':.92,'rare':.90,'legendary':.85,'unique':.85}[rarity]
 explicit=re.search(r'Puissance de base réduite de (\d+) %',m['tradeoff_fr'],re.I)
 if explicit:budget=1-int(explicit.group(1))/100
 for k in ('Power','HPBonus','MPBonus'):
  if k in b['stats'] and b['stats'][k]>0:b['stats'][k]=max(1,int(b['stats'][k]*budget))
 if rarity in ('legendary','unique'):
  b['price_gil']=0;b['sell_price_gil']=0;b['shop_enabled_proposal']=False;b['sale_enabled_proposal']=False
 elif item['category']=='Item':
  b['price_gil']=prices[int(key.rsplit('_',1)[1])-1];b['sell_price_gil']=b['price_gil']//2;b['shop_enabled_proposal']=True;b['sale_enabled_proposal']=True
 else:
  base=int(item['baseline_reference']['common_raw_fields'].get('Price','0'))
  factor={'common':1.1,'uncommon':1.2,'rare':1.35}[rarity]
  b['price_gil']=max(50,round((base*factor if base else old_price)/25)*25);b['sell_price_gil']=b['price_gil']//2;b['shop_enabled_proposal']=True;b['sale_enabled_proposal']=True
 b['price_status']='PROVISIONAL_NOT_PLAYTESTED';b['stat_budget_proposal']={'source':'previous design stats','multiplier':budget,'removed_flat_bonuses':[k for k in old_stats if k not in b['stats']],'rounding':'floor; positive stat minimum 1','purpose_fr':'Céder une part des caractéristiques à l’effet tactique ; ce sont des choix de design, pas des valeurs moteur vérifiées.'}
 b['special_effect_fr']=m['effect_fr'];b['tradeoff_fr']=m['tradeoff_fr'];b['tactical_role_fr']=m['role_fr'];b['special_effect_binding']='UNKNOWN';b['needs_custom_hook']=True;b['fallback_fr']=fallback;b['stacking_policy']=policy
 # Numerics are explicit design data, not constants to hardcode in runtime scripts.
 params={}; templates={}
 for field in ('effect_fr','tradeoff_fr'):
  def extract(match):
   pid=f'{field}_{len(params)+1:02}';params[pid]={'value':int(match.group()),'unit_context_fr':m[field][max(0,match.start()-24):min(len(m[field]),match.end()+28)]};return '{'+pid+'}'
  templates[field]=re.sub(r'(?<!\w)\d+(?!\w)',extract,m[field])
 spec={'schema':'tfj_mechanic_design_spec_v2','item_id':key,'mechanic_id':m['mechanic_id'],'role_fr':m['role_fr'],'text_templates':templates,'parameters':params,'implementation_status':'UNKNOWN','executable':False,'event_hook':None,'engine_status_id':None,'engine_ability_id':None,'default_rules_ref':'BALANCE_RULES.md','target_and_trigger_fr':m['effect_fr'],'constraints_fr':m['tradeoff_fr'],'fallback_fr':fallback,'requires_design_translation_before_code':True,'test_cases_required':['trigger eligible / ineligible','recipient selection / tie','expiration / turn boundary','counter / reset / KO','proc recursion / stacking / minimum cost','save-load / acquisition / unique quantity','vanilla inventory and behavior unchanged']}
 b['effect_spec']=spec;specifications.append(spec)
 item['description_fr']=m['effect_fr'];item['design_status']='REVISED_ORIGINALITY_DESIGN_NOT_IMPLEMENTED';item['originality_review']={'source_baseline_id':item['baseline_reference']['item_id'],'baseline_name_en':item['baseline_reference']['name_en'],'difference_fr':m['role_fr']+' '+m['effect_fr'],'review_scope':'static baseline item tables and previous design; all vanilla ability internals NOT verified','exact_text_duplicate':False,'semantic_distinctness_status':'DESIGNED_DISTINCT_TRIGGER_TARGET_EFFECT_CONSTRAINT; runtime and exhaustive semantic baseline comparison pending'}
 item['runtime_item_id']=None; item['native_binding']={k:(None if k!='status' else 'UNKNOWN') for k in item['native_binding']}
 for check in ('new mechanic prototype','duration and percentage units','no plain vanilla fallback','distinct gameplay playtest'):
  if check not in item['validation_required']:item['validation_required'].append(check)
 a=item['art'];a['binding_status']='UNKNOWN';a['ready']=False;a['runtime_ready']=False
 if key in selected:
  s=selected[key];a['status']='OPENAI_IVALICE_V2_SELECTED_AUTHORING_NOT_RUNTIME' if key in ivalice_v2 else ('OPENAI_PRESTIGE_SELECTED_AUTHORING_NOT_RUNTIME' if key in prestige else ('KONTEXT_SELECTED_AUTHORING_NOT_RUNTIME' if key in extra else 'KLEIN_SELECTED_AUTHORING_NOT_RUNTIME'));a['selected_image_source']='../'+artroot(s).name+'/'+s['image'];a['selected_image_sha256']=s['sha256'];a['preview']='art/previews100/'+key+'.png';a['alpha_ready']=s.get('alpha_ready',False)
 else:a['status']='RESERVED_FOR_OTHER_MODEL';a['preview']=None;a['alpha_ready']=False
 changes.append({'id':key,'name_fr':item['name_fr'],'old_effect_fr':prior['balance_proposal']['special_effect_fr'],'new_effect_fr':m['effect_fr'],'tradeoff_fr':m['tradeoff_fr'],'old_price_gil':old_price,'new_price_gil':b['price_gil'],'old_stats':old_stats,'new_stats':b['stats'],'baseline_name_en':item['baseline_reference']['name_en'],'art_regenerated':False,'runtime_ready':False})
 signatures={}
 for field,template in templates.items():assert template.format(**{k:v['value'] for k,v in params.items()})==m[field]
write_json('items.json',{'schema':'tfj_equipment_originality_design_v2','project':'The Forgotten Jobs','runtime_ready':False,'supersedes_design':'../'+SOURCE.name+'/items.json','source_sha256':source_sha,'revision_scope':'271 gameplay designs; existing art preserved, no game modifications','items':items})
write_json('mechanics.json',{'schema':'tfj_mechanic_design_collection_v2','executable':False,'mechanics':specifications})
write_json('changes.json',changes)
# Include the precise static evidence used, unchanged.
ref=ROOT/'references';ref.mkdir(exist_ok=True)
shutil.copy2(SOURCE/'references/baseline-inventory.csv',ref/'baseline-inventory.csv')
for src in sorted((SOURCE/'references/baseline-tables').glob('*.xml')):
 (ref/'baseline-tables').mkdir(exist_ok=True);shutil.copy2(src,ref/'baseline-tables'/src.name)
(ROOT/'art/previews100').mkdir(parents=True,exist_ok=True)
for key,s in selected.items():shutil.copy2(artroot(s)/s['preview100'],ROOT/'art/previews100'/f'{key}.png')
write_json('art/provenance.json',[{'id':key,'source_image':'../'+artroot(s).name+'/'+s['image'],'source_sha256':s['sha256'],'preview_source':'../'+artroot(s).name+'/'+s['preview100'],'preview_sha256':SHA(ROOT/'art/previews100'/f'{key}.png'),'alpha_ready':s.get('alpha_ready',False),'runtime_ready':False} for key,s in selected.items()])
(ROOT/'art/full').mkdir(exist_ok=True)
for key,s in extra.items():shutil.copy2(artroot(s)/s['image'],ROOT/'art/full'/f'{key}.png')
# An exact signature omits names, numerical amounts and role labels. It is a screening check, not a proof of semantic novelty.
def signature(t):return re.sub(r'\d+','N',re.sub(r'\s+',' ',t.lower())).strip()
seen=collections.defaultdict(list)
for i in items:seen[signature(i['description_fr']+' '+i['balance_proposal']['tradeoff_fr'])].append(i['id'])
duplicates=[v for v in seen.values() if len(v)>1]
assert not duplicates,duplicates
baseline=list(csv.DictReader((ref/'baseline-inventory.csv').open(encoding='utf-8-sig',newline='')))
assert len({i['id'] for i in items})==271
assert all(i['runtime_item_id'] is None and all(v is None for k,v in i['native_binding'].items() if k!='status') for i in items)
assert all(i['balance_proposal']['needs_custom_hook'] and not i['balance_proposal']['effect_spec']['executable'] for i in items)
assert all(i['description_fr']!=o['description_fr'] for i,o in zip(items,old['items']))
assert SHA(SOURCE/'items.json')==source_sha
similar=[]
for n,a in enumerate(items):
 for b in items[n+1:]:
  ratio=difflib.SequenceMatcher(None,signature(a['description_fr']),signature(b['description_fr'])).ratio()
  if ratio>=.74:similar.append({'a':a['id'],'b':b['id'],'ratio':round(ratio,3),'status':'REVIEW_REQUIRED_NOT_DUPLICATE_PROOF'})
write_json('originality-audit.json',{'total':271,'rarities':dict(collections.Counter(i['rarity'] for i in items)),'categories':dict(collections.Counter(i['category'] for i in items)),'revised_effects':271,'new_mechanics':271,'unique_mechanic_ids':271,'normalized_exact_duplicates':duplicates,'lexical_similarities_to_review':sorted(similar,key=lambda s:-s['ratio']),'source_design_preserved':True,'static_baseline_rows':len(baseline),'baseline_coverage_limits':'Item ability options and all runtime skills are not exhaustively decoded here. No claim of exhaustive semantic disjointness from every vanilla ability. No runtime validation.','native_ids_allocated':0,'art_generated':0,'previews_reused':len(selected),'reserved_art':271-len(selected),'validation_result':'STATIC_DESIGN_CHECKS_PASS','runtime_ready':False})
# Portable full catalogue: existing previews plus all 68 pending art designs.
esc=lambda s:html.escape(str(s),quote=True)
parts=['''<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>The Forgotten Jobs — 271 objets revus</title><style>body{font:16px/1.55 system-ui;background:#181c24;color:#e9e5dc;max-width:1450px;margin:auto;padding:24px}h1,h2{color:#dec394}a{color:#b4d6f7}.controls{position:sticky;top:0;background:#181c24;padding:12px 0;z-index:2;display:flex;gap:10px;flex-wrap:wrap}input,select{font:inherit;color:inherit;background:#29313d;border:1px solid #657080;padding:8px;border-radius:6px}input{min-width:240px;flex:1}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:16px}.card{background:#262e3b;padding:18px;border-radius:10px;border:1px solid #414955}.card[hidden]{display:none}.top{display:flex;gap:16px;align-items:center}.icon{width:100px;height:100px;object-fit:contain;background:white;border-radius:5px}.missing{width:100px;min-width:100px;height:100px;display:grid;place-items:center;text-align:center;font-size:13px;background:#333a46;border:1px dashed #7b818b;color:#c5c7ce}.badge{color:#b3c5d9;font-size:13px}.role{color:#edcf91}.cost{color:#9cd1b4}.constraint{color:#edbfa3}details{border-top:1px solid #4c5260;padding-top:10px;margin-top:14px}summary{cursor:pointer;color:#b4d6f7}.note{background:#293342;padding:14px;border-left:3px solid #d1b684}code{overflow-wrap:anywhere;font-size:12px}table{border-collapse:collapse}td,th{padding:6px;border:1px solid #555;text-align:left}.muted{color:#b4bdca;font-size:14px}</style></head><body><h1>271 objets — identité tactique revue</h1><p>Chaque fiche remplace l’ancien effet de progression par une condition, un rôle et une limite propres. Les objets vanilla servent de références et restent inchangés.</p><p class="note">Propositions de design pour Claude. Mécaniques et équilibre à prototyper ; aucune intégration jouable confirmée. 203 visuels Klein conservés ; 34 légendaires et 34 uniques attendent leur visuel. L’originalité est examinée sur les tables disponibles, sans prétendre connaître tous les comportements internes du jeu.</p><p><a href="items.json">Fiches complètes</a> · <a href="CLAUDE_HANDOFF.md">Passation Claude</a> · <a href="REVISION.md">Bilan de la révision</a> · <a href="originality-audit.json">Audit</a></p><div class="controls"><input id="query" placeholder="Nom, effet, rôle, identifiant…"><select id="family"><option value="">Toutes les familles</option>''']
for cat in sorted({i['category_fr'] for i in items}):parts.append(f'<option>{esc(cat)}</option>')
parts.append('</select><select id="rarity"><option value="">Toutes les raretés</option>')
labels={'common':'Commun','uncommon':'Peu commun','rare':'Rare','legendary':'Légendaire','unique':'Unique'}
for value,label in labels.items():parts.append(f'<option value="{value}">{label}</option>')
parts.append('</select><span id="count"></span></div><div class="grid">')
for i,c in zip(items,changes):
 b=i['balance_proposal']; key=i['id']; search=' '.join((i['name_fr'],key,i['description_fr'],b['tradeoff_fr'],b['tactical_role_fr'])).lower()
 if key in ivalice_v2:search+=' fft v2'
 parts.append(f'<article id="{key}" class="card" data-family="{esc(i["category_fr"])}" data-rarity="{i["rarity"]}" data-search="{esc(search)}"><div class="top">')
 image_style=' style="background:#292a2d"' if key in ivalice_v2 else ''
 icon=f'<img class="icon"{image_style} loading="lazy" src="art/previews100/{key}.png" alt="{esc(i["name_fr"])}">'
 if key in extra:icon=f'<a href="art/full/{key}.png" title="Voir le visuel en grand">'+icon+'</a>'
 parts.append(icon if key in selected else '<div class="missing">Visuel réservé<br>autre modèle</div>')
 parts.append(f'<div><h2>{esc(i["name_fr"])}</h2><span class="badge">{esc(i["category_fr"])} · {labels[i["rarity"]]}</span></div></div><p class="role">{esc(b["tactical_role_fr"])}</p><p><strong>Effet :</strong> {esc(i["description_fr"])}</p><p class="constraint"><strong>Limite / contrepartie :</strong> {esc(b["tradeoff_fr"])}</p>')
 cost=f'{b["price_gil"]:,} gils proposés'.replace(',',' ') if b['shop_enabled_proposal'] else 'Récompense dédiée · hors boutique · non revendable'
 parts.append(f'<p class="cost">{cost}</p><details><summary>Ancien effet, référence et fiche technique</summary><p><strong>Ancien :</strong> {esc(c["old_effect_fr"])}</p><p><strong>Différence :</strong> {esc(i["originality_review"]["difference_fr"])}</p><p><strong>Référence native :</strong> {esc(c["baseline_name_en"])} — référence de famille, aucun remplacement.</p><p><strong>Caractéristiques proposées :</strong> {esc(json.dumps(b["stats"],ensure_ascii=False))}</p><p><strong>Acquisition proposée :</strong> {esc(i["acquisition_proposal"]["proposal_fr"])}</p><p><strong>Prix précédent :</strong> {c["old_price_gil"]} gils. Prix et progression à tester.</p><p class="muted">L’effet remplace l’ancien passif proposé. Liaison moteur UNKNOWN. {esc(fallback)}</p><code>{key} · {b["effect_spec"]["mechanic_id"]}</code></details></article>')
parts.append('''</div><script>const q=document.getElementById('query'),f=document.getElementById('family'),r=document.getElementById('rarity'),cards=[...document.querySelectorAll('.card')];function filter(){let count=0;for(const c of cards){c.hidden=!(c.dataset.search.includes(q.value.toLowerCase())&&(!f.value||c.dataset.family===f.value)&&(!r.value||c.dataset.rarity===r.value));if(!c.hidden)count++}document.getElementById('count').textContent=count+' / 271';}for(const control of [q,f,r])control.addEventListener('input',filter);filter();</script></body></html>''')
parts=[p.replace('203 visuels Klein conservés ; 34 légendaires et 34 uniques attendent leur visuel.',f'203 visuels Klein conservés ; {len(ivalice_v2)} / 68 pièces exceptionnelles redessinées depuis les références natives FFT avec des silhouettes et palettes distinctes. Recherchez « v2 » pour afficher les nouveaux visuels. Cliquez sur leur image pour l’ouvrir en grand. Les petits sprites des armes équipées et leur intégration en jeu restent à réaliser.') for p in parts]
comparison=IVALICE_V2/'review/native-before-after.jpg'
if comparison.exists():
 shutil.copy2(comparison,ROOT/'native-before-after.jpg')
 shutil.copy2(comparison,ART/'native-before-after.jpg')
 parts=[p.replace('<a href="items.json">Fiches complètes</a>','<a href="native-before-after.jpg">Comparatif natif / ancien / nouveau</a> · <a href="items.json">Fiches complètes</a>') for p in parts]
featured_ids=['tfj_katana_09','tfj_bow_10','tfj_gun_07','tfj_staff_08','tfj_shield_16','tfj_armor_13','tfj_robe_07','tfj_perfume_04']
featured=[ivalice_v2[key] for key in featured_ids if key in ivalice_v2]
if featured:
 examples='<section style="margin:24px 0"><h2>Nouvelle direction FFT — exemples</h2><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(145px,1fr));gap:12px">'
 for s in featured:
  key=s['id'];examples+=f'<a href="art/full/{key}.png" style="display:flex;flex-direction:column;align-items:center;gap:8px;padding:10px;background:#292a2d;border:1px solid #4c5260;border-radius:6px;font-size:13px;text-align:center"><img src="art/previews100/{key}.png" alt="{esc(s["name_fr"])}" width="100" height="100"><span>{esc(s["name_fr"])}</span></a>'
 examples+='</div></section>'
 parts=[p.replace('<div class="controls">',examples+'<div class="controls">') for p in parts]
(ROOT/'catalogue.html').write_text(''.join(parts),encoding='utf-8')
# Serve updated current 8852 catalogue without moving the user's tab or touching sealed ZIPs.
# Copy portable display assets, maintain previous art gallery as a historical page.
if not (ART/'catalogue-art-before-originality.html').exists():shutil.copy2(ART/'catalogue.html',ART/'catalogue-art-before-originality.html')
for name in ('items.json','changes.json','mechanics.json','originality-audit.json'):
 shutil.copy2(ROOT/name,ART/('originality-'+name))
shutil.copytree(ROOT/'art/previews100',ART/'originality-previews100',dirs_exist_ok=True)
shutil.copytree(ROOT/'art/full',ART/'originality-full',dirs_exist_ok=True)
current=''.join(parts).replace('art/previews100/','originality-previews100/').replace('art/full/','originality-full/').replace('href="items.json"','href="originality-items.json"').replace('href="originality-audit.json"','href="originality-originality-audit.json"')
(ART/'catalogue.html').write_text(current,encoding='utf-8')
print(json.dumps({'revised':len(items),'mechanics':len(specifications),'reused_previews':len(selected),'similarity_candidates':len(similar),'source_sha':source_sha,'current_catalogue_updated':True},ensure_ascii=False))

for name in ("CLAUDE_HANDOFF.md","BALANCE_RULES.md","REVISION.md"):
 if (ROOT/name).exists():shutil.copy2(ROOT/name,ART/name)
