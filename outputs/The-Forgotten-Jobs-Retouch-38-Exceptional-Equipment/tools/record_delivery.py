from pathlib import Path
import json,hashlib,shutil
root=Path(__file__).resolve().parents[1]
base=next(p for p in root.parents if (p/'work/upstream').is_dir())
rows=json.loads((root/'selected-alternatives.json').read_text(encoding='utf8'))
decisions_path=root/'review/visual-decisions.json'
decisions=json.loads(decisions_path.read_text(encoding='utf8'))
decisions['boards']=[p if p.startswith(('review/','corrections/')) else 'review/'+p for p in decisions['boards']]
for p in decisions['boards']:assert (root/p).is_file(),p
decisions_path.write_text(json.dumps(decisions,ensure_ascii=False,indent=2),encoding='utf8')
for row in rows:
    path=root/'sources'/f"{row['id']}.json"
    record=json.loads(path.read_text(encoding='utf8'))
    record.update(status=row['status'],selected_sha256=row['sha256'],review=row['review'],runtime_ready=False)
    path.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8')
for item_id,reason in decisions['resolved_corrections'].items():
    path=root/'rejected'/f'{item_id}-v1.json'
    record=json.loads(path.read_text(encoding='utf8'));record.update(status='REJECTED_VARIANT',reason=reason,runtime_ready=False)
    path.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8')
    path=root/'corrections'/f'{item_id}-v2.json'
    record=json.loads(path.read_text(encoding='utf8'));record.update(status='VISUALLY_REVIEWED_SELECTED_CORRECTION',runtime_ready=False)
    path.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8')
validation=json.loads((root/'validation.json').read_text(encoding='utf8'))
validation.update(legendary=19,unique=19,families=19,corrected_variants=4,initial_rejected_variants=4,visible_preview_rgba_color_range=[min(p['visible_preview_rgba_colors'] for r in rows for p in r['poses']),max(p['visible_preview_rgba_colors'] for r in rows for p in r['poses'])],indexed_palette='NOT_CREATED',summary_board='VISUALLY_INSPECTED')
(root/'validation.json').write_text(json.dumps(validation,indent=2),encoding='utf8')
# Refresh only the companion review directories; preserve all existing art authorities.
for catalogue in ('The-Forgotten-Jobs-Equipment-Klein-Production','The-Forgotten-Jobs-Equipment-Originality-Revision'):
    shutil.copytree(root,base/'outputs'/catalogue/'retouch-38',dirs_exist_ok=True,ignore=shutil.ignore_patterns('tools','file-manifest.json'))
print('Recorded final review, rejected variants, source provenance and colour limitations.')
