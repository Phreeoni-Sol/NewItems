"""Record the agent's completed visual inspection of the 19 current contact sheets.
This operation does not make an in-game approval or run automatically during conversion.
"""
from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parents[1];project=root.parents[1]
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rows=read(root/'conversion-manifest.json')
assert len(rows)==145
gate=read(root/'reports/quality-gate.json')
assert gate['equipment']==145 and not gate['visual_issues'] and not gate['signature_issues']
assert read(root/'reports/encoding-validation.json')['equipment']==145
assert read(root/'reports/palette-validation.json')['rare_blue_accent']=='PASS'
reviewed_boards=[f'review/native-{i:02d}.png' for i in range(1,20)]
assert all((root/p).is_file() for p in reviewed_boards)
entries=[]
selected={r['id']:r for r in read(root/'corrections/selected-overrides.json')}
for row in rows:
    row['visual_review']='INSPECTED_CURRENT_NATIVE_AUTHORING_CONTACT_SHEET'
    row['creative_source_retouch']=row['id'] in selected
    row['pixel_retouched']=False
    row['pixel_retouched_note']='No hand-painted pixel claims; selected generative source revisions and deterministic native conversion are recorded separately.'
    row['palette_quantization']='RGB555_FARTHEST_COLOR_SEEDS_WEIGHTED_LLOYD_8_ITERATIONS_MAX_15_OPAQUE_COLORS'
    row['review_limits']='Authoring previews inspected; actual actor placement, animation, scene contrast, UI binding and game behavior are not tested.'
    (root/'items'/row['id']/'layout.json').write_text(json.dumps(row,ensure_ascii=False,indent=2),encoding='utf8')
    entries.append({'id':row['id'],'source_sha256':row['source_sha256'],'binary_sha256':row['sha256'],'view_sha256':[sha(root/f['readback_png']) for f in row['frames']],'status':row['visual_review'],'runtime_ready':False})
(root/'conversion-manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
report={'equipment_reviewed':145,'views_reviewed':580,'reviewed_boards':{p:sha(root/p) for p in reviewed_boards},'items':entries,'runtime_ready':False,'game_test':'NOT_RUN','scope':'Visual inspection of current authoring contact sheets. Dark silhouettes and actor-scale interpretation need game-scene tests.'}
(root/'reports/visual-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
for entry in selected.values():
    entry['status']='SELECTED_INSPECTED_NATIVE_AUTHORING_PREVIEW_RUNTIME_PENDING'
(root/'corrections/selected-overrides.json').write_text(json.dumps(list(selected.values()),ensure_ascii=False,indent=2),encoding='utf8')
completion=project/'outputs/The-Forgotten-Jobs-Combat-Completion-88'
state=read(completion/'production-state.json');state['status']='AUTHORING_SOURCES_AND_NATIVE_ENCODING_COMPLETE_RUNTIME_PENDING'
(completion/'production-state.json').write_text(json.dumps(state,indent=2),encoding='utf8')
for item in read(completion/'review/measurements.json'):
    p=completion/'records'/f"{item['id']}.json"
    if not p.exists():continue
    record=read(p);record.update(status='SOURCE_CONTACT_SHEET_AND_NATIVE_AUTHORING_PREVIEW_INSPECTED',source_sha256=item['sha256'],native_conversion_ref=f"../The-Forgotten-Jobs-Equipment-Native-Quality-V2/items/{item['id']}/layout.json",runtime_ready=False)
    p.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'reviewed_equipment':145,'reviewed_views':580,'selected_source_retouches':len(selected),'runtime_ready':False}))
