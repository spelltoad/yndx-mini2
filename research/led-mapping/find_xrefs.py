"""Heuristic Thumb PC-relative string xrefs, not a complete decompiler."""
from pathlib import Path
import struct, re, bisect, json
from elftools.elf.elffile import ELFFile
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_LITTLE_ENDIAN

root = Path(__file__).parent
with (root/'artifacts/maind').open('rb') as f:
    elf = ELFFile(f)
    text = elf.get_section_by_name('.text')
    base, code = text['sh_addr'], text.data()
    sections = [(s['sh_addr'], s.data()) for s in elf.iter_sections() if s['sh_type'] != 'SHT_NOBITS' and s['sh_addr']]
    def word(addr):
        for b,d in sections:
            if b <= addr and addr+4 <= b+len(d): return struct.unpack_from('<I',d,addr-b)[0]
    rd = elf.get_section_by_name('.rodata'); rb, data = rd['sh_addr'], rd.data()
    targets = {}
    for match in re.finditer(rb'[^\x00]{0,100}(?:player_continue|player_pause|handleTogglePlayPause|handlePlayPause)\x00', data):
        # Record only complete strings and their actual starting addresses.
        raw=match.group()[:-1]
        targets[rb+match.start()] = raw.decode('utf-8',errors='replace')
    ex = elf.get_section_by_name('.ARM.exidx')
    bounds=[]
    for i in range(0,ex.data_size,8):
        n=struct.unpack_from('<I',ex.data(),i)[0]&0x7fffffff
        if n&0x40000000: n-=0x80000000
        bounds.append((ex['sh_addr']+i+n)&~1)
    bounds.sort()
    print('targets',json.dumps({hex(k):v for k,v in targets.items()}))
    cs=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_LITTLE_ENDIAN); cs.skipdata=True
    regs={}; recent=[]; hits=[]
    for a,size,m,op in cs.disasm_lite(code,base):
        recent.append((hex(a),m,op)); recent=recent[-12:]
        dest=op.split(',')[0].strip()
        result=None
        l=re.fullmatch(r'(r\d+|ip|sl|fp|lr), \[pc, #(0x[0-9a-f]+|\d+)\]',op)
        if m in ('ldr','ldr.w') and l:
            val=word(((a+4)&~3)+int(l[2],0))
            if val is not None: result=val
        elif m in ('movw','movt'):
            v=re.fullmatch(r'(r\d+|ip|sl|fp|lr), #(0x[0-9a-f]+|\d+)',op)
            if v: result=int(v[2],0) if m=='movw' else ((regs.get(dest,(0,0))[0]&65535)|(int(v[2],0)<<16))
        elif m in ('add','add.w','adds'):
            parts=[x.strip() for x in op.split(',')]
            if len(parts)==2 and parts[1]=='pc' and dest in regs and a-regs[dest][1]<64:
                result=(regs[dest][0]+a+4)&0xffffffff
            elif len(parts)==3 and parts[1]=='pc' and parts[2].startswith('#'):
                result=(((a+4)&~3)+int(parts[2][1:],0))&0xffffffff
        if result is not None:
            regs[dest]=(result,a)
            if result in targets:
                bi=bisect.bisect_right(bounds,a)-1
                entry={'address':hex(a),'target':hex(result),'string':targets[result], 'function_start':hex(bounds[bi]),'function_end':hex(bounds[bi+1]) if bi+1<len(bounds) else None,'context':recent[:]}
                hits.append(entry); print(json.dumps(entry))
        elif m not in ('cmp','tst','str','str.w','strb','strh','push','nop','it','itt','ite'):
            regs.pop(dest,None)
        if m in ('b','b.w','bx','bl','blx','pop'): regs.clear()
    (root/'xrefs.json').write_text(json.dumps(hits,indent=2),encoding='utf-8')
    print('hits',len(hits))
