from pathlib import Path
import json
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[1]
rows=json.loads((root/'review/measurements.json').read_text(encoding='utf8'))
count=len(rows)
for start in range(0,count,4):
    subset=rows[start:start+4]
    board=Image.new('RGB',(1080,1160),(31,30,27));draw=ImageDraw.Draw(board)
    for i,row in enumerate(subset):
        x=(i%2)*540;y=(i//2)*580
        draw.text((x+15,y+12),row['id']+' / '+row['name_fr'],fill='white')
        im=Image.open(root/'sources'/f"{row['id']}.png").convert('RGBA')
        im.thumbnail((510,510),Image.Resampling.NEAREST)
        board.paste(im,(x+15+(510-im.width)//2,y+48+(510-im.height)//2),im)
    board.save(root/f'review/source-{count:02d}-{start//4+1:02d}.jpg')
for start in range(0,count,6):
    subset=rows[start:start+6]
    board=Image.new('RGB',(1040,len(subset)*215),(31,30,27));draw=ImageDraw.Draw(board)
    for i,row in enumerate(subset):
        y=i*215;draw.text((16,y+12),row['id']+' / '+row['name_fr'],fill='white')
        for j,pose in enumerate(row['poses']):
            im=Image.open(root/pose['path']).convert('RGBA').resize((144,144),Image.Resampling.NEAREST)
            board.paste(im,(30+j*250,y+42),im)
    board.save(root/f'review/miniature-{count:02d}-{start//6+1:02d}.jpg')
print('Source boards:',(count+3)//4,'miniature boards:',(count+5)//6)
