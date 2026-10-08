from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
root=Path('outputs/The-Forgotten-Jobs-Equipment-Klein-Production');cases=json.loads((root/'correction-plan.json').read_text(encoding='utf-8'));ready=[c for c in cases if (root/'corrections/images'/(c['id']+'.png')).exists()];out=root/'corrections/contact-sheets';out.mkdir(exist_ok=True)
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',n)
for start in range(0,len(ready),4):
 group=ready[start:start+4];board=Image.new('RGB',(780,len(group)*310+45),(26,30,38));d=ImageDraw.Draw(board);d.text((20,8),'Corrections Klein — référence / première passe / nouvelle passe',font=font(20),fill='white')
 for j,c in enumerate(group):
  y=45+j*310;d.text((20,y),c['name_fr'],font=font(20),fill=(235,211,167));paths=[Path(c['reference']),root/'images'/(c['id']+'.png'),root/'corrections/images'/(c['id']+'.png')]
  for k,(p,label) in enumerate(zip(paths,['Référence native','Première passe','Correction'])):
   im=Image.open(p).convert('RGBA');im.thumbnail((100,100),Image.Resampling.LANCZOS);tile=Image.new('RGBA',(100,100),'white');tile.alpha_composite(im,((100-im.width)//2,(100-im.height)//2));x=20+k*255;board.paste(tile.convert('RGB').resize((200,200),Image.Resampling.NEAREST),(x,y+35));d.text((x,y+243),label,font=font(17),fill='white')
 board.save(out/f'page-{start//4+1:02}.png')
print('Correction pages',len(ready))
