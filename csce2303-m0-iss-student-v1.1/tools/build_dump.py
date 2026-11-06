#!/usr/bin/env python3
"""Build a course Thumb program with GNU Arm and write .dump and .objdump files.

python3 tools/build_dump.py templates/c_template.c --toolchain /path/to/toolchain/bin
The script itself needs only Python 3.8+. GNU Arm GCC and binutils are needed only for this optional offline build.
No installation or environment changes are made by this script.
"""
import argparse
from pathlib import Path
import shutil
import subprocess
import sys

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('source', type=Path)
    ap.add_argument('--toolchain', type=Path, help='GNU Arm bin directory (otherwise use PATH)')
    a = ap.parse_args()
    source = a.source.resolve()
    if source.suffix not in ('.c', '.s', '.S'):
        ap.error('source must be .c, .s or .S')
    if not source.is_file(): ap.error('source file does not exist')
    def tool(name):
        base = 'arm-none-eabi-' + name
        if a.toolchain:
            for suffix in ('', '.exe'):
                p = a.toolchain / (base + suffix)
                if p.is_file(): return str(p.resolve())
            ap.error(f'{base} not found in {a.toolchain}')
        result = shutil.which(base)
        if not result: ap.error(f'{base} not found; supply --toolchain with its bin directory')
        return result
    gcc, readelf, objdump = (tool(n) for n in ('gcc','readelf','objdump'))
    print(subprocess.check_output([gcc,'--version'], text=True).splitlines()[0])
    common = ['-mcpu=cortex-m0','-mthumb']
    if source.suffix=='.c':
        flags=['-O2','-ffreestanding','-fno-builtin','-fno-stack-protector','-nostdlib']
    else: flags=['-nostdlib','-x','assembler']
    link=['-Wl,--section-start=.vectors=0','-Wl,-Ttext=0x100','-Wl,-Tdata=0x20000000']
    elf=source.with_suffix('.elf')
    subprocess.run([gcc,*common,*flags,*link,str(source),'-o',str(elf)],check=True)
    dump=subprocess.run([readelf,'-x','.vectors','-x','.text','-x','.rodata','-x','.data',str(elf)],capture_output=True,check=True)
    source.with_suffix('.dump').write_bytes(dump.stdout)
    dis=subprocess.check_output([objdump,'-d',str(elf)])
    source.with_suffix('.objdump').write_bytes(dis)
    print(source.with_suffix('.dump'))
    print(source.with_suffix('.objdump'))

if __name__=='__main__':
    try: main()
    except subprocess.CalledProcessError as e:
        print(f'build failed (exit {e.returncode})',file=sys.stderr)
        sys.exit(1)
