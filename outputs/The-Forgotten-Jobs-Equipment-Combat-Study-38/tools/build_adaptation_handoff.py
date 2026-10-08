"""Evidence and authoring contracts only. Does not edit art or game data."""
from pathlib import Path
from collections import Counter
import hashlib, json, shutil, html, zipfile
from PIL import Image

BASE=next(p for p in Path(__file__).resolve().parents if (p/'work/upstream').is_dir())
ART=BASE/'outputs/The-Forgotten-Jobs-Equipment-Combat-Study-38'
NATIVE=BASE/'outputs/The-Forgotten-Jobs-Native-Weapon-Geometry'
OUT=BASE/'outputs/The-Forgotten-Jobs-Equipment-Adaptation-Handoff'
OUT.mkdir(exist_ok=True)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,obj):(OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf8')
selected=json.loads((ART/'selected-concepts.json').read_text(encoding='utf8'))
assert len(selected)==38 and len({x['id'] for x in selected})==38
historical=BASE/'work/upstream/fftpatcher-src/ShishiSpriteEditor/Resources'
comparisons=[]
for name in ('WEP1.SHP','WEP2.SHP','WEP1.SEQ','WEP2.SEQ'):
    a=historical/name;b=NATIVE/f'native/0002.pac_battle_{name.lower().replace(".","_")}.bin'
    equal=a.read_bytes()==b.read_bytes()
    assert equal
    comparisons.append({'resource':name,'historical_path':str(a.relative_to(BASE)),'native_path':str(b.relative_to(BASE)),'bytes':b.stat().st_size,'sha256':digest(b),'identical_bytes':equal})
write('historical-byte-comparison.json',comparisons)

rules={
'Knife':'Garder la silhouette de lame courte et un seul détail distinctif lisible ; vérifier la garde contre les doigts.',
'NinjaBlade':'Distinguer pointe et courbure des katanas ; vérifier le passage de la lame devant et derrière la main.',
'Sword':'Garder largeur de lame, garde et pommeau distincts ; fixer le centre de prise après capture native.',
'KnightSword':'Préserver la masse et la pointe caractéristique sans agrandir depuis une limite supposée ; vérifier le corps derrière la lame.',
'Katana':'Conserver courbure et tsuba ; contrôler la continuité du fil aux angles requis.',
'Axe':'Préserver profil du fer et asymétrie tête/manche ; tester le centre de prise et les collisions visuelles.',
'Staff':'Conserver courbe ou fourche supérieure et matière du bois ; garder la hampe continue après réduction.',
'Flail':'Séparer visuellement chaîne, poignée et poids ; cinématique de la chaîne UNKNOWN, ne pas figer une hypothèse comme animation native.',
'Gun':'Préserver longueur du canon et profil de crosse ; vérifier direction du canon et contact de main sans supposer de recul.',
'Crossbow':'Garder arc transversal, stock et corde distincts ; vérifier prise, occultation et direction de tir.',
'Rod':'Préserver la tête caractéristique et le manche court ; toute lumière animée nécessite une couche démontrée.',
'Bow':'Garder une silhouette continue d’arc et une corde lisible ; vérifier mains et tension avant de dessiner la pose de tir.',
'Instrument':'Garder caisse, bras et rythme de cordes lisibles ; pose de jeu et déplacement des mains UNKNOWN.',
'Book':'Conserver volume, dos, fermoir et marque principale ; état ouvert ou fermé à relever dans une animation native.',
'Polearm':'Préserver forme de pointe et longueur relative ; vérifier prise à deux mains, pointe et traversée du corps.',
'Pole':'Différencier extrémités et bandes sans silhouette de lance ; vérifier prise et angles effectivement utilisés.',
'Bag':'Conserver volume, anse et boucle ; mouvement souple et mode de frappe UNKNOWN.',
'Cloth':'Préserver un tissu connecté et son bord distinctif ; déformation et pose de frappe UNKNOWN.',
'Shield':'Préserver contour asymétrique et emblème ; relever avant/arrière, poignée et occultation du bras.'}
rows=[]
(OUT/'previews').mkdir(exist_ok=True)
for item in selected:
    assert item['category'] in rules
    assert digest(ART/item['sheet'])==item['sha256']
    measurements=[]
    for pose in item['poses']:
        source=ART/pose
        target=OUT/'previews'/source.name
        shutil.copy2(source,target)
        im=Image.open(source).convert('RGBA');assert im.size==(36,36)
        colors=Counter(p for p in im.getdata() if p[3]>16)
        opaque=sum(n for p,n in colors.items() if p[3]==255)
        measurements.append({'preview':f'previews/{source.name}','sha256':digest(source),'visible_pixels_alpha_gt16':sum(colors.values()),'distinct_visible_rgba_colors':len(colors),'fully_opaque_pixels':opaque,'semi_transparent_visible_pixels':sum(colors.values())-opaque})
    rows.append({'id':item['id'],'name_fr':item['name_fr'],'category':item['category'],'rarity':item['rarity'],'signature_to_preserve':item['signature'],'palette_intent':item['palette'],'retouch_focus':rules[item['category']],'source_sheet':str((ART/item['sheet']).relative_to(BASE)),'source_sha256':item['sha256'],'preview_measurements':measurements,'measurements_are_native_constraints':False,'native_sprite_id':None,'native_palette_id':None,'native_sequence_id':None,'hand_anchor':'UNKNOWN','required_native_poses':'UNKNOWN','unit_overlay_test':'NOT_RUN','alpha_and_blending_runtime':'UNKNOWN','native_encoding':'NOT_CREATED','status':'AUTHORING_PLAN_ONLY','runtime_ready':False})
write('adaptation-contracts-38.json',rows)
manager=BASE/'work/upstream/modloader-src/fftivc.utility.modloader/Tables/FFTOItemDataManager.cs'
base_manager=manager.with_name('FFTOTableManagerBase.cs')
layout=Path('D:/FINAL-FANTASY-TACTICS-The-Ivalice-Chronicles/CoopMod/tools/Reloaded-II/Mods/fftivc.utility.modloader/Nex/Layouts/ffto/Item.layout')
evidence={'new_ids_allocated':0,'engine_item_limit':'UNKNOWN','renderer_consumer':'UNKNOWN','sources':[{'path':str(p),'sha256':digest(p)} for p in (manager,base_manager,layout)],'loader_observation':'Local FFTOItemDataManager has two fixed pointers (256 and 5 entries), NumEntries=261; base ApplyPendingFileChanges skips indices beyond original entries. This XML patch path does not append entries. This is not proof of an engine limit.','nex_layout_observation':'Installed localized Item.layout declares names/descriptions/UI fields; no declared Palette or SpriteID column. Unknown columns remain unknown; no renderer priority inferred.'}
write('integration-evidence.json',evidence)
shutil.copy2(layout,OUT/'Item.layout.reference.txt')
(OUT/'review').mkdir(exist_ok=True)
for name in ('wep1-atlas-crops.png','wep2-atlas-crops.png'):
    shutil.copy2(NATIVE/'review'/name,OUT/'review'/name)
cards=[]
for row in rows:
    esc=html.escape
    imgs=''.join(f'<img src="{p["preview"]}" alt="vue proposée {i+1}">' for i,p in enumerate(row['preview_measurements']))
    cards.append(f'<article><h2>{esc(row["name_fr"])}</h2><p>{esc(row["category"])} · {esc(row["rarity"])} · {row["id"]}</p><div>{imgs}</div><p>{esc(row["retouch_focus"])}</p><small>Placement main : UNKNOWN · conversion : à faire</small></article>')
(OUT/'index.html').write_text('''<!doctype html><html lang="fr"><meta charset="utf-8"><title>38 équipements — préparation de la retouche</title><style>body{background:#25231f;color:#eee7d7;font:16px system-ui;max-width:1200px;margin:32px auto;padding:20px}h1{color:#d8b276}section{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:16px}article{background:#34312a;padding:20px;border:1px solid #756346}article img{width:72px;height:72px;image-rendering:pixelated;margin:4px}small{color:#d8b276}.native{max-width:100%;image-rendering:pixelated}a{color:#d8b276}</style><h1>38 équipements : préparer la retouche native</h1><p>152 aperçus de conception, agrandis ×2 sans lissage. Les 36 × 36 sont un choix de présentation, pas un format du moteur. Aucune vue n’est une capture d’équipement porté en jeu.</p><p><a href="CLAUDE_ADAPTATION_HANDOFF.md">Instructions pour Claude</a> · <a href="adaptation-contracts-38.json">38 fiches avec provenance et mesures</a></p><section>'''+''.join(cards)+'''</section><h2>Repères natifs séparés</h2><p>Découpes vanilla suivant le lecteur historique et sa première palette. Pas de correspondance attribuée à un nouvel objet.</p><img class="native" src="review/wep1-atlas-crops.png" alt="découpes natives WEP1"><img class="native" src="review/wep2-atlas-crops.png" alt="découpes natives WEP2"></html>''',encoding='utf8')
write('validation.json',{'status':'PASS_AUTHORING_ONLY','contracts':len(rows),'previews':sum(len(r['preview_measurements']) for r in rows),'families':len(rules),'historical_resources_identical':len(comparisons),'runtime_ready':False,'original_art_sha_verified':True,'native_binaries_modified':False,'browser_qa':'BLOCKED_BY_URL_POLICY','game_tests':'NOT_RUN'})
print(json.dumps({'contracts':len(rows),'previews':152,'historical_files_identical':len(comparisons),'output':str(OUT)}))
