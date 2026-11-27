#!/usr/bin/env python3
"""iss.py -- CSCE 2303 Cortex-M0 simulator skeleton.   Run: python3 iss.py prog.dump"""
import sys
import argparse
import decoder
from cpu import CPU, execute
from Memory import *
import Memory
from contextlib import nullcontext
import re
import alu
from instruction import INSTRUCTION, Op

cpu = CPU()



# All sections like text and other
sections = {}

def fault(kind):
    print(f"FAULT {kind} at pc=0x{cpu.r[15]:08x}", file=sys.stderr)
    sys.exit(255)

def load_error(msg):
    print(f"load error: {msg}", file=sys.stderr)
    sys.exit(253)





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

stdin_data = None
std_pointer = 0

# i hate re, if someone finds an issue with it plz tell me
INTEGER_INPUT = re.compile(rb"[ \t\n\r\v\f]*([+-]?[0-9]+)?")


def svc(n):
    global stdin_data, std_pointer
    
    if n == 0x00:                              # EXIT
        return cpu.r[0] & 0xFF
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
    elif (n == 0x13):
        value = cpu.r[0] & 0xFFFFFFFF
        sys.stdout.buffer.write(f"0x{value:08X}".encode("ascii"))
    elif (n == 0x14):
        if (stdin_data is None):
            stdin_data = sys.stdin.buffer.read()
        cpu.r[0] = 0xFFFFFFFF
        if (std_pointer < len(stdin_data)):
            cpu.r[0] = stdin_data[std_pointer]
            std_pointer += 1
    elif (n == 0x15):
        if (stdin_data is None):
            stdin_data = sys.stdin.buffer.read()
        match = INTEGER_INPUT.match(stdin_data, std_pointer)
        std_pointer = match.end()
        token = match.group(1)
        
        value = 0
        if (token):
            value = int(token)
        cpu.r[0] = value & 0xFFFFFFFF
    elif n == 0x22:                            # READ
        descriptor, address, count = cpu.r[:3]
        if descriptor != 0:
            cpu.r[0] = 0xFFFFFFF7
            return
        if count == 0:
            cpu.r[0] = 0
            return

        if stdin_data is None:
            stdin_data = sys.stdin.buffer.read()
        data = stdin_data[std_pointer:std_pointer + count]
        bytes_read = len(data)
        if bytes_read == 0:
            cpu.r[0] = 0
            return

        if address < RAM_BASE or address + bytes_read > RAM_BASE + RAM_SIZE:
            raise MemError("BUS")
        for offset, byte in enumerate(data):
            write_mem(address + offset, byte, 1)
        std_pointer += bytes_read
        cpu.r[0] = bytes_read
    elif n == 0x23:                            # WRITE
        descriptor, address, count = cpu.r[:3]
        if descriptor not in (1, 2):
            cpu.r[0] = 0xFFFFFFF7
            return
        if count == 0:
            cpu.r[0] = 0
            return

        buffer, offset = region(address)
        if buffer is None or offset + count > len(buffer):
            raise MemError("BUS")
        if descriptor == 1:
            stream = sys.stdout
        else:
            stream = sys.stderr
        stream.buffer.write(buffer[offset:offset + count])
        cpu.r[0] = count
    elif n == 0x30:                            # INSTRET
        count = cpu.instret + 1
        cpu.r[0] = count & 0xFFFFFFFF
        cpu.r[1] = (count >> 32) & 0xFFFFFFFF
    elif (n == 0x31):
        pass
    elif (n == 0x32):
        pass
    elif n == 0x40:                            # DUMP_REGS
        names = (*TRACE_REGISTERS, "pc")
        fields = []
        for name, value in zip(names, cpu.r):
            fields.append(f"{name}={value:08x}")
        flags = f"{int(cpu.N)}{int(cpu.Z)}{int(cpu.C)}{int(cpu.V)}"
        fields.append(f"NZCV={flags}")
        output = " ".join(fields) + "\n"
        sys.stderr.buffer.write(output.encode("ascii"))
        sys.stderr.buffer.flush()
    elif (n == 0x41):
        pass
    elif (n == 0x42):
        pass
    elif (n == 0x43):
        pass
    

    # TODO: the other services in section 5 of the handout
    else:
        fault("UNDEFINED")

TRACE_REGISTERS = (*[f"r{i}" for i in range(13)], "sp", "lr")

# just to make thigs clear, instead of a lambda function, I wrote a func that returns address so we sort on it
def write_address(write):
    address, _, _ = write
    return address

def write_trace_entry(trace, pc, hw, hw2, before, writes):
    encoding = f"{hw:04x}"
    if hw2 is not None:
        encoding += f"{hw2:04x}"
        
    fields = [f"{pc:08x}", encoding]

    for i, name in enumerate(TRACE_REGISTERS):
        # checking law this register changed, if so, print
        if before[i] != cpu.r[i]:
            fields.append(f"{name}={cpu.r[i] & 0xFFFFFFFF:08x}")

    writes_by_address = sorted(writes, key=write_address)
    
    for address, value, size in writes_by_address:
        fields.append(f"[{address:08x}]={value:0{size * 2}x}")

    nFlag = int(cpu.N)
    zFlag = int(cpu.Z)
    cFlag = int(cpu.C)
    vFlag = int(cpu.V)
    
    flags = str(nFlag) + str(zFlag) + str(cFlag) + str(vFlag)
    
    fields.append(f"NZCV={flags}")
    trace.write(" ".join(fields) + "\n")

def step(trace=None):
    """Execute one instruction. r[15] holds the address of the current
    instruction; an instruction that reads pc must see r[15] + 4."""
    pc = cpu.r[15]
    before = None
    writes = None
    exit_status = None
    
    if (trace is not None):
        before = cpu.r[:15]
        writes = []

    try:        
        hw = read_mem(pc, 2)
        nxt = pc + 2
        hw2 = None
        if (hw >> 11) in (0b11101, 0b11110, 0b11111):  # first half of a 32-bit instruction
            hw2 = read_mem(pc + 2, 2)
            nxt = pc + 4

        instr = decoder.decode(hw, hw2) # return instruction decoded
        if instr.op == Op.SVC:
            exit_status = svc(instr.n)
        else:
            Memory.trace_writes = writes
            nxt = execute(instr, cpu, nxt)
        
    
    except decoder.DecodeFault as error:
        fault(str(error))
    except alu.AlUExceptoin as error:
        fault(str(error))
    except MemError as error:
        fault(str(error))
    finally:
        Memory.trace_writes = None
   
    cpu.r[15] = nxt & 0xFFFFFFFF
    cpu.instret += 1
    if trace is not None:
        write_trace_entry(trace, pc, hw, hw2, before, writes)
  
    return exit_status

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
        hw2 = None  # in case of having 32-bit instruction 

        if (hw1 >> 11) in (0b11101, 0b11110, 0b11111):
            hw2 = read_code16(pc + 2)
            enc = f"{hw1:04x}{hw2:04x}"
            size = 4
        else:
            enc = f"{hw1:04x}"
            size = 2

        try:
            instruct= decoder.decode(hw1, hw2)
            text = decoder.disasm(instruct, pc)
        except decoder.DecodeFault:
            enc = f"{hw1:04x}"
            text = f".short\t0x{hw1:04x}"
            size = 2

        
        print(f"{pc:08x}: {enc} {text}")
        pc += size



def main():
    args = parse_args(sys.argv[1:])


    load_dump(args.program)

    if args.disasm:
        disassemble_text()
        return

    reset()
    
    
    trace_context = (
        open(args.trace, "w", encoding="ascii")
        if args.trace is not None
        else nullcontext(None)
    )
    

    with trace_context as trace:
        while True:
            if cpu.instret >= args.max_instr:
                print(f"LIMIT at pc=0x{cpu.r[15]:08x}", file=sys.stderr)
                sys.exit(254)

            exit_status = step(trace)
            if exit_status is not None:
                sys.exit(exit_status)



if __name__ == "__main__":
    main()
    
