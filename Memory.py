

class MemError(Exception):
    pass

ROM_BASE, ROM_SIZE = 0x00000000, 1 << 20        # 1 MB
RAM_BASE, RAM_SIZE = 0x20000000, 256 << 10      # 256 KB

rom = bytearray(ROM_SIZE)
ram = bytearray(RAM_SIZE)

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
    buf[off:off + size] = (value & ((1 << 8 * size) - 1)).to_bytes(size, "little")