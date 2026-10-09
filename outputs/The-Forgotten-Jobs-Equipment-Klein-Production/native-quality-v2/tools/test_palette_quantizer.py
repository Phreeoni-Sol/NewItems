from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parent))
from palette_quantizer import quantize_words
from weapon_codec import rgba555,rgb555
root=Path(__file__).resolve().parents[1]
colors=[(240,210,150)]*1000+[(80,40,20)]*900+[(16,144,248)]*4
words=quantize_words(colors)
assert words==quantize_words(colors), 'Nondeterministic output'
assert len(words)<=15 and all(0<w<32768 for w in words)
assert any(b>r+40 and b>g+10 for r,g,b,a in map(rgba555,words)), 'Rare blue accent was lost'
assert quantize_words([(0,0,0)]*100)==[1]
many=[(r,g,b) for r in range(0,256,32) for g in range(0,256,32) for b in range(0,256,32)]
assert len(quantize_words(many))==15
report={'rare_blue_accent':'PASS','determinism':'PASS','opaque_black_preserved_as_nontransparent_word':'PASS','fifteen_opaque_colors_maximum':'PASS','rgb555_and_zero_reservation':'PASS'}
(root/'reports/palette-validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report))
