from pathlib import Path
import json
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[1]
base=next(p for p in root.parents if (p/'work/upstream').is_dir())
old=base/'outputs/The-Forgotten-Jobs-Equipment-Combat-Study-38'
rows=json.loads((root/'review/measurements.json').read_text(encoding='utf8'))
board=Image.new('RGB',(1040,len(rows)*360),(34,32,29));draw=ImageDraw.Draw(board)
for row_index,row in enumerate(rows):
    y=row_index*360;draw.text((16,y+8),row['name_fr'],fill='#e6c38b')
    for variant in range(2):
        draw.text((16,y+35+variant*158),'Avant' if variant==0 else 'Nouveau dessin',fill='white')
        for pose_index in range(4):
            path=old/f"poses/{row['id']}-{pose_index+1}-preview36.png" if variant==0 else root/row['poses'][pose_index]['path']
            im=Image.open(path).convert('RGBA').resize((144,144),Image.Resampling.NEAREST)
            board.paste(im,(170+pose_index*212,y+28+variant*158),im)
board.save(root/'review/before-after-three-witnesses.jpg')
print('Saved faithful comparison of 24 existing previews.')
