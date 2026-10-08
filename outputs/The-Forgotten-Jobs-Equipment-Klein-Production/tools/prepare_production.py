from pathlib import Path
import json,collections
src=Path('outputs/The-Forgotten-Jobs-Equipment-Enhanced-Revision');root=Path('outputs/The-Forgotten-Jobs-Equipment-Klein-Production');root.mkdir(exist_ok=True)
for name in ['tools','prompts','references','images','records','previews100','previews48']: (root/name).mkdir(exist_ok=True)
items=json.loads((src/'revision-manifest.json').read_text(encoding='utf-8'))['items'];plan=[];reserved=[]
for item in items:
 if item['rarity'] in ['legendary','unique']:
  reserved.append(dict(id=item['id'],name_fr=item['name_fr'],rarity=item['rarity'],category=item['category'],status='RESERVED_FOR_OTHER_MODEL',runtime_item_id=None));continue
 ref=src/item['style_references'][0];local=root/'references'/ref.name
 if not local.exists():local.write_bytes(ref.read_bytes())
 prompt=f"Create ONE original {item['category']} equipment inventory icon. New design motif: {item['visual_intent']}. The attached image is an actual native FFT The Ivalice Chronicles Enhanced inventory texture and is ONLY a style and composition reference. Follow its viewing angle, orientation, compact silhouette, relative object scale, muted color palette and delicate proportions. Match its worn hand-painted textured materials, restrained highlights, and soft slightly distressed painterly edges. Use practical believable construction and sparse ornament. Do not duplicate the reference object; follow the new design motif. Keep the complete object readable at 100x100 and 48x48 with safe padding. Single isolated object, no scenery, no frame, no floor shadow, no reflection, no cast shadow. Absolutely no lettering, words, numbers, logos, labels, writing, signatures or watermarks anywhere, including on the object itself. No product photography, glossy concept-art rendering, neon glow, thick black outlines or hard pixel-art clusters. Flat uniform pure white background if genuine transparent alpha is unsupported; never a checkerboard pattern."
 if item['category'] in ['Knife','Sword','KnightSword','Katana','NinjaBlade']:prompt+=' IMPORTANT: blade point at UPPER LEFT and grip at LOWER RIGHT. Never reverse this diagonal; never place the grip at the upper right.'
 elif item['category']=='Bow':prompt+=' A complete coherent bow with slender limbs, small central grip and one continuous bowstring; match the native reference diagonal. No oversized central handle, no quiver, no arrow, no second bow.'
 elif item['category']=='Shield':prompt+=' The surface is completely unlettered. Any stripe or emblem is only a simple geometric decoration, with no typography.'
 elif item['category'] in ['Armor','Helmet','Shield']:prompt+=' Suppress glossy hard plastic-like highlights; preserve subdued scratched metal and worn surfaces.'
 (root/'prompts'/(item['id']+'.txt')).write_text(prompt,encoding='utf-8')
 plan.append(dict(id=item['id'],name_fr=item['name_fr'],category=item['category'],rarity=item['rarity'],visual_intent=item['visual_intent'],reference=str(local),prompt=prompt,status='PLANNED',runtime_item_id=None,runtime_ready=False))
assert len(plan)==203 and len(reserved)==68
(root/'production-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8');(root/'reserved-legendary-unique.json').write_text(json.dumps(reserved,ensure_ascii=False,indent=2),encoding='utf-8')
pilot=[]
for category in ['Knife','Sword','Armor','Shield','Ring','Bow','Staff','Helmet']:pilot.append(next(i['id'] for i in plan if i['category']==category))
(root/'pilot-ids.json').write_text(json.dumps(pilot),encoding='utf-8')
print('Prepared',len(plan),'Klein objects and',len(reserved),'reserved legendary/unique; planned base cost',len(plan)*.005)
