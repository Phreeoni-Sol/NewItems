from pathlib import Path
import json,shutil
root=Path(__file__).resolve().parents[1]
for p in (root/'sources').glob('*.json'):
    obj=json.loads(p.read_text(encoding='utf8'))
    obj.update(status='VISUALLY_REVIEWED_CONCEPT_ONLY',runtime_ready=False,pixel_retouched=False)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf8')
for p in (root/'rejected').glob('*.json'):
    obj=json.loads(p.read_text(encoding='utf8'))
    obj.update(status='REJECTED_VARIANT',reason='Four tines not retained in every source view.',runtime_ready=False)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf8')
for p in (root/'corrections').glob('*.json'):
    obj=json.loads(p.read_text(encoding='utf8'))
    obj.update(status='SELECTED_SOURCE_DESIGN_ONLY',runtime_ready=False,pixel_retouched=False)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf8')
validation=json.loads((root/'validation.json').read_text(encoding='utf8'))
validation.update(pixel_retouched=False,known_author_preview_issues=10,preview_sizes_are_native_constraints=False,source_corrections=1,archive_scope='19 source designs; no native-ready assets')
(root/'validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2),encoding='utf8')
for base in ('The-Forgotten-Jobs-Equipment-Klein-Production','The-Forgotten-Jobs-Equipment-Originality-Revision'):
    folder=root.parent/base
    shutil.copytree(root,folder/'ordinary-combat-19',dirs_exist_ok=True)
    catalogue=folder/'catalogue.html'
    if catalogue.exists():
        content=catalogue.read_text(encoding='utf8')
        if 'ordinary-combat-19/index.html' not in content:
            marker='<p style="padding:20px"><a href="ordinary-combat-19/index.html">19 équipements ordinaires : icônes et 76 vues de combat proposées</a></p>'
            assert '</body>' in content
            catalogue.write_text(content.replace('</body>',marker+'</body>'),encoding='utf8')
    for page,link in ((folder/'catalogue.html','ordinary-combat-19/index.html'),(folder/'combat-study/index.html','../ordinary-combat-19/index.html')):
        assert link in page.read_text(encoding='utf8')
print('Source metadata, companion catalogues and local links verified.')
