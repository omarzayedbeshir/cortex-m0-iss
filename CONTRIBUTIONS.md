# Contributions

## CP1

### Omar Zayed (member C)
- Wrote `prog2.s` and `prog2.dump` (Thumb rewrite of the second RARS HW3 program).
- Extended the starter dump loader to track section bounds and report out-of-range ROM/RAM addresses with the dump path and line number.
- Added command-line argument parsing and the initial `--disasm` driver for the `.text` section.

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
- Implemented `PUTHEX`, `GETCHAR`, and `GETINT`, and updated `EXIT` so it could be traced before the simulator returned the guest's status.
- Added instruction tracing for register changes, memory writes, and NZCV. Routed fetch and execution faults through the simulator's fault handler.
- Updated reset to initialize the CPU object's registers, flags, and retired-instruction count and to align the initial stack pointer. Also aligned stack pointer writes in `ADD` and `MOV`.
- Fixed memory-operation dispatch argument order and decoding for `ADC`, `RSB`, and stack-pointer adjustments.
- Added the `GETCHAR`-based version of Program 2 for CP2 and wrote unit tests for console output, shared input and EOF, and exit status.

### Mohammed Al-Kaf (member A)
- Implemented effective address calculation (`Address`) in `Memory.py` for immediate-offset, SP-relative, PC-relative, and register-offset addressing modes.
- Implemented word load and store operations (`load`, `store`) for `LDR` and `STR`.
- Implemented stack operations for `PUSH` and `POP`.


### Youssef Bawahab (member B)
-developoing the alu.py with Arithmetic, logic, shifts, flags and branches, including BL, BX and BLX. 
-Handling the PC and next called instructions addresses.  
-Update the CPU with the execute function and handling calling.

## CP3

### Omar Zayed (member C)
- Implemented `READ` and `WRITE`, including descriptor checks and buffer validation. `READ` shares the console input cursor, and `WRITE` supports both stdout and stderr.
- Implemented `INSTRET` with a 64-bit count that includes the current SVC, and `DUMP_REGS` with labeled registers and NZCV on stderr.
- Added six regression tests covering `READ` bounds and shared input, writes into ROM by `READ`, `WRITE` buffer validation, `INSTRET`, `DUMP_REGS`, and reset-fault tracing.
