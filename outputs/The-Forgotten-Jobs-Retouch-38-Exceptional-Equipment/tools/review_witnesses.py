from pathlib import Path
from collections import Counter
import hashlib,json
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[1]
plan=json.loads((root/'generation-plan.json').read_text(encoding='utf8'))
(root/'poses').mkdir(exist_ok=True)
(root/'review').mkdir(exist_ok=True)
reports=[]
for item in plan['items']:
    path=root/'sources'/f"{item['id']}.png"
    if not path.exists():continue
    im=Image.open(path).convert('RGBA');alpha=im.getchannel('A')
    strong=alpha.point(lambda a:255 if a>16 else 0)
    w,h=im.size
    def cut(axis):
        n=w if axis=='x' else h
        empty=[]
        for k in range(int(n*.35),int(n*.65)):
            band=strong.crop((k,0,k+1,h) if axis=='x' else (0,k,w,k+1))
            if band.getbbox() is None:empty.append(k)
        return min(empty,key=lambda k:abs(k-n/2)) if empty else None
    sx,sy=cut('x'),cut('y');a=Counter(alpha.get_flattened_data())
    report={'id':item['id'],'name_fr':item['name'],'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'size':[w,h],'split_xy':[sx,sy],'alpha_extrema':alpha.getextrema(),'alpha0_pixels':a[0],'alpha255_pixels':a[255],'alpha1_to239_pixels':sum(v for k,v in a.items() if 0<k<240),'visible_rgba_colors':len({p for p in im.get_flattened_data() if p[3]>16}),'detection_threshold':16,'original_alpha_preserved':True,'status':'AWAITING_VISUAL_REVIEW','runtime_ready':False,'poses':[]}
    if sx is not None and sy is not None:
        for i,box in enumerate(((0,0,sx,sy),(sx,0,w,sy),(0,sy,sx,h),(sx,sy,w,h)),1):
            cell=im.crop(box);bbox=cell.getchannel('A').point(lambda a:255 if a>16 else 0).getbbox()
            assert bbox
            # Faithful cut/resize only. Original colors and alpha are not edited.
            crop=cell.crop(bbox);crop.save(root/'poses'/f"{item['id']}-{i}-source.png")
            scale=min(32/crop.width,32/crop.height)
            small=crop.resize((max(1,round(crop.width*scale)),max(1,round(crop.height*scale))),Image.Resampling.NEAREST)
            canvas=Image.new('RGBA',(36,36));canvas.paste(small,((36-small.width)//2,(36-small.height)//2))
            name=f"poses/{item['id']}-{i}-preview36.png";canvas.save(root/name)
            report['poses'].append({'path':name,'source_bbox':list(bbox),'source_dimensions':list(crop.size),'visible_preview_rgba_colors':len({p for p in canvas.get_flattened_data() if p[3]>16})})
    reports.append(report)
board=Image.new('RGB',(1000,max(1,len(reports))*270),(36,34,31));draw=ImageDraw.Draw(board)
for y,row in enumerate(reports):
    yy=y*270;draw.text((20,yy+12),row['name_fr']+' / '+row['id'],fill='white')
    for i,p in enumerate(row['poses']):
        im=Image.open(root/p['path']).convert('RGBA').resize((144,144),Image.Resampling.NEAREST)
        x=20+i*240;board.paste(im,(x,yy+45),im)
        draw.text((x,yy+210),f"36x36 preview, {p['visible_preview_rgba_colors']} colors",fill='white')
board.save(root/'review/all-equipment-preview.jpg')
(root/'review/measurements.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'sources':len(reports),'poses':sum(len(r['poses']) for r in reports),'missing_clear_gutters':[r['id'] for r in reports if None in r['split_xy']]}))
