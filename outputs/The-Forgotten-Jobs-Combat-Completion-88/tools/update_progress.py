from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parents[1]
plan=json.loads((root/'generation-plan.json').read_text(encoding='utf8'))['items']
measured=json.loads((root/'review/measurements.json').read_text(encoding='utf8')) if (root/'review/measurements.json').exists() else []
processed={r['id'] for r in measured if len(r['poses'])==4}
present={r['id'] for r in plan if (root/'sources'/f"{r['id']}.png").is_file()}
state={'target':len(plan),'generated':len(present),'four_views_decoded':len(processed),'remaining':len(plan)-len(present),'missing':[r['id'] for r in plan if r['id'] not in present],'layout_review_required':sorted(present-processed),'status':'ART_PRODUCTION_COMPLETE_ENCODING_REVIEW_REQUIRED' if len(present)==len(plan) else 'IN_PROGRESS','runtime_ready':False}
(root/'production-state.json').write_text(json.dumps(state,indent=2),encoding='utf8')
text=f"""# Avancement du lot complémentaire

{len(present)}/{len(plan)} planches générées ; {len(processed)} découpées en quatre vues.
{len(plan)-len(present)} sources restent à produire. Les détails sont dans production-state.json.
Outil : OpenAI imagegen intégré. Sources sauvegardées dans sources/, prompts dans records/.

La découpe utilise des séparations transparentes, ou quatre silhouettes connexes à alpha >= 128
quand les rangées se chevauchent. Cette seconde règle suit le seuil de conversion documenté ;
elle ne dessine aucun pixel et ne prouve pas un format d'animation.

## Reprise et validation
Lire generation-plan.json et production-state.json ; ignorer les sources présentes.
Arrêter toute la file sur la première erreur de quota. Ne pas relancer prepare.py.
Relancer tools/cut_sheets.py puis tools/update_progress.py.
Exécuter les outils build_conversion.py, verify_conversion.py, quality_gate.py et build_catalogue.py
du dossier Equipment-Native-Quality-V2. Examiner aussi les previews après réduction.
La présence d'une source ou un encodage réussi ne vaut pas validation dans le jeu.
"""
(root/'STATUS.md').write_text(text,encoding='utf8')
(root/'RESUME.md').write_text(text,encoding='utf8')
print(json.dumps(state))
