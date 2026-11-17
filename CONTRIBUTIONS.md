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
- Designed the instruction representation (`Op` enum and `INSTRUCTION` dataclass in `instruction.py`) with Youssef.
- Wrote the Thumb instruction decoder (`decode` in `decoder.py`) covering all 43 required ARMv6-M instructions 
- Wrote the disassembler (`disasm`, `register`, `register_list`) to match GNU `objdump` formatting for `--disasm`.

### Youssef Bawahab (member B)
- Wrote `prog3.s` and `prog3.dump` (Thumb rewrite of the fourth RARS HW3 program).
- Wrote the CPU class, instructions (shared with Moahmmed)


## CP2

### Omar Zayed (member C)
- Implemented the CP2 supervisor call services, including hexadecimal output and console input.
- Added instruction tracing and fixed execution issues across the simulator, CPU, decoder, and memory handling.
- Activated and corrected CPU reset, including stack pointer alignment and CPU state references.

### Mohammed Al-Kaf (member A)
- Implemented effective address calculation (`Address`) in `Memory.py` for immediate-offset, SP-relative, PC-relative, and register-offset addressing modes.
- Implemented word load and store operations (`load`, `store`) for `LDR` and `STR`.
- Implemented stack operations for `PUSH` and `POP`.


### Youssef Bawahab (member B)
-developoing the alu.py with Arithmetic, logic, shifts, flags and branches, including BL, BX and BLX. 
-Handling the PC and next called instructions addresses.  
-Update the CPU with the execute function and handling calling.
