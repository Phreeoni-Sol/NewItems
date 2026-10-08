"""Read-only inspection of the extracted bank using the historical FFT layout.
No game writer or item binding. Round-trip check preserves every source byte.
"""
from pathlib import Path
import hashlib
import json
import struct
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parents[1]
SOURCE = PROJECT / 'work/effects-reference/0002.pac_battle_wep_spr.bin'
EXPECTED_SHA = '7a4c733e1654f9f1ff41e1281fd26fce894bd608bc1c95e1e4713aecdc0eff0a'
raw = SOURCE.read_bytes()
assert hashlib.sha256(raw).hexdigest() == EXPECTED_SHA
assert len(raw) == 85504
(ROOT / 'references').mkdir(parents=True, exist_ok=True)
banks = []
offset = 0
for name, height in [('weapon',256),('effect',256),('trap',144)]:
    size = 512 + 256 * height // 2
    bank = raw[offset:offset+size]
    palette_bytes, packed = bank[:512], bank[512:]
    indices = bytes(value for byte in packed for value in (byte & 15, byte >> 4))
    assert bytes(indices[i] | (indices[i+1] << 4) for i in range(0,len(indices),2)) == packed
    values = struct.unpack('<256H',palette_bytes)
    assert struct.pack('<256H',*values) == palette_bytes
    paths = []
    # Historical palette interpretation, not a declaration of runtime blend rules.
    for p in range(16):
        colors = []
        for j,v in enumerate(values[p*16:p*16+16]):
            colors.append(((v&31)<<3,((v>>5)&31)<<3,((v>>10)&31)<<3,0 if j==0 and v==0 else 255))
        im = Image.new('RGBA',(256,height)); im.putdata([colors[i] for i in indices])
        path = ROOT / 'references' / f'{name}-palette-{p:02}.png'
        im.save(path); paths.append(path.relative_to(ROOT).as_posix())
    board = Image.new('RGB',(4*530,4*(height*2+36)),(35,37,42))
    d = ImageDraw.Draw(board)
    for p,path in enumerate(paths):
        x,y=(p%4)*530,(p//4)*(height*2+36)
        d.text((x+8,y+4),f'{name} / historical palette {p:02}',fill='white')
        im=Image.open(ROOT/path).resize((512,height*2),Image.Resampling.NEAREST)
        board.paste(im,(x+8,y+28),im)
    board.save(ROOT/'references'/f'{name}-palette-board.jpg')
    banks.append({'bank':name,'offset':offset,'bytes':size,'width':256,'height':height,'palettes':16,'palette_words':list(values),'pngs':paths,'pixel_roundtrip':'PASS','palette_roundtrip':'PASS'})
    offset += size
assert offset == len(raw)
report = {'source':str(SOURCE.relative_to(PROJECT)),'source_sha256':EXPECTED_SHA,'source_bytes':len(raw),'interpretation':'HISTORICAL_LAYOUT_CONFIRMED_BY_SIZE_AND_BYTE_ROUNDTRIP_ONLY','runtime_rendering':'NOT_TESTED','enhanced_binding':'UNKNOWN','new_item_binding':'UNKNOWN','banks':banks}
(ROOT/'weapon-bank-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'banks':len(banks),'decoded_palettes':48,'source_unchanged':hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED_SHA,'roundtrip':'PASS','enhanced_binding':'UNKNOWN'}))
