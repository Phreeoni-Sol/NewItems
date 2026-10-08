from pathlib import Path
import json
from PIL import Image,ImageDraw

root=Path(__file__).resolve().parents[1]
choices=json.loads((root/'choices.json').read_text(encoding='utf-8'))
art=root.parent/'The-Forgotten-Jobs-Equipment-Ivalice-Style-V2'
inventory={i['id']:i for i in json.loads((art/'selected-manifest.json').read_text(encoding='utf-8'))}
records=[];errors=[]
for key,filename in choices.items():
    source=root/'concepts'/filename
    if not source.exists():continue
    im=Image.open(source)
    alpha=im.getchannel('A') if im.mode=='RGBA' else None
    ext=alpha.getextrema() if alpha else None
    row={'id':key,'image':filename,'size':im.size,'alpha':ext,'structural_check':'PASS'}
    if not alpha or ext[0]!=0 or ext[1]<240:
        row['structural_check']='FAIL_ALPHA';errors.append(row)
    else:
        w,h=im.size;mask=alpha.point(lambda a:255 if a>16 else 0)
        split_x=min(range(w*35//100,w*65//100),key=lambda x:sum(mask.crop((x,0,x+1,h)).get_flattened_data()))
        split_y=min(range(h*35//100,h*65//100),key=lambda y:sum(mask.crop((0,y,w,y+1)).get_flattened_data()))
        row['split_xy']=[split_x,split_y]
        if mask.crop((split_x,0,split_x+1,h)).getbbox() or mask.crop((0,split_y,w,split_y+1)).getbbox():
            row['structural_check']='FAIL_GUTTER';errors.append(row)
    records.append(row)
    if row['structural_check']=='PASS':
        x,y=row['split_xy'];w,h=im.size
        row['preview_poses']=[]
        for n,box in enumerate(((0,0,x,y),(x,0,w,y),(0,y,x,h),(x,y,w,h))):
            cell=im.crop(box);bounds=cell.getchannel('A').point(lambda a:255 if a>16 else 0).getbbox()
            if not bounds:
                row['structural_check']='FAIL_EMPTY_VIEW';errors.append(row);break
            small=cell.crop(bounds);small.thumbnail((32,32),Image.Resampling.NEAREST)
            canvas=Image.new('RGBA',(36,36));canvas.alpha_composite(small,((36-small.width)//2,(36-small.height)//2))
            path=root/'review'/f'{key}-view-{n+1}-36.png';canvas.save(path)
            row['preview_poses'].append(path.relative_to(root).as_posix())
(root/'review/generated-structure.json').write_text(json.dumps({'generated':len(records),'target':38,'errors':errors,'records':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for page in range(0,len(records),4):
    board=Image.new('RGB',(1280,1080),(35,37,42));d=ImageDraw.Draw(board)
    for n,row in enumerate(records[page:page+4]):
        key=row['id'];x,y=(n%2)*640,(n//2)*540
        d.text((x+12,y+8),key+' / '+inventory[key]['name_fr'],fill='white')
        icon=Image.open(art/inventory[key]['image']).convert('RGBA');icon.thumbnail((100,100))
        board.paste(icon,(x+12,y+40),icon)
        sheet=Image.open(root/'concepts'/row['image']).convert('RGBA');sheet.thumbnail((460,455))
        board.paste(sheet,(x+130,y+40),sheet)
        d.text((x+12,y+500),row['structural_check']+' / '+str(row['alpha']),fill='#d9bc88')
    board.save(root/'review'/f'generated-{len(records):02}-board-{page//4+1:02}.jpg')
for page in range(0,len(records),6):
    board=Image.new('RGB',(1200,900),(35,37,42));d=ImageDraw.Draw(board)
    for n,row in enumerate(records[page:page+6]):
        key=row['id'];x,y=(n%3)*400,(n//3)*450
        d.text((x+10,y+8),inventory[key]['name_fr'],fill='white')
        d.text((x+10,y+26),key,fill='#d9bc88')
        icon=Image.open(art/inventory[key]['image']).convert('RGBA');icon.thumbnail((100,100))
        board.paste(icon,(x+135,y+50),icon)
        for p,path in enumerate(row.get('preview_poses',[])):
            im=Image.open(root/path).resize((120,120),Image.Resampling.NEAREST)
            board.paste(im,(x+55+(p%2)*155,y+165+(p//2)*135),im)
    board.save(root/'review'/f'reduced-{len(records):02}-board-{page//6+1:02}.jpg')
print(json.dumps({'generated':len(records),'target':38,'errors':errors}))
