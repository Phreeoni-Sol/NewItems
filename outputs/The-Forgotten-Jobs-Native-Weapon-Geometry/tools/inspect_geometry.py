"""Read-only diagnostics of extracted data against historical FFTPatcher layouts.
No runtime binding, sequence execution, or binary modification.
"""
from pathlib import Path
import hashlib, json, struct
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SIZES = [(8,8),(16,8),(16,16),(16,24),(24,8),(24,16),(24,24),(32,8),(32,16),(32,24),(32,32),(32,40),(48,16),(40,32),(48,48),(56,56)]
def sha(b): return hashlib.sha256(b).hexdigest()
def u32(b,p): return struct.unpack_from('<I',b,p)[0]
spr = (ROOT/'native/0002.pac_battle_wep_spr.bin').read_bytes()
assert len(spr)==85504
palette=[]
for i in range(16):
    v=struct.unpack_from('<H',spr,i*2)[0]
    palette.append(((v&31)*255//31,((v>>5)&31)*255//31,((v>>10)&31)*255//31,0 if v==0 else 255))
bank=Image.new('RGBA',(256,256))
pix=[]
for v in spr[512:33280]: pix.extend((palette[v&15],palette[v>>4]))
bank.putdata(pix)
(ROOT/'review').mkdir(exist_ok=True)
result={'status':'HISTORICAL_LAYOUT_DIAGNOSTIC_ONLY','runtime_ready':False,'item_sprite_binding':'UNKNOWN','rotation_runtime_semantics':'UNKNOWN','banks':[]}
for name in ('wep1','wep2'):
    path=ROOT/f'native/0002.pac_battle_{name}_shp.bin'
    data=path.read_bytes()
    offsets=[0]; cursor=0x48
    while True:
        value=u32(data,cursor);cursor+=4
        if value==0:break
        offsets.append(value)
        assert cursor<=0x846
    rows=[]
    for idx,off in enumerate(offsets):
        pos=0x846+off
        assert pos+6<=len(data)
        rotation,x,y,flags=struct.unpack_from('<HbbH',data,pos)
        assert struct.pack('<HbbH',rotation,x,y,flags)==data[pos:pos+6]
        tx=(flags&31)*8;ty=((flags>>5)&31)*8
        w,h=SIZES[(flags>>10)&15]
        rows.append({'frame_index':idx,'record_offset':pos,'record_hex':data[pos:pos+6].hex(),'rotation_raw':rotation,'signed_xy':[x,y],'historical_editor_location':[x+53,y+118],'atlas_rectangle':[tx,ty,w,h],'flip_x':bool(flags&0x4000),'flip_y':bool(flags&0x8000),'inside_weapon_bank':tx+w<=256 and ty+h<=256})
    unique=list(dict.fromkeys(tuple(r['atlas_rectangle']) for r in rows))
    # Contact sheet shows atlas cuts only; deliberately no inferred rotations or unit placement.
    board=Image.new('RGB',(800,((len(unique)+7)//8)*110),(31,30,28));draw=ImageDraw.Draw(board)
    for i,(x,y,w,h) in enumerate(unique):
        crop=bank.crop((x,y,x+w,y+h));crop.thumbnail((76,76),Image.Resampling.NEAREST)
        xx=(i%8)*100;yy=(i//8)*110
        board.paste(crop,(xx+(100-crop.width)//2,yy+5),crop)
        draw.text((xx+4,yy+83),f'{x},{y} {w}x{h}',fill='white')
    board.save(ROOT/f'review/{name}-atlas-crops.png')
    seq=(ROOT/f'native/0002.pac_battle_{name}_seq.bin').read_bytes()
    seqoffs=[]
    for i in range(256):
        v=u32(seq,4+i*4)
        if v==0xffffffff:break
        seqoffs.append(v)
    spans=[]
    for i,off in enumerate(seqoffs):
        start=0x406+off;end=0x406+seqoffs[i+1] if i+1<len(seqoffs) else len(seq)
        valid=0x406<=start<=end<=len(seq)
        spans.append({'sequence_index':i,'start':start,'end':end,'bytes':end-start,'bounds_valid':valid,'raw_hex':seq[start:end].hex() if valid else None})
    entry={'name':name,'shape_sha256':sha(data),'shape_bytes':len(data),'frame_count_historical_layout':len(rows),'unique_rectangles':len(unique),'out_of_bank_rectangles':sum(not r['inside_weapon_bank'] for r in rows),'rotation_raw_values':sorted(set(r['rotation_raw'] for r in rows)),'record_roundtrip':'PASS','frames':rows,'sequence_sha256':sha(seq),'sequence_bytes':len(seq),'sequence_offset_count':len(seqoffs),'sequence_spans':spans,'sequence_bounds_valid':all(r['bounds_valid'] for r in spans),'sequence_opcodes':'NOT_INTERPRETED'}
    result['banks'].append(entry)
(ROOT/'reports/geometry.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps([{k:v for k,v in b.items() if k not in ('frames','sequence_spans')} for b in result['banks']],indent=2))
