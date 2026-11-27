# Cortex-M0 Instruction Set Simulator

A Python instruction set simulator (ISS) for the CSCE 2303 Cortex-M0 project. It loads ARM Thumb programs from `readelf -x` section dumps and can disassemble the program or execute it with an instruction trace.

## Quick start

Use Python 3.10 or newer on Linux. The simulator uses the Python standard library, and the prebuilt dumps run without an ARM toolchain. Run the commands below from the repository root.

```bash
python3 iss.py csce2303-m0-iss-student-v1.1/public-tests/cp2/fact/prog.dump
```

The factorial example prints `10! = 3628800` and exits with status 0.

## Command line

```text
python3 iss.py [--disasm] [--trace FILE] [--max-instr N] [--seed N] [--cpu {m0,m0plus}] PROGRAM
```

| Argument | Behavior |
| --- | --- |
| `PROGRAM` | Path to a linked program's section dump in `readelf -x` format. |
| `--disasm` | Print the instructions in the dump's `.text` section and exit. |
| `--trace FILE` | Write an execution trace to a file. |
| `--max-instr N` | Limit execution to N instructions. The default is 100,000,000. Use a lower limit when debugging loops. |
| `--seed N`, `--cpu {m0,m0plus}` | Accepted for compatibility with the course interface. Random generation and cycle timing are final-checkpoint extensions. |

The `--disasm` output follows the default GNU ARM `objdump` register naming. It uses `r0` through `r9`, then `sl` for `r10`, `fp` for `r11`, `ip` for `r12`, `sp` for `r13`, `lr` for `r14`, and `pc` for `r15`.

```bash
program=csce2303-m0-iss-student-v1.1/public-tests/cp2/fact/prog.dump
python3 iss.py --disasm "$program"
python3 iss.py --trace /tmp/m0-fact.trace --max-instr 1000 "$program"
head /tmp/m0-fact.trace
```

The trace records the instruction address and encoding, changed registers, instruction memory writes in address order, and the four `NZCV` flags. It includes `EXIT` when enabled and skips faulting instructions and memory writes performed by `READ`. A reset fault leaves an empty trace file when tracing is requested. The console output services use stdout, and diagnostics use stderr. `WRITE` can target either stream. Exit status comes from the low byte of the guest's exit argument. The simulator uses 253 for load errors, 254 for the instruction limit, and 255 for faults.

## CP3 functionality

- Reset reads the initial stack pointer and Thumb reset vector from memory. The simulator then fetches and executes instructions from the entry point.
- Execution covers the course's 43-instruction Thumb subset, including byte and halfword accesses, `LDM` and `STM`, sign and zero extension, byte reversal, and indirect calls.
- Memory is little-endian, with 1 MiB of ROM at `0x00000000` and 256 KiB of RAM at `0x20000000`.
- The simulator reports `BUS`, `UNALIGNED`, `INVSTATE`, and `UNDEFINED` faults.

### Core services

`GETCHAR`, `GETINT`, and `READ` share an input cursor. The simulator buffers stdin through EOF on the first service that consumes input, so pipe input into the process or redirect a file.

| SVC | Service | Behavior |
| --- | --- | --- |
| `0x00` | `EXIT` | Exit with the low byte of `r0`. |
| `0x10` | `PUTCHAR` | Write the low byte of `r0`. |
| `0x11` | `PUTS` | Write the NUL-terminated byte string at the address in `r0`. |
| `0x12` | `PUTINT` | Print `r0` as a signed decimal integer. |
| `0x13` | `PUTHEX` | Print `r0` as `0x` followed by eight uppercase hex digits. |
| `0x14` | `GETCHAR` | Return the next input byte in `r0`, or `-1` at EOF. |
| `0x15` | `GETINT` | Read a signed decimal integer into `r0`, skipping ASCII whitespace. Return zero when there is no integer. |
| `0x22` | `READ` | Read up to `r2` bytes from stdin (descriptor `0` in `r0`) into RAM at `r1`. Return the byte count in `r0`, or zero at EOF. |
| `0x23` | `WRITE` | Write `r2` bytes at `r1` to stdout (descriptor `1`) or stderr (descriptor `2`). Pass the descriptor in `r0`, which receives the byte count. |
| `0x30` | `INSTRET` | Return the 64-bit retired-instruction count, including this SVC, with the low word in `r0` and the high word in `r1`. |
| `0x40` | `DUMP_REGS` | Print labeled register values and `NZCV` to stderr. |

`READ` and `WRITE` return `-9` for an invalid descriptor. An invalid memory range raises a `BUS` fault. `READ` checks the bytes it actually transfers.

## Team programs

The team’s Thumb assembly sources and prebuilt dumps are in [the programs directory](programs/).

```bash
programs=programs

# Program 1 expects a first value, last value, and step.
printf '1\n10\n2\n' | python3 iss.py "$programs/prog1.dump"

# Program 2 counts uppercase letters, lowercase letters, and digits.
printf 'Hello world.\n' | python3 iss.py "$programs/prog2.dump"

# Program 3 expects an array length followed by that many integers.
printf '4\n3\n-1\n8\n2\n' | python3 iss.py "$programs/prog3.dump"
```

| Program | Expected results after the prompts |
| --- | --- |
| Program 1 | Sum 25, count 4 |
| Program 2 | 1 uppercase letter, 9 lowercase letters, 0 digits |
| Program 3 | Sum 12, maximum 8, minimum -1 |

`prog2.dump` uses the CP3 `READ` service. The CP2 variant, `prog2_valid_for_cp2.dump`, uses `GETCHAR`.

## Verification

Run the public CP1 through CP3 fixtures and the local unit tests.

```bash
runner=csce2303-m0-iss-student-v1.1/public-tests/run_tests.py
python3 "$runner" --iss 'python3 iss.py' cp1 cp2 cp3
python3 -m unittest discover -s tests -v
```

The expected result is **38 passing public cases** (3 CP1, 9 CP2, and 26 CP3) and **9 passing unit tests**. The public runner compares disassembly for CP1 and checks output, exit status, traces, and fault or debug output where fixtures specify them for CP2 and CP3.

To check a dump against the course implementation, open [refiss v1.1](csce2303-m0-iss-student-v1.1/refiss-v1.1.html) in a browser and run the same dump with the same input.

## Building a new program dump

The [course build guide](csce2303-m0-iss-student-v1.1/BUILDING.md) documents the Compiler Explorer setup and the optional local GNU Arm toolchain. Start from the supplied assembly template or bare-metal C template and keep the startup code and vector table. Use the core services listed above for program I/O and exit. Build a linked program with the course settings, generate its section dump, and pass the resulting `.dump` file to `iss.py`.

## Repository layout

| Path | Purpose |
| --- | --- |
| [iss.py](iss.py) | Command line, dump loading, reset, fetch loop, core services, and traces |
| [cpu.py](cpu.py) | Registers, flags, and instruction dispatch |
| [instruction.py](instruction.py) | Decoded instruction and opcode definitions |
| [decoder.py](decoder.py) | Thumb instruction decoding and disassembly |
| [alu.py](alu.py) | Arithmetic, logic, shifts, flags, and branch execution |
| [Memory.py](Memory.py) | ROM and RAM, memory access, load/store addressing, and stack operations |
| [programs/](programs/) | Team-written CP1 Thumb assembly programs and prebuilt dumps |
| [tests/](tests/) | Team-written Python unit tests |
| [Course starter kit](csce2303-m0-iss-student-v1.1/) | Templates, reference simulator, examples, and public test fixtures |
| [CONTRIBUTIONS.md](CONTRIBUTIONS.md) | Team contributions by checkpoint |
