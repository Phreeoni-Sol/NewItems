from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,re,urllib.request,zipfile,hashlib
from html.parser import HTMLParser
root=Path('outputs/The-Forgotten-Jobs-Equipment-Klein-Production');selected=json.loads((root/'selected-manifest.json').read_text(encoding='utf-8'));byid={i['id']:i for i in selected}
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',n)
board=Image.new('RGB',(1000,590),(27,31,39));d=ImageDraw.Draw(board);d.text((20,12),'The Forgotten Jobs — aperçu du lot Klein',font=font(24),fill='white')
ids=['tfj_sword_03','tfj_armor_03','tfj_shield_03','tfj_helmet_03','tfj_bow_03','tfj_ring_03','tfj_cloak_03','tfj_item_05']
for n,id in enumerate(ids):
 x=20+(n%4)*250;y=55+(n//4)*255;i=byid[id];im=Image.open(root/i['preview100']).convert('RGB');board.paste(im.resize((200,200),Image.Resampling.NEAREST),(x,y));d.text((x,y+207),i['name_fr'],font=font(16),fill='white')
d.text((20,568),'203 objets · 68 légendaires/uniques réservés · transparence et intégration à finaliser',font=font(16),fill=(192,202,218));board.save(root/'overview.png')
status=json.loads((root/'production-status.json').read_text());status.update(generated_variants=216,corrected_objects=12,selected_objects=203,expected_generated_cost_pollen=1.08,actual_account_debit='NOT_VERIFIED',art_review_status='CONTACT_SHEET_REVIEW_AND_MAJOR_SHAPE_CORRECTIONS; FULL_STYLE_AND_GAME_REVIEW_PENDING');(root/'production-status.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
links=[]
class Parser(HTMLParser):
 def handle_starttag(self,t,a):
  for k,v in a:
   if k in ['src','href'] and v and not v.startswith('#'):links.append(v)
Parser().feed((root/'catalogue.html').read_text(encoding='utf-8'));assert all((root/p).is_file() for p in links)
for p in root.rglob('*'):
 if p.suffix in ['.py','.json','.md','.txt','.html']:assert not re.search(r'sk_[A-Za-z0-9]{20,}',p.read_text(encoding='utf-8-sig',errors='replace')),'Secret detected in '+str(p)
assert len(selected)==203 and all(i['rarity'] not in ['unique','legendary'] and i['runtime_item_id'] is None and not i['runtime_ready'] for i in selected)
assert urllib.request.urlopen('http://127.0.0.1:8852/catalogue.html',timeout=10).status==200
zip_path=Path('outputs/The-Forgotten-Jobs-Equipment-Klein-203-Items.zip')
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(root.rglob('*')):
  if p.is_file():z.write(p,root.name+'/'+p.relative_to(root).as_posix())
with zipfile.ZipFile(zip_path) as z:assert z.testzip() is None;count=len(z.infolist())
sha=hashlib.sha256(zip_path.read_bytes()).hexdigest();zip_path.with_suffix('.zip.sha256').write_text(sha+'  '+zip_path.name+'\n',encoding='ascii');print('Verified',len(links),'catalogue links;',len(selected),'selected images; ZIP',count,'entries;',zip_path.stat().st_size,'bytes; SHA256',sha)
