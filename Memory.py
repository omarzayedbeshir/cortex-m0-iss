from __future__ import annotations 
from instruction import *


class MemError(Exception):
    pass

ROM_BASE, ROM_SIZE = 0x00000000, 1 << 20        # 1 MB
RAM_BASE, RAM_SIZE = 0x20000000, 256 << 10      # 256 KB

rom = bytearray(ROM_SIZE)
ram = bytearray(RAM_SIZE)
trace_writes = None

def region(addr):
    """Return (buffer, offset) for a mapped address, or (None, 0)."""
    if ROM_BASE <= addr < ROM_BASE + ROM_SIZE:
        return rom, addr - ROM_BASE
    if RAM_BASE <= addr < RAM_BASE + RAM_SIZE:
        return ram, addr - RAM_BASE
    return None, 0

def read_mem(addr, size):
    if addr % size:
        raise MemError("UNALIGNED")
    buf, off = region(addr)
    if buf is None:
        raise MemError("BUS")
    return int.from_bytes(buf[off:off + size], "little")

def write_mem(addr, value, size):
    if addr % size:
        raise MemError("UNALIGNED")
    buf, off = region(addr)
    if buf is not ram:
        raise MemError("BUS")
    value &= (1 << (8 * size)) - 1
    buf[off:off + size] = value.to_bytes(size, "little")

    if (trace_writes is not None):
        trace_writes.append((addr, value, size))

    #___________________ Load and Store  operations __________

# Determine the Address to load or store: 
def Address(instr: INSTRUCTION, cpu: CPU) -> None:
    if instr.isImm: 
        if instr.rs1 == 15 :     # cases where base address is PC
            base = (cpu.r[15] + 4) & 0xFFFFFFFC  # to make the base aligned, we set bit 0, 1 = zero 
        else :
            base = cpu.r[instr.rs1]             # cases where base addres in rs1 

        return (base + instr.imm32) & 0xFFFFFFFF                # 0xFFFFFFFF mask to restrict results to 32 bit
    return (cpu.r[instr.rs1] + cpu.r[instr.rs2]) & 0xFFFFFFFF



def store(instr: INSTRUCTION, cpu: CPU ) -> None :
    s_address = Address(instr, cpu)
    op = instr.op
    val = cpu.r[instr.rt]

    if op == Op.STR:                    #storing register , 32 bit
        write_mem(s_address, val, 4)
    elif op == Op.STRH:
        write_mem(s_address, val & 0xFFFF, 2)   # storing half word, lower 16 bits
    elif op == Op.STRB:
        write_mem(s_address, val & 0xFF, 1)     # storing byte , lower 8 bits
            

def load(instr: INSTRUCTION, cpu: CPU ) -> None:

    l_address = Address(instr, cpu)
    op = instr.op

    if op == Op.LDR:
        val = read_mem(l_address, 4)    # loading register
    elif op == Op.LDRH:
        val = read_mem(l_address, 2)    # loading halfword 
    elif op == Op.LDRB:
        val = read_mem(l_address, 1)    # loading byte
    elif op == Op.LDRSH:
        val = read_mem(l_address, 2)    # loading Signed halfword
        if val & 0x8000:
            val -= 0x10000
    elif op == Op.LDRSB:
        val = read_mem(l_address, 1)    # loading signed byte
        if val & 0x80:
            val -= 0x100


    cpu.r[instr.rt] = val & 0xFFFFFFFF  # rt is the register receiving data (I used rt as in the manual)




def loadMult(instr, cpu) -> None:
    
    l_address = cpu.r[instr.rs1]    

    for i in range(8):          # checking registers bit by bit to determine affected ones
        if (instr.registers >> i) & 1:  
            cpu.r[i] = read_mem(l_address, 4)
            l_address = (l_address + 4) & 0xFFFFFFFF    # to restrict it to 32 bits as register length 

    # Writeback occurs only if Rn is not in the loaded register list
    if not ((instr.registers >> instr.rs1) & 1):
        cpu.r[instr.rs1] = l_address


def StorMult(instr, cpu) -> None:
    
    s_address = cpu.r[instr.rs1]  


     # checking registers bit by bit to determine affected ones
    for i in range(8):
        if (instr.registers >> i) & 1:
            write_mem(s_address, cpu.r[i], 4)    # if true so we write on 
            s_address = (s_address + 4) & 0xFFFFFFFF      # to restrict it to 32 bits as register length 

    cpu.r[instr.rs1] = s_address

# ______________ PUSH , POP #________________

def exec_push(instr, cpu) -> None:
    
    count = bin(instr.registers).count("1") # counting ones, so we know how many bytes required in the stack
    address = (cpu.r[13] - 4 * count) & 0xFFFFFFFF # allocate space according to num of regs
    cpu.r[13] = address

    for i in range(16):
        if (instr.registers >> i) & 1: # identifying which regs to push to stack
            write_mem(address, cpu.r[i], 4)
            address = (address + 4) & 0xFFFFFFFF


def exec_pop(instr, cpu, nxt: int) -> int:
    
    address = cpu.r[13]

    for i in range(16):
        if (instr.registers >> i) & 1:   # identifying which regs to pop from stack
            val = read_mem(address, 4)
            if i == 15:  
                if not (val & 1):
                    raise MemError("INVSTATE")
                nxt = val & ~1
            else:
                cpu.r[i] = val
            address = (address + 4) & 0xFFFFFFFF

    cpu.r[13] = address
    return nxt
