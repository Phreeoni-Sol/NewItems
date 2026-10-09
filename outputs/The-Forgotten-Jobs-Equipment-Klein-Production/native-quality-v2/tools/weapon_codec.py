"""Observed weapon SPR pixel/palette layout; no SHP, SEQ, binding or game writes."""
import struct
PROFILES=((256,256),(256,256),(256,144))
def encode_bank(words,indices,width,height):
    if len(words)!=256 or len(indices)!=width*height:raise ValueError('Invalid bank dimensions')
    if any(not 0<=v<=65535 for v in words) or any(not 0<=v<16 for v in indices):raise ValueError('Out-of-range palette or index')
    return struct.pack('<256H',*words)+bytes(indices[i]|(indices[i+1]<<4) for i in range(0,len(indices),2))
def decode_bank(data,width,height):
    if len(data)!=512+width*height//2:raise ValueError('Invalid bank size')
    words=list(struct.unpack('<256H',data[:512]))
    indices=bytearray(width*height)
    for i,value in enumerate(data[512:]):indices[2*i]=value&15;indices[2*i+1]=value>>4
    return words,bytes(indices)
def encode_container(banks):
    if len(banks)!=3:raise ValueError('Three observed banks required')
    return b''.join(encode_bank(words,pixels,*size) for (words,pixels),size in zip(banks,PROFILES))
def decode_container(data):
    if len(data)!=85504:raise ValueError('Observed WEP SPR is 85504 bytes')
    banks=[];offset=0
    for w,h in PROFILES:
        size=512+w*h//2;banks.append(decode_bank(data[offset:offset+size],w,h));offset+=size
    return banks
def rgb555(rgb):
    r,g,b=(int(c)//8 for c in rgb)
    return (r|(g<<5)|(b<<10)) or 1
def rgba555(word):
    return ((word&31)*255//31,((word>>5)&31)*255//31,((word>>10)&31)*255//31,0 if word==0 else 255)
