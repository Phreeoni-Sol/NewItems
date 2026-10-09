"""Link selected assets to all designs without allocating or guessing engine IDs."""
from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parents[1];project=root.parents[1]
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
design_root=project/'outputs/The-Forgotten-Jobs-Equipment-Originality-Revision'
designs=read(design_root/'items.json')['items']
inventory={}
for folder in ('The-Forgotten-Jobs-Equipment-Klein-Production','The-Forgotten-Jobs-Equipment-Ivalice-Style-V2'):
    base=project/'outputs'/folder
    for entry in read(base/'selected-manifest.json'):
        p=base/entry['image'];assert sha(p)==entry['sha256']
        assert entry['id'] not in inventory
        inventory[entry['id']]={'source':p.relative_to(project).as_posix(),'sha256':entry['sha256'],'alpha_ready':entry['alpha_ready'],'native_icon_binding':'UNKNOWN'}
combat={r['id']:r for r in read(root/'conversion-manifest.json')}
expected={r['id'] for r in read(project/'outputs/The-Forgotten-Jobs-Combat-Completion-88/generation-plan.json')['items']}
for folder in ('The-Forgotten-Jobs-Ordinary-Combat-Lot-19','The-Forgotten-Jobs-Retouch-38-Exceptional-Equipment'):
    expected.update(r['id'] for r in read(project/'outputs'/folder/'selected-alternatives.json'))
assert len(expected)==145 and len(inventory)==len(designs)==271
assert set(combat).issubset(expected)
rows=[]
for design in designs:
    ident=design['id'];assert ident in inventory
    entry={'id':ident,'name_fr':design['name_fr'],'category':design['category'],'rarity':design['rarity'],'design_ref':'outputs/The-Forgotten-Jobs-Equipment-Originality-Revision/items.json#'+ident,'mechanic_id':design['balance_proposal']['effect_spec']['mechanic_id'],'mechanic_implementation':'UNKNOWN','inventory':inventory[ident],'combat_art_expected':ident in expected,'combat':None,'native_binding':{'item_id':None,'secondary_id':None,'sprite_id':None,'palette_id':None,'hand_anchor':None,'SHP':None,'SEQ':None},'runtime_ready':False}
    if ident in combat:
        row=combat[ident]
        entry['combat']={'layout':(root/'items'/ident/'layout.json').relative_to(project).as_posix(),'binary_sha256':row['sha256'],'source_sha256':row['source_sha256'],'encoding_status':'PASS_ENCODING_ONLY','visual_review':row['visual_review'],'animation_semantics':'UNKNOWN'}
    rows.append(entry)
report={'schema':'tfj_asset_integration_contract_v1','equipment_designs':271,'combat_expected':145,'combat_encoded':len(combat),'combat_missing':sorted(expected-set(combat)),'item_ids_allocated':0,'vanilla_replacements':0,'runtime_ready':False,'items':rows}
(root/'equipment-integration-contract.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k!='items'}))
