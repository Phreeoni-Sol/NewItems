from pathlib import Path
import sys,json,hashlib,math
from collections import Counter,deque
from PIL import Image,ImageDraw
sys.path.insert(0,str(Path(__file__).resolve().parent))
from weapon_codec import encode_bank,encode_container,decode_container,rgb555,rgba555
root=Path(__file__).resolve().parents[1];project=root.parents[1]
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for folder in ('items','reports','review'):(root/folder).mkdir(parents=True,exist_ok=True)
geometry=read(project/'outputs/The-Forgotten-Jobs-Native-Weapon-Geometry/reports/geometry.json')
sizes=sorted({tuple(f['atlas_rectangle'][2:]) for b in geometry['banks'] for f in b['frames']})
assert sizes==[(16,16),(16,24),(24,8),(24,16),(24,24),(32,16),(32,24),(48,16)]
inputs=[]
for folder in ('The-Forgotten-Jobs-Retouch-38-Exceptional-Equipment','The-Forgotten-Jobs-Ordinary-Combat-Lot-19'):
    src=project/'outputs'/folder
    for item in read(src/'selected-alternatives.json'):
        inputs.append({'id':item['id'],'name':item.get('name',item.get('name_fr')),'category':item['category'],'folder':src,'source_sha':item.get('source_sha256',item.get('sha256'))})
src=project/'outputs/The-Forgotten-Jobs-Combat-Completion-88'
for item in read(src/'review/measurements.json'):
    if len(item['poses'])==4:inputs.append({'id':item['id'],'name':item['name'],'category':item['category'],'folder':src,'source_sha':item['sha256']})
assert len({x['id'] for x in inputs})==len(inputs)
def components(im):
    points={(x,y) for y in range(im.height) for x in range(im.width) if im.getpixel((x,y))[3]>0};counts=[]
    while points:
        q=[points.pop()];n=0
        while q:
            x,y=q.pop();n+=1
            for dx,dy in ((-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)):
                p=(x+dx,y+dy)
                if p in points:points.remove(p);q.append(p)
        counts.append(n)
    return sorted(counts,reverse=True)
rows=[]
for item in inputs:
    ident=item['id'];src=item['folder'];dest=root/'items'/ident;dest.mkdir(exist_ok=True)
    assert sha(src/'sources'/f'{ident}.png')==item['source_sha']
    source_crops=[Image.open(src/'poses'/f'{ident}-{i}-source.png').convert('RGBA') for i in range(1,5)]
    frame_images=[];frames=[]
    # A single sampling scale per equipment preserves relative source proportions.
    # Independent fitting enlarged horizontal views much more than diagonal ones.
    pose_limits=[max(min((w-2)/im.width,(h-2)/im.height) for w,h in sizes) for im in source_crops]
    common_scale=min(pose_limits)
    for i,im in enumerate(source_crops):
        # Deterministic format adaptation only: faithful nearest-neighbor sampling, no drawn repairs.
        scaled_size=(max(1,round(im.width*common_scale)),max(1,round(im.height*common_scale)))
        fitting=[(w,h) for w,h in sizes if scaled_size[0]<=w-2 and scaled_size[1]<=h-2]
        assert fitting
        w,h=min(fitting,key=lambda s:(s[0]*s[1],s[0]+s[1]))
        small=im.resize(scaled_size,Image.Resampling.NEAREST)
        canvas=Image.new('RGBA',(w,h));canvas.paste(small,((w-small.width)//2,(h-small.height)//2))
        frame_images.append(canvas)
        frames.append({'view':i+1,'rectangle':[i*64,0,w,h],'source_size':list(im.size),'resampled_size':list(small.size),'sampling_scale':common_scale,'scale_policy':'ONE_SCALE_PER_EQUIPMENT','hand_anchor':'UNKNOWN','pose_runtime_semantics':'UNKNOWN'})
    colors=[p[:3] for im in frame_images for p in im.get_flattened_data() if p[3]>=128]
    assert colors
    strip=Image.new('RGB',(len(colors),1));strip.putdata(colors)
    paletted=strip.quantize(colors=15,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE)
    flat=paletted.getpalette();used=sorted(set(paletted.get_flattened_data()))
    words=[0]+list(dict.fromkeys(rgb555(tuple(flat[n*3:n*3+3])) for n in used))
    words+=([words[-1]]*(16-len(words)));assert len(words)==16
    rgba=[rgba555(w) for w in words]
    atlas=Image.new('P',(256,256));atlas.putpalette([c for color in rgba for c in color[:3]]+[0]*(768-48));atlas.info['transparency']=0
    errors=[];rgba_atlas=Image.new('RGBA',(256,256))
    for i,im in enumerate(frame_images):
        pixels=[]
        for pixel in im.get_flattened_data():
            if pixel[3]<128:pixels.append(0);continue
            j=min(range(1,16),key=lambda j:sum((pixel[k]-rgba[j][k])**2 for k in range(3)))
            pixels.append(j);errors.append(sum((pixel[k]-rgba[j][k])**2 for k in range(3))/3)
        indexed=Image.new('P',im.size);indexed.putpalette(atlas.getpalette());indexed.putdata(pixels);indexed.info['transparency']=0
        indexed.save(dest/f'view-{i+1}-indexed.png')
        preview=Image.new('RGBA',im.size);preview.putdata([rgba[p] for p in pixels]);preview.save(dest/f'view-{i+1}-readback.png')
        atlas.paste(indexed,(i*64,0));rgba_atlas.paste(preview,(i*64,0))
        cc=components(preview)
        frames[i].update(indexed_png=f'items/{ident}/view-{i+1}-indexed.png',readback_png=f'items/{ident}/view-{i+1}-readback.png',connected_component_sizes=cc,visible_pixels=sum(cc),has_multiple_components=len(cc)>1)
    palette_words=words*16;indices=bytes(atlas.get_flattened_data())
    banks=[(palette_words,indices),([0]*256,bytes(256*256)),([0]*256,bytes(256*144))]
    binary=encode_container(banks)
    assert decode_container(binary)==banks
    (dest/'weapon-authoring.wep.spr.bin').write_bytes(binary)
    (dest/'weapon-bank.spr.bin').write_bytes(encode_bank(palette_words,indices,256,256))
    atlas.save(dest/'atlas-indexed.png');rgba_atlas.save(dest/'atlas-readback.png')
    row={'id':ident,'name':item['name'],'category':item['category'],'source':str((src/'sources'/f'{ident}.png').relative_to(project)),'source_sha256':item['source_sha'],'encoding':'OBSERVED_WEP_SPR_3_BANK_LAYOUT','encoding_roundtrip':'PASS','runtime_ready':False,'visual_review':'PENDING','pixel_retouched':False,'palette_rgb555':words,'palette_slots':'Same local palette repeated 16 times; not allocated runtime CLUT IDs','alpha_policy':'<128 maps to transparent index 0, >=128 to opaque indices 1..15; bit15 zero; authoring conversion rule','rms_rgb_error':round(math.sqrt(sum(errors)/len(errors)),3),'frames':frames,'native_item_id':None,'native_sprite_id':None,'native_palette_id':None,'hand_anchor':'UNKNOWN','SHP':'NOT_CREATED','SEQ':'NOT_CREATED','atlas_layout':'Four independent views at x=0,64,128,192; observed rectangle sizes; placement is an authoring proposal','other_banks':'Zero-filled authoring banks, never overwrite stock WEP with this file','sha256':sha(dest/'weapon-authoring.wep.spr.bin')}
    (dest/'layout.json').write_text(json.dumps(row,ensure_ascii=False,indent=2),encoding='utf8');rows.append(row)
(root/'conversion-manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
for start in range(0,len(rows),8):
    board=Image.new('RGB',(1100,len(rows[start:start+8])*150),(35,33,30));draw=ImageDraw.Draw(board)
    for j,row in enumerate(rows[start:start+8]):
        y=j*150;draw.text((12,y+8),row['id']+' / '+row['name'],fill='white')
        for k,f in enumerate(row['frames']):
            im=Image.open(root/f['readback_png']).convert('RGBA');im=im.resize((im.width*4,im.height*4),Image.Resampling.NEAREST)
            board.paste(im,(20+k*270,y+35),im)
    board.save(root/f'review/native-{start//8+1:02d}.png')
print(json.dumps({'equipment_encoded':len(rows),'views':len(rows)*4,'multiple_component_views':sum(f['has_multiple_components'] for r in rows for f in r['frames']),'visual_review':'PENDING','runtime_ready':False}))
