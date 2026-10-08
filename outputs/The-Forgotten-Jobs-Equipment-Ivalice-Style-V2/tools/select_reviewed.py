"""Record explicit visual reviews, preserving unreviewed generations separately."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
generated={x['id']:x for x in json.loads((ROOT/'review/generated-manifest.json').read_text(encoding='utf-8-sig'))}
selected={x['id']:x for x in json.loads((ROOT/'selected-manifest.json').read_text(encoding='utf-8-sig'))} if (ROOT/'selected-manifest.json').exists() else {}
for key in sys.argv[1:]:
 x=generated[key];assert x['alpha_ready'] and not x['runtime_ready']
 x['status']='SELECTED_VISUALLY_REVIEWED_AUTHORING'
 x['visual_review']='Inspected complete silhouette, category, native-inspired restrained textured rendering, differentiated palette and local effects. Alpha checked. Inventory authoring only; combat art absent.'
 if key=='tfj_shield_16' and not x['image'].startswith('corrections/'):x['visual_review']+=' Angular tapered shield rather than exact planned hexagon.'
 if key=='tfj_knight_sword_06':x['visual_review']+=' Large open blade slot is not clearly represented; violet base recess substitutes visually. Documented motif deviation.'
 selected[key]=x
(ROOT/'selected-manifest.json').write_text(json.dumps(list(selected.values()),ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'selected':len(selected),'generated':len(generated),'planned':68}))
