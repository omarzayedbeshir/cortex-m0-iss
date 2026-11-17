# Contributions

## CP1

### Omar Zayed (member C)
- Wrote `prog2.s` and `prog2.dump` (Thumb rewrite of the second RARS HW3 program).
- Wrote the loader (`load_dump`) parsing readelf section dumps into ROM/RAM.
- Wrote the memory map and access helpers (`region`, `read_mem`, `write_mem`).
- Wrote reset (`reset`), fault/error helpers, and their exit codes.
- Wrote the command line (`parse_args`) and the `--disasm` driver (`disassemble_text`).

### Mohammed Al-Kaf (member A)
- Wrote `prog1.s` and `prog1.dump` (Thumb rewrite of the first RARS HW3 program).

### Youssef Bawahab (member B)
- Wrote `prog3.s` and `prog3.dump` (Thumb rewrite of the fourth RARS HW3 program).
- Wrote the CPU class, instructions (shared with Moahmmed)


## CP2
### Youssef Bawahab (member B)
-developoing the alu.py with Arithmetic, logic, shifts, flags and branches, including BL, BX and BLX. 
-Handling the PC and next called instructions addresses.  
-Update the CPU with the execute function and handling calling.

