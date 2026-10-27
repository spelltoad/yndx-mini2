"""Dump selected Thumb ranges with PC-relative literal comments (static only)."""
import sys, struct
from pathlib import Path
from elftools.elf.elffile import ELFFile
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_LITTLE_ENDIAN
r=Path(__file__).parent
with (r/'artifacts/maind').open('rb') as f:
 e=ELFFile(f); sections=[(s['sh_addr'],s.data()) for s in e.iter_sections() if s['sh_addr'] and s['sh_type']!='SHT_NOBITS']
 def raw(a,n):
  for b,d in sections:
   if b<=a and a+n<=b+len(d): return d[a-b:a-b+n]
 def word(a):
  d=raw(a,4); return struct.unpack('<I',d)[0] if d else None
 def string(a):
  d=raw(a,1)
  if not d: return ''
  for b,data in sections:
   if b<=a<b+len(data):
    x=data[a-b:a-b+220].split(b'\0')[0]
    if x and all(c in (9,10,13) or 32<=c<127 for c in x): return repr(x.decode())
  return ''
 cs=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_LITTLE_ENDIAN); cs.skipdata=True
 for arg in sys.argv[1:]:
  a,z=[int(n,16) for n in arg.split(':')]; print('\nRANGE',hex(a),hex(z)); regs={}
  for addr,size,m,op in cs.disasm_lite(raw(a,z-a),a):
   comment=''; parts=[p.strip() for p in op.split(',')]; dest=parts[0]
   if m in ('ldr','ldr.w') and '[pc, #' in op:
    off=int(op.split('#')[1].split(']')[0],0); v=word(((addr+4)&~3)+off)
    if v is not None: regs[dest]=v; comment=f'literal {v:#x}'
   elif m=='add' and len(parts)==2 and parts[1]=='pc' and dest in regs:
    v=(regs[dest]+addr+4)&0xffffffff; regs[dest]=v; comment=f'PC target {v:#x} '+string(v)
   else:
    if m not in ('str','str.w','strb','strh','cmp','tst','push','nop'): regs.pop(dest,None)
   print(f'{addr:08x} {m:10} {op:42} {comment}')
