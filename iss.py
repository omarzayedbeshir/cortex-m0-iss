#!/usr/bin/env python3
"""iss.py -- CSCE 2303 Cortex-M0 simulator skeleton.   Run: python3 iss.py prog.dump"""
import sys
from cpu import CPU
import decoder 
import re
import argparse

MAX_INSTR = 100_000_000
ROM_BASE, ROM_SIZE = 0x00000000, 1 << 20       # 1 MB
RAM_BASE, RAM_SIZE = 0x20000000, 256 << 10     # 256 KB


rom = bytearray(ROM_SIZE)
ram = bytearray(RAM_SIZE)

# All sections like text and other
sections = {}

def fault(kind):
    print(f"FAULT {kind} at pc=0x{cpu.r[15]:08x}", file=sys.stderr)
    sys.exit(255)

def load_error(msg):
    print(f"load error: {msg}", file=sys.stderr)
    sys.exit(253)

def region(addr):
    """Return (buffer, offset) for a mapped address, or (None, 0)."""
    if ROM_BASE <= addr < ROM_BASE + ROM_SIZE:
        return rom, addr - ROM_BASE
    if RAM_BASE <= addr < RAM_BASE + RAM_SIZE:
        return ram, addr - RAM_BASE
    return None, 0


def read_mem(addr, size):                      # size = 1, 2 or 4
    if addr % size:
        fault("UNALIGNED")
    buf, off = region(addr)
    if buf is None:
        fault("BUS")
    return int.from_bytes(buf[off:off + size], "little")


def write_mem(addr, value, size):
    if addr % size:
        fault("UNALIGNED")
    buf, off = region(addr)
    if buf is not ram:                         # only RAM is writable
        fault("BUS")
    buf[off:off + size] = (value & ((1 << 8 * size) - 1)).to_bytes(size, "little")


def load_dump(path):
    """Load a `readelf -x` dump. A data line looks like
         '  0x00000100 094811df 0a2000f0 03f812df 002000df .H... ......'
    The 35 characters after the address hold up to 16 bytes; the rest is ASCII."""
    sections.clear()
    current = None
    try:
        lines = open(path).read().splitlines()
    except OSError as e:
        load_error(str(e))
    for lineno, line in enumerate(lines, 1):
        s = line.lstrip()
        m = re.match(r"\s*Hex dump of section '([^']+)':", line)
        if s.startswith("0x"):             # headers, blank lines
            addr = int(s[2:10], 16)
            data = bytes.fromhex(s[11:46])

            if (current is not None):
                sec = sections[current]
                if sec["start"] is None:
                    sec["start"] = addr
                sec["end"] = addr + len(data)
                    
            for b in data:
                buf, off = region(addr)
                if (buf is None):
                    load_error(f"{path}:{lineno}: address 0x{addr:08x} is outside ROM/RAM") 
                buf[off] = b
                addr += 1
        elif (m):
            current = m.group(1)
            sections[current] = {"start": None, "end": None}
        else: # if line is empty after we removed new lines and spaces or any of cases not above 
            continue

def reset():
    cpu.r[:] = [0] * 16
    cpu.N = cpu.Z = cpu.C = cpu.V = False
    cpu.instret = 0


    cpu.r[13] = read_mem(0, 4) & 0xFFFFFFFC # initial sp
    pc = read_mem(4, 4) # reset vector
    cpu.r[15] = pc # diagnostic uses the reset vector
    if not (pc & 1):
        fault("INVSTATE")
    cpu.r[15] = pc & ~1
    cpu.r[14] = 0xFFFFFFFF


def set_nz(x):
    cpu.N = x >> 31
    cpu.Z = int(x == 0)


def svc(n):
    if n == 0x00:                              # EXIT
        sys.stdout.flush()
        sys.exit(cpu.r[0] & 0xFF)
    elif n == 0x10:                            # PUTCHAR
        sys.stdout.buffer.write(bytes([cpu.r[0] & 0xFF]))
    elif n == 0x11:                            # PUTS
        a = cpu.r[0]
        while read_mem(a, 1) != 0:
            sys.stdout.buffer.write(bytes([read_mem(a, 1)]))
            a += 1
    elif n == 0x12:                            # PUTINT
        v = cpu.r[0] - (1 << 32) if cpu.r[0] & 0x80000000 else cpu.r[0]
        sys.stdout.buffer.write(str(v).encode("ascii"))
    # TODO: the other services in section 5 of the handout
    else:
        fault("UNDEFINED")


def step():
    """Execute one instruction. r[15] holds the address of the current
    instruction; an instruction that reads pc must see r[15] + 4."""
    pc = cpu.r[15]
    hw = read_mem(pc, 2)
    nxt = pc + 2
    hw2 = None
    if (hw >> 11) in (0b11101, 0b11110, 0b11111):  # first half of a 32-bit instruction
        hw2 = read_mem(pc + 2, 2)
        nxt = pc + 4

    try:
        instr = decoder.decode(hw, hw2) # return instruction decoded
    except decoder.DecodeFault as error:
        fault(str(error))

    #nxt = execute(instr, pc, nxt)

    cpu.r[15] = nxt & 0xFFFFFFFF
    cpu.instret += 1
    # TODO: write a trace line here when --trace is given (section 6)

def parse_args(argv):
    p = argparse.ArgumentParser(prog="iss")
    p.add_argument("--disasm", action="store_true")
    p.add_argument("--trace", metavar="FILE")
    p.add_argument("--max-instr", type=int, default=100_000_000)
    p.add_argument("--seed", type=int, default=2463534242)
    p.add_argument("--cpu", choices=("m0", "m0plus"), default="m0")
    p.add_argument("program")
    return p.parse_args(argv)

def text_range():
    sec = sections.get(".text")
    if not sec or sec["start"] is None:
        return None
    return sec["start"], sec["end"]

def read_code16(addr):
    buf, off = region(addr)
    if buf is None or off + 2 > len(buf):
        print(f"load error at 0x{addr:08x}", file=sys.stderr)
        sys.exit(253)
    return int.from_bytes(buf[off:off + 2], "little")

def disassemble_text():
    rng = text_range()
    if rng is None:
        print("no .text section", file=sys.stderr)
        sys.exit(253)

    pc, end = rng
    while pc < end:
        hw1 = read_code16(pc)

        if (hw1 >> 11) in (0b11101, 0b11110, 0b11111):
            hw2 = read_code16(pc + 2)
            enc = f"{hw1:04x}{hw2:04x}"
            text = decode32(pc, hw1, hw2)
            size = 4
        else:
            enc = f"{hw1:04x}"
            text = decode16(pc, hw1)
            size = 2

        try:
            instr = decoder.decode(hw1, hw2)
            text = decoder.disasm(instr, pc)
        except decoder.DecodeFault as err:
            fault(str(err))

        
        print(f"{pc:08x}: {enc} {text}")
        pc += size

cpu = CPU()

def main():
    # TODO: parse the options in section 6 
    global cpu
    args = parse_args(sys.argv[1:])


    load_dump(args.program)

    if args.disasm:
        disassemble_text()
        return

    reset()

    while True:
        if cpu.instret >= MAX_INSTR:
            print(f"LIMIT at pc=0x{cpu.r[15]:08x}", file=sys.stderr)
            sys.exit(254)
        step()



if __name__ == "__main__":
    main()
    
