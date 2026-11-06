# Building bare-metal project programs

Release 1.1, November 3, 2026. Both assembly and C build directly in Compiler
Explorer. The target programs have no standard library, libgcc, heap or operating
system. A compiler and the supplied small runtime block are sufficient.

| Template | Link | What it produces |
| --- | --- | --- |
| Thumb assembly | https://godbolt.org/z/e8asPbvj7 | Linked image and readelf section dump |
| Bare-metal C | https://godbolt.org/z/bGc7P8YEf | Linked image and readelf section dump, with no libraries |
| Thumb and RV32I comparison | https://godbolt.org/z/jYG4v53bn | Unlinked objects and .text sizes for the same functions |

The executable templates use ARM GCC 13.2.0 (unknown-eabi), ID `carmug1320`.
The comparison adds RISC-V (32-bits) GCC 13.2.0, ID `rv32-cgcc1320`.

## Build in the browser

1. Open the assembly or C link and replace only the program portion. Keep the
   vector table/startup code and fixed build flags.
2. Wait for the compiler and readelf pane. Both execution templates enable Link
   to binary and run readelf with `-x .vectors -x .text -x .rodata -x .data`.
3. Copy the entire readelf output to a .dump file and load it into refiss or your
   simulator. Warnings about absent .rodata or .data sections are harmless if
   the source does not define those sections.

For assembly, retain the initial comment containing `main(void)`: the language
selector is C with `-x assembler`, and the comment prevents Compiler Explorer
from appending a C main stub. The comparison link produces object files only;
its output is not an executable dump.

## Bare-metal C contract

Copy `templates/c_template.c` and keep its runtime block. It supplies the vector
table, `_start`, BSS clearing, a call to `main(void)`, EXIT on return, and direct
SVC wrappers. The dump loader already loads initialized .data at its RAM address.
There is no CRT or library startup code.

| Function | Service and behavior |
| --- | --- |
| `iss_putchar(int)` | PUTCHAR; writes the low byte |
| `iss_puts(const char *)` | PUTS; writes a NUL-terminated string, no added newline |
| `iss_putint(int)` | PUTINT; signed decimal, no added newline |
| `iss_puthex(unsigned)` | PUTHEX; 0x followed by eight uppercase hex digits |
| `iss_getchar(void)` | GETCHAR; returns a byte or -1 at EOF |
| `iss_getint(void)` | GETINT; see the handout's input parsing rules |
| `iss_read(int, void *, unsigned)` | READ; returns bytes read or -9, with no errno layer |
| `iss_write(int, const void *, unsigned)` | WRITE; returns bytes written or -9 |

The block has no wrappers for INSTRET, the extended services or DUMP_REGS. Add your own
in the same style below the runtime block, not inside it. A 64-bit result comes back in
r0 (low) and r1 (high), which is how AAPCS returns `unsigned long long`:

```c
#define ISS_SVC __attribute__((naked, noinline, unused)) static
ISS_SVC unsigned long long iss_instret(void)        { __asm volatile("svc #0x30\n bx lr"); }
ISS_SVC unsigned long long iss_cycles(void)         { __asm volatile("svc #0x31\n bx lr"); }
ISS_SVC unsigned iss_rand(void)                     { __asm volatile("svc #0x32\n bx lr"); }
ISS_SVC void iss_dump_regs(void)                    { __asm volatile("svc #0x40\n bx lr"); }
ISS_SVC void iss_dump_mem(const void *p, unsigned n) { __asm volatile("svc #0x41\n bx lr"); }
ISS_SVC void iss_trace_on(void)                     { __asm volatile("svc #0x42\n bx lr"); }
ISS_SVC void iss_trace_off(void)                    { __asm volatile("svc #0x43\n bx lr"); }
```

Each call executes the call instruction and the wrapper's `bx lr` as well as the SVC.
INSTRET and CYCLES count them and the trace shows them; subtract them as measurement
overhead (handout section 9). DUMP_REGS called this way reports the wrapper's pc and
the caller's return address in lr.

The build flags are:

```
-mcpu=cortex-m0 -mthumb -O2 -ffreestanding -fno-builtin -fno-stack-protector -nostdlib
-Wl,--section-start=.vectors=0 -Wl,-Ttext=0x100 -Wl,-Tdata=0x20000000
```

Use integer computations, fixed arrays and your own loops. Do not call printf,
scanf, malloc, string-library functions or other library routines. M0 division
and floating-point operations normally require compiler helper routines; they
are not linked here. Avoid them or supply your own implementation. Some complex
C operations can also emit helpers such as memcpy. An undefined helper at link
time is an error to resolve in your source, not a reason to add libraries.
Ordinary 32-bit multiplication and 64-bit addition are usable; the examples
include a 64-bit addition with carry. All generated instructions must stay in
the handout's 43-instruction subset.

## Optional offline build

Compiler Explorer is sufficient. If you prefer local tools, use GNU Arm GCC and
binutils targeting arm-none-eabi; no target libraries are required. The helper was
tested with Arm GNU Toolchain 13.2.Rel1 (GCC 13.2.1).

```sh
python3 tools/build_dump.py templates/c_template.c --toolchain /path/to/toolchain/bin
```

The helper also accepts .s files. Omit --toolchain if the tools are on PATH.
It writes .elf, .dump and .objdump next to the source. Python 3.8+ is sufficient
for the helper; Windows tool paths ending in .exe are supported. Build the
simulator itself with your normal host C/C++ compiler or Python, not the target
compiler. The host simulator may use its normal standard library.

## Reproducible comparison measurements

Place only the measured function and its own helpers in the comparison source.
Use the same C source for both architectures with `-O2 -ffreestanding -fno-builtin`,
plus `-mcpu=cortex-m0 -mthumb` or `-march=rv32i -mabi=ilp32`. No startup, I/O or
library code belongs in the function-only object used for .text measurements.
For hand-written functions, use -x assembler with the corresponding compiler;
do not feed Thumb assembly to the RISC-V pane.

Measure code size with the same compiler version and flags as the code executed.
For local builds, compile a function-only source with -c and inspect it with
arm-none-eabi-readelf -SW. Record compiler versions: the online GCC 13.2.0 and
local GCC 13.2.1 are not assumed identical.

For Thumb execution, place the function and caller in the assembly or bare-metal
C runtime template. For RV32I, place hand-written or GCC-generated assembly in a
RARS harness, adapting directives without changing instructions. Resolve helper
calls in your source and verify results. Use identical input bytes and arrays.

Count from the function's first instruction through its return, including nested
calls. Exclude startup, I/O, the top-level call and counter-reading overhead.
For INSTRET/CYCLES deltas, subtract those caller/instrumentation instructions
(including the second SVC) and their cycles, and list the correction. A trace count
of the same interval is accepted. CPI is corrected cycles / corrected instructions.
