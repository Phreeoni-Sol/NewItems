"""Crop the generated correction; do not draw, recolor, or repair pixels."""
from pathlib import Path
import json, hashlib
from PIL import Image
root=Path(__file__).resolve().parents[1]
import sys
ident=sys.argv[1] if len(sys.argv)>1 else 'tfj_bow_10'
filename=sys.argv[2] if len(sys.argv)>2 else 'tfj_bow_10-attempt-02.png'
assert ident.replace('_','').isalnum() and Path(filename).name==filename
p=root/'corrections'/filename
im=Image.open(p).convert('RGBA')
w,h=im.size
mask=im.getchannel('A').point(lambda a:255 if a>16 else 0)
splits=[]
for axis,n in [('x',w),('y',h)]:
    empty=[k for k in range(int(n*.35),int(n*.65)) if mask.crop((k,0,k+1,h) if axis=='x' else (0,k,w,k+1)).getbbox() is None]
    assert empty, 'No genuinely empty center gutter'
    splits.append(min(empty,key=lambda k:abs(k-n/2)))
x,y=splits
dest=root/'corrections/selected'
(dest/'sources').mkdir(parents=True,exist_ok=True)
(dest/'poses').mkdir(exist_ok=True)
(dest/'sources'/f'{ident}.png').write_bytes(p.read_bytes())
for i,box in enumerate([(0,0,x,y),(x,0,w,y),(0,y,x,h),(x,y,w,h)],1):
    cell=im.crop(box)
    bbox=cell.getchannel('A').point(lambda a:255 if a>16 else 0).getbbox()
    assert bbox
    cell.crop(bbox).save(dest/f'poses/{ident}-{i}-source.png')
selected=root/'corrections/selected-overrides.json'
record=json.loads(selected.read_text(encoding='utf8')) if selected.exists() else []
record=[r for r in record if r['id']!=ident]+[{'id':ident,'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'status':'CANDIDATE_PENDING_NATIVE_REVIEW','split_xy':splits}]
(root/'corrections/selected-overrides.json').write_text(json.dumps(record,indent=2),encoding='utf8')
print(json.dumps(record))
