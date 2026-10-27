"""Static ELF inventory only; never executes the artifact."""
from pathlib import Path
from elftools.elf.elffile import ELFFile
import hashlib

path = Path(__file__).parent / 'artifacts' / 'maind'
with path.open('rb') as stream:
    elf = ELFFile(stream)
    print('sha256', hashlib.sha256(path.read_bytes()).hexdigest())
    print('header', elf.header)
    for sec in elf.iter_sections():
        print('section', sec.name, hex(sec['sh_addr']), hex(sec['sh_offset']), sec['sh_size'])
    for name in ('.symtab', '.dynsym'):
        sec = elf.get_section_by_name(name)
        if sec is not None:
            print(name, sec.num_symbols())
            for sym in sec.iter_symbols():
                if any(key in sym.name.lower() for key in ('playpause', 'ledpattern', 'playbackcontrol', 'ledmanager', 'ledcontroller')):
                    print('symbol', hex(sym['st_value']), sym['st_size'], sym.name)
    for sec in elf.iter_sections():
        if sec['sh_type'] == 'SHT_NOBITS':
            continue
        data = sec.data()
        for key in (b'player_continue\0', b'player_pause\0', b'handleTogglePlayPause\0', b'handlePlayPause\0'):
            start = 0
            while (pos := data.find(key, start)) >= 0:
                print('string', key, 'section', sec.name, 'VA', hex(sec['sh_addr'] + pos), 'file', hex(sec['sh_offset'] + pos))
                start = pos + len(key)
