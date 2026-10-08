from pathlib import Path
import json,hashlib,html,re,sys,xml.etree.ElementTree as ET
from html.parser import HTMLParser
sys.stdout.reconfigure(encoding='utf-8')
R=Path(__file__).resolve().parents[1]; S=R.parent/'The-Forgotten-Jobs-Equipment-Expansion'; A=R.parent/'The-Forgotten-Jobs-Equipment-Klein-Production'
J=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
d=J(R/'items.json');items=d['items'];old=J(S/'items.json')['items'];spec=J(R/'mechanics.json')['mechanics'];audit=J(R/'originality-audit.json');changes=J(R/'changes.json');art=J(R/'art/provenance.json')
assert len(items)==len(spec)==len(changes)==271
assert {i['id'] for i in items}=={i['id'] for i in old}=={i['item_id'] for i in spec}=={i['id'] for i in changes}
assert len({i['mechanic_id'] for i in spec})==271
assert H(S/'items.json')==d['source_sha256']
old_by={i['id']:i for i in old};checks=[]
for i in items:
 b=i['balance_proposal'];s=b['effect_spec'];o=old_by[i['id']]
 assert i['name_fr']==o['name_fr'] and i['category']==o['category'] and i['rarity']==o['rarity']
 assert i['baseline_reference']==o['baseline_reference'] and i['acquisition_proposal']==o['acquisition_proposal']
 assert i['runtime_item_id'] is None and i['native_binding']['status']=='UNKNOWN'
 assert all(v is None for k,v in i['native_binding'].items() if k!='status')
 assert b['special_effect_binding']=='UNKNOWN' and b['needs_custom_hook'] and not s['executable']
 assert 'clone vanilla' in b['fallback_fr']
 assert i['description_fr']==b['special_effect_fr']!=o['balance_proposal']['special_effect_fr']
 assert b['tradeoff_fr'] and b['tactical_role_fr']
 for f,t in s['text_templates'].items():assert t.format(**{k:v['value'] for k,v in s['parameters'].items()})==b[f if f=='tradeoff_fr' else 'special_effect_fr']
 assert all(v>=0 for v in b['stats'].values())
 if i['rarity'] in ('legendary','unique'):assert not b['shop_enabled_proposal'] and not b['sale_enabled_proposal'] and b['price_gil']==b['sell_price_gil']==0
 else:assert b['price_gil']>0 and b['sell_price_gil']==b['price_gil']//2
for p in (R/'references/baseline-tables').glob('*.xml'):
 ET.parse(p);assert H(p)==H(S/'references/baseline-tables'/p.name)
assert H(R/'references/baseline-inventory.csv')==H(S/'references/baseline-inventory.csv')
for p in art:
 assert H((R/p['source_image']).resolve())==p['source_sha256']
 assert H(R/'art/previews100'/f"{p['id']}.png")==p['preview_sha256']
expected_art=203+len(J(R.parent/'The-Forgotten-Jobs-Equipment-Kontext-Legendary-Unique/selected-manifest.json'))
assert len(art)==expected_art and len([i for i in items if i['art']['status']=='RESERVED_FOR_OTHER_MODEL'])==271-expected_art
assert not audit['normalized_exact_duplicates'] and not audit['lexical_similarities_to_review']
# Validate actual display links, card coverage and escaping, including the currently served copy.
class Page(HTMLParser):
 def __init__(self):super().__init__();self.cards=[];self.paths=[]
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if tag=='article':self.cards.append(d['id'])
  if tag=='img':self.paths.append(d['src'])
  if tag=='a':self.paths.append(d['href'])
for directory in (R,A):
 parser=Page();parser.feed((directory/'catalogue.html').read_text(encoding='utf-8'))
 assert set(parser.cards)=={i['id'] for i in items} and len(parser.cards)==271
 for link in parser.paths:
  if not link.startswith(('http:','https:','#')):assert (directory/link).is_file(),(directory,link)
# Regression assertions around the reported vanilla clone.
pastille=next(i for i in items if i['id']=='tfj_item_09')
assert pastille['balance_proposal']['price_gil']==150 and 'bloque une seule nouvelle application' in pastille['description_fr']
result={'status':'PASS','item_count':271,'source_preserved':True,'existing_images_sha256_checked':len(art),'baseline_tables_checked':7,'catalogue_links_checked':True,'all_runtime_ids_null':True,'runtime_tests':'NOT_RUN_NO_IMPLEMENTATION','semantic_comparison':'STATIC_PROFILE_REVIEW_ONLY_NOT_EXHAUSTIVE_VANILLA_ABILITIES'}
(R/'validation-report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False))
