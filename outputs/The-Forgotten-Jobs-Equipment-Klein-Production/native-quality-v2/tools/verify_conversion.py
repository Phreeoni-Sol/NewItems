"""Independent byte reader for authored payloads, plus round-trip of local reference."""
from pathlib import Path
import sys,json,struct,hashlib
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parent))
from weapon_codec import encode_container,decode_container,encode_bank,decode_bank
root=Path(__file__).resolve().parents[1];project=root.parents[1]
rows=json.loads((root/'conversion-manifest.json').read_text(encoding='utf8'))
checks=[]
# Known nibble-order fixture and explicit malformed inputs, independent of the art.
sample=bytes(range(16))*4096
bank=encode_bank(list(range(256)),sample,256,256)
assert bank[512:520]==bytes([0x10,0x32,0x54,0x76,0x98,0xba,0xdc,0xfe])
assert decode_bank(bank,256,256)==(list(range(256)),sample)
for bad in (bank[:-1],bank+b'\0'):
    try:decode_bank(bad,256,256)
    except ValueError:pass
    else:raise AssertionError('Bad bank size accepted')
for row in rows:
    folder=root/'items'/row['id'];raw=(folder/'weapon-authoring.wep.spr.bin').read_bytes()
    assert len(raw)==85504 and hashlib.sha256(raw).hexdigest()==row['sha256']
    assert raw[33280:]==bytes(52224)
    assert raw[:33280]==(folder/'weapon-bank.spr.bin').read_bytes()
    # Read directly from bytes, without using the encoder's decoder or generated PNG palette.
    palette=[int.from_bytes(raw[2*i:2*i+2],'little') for i in range(16)]
    assert palette[0]==0 and all(0<w<0x8000 for w in palette[1:])
    assert all(raw[32*i:32*i+32]==raw[:32] for i in range(16))
    def color(index):
        word=palette[index]
        return ((word%32)*255//31,((word//32)%32)*255//31,((word//1024)%32)*255//31,255 if index else 0)
    pixels=[]
    for position in range(65536):
        value=raw[512+position//2];index=(value>>(4*(position%2)))&15
        pixels.append(color(index))
    image=Image.new('RGBA',(256,256));image.putdata(pixels)
    assert image.tobytes()==Image.open(folder/'atlas-readback.png').convert('RGBA').tobytes()
    for frame in row['frames']:
        x,y,w,h=frame['rectangle']
        assert x%8==0 and y%8==0 and x+w<=256 and y+h<=256
        expected=Image.open(root/frame['readback_png']).convert('RGBA')
        assert image.crop((x,y,x+w,y+h)).tobytes()==expected.tobytes()
        assert set(expected.getchannel('A').get_flattened_data())<={0,255}
        assert len(set(expected.get_flattened_data()))<=16
    assert row['runtime_ready'] is False and row['native_sprite_id'] is None and row['native_palette_id'] is None
    checks.append({'id':row['id'],'independent_byte_readback':'PASS','visible_views':len(row['frames'])})
fixture=project/'outputs/The-Forgotten-Jobs-Native-Weapon-Geometry/native/0002.pac_battle_wep_spr.bin'
native_status='NOT_PRESENT'
if fixture.exists():
    data=fixture.read_bytes()
    assert hashlib.sha256(data).hexdigest()=='7a4c733e1654f9f1ff41e1281fd26fce894bd608bc1c95e1e4713aecdc0eff0a'
    assert encode_container(decode_container(data))==data
    native_status='PASS_BYTE_IDENTICAL_ROUNDTRIP_READ_ONLY'
report={'status':'PASS_ENCODING_ONLY','equipment':len(rows),'views':sum(len(x['frames']) for x in rows),'independent_pixel_readback':'PASS','nibble_order_fixture':'PASS','invalid_length_rejection':'PASS','native_reference':native_status,'game_test':'NOT_RUN','runtime_ready':False,'new_runtime_ids':0,'checks':checks}
(root/'reports/encoding-validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k!='checks'}))
