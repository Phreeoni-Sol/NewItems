"""Evidence-based authoring checks. Passing encoding never implies game readiness."""
from pathlib import Path
import hashlib, json

root = Path(__file__).resolve().parents[1]
project = root.parents[1]
rows = json.loads((root / 'conversion-manifest.json').read_text(encoding='utf8'))
issues = []
checks = []
for row in rows:
    ident = row['id']
    source = project / row['source']
    assert hashlib.sha256(source.read_bytes()).hexdigest() == row['source_sha256'], ident
    frames = row['frames']
    assert len(frames) == 4, ident
    scales = {frame['sampling_scale'] for frame in frames}
    assert len(scales) == 1, (ident, 'orientation-dependent scale')
    for frame in frames:
        scale = frame['sampling_scale']
        assert frame['resampled_size'] == [max(1, round(n * scale)) for n in frame['source_size']], ident
        assert frame['visible_pixels'] > 0, ident
        assert frame['sampling_phase'][0] in (0,-.25,.25,-.4,.4)
        assert frame['sampling_phase'][1] in (0,-.25,.25,-.4,.4)
        if frame['has_multiple_components']:
            issues.append({'id': ident, 'view': frame['view'], 'reason': 'DISCONNECTED_PIXELS_REQUIRE_VISUAL_REVIEW', 'components': frame['connected_component_sizes']})
    assert row['runtime_ready'] is False
    assert all(row[k] is None for k in ('native_item_id', 'native_sprite_id', 'native_palette_id'))
    checks.append({'id': ident, 'source_sha256': row['source_sha256'], 'binary_sha256': row['sha256'], 'common_scale': 'PASS', 'provenance': 'PASS'})
report = {'equipment': len(rows), 'views': 4 * len(rows), 'technical_checks': 'PASS', 'visual_issues': issues, 'checks': checks, 'runtime_ready': False, 'game_test': 'NOT_RUN', 'note': 'Connectivity is a diagnostic, not an automatic visual approval. Scale preserves source proportions; it does not establish actual in-game dimensions.'}
signature_file=root/'reports/signature-validation.json'
if signature_file.exists():
    report['signature_issues']=[r for r in json.loads(signature_file.read_text(encoding='utf8'))['checks'] if r['status']=='RETOUCH_REQUIRED']
(root / 'reports/quality-gate.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k not in ('checks', 'note')}))
