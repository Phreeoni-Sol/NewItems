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
    row['segmentation']='EMPTY_GUTTERS_ALPHA_GT_16'
    if None not in splits:
        x,y=splits
        for i,box in enumerate([(0,0,x,y),(x,0,w,y),(0,y,x,h),(x,y,w,h)],1):
            cell=im.crop(box);bbox=cell.getchannel('A').point(lambda a:255 if a>16 else 0).getbbox()
            if not bbox:continue
            crop=cell.crop(bbox);name=f"poses/{item['id']}-{i}-source.png";crop.save(root/name)
            row['poses'].append({'path':name,'source_bbox':bbox,'source_dimensions':crop.size})
    else:
        # Some sheets have overlapping row extents but four separate opaque silhouettes.
        # Match the documented native alpha threshold without painting or changing pixels.
        opaque=im.getchannel('A').point(lambda a:255 if a>=128 else 0)
        points={(x,y) for y in range(h) for x in range(w) if opaque.getpixel((x,y))}
        parts=[];part_pixels={}
        while points:
            seed=points.pop();queue=[seed];pixels=[]
            while queue:
                px,py=queue.pop();pixels.append((px,py))
                for dx,dy in ((-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)):
                    near=(px+dx,py+dy)
                    if near in points:points.remove(near);queue.append(near)
            if len(pixels)>=100:
                xs,ys=zip(*pixels);bounds=(min(xs),min(ys),max(xs)+1,max(ys)+1)
                parts.append(bounds);part_pixels[bounds]=pixels
        if len(parts)==4:
            parts.sort(key=lambda b:(b[1]+b[3])/2)
            parts=sorted(parts[:2],key=lambda b:b[0])+sorted(parts[2:],key=lambda b:b[0])
            # Require the four boxes to occupy the expected quadrants.
            valid=all(((b[0]+b[2])/2<w/2)==(i%2==0) and ((b[1]+b[3])/2<h/2)==(i<2) for i,b in enumerate(parts))
            if valid:
                row['segmentation']='FOUR_CONNECTED_OPAQUE_SILHOUETTES_ALPHA_GE_128'
                for i,bbox in enumerate(parts,1):
                    # A bounding rectangle can include another pose when row extents overlap.
                    # Extract ONLY this component's original pixels; never draw replacements.
                    crop=im.crop(bbox);alpha=Image.new('L',crop.size)
                    for px,py in part_pixels[bbox]:
                        alpha.putpixel((px-bbox[0],py-bbox[1]),im.getpixel((px,py))[3])
                    crop.putalpha(alpha)
                    name=f"poses/{item['id']}-{i}-source.png";crop.save(root/name)
                    row['poses'].append({'path':name,'source_sheet_bbox':bbox,'source_dimensions':crop.size,'extraction':'ONLY_SELECTED_CONNECTED_COMPONENT_ORIGINAL_COLORS_AND_ALPHA_GE_128','opaque_source_pixels':len(part_pixels[bbox])})
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
