from pathlib import Path
import json
from PIL import Image,ImageDraw

root=Path(__file__).resolve().parents[1]
records={i['id']:i for i in json.loads((root/'selected-concepts.json').read_text(encoding='utf-8'))}
ids=['tfj_shield_16','tfj_knife_10','tfj_axe_03','tfj_flail_03','tfj_bow_09','tfj_instrument_03','tfj_book_04','tfj_cloth_03']
board=Image.new('RGB',(1200,720),(35,37,42));d=ImageDraw.Draw(board)
d.text((18,12),'38 ETUDES / 152 VUES PROPOSEES / FORMAT NATIF ET ANIMATIONS NON VALIDES',fill='#d7c298')
for n,key in enumerate(ids):
    row=records[key];x=(n%4)*300;y=40+(n//4)*335
    d.text((x+12,y+8),row['name_fr'],fill='white')
    icon=Image.open(root/'inventory'/f'{key}.png').convert('RGBA');icon.thumbnail((80,80))
    board.paste(icon,(x+108,y+35),icon)
    for p,path in enumerate(row['poses']):
        im=Image.open(root/path).resize((90,90),Image.Resampling.NEAREST)
        board.paste(im,(x+48+(p%2)*116,y+125+(p//2)*97),im)
board.save(root/'review/eight-families-summary.jpg')
