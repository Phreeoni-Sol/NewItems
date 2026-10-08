from pathlib import Path
import json
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[1]
rows={r['id']:r for r in json.loads((root/'review/measurements.json').read_text(encoding='utf8'))}
ids=['tfj_knife_09','tfj_katana_09','tfj_bow_09','tfj_bow_10']
board=Image.new('RGB',(1040,4*215),(33,31,28));draw=ImageDraw.Draw(board)
for i,item_id in enumerate(ids):
    row=rows[item_id];y=i*215;draw.text((15,y+10),row['name_fr']+' / correction v2',fill='white')
    for j,p in enumerate(row['poses']):
        im=Image.open(root/p['path']).convert('RGBA').resize((144,144),Image.Resampling.NEAREST)
        board.paste(im,(25+j*250,y+40),im)
board.save(root/'review/corrected-four-miniatures.jpg')
ids=['tfj_shield_16','tfj_knife_10','tfj_axe_03','tfj_flail_03','tfj_gun_07','tfj_bow_10','tfj_book_04','tfj_cloth_03']
board=Image.new('RGB',(1120,800),(33,31,28));draw=ImageDraw.Draw(board)
for i,item_id in enumerate(ids):
    row=rows[item_id];x=(i%2)*560;y=(i//2)*200
    draw.text((x+15,y+12),row['name_fr'],fill='white')
    for j,p in enumerate(row['poses']):
        im=Image.open(root/p['path']).convert('RGBA').resize((108,108),Image.Resampling.NEAREST)
        board.paste(im,(x+15+j*130,y+53),im)
board.save(root/'review/eight-families-summary.jpg')
print('Saved correction review and eight-family summary.')
