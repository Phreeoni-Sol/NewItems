from pathlib import Path
import json
from PIL import Image
root=Path(__file__).resolve().parents[1]
def runs(values):
    count=0;last=False
    for value in values:
        if value and not last:count+=1
        last=value
    return count
checks=[]
for view in (1,4):
    im=Image.open(root/f'items/tfj_staff_02/view-{view}-readback.png').convert('RGBA')
    box=im.getchannel('A').getbbox();assert box
    ys=range(box[1],min(box[3],box[1]+max(3,(box[3]-box[1])//3)))
    rows=[{'y':y,'opaque_runs':runs([im.getpixel((x,y))[3]>0 for x in range(im.width)])} for y in ys]
    passed=sum(r['opaque_runs']==4 for r in rows)>=2
    checks.append({'id':'tfj_staff_02','view':view,'signature':'FOUR_SEPARATE_PRONGS_IN_FRONT_AND_REAR','status':'PASS_AUTHORING_SIGNATURE' if passed else 'RETOUCH_REQUIRED','rows':rows})
for view in range(1,5):
    im=Image.open(root/f'items/tfj_staff_02/view-{view}-readback.png').convert('RGBA')
    count=sum(a>0 and b>r+40 and b>g+10 for r,g,b,a in im.get_flattened_data())
    checks.append({'id':'tfj_staff_02','view':view,'signature':'BLUE_GEM_ACCENT_SURVIVES_PALETTE_REDUCTION','blue_pixels':count,'status':'PASS_AUTHORING_SIGNATURE' if count>=1 else 'RETOUCH_REQUIRED'})
def enclosed_area(im):
    transparent={(x,y) for y in range(im.height) for x in range(im.width) if im.getpixel((x,y))[3]==0}
    areas=[]
    while transparent:
        queue=[transparent.pop()];area=0;border=False
        while queue:
            x,y=queue.pop();area+=1;border|=x in (0,im.width-1) or y in (0,im.height-1)
            for p in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                if p in transparent:transparent.remove(p);queue.append(p)
        if not border:areas.append(area)
    return sorted(areas,reverse=True)
manifest=json.loads((root/'conversion-manifest.json').read_text(encoding='utf8'))
for row in manifest:
    if row['category']!='Bow':continue
    for view in (1,2):
        im=Image.open(root/f'items/{row["id"]}/view-{view}-readback.png').convert('RGBA')
        areas=enclosed_area(im)
        checks.append({'id':row['id'],'view':view,'signature':'BOW_LIMB_AND_CORD_ENCLOSE_VISIBLE_SPACE_IN_DIAGONAL_AUTHORING_VIEW','enclosed_areas':areas,'status':'PASS_AUTHORING_SIGNATURE' if areas and areas[0]>=3 else 'RETOUCH_REQUIRED'})
report={'scope':'Specific authoring silhouette signatures, not in-game validation; enclosure test uses 4-neighbor transparent connectivity','checks':checks,'runtime_ready':False}
(root/'reports/signature-validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report))
