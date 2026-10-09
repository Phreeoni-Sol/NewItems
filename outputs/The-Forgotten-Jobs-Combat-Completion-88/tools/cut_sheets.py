from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[1]
items=json.loads((root/'generation-plan.json').read_text(encoding='utf8'))['items']
(root/'poses').mkdir(exist_ok=True)
rows=[]
for item in items:
    p=root/'sources'/f"{item['id']}.png"
    if not p.exists():continue
    im=Image.open(p).convert('RGBA');w,h=im.size
    mask=im.getchannel('A').point(lambda a:255 if a>16 else 0)
    splits=[]
    for axis,n in [('x',w),('y',h)]:
        empty=[k for k in range(int(n*.35),int(n*.65)) if mask.crop((k,0,k+1,h) if axis=='x' else (0,k,w,k+1)).getbbox() is None]
        splits.append(min(empty,key=lambda k:abs(k-n/2)) if empty else None)
    row={'id':item['id'],'name':item['name'],'category':item['category'],'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'split_xy':splits,'runtime_ready':False,'poses':[]}
    if None not in splits:
        x,y=splits
        for i,box in enumerate([(0,0,x,y),(x,0,w,y),(0,y,x,h),(x,y,w,h)],1):
            cell=im.crop(box);bbox=cell.getchannel('A').point(lambda a:255 if a>16 else 0).getbbox()
            if not bbox:continue
            crop=cell.crop(bbox);name=f"poses/{item['id']}-{i}-source.png";crop.save(root/name)
            row['poses'].append({'path':name,'source_bbox':bbox,'source_dimensions':crop.size})
    rows.append(row)
(root/'review/measurements.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
for start in range(0,len(rows),8):
    board=Image.new('RGB',(1600,900),(30,29,26));draw=ImageDraw.Draw(board)
    for j,row in enumerate(rows[start:start+8]):
        x=(j%4)*400;y=(j//4)*450
        draw.text((x+8,y+8),row['id']+' / '+row['name'],fill='white')
        im=Image.open(root/'sources'/f"{row['id']}.png").convert('RGBA');im.thumbnail((380,390),Image.Resampling.NEAREST)
        board.paste(im,(x+10,y+42),im)
    board.save(root/f'review/source-{len(rows):02d}-{start//8+1:02d}.jpg')
print(json.dumps({'sources':len(rows),'poses':sum(len(x['poses']) for x in rows),'bad_layout':[x['id'] for x in rows if len(x['poses'])!=4]}))
