#!/usr/bin/env python3
"""iss.py -- CSCE 2303 Cortex-M0 simulator skeleton.   Run: python3 iss.py prog.dump"""
import sys

ROM_BASE, ROM_SIZE = 0x00000000, 1 << 20       # 1 MB
RAM_BASE, RAM_SIZE = 0x20000000, 256 << 10     # 256 KB
MAX_INSTR = 100_000_000

rom = bytearray(ROM_SIZE)
ram = bytearray(RAM_SIZE)
r = [0] * 16                    # r[13] = sp, r[14] = lr, r[15] = pc
N = Z = C = V = 0               # the APSR flags
instret = 0


def fault(kind):
    print(f"FAULT {kind} at pc=0x{r[15]:08x}", file=sys.stderr)
    sys.exit(255)


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
    try:
        lines = open(path).read().splitlines()
    except OSError as e:
        print(e, file=sys.stderr)
        sys.exit(253)
    for line in lines:
        s = line.lstrip()
        if not s.startswith("0x"):             # headers, blank lines
            continue
        addr = int(s[2:10], 16)
        for byte in bytes.fromhex(s[11:46]):
            buf, off = region(addr)
            if buf is None:
                print("load error", file=sys.stderr)
                sys.exit(253)
            buf[off] = byte
            addr += 1


def reset():
    r[13] = read_mem(0, 4)                     # initial sp
    pc = read_mem(4, 4)                        # reset vector
    r[15] = pc                                 # diagnostic uses the reset vector
    if not pc & 1:
        fault("INVSTATE")
    r[15] = pc & ~1
    r[14] = 0xFFFFFFFF


def set_nz(x):
    global N, Z
    N = x >> 31
    Z = int(x == 0)


def svc(n):
    if n == 0x00:                              # EXIT
        sys.stdout.flush()
        sys.exit(r[0] & 0xFF)
    elif n == 0x10:                            # PUTCHAR
        sys.stdout.buffer.write(bytes([r[0] & 0xFF]))
    elif n == 0x11:                            # PUTS
        a = r[0]
        while read_mem(a, 1) != 0:
            sys.stdout.buffer.write(bytes([read_mem(a, 1)]))
            a += 1
    elif n == 0x12:                            # PUTINT
        v = r[0] - (1 << 32) if r[0] & 0x80000000 else r[0]
        sys.stdout.buffer.write(str(v).encode("ascii"))
    # TODO: the other services in section 5 of the handout
    else:
        fault("UNDEFINED")


def step():
    """Execute one instruction. r[15] holds the address of the current
    instruction; an instruction that reads pc must see r[15] + 4."""
    global instret
    pc = r[15]
    hw = read_mem(pc, 2)
    nxt = pc + 2

    if (hw >> 11) in (0b11101, 0b11110, 0b11111):    # first half of a 32-bit instruction
        hw2 = read_mem(pc + 2, 2)
        nxt = pc + 4
        fault("UNDEFINED")                            # TODO: BL, from hw and hw2
    elif (hw & 0xF800) == 0x2000:                     # MOVS Rd, #imm8
        rd = (hw >> 8) & 7
        r[rd] = hw & 0xFF
        set_nz(r[rd])
    elif (hw & 0xF800) == 0xE000:                     # B label (unconditional)
        off = hw & 0x7FF
        if off & 0x400:
            off -= 0x800                              # sign-extend 11 bits
        nxt = pc + 4 + off * 2
    elif (hw & 0xFF00) == 0xDF00:                     # SVC #imm8
        svc(hw & 0xFF)
    # TODO: the other instructions in section 4 of the handout
    else:
        fault("UNDEFINED")

    r[15] = nxt & 0xFFFFFFFF
    instret += 1
    # TODO: write a trace line here when --trace is given (section 6)


def main():
    # TODO: parse the options in section 6
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} PROGRAM", file=sys.stderr)
        sys.exit(2)
    load_dump(sys.argv[1])
    reset()
    while True:
        if instret >= MAX_INSTR:
            print(f"LIMIT at pc=0x{r[15]:08x}", file=sys.stderr)
            sys.exit(254)
        step()


if __name__ == "__main__":
    main()
