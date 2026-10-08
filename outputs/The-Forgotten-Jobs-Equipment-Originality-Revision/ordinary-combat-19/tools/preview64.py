from pathlib import Path
import json
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[1]
rows=json.loads((root/'review/measurements.json').read_text(encoding='utf8'))
for row in rows:
    for i,p in enumerate(row['poses'],1):
        im=Image.open(root/'poses'/f"{row['id']}-{i}-source.png").convert('RGBA')
        im.thumbnail((60,60),Image.Resampling.NEAREST)
        out=Image.new('RGBA',(64,64));out.paste(im,((64-im.width)//2,(64-im.height)//2))
        name=f"poses/{row['id']}-{i}-preview64.png";out.save(root/name)
        p['preview64_path']=name
for start in range(0,len(rows),6):
    sub=rows[start:start+6]
    board=Image.new('RGB',(1040,len(sub)*215),(31,30,27));draw=ImageDraw.Draw(board)
    for i,row in enumerate(sub):
        y=i*215;draw.text((16,y+12),row['id']+' / '+row['name_fr'],fill='white')
        for j,p in enumerate(row['poses']):
            im=Image.open(root/p['preview64_path']).resize((128,128),Image.Resampling.NEAREST)
            board.paste(im,(30+j*250,y+42),im)
    board.save(root/f'review/preview64-{start//6+1:02d}.jpg')
(root/'review/measurements.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
print('76 faithful 64px authoring previews; no native dimension claim.')
