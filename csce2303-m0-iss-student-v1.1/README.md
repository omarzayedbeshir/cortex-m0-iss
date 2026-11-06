# CSCE 2303 Cortex-M0 ISS project: files

| File or folder | Use it for |
| --- | --- |
| `CSCE2303_M0_ISS_Handout.docx` | Project specification, deadlines and grading requirements. |
| `BUILDING.md`, `templates/`, `tools/` | Tested Compiler Explorer links and an optional offline build helper. |
| `refiss-v1.1.html` | The reference simulator. Double-click it to open it in your browser; it works offline. Handout section 7 explains it. |
| `skeletons/iss.c`, `skeletons/iss.py` | Starting points for your simulator (handout section 13). Keep the one in your language. |
| `examples/` | The factorial program and a C program from the handout, each with its `.dump`. |
| `public-tests/` | The public tests for every checkpoint, and `run_tests.py` to run them. |

## Running the public tests

```
python3 public-tests/run_tests.py --iss "./iss" cp1
python3 public-tests/run_tests.py --iss "python3 iss.py" cp2
python3 public-tests/run_tests.py --iss "./iss" all
python3 public-tests/run_tests.py --iss "./iss" cp3/fnptr
```

`--iss` is the command that starts your simulator. Each test folder holds the program
(`prog.dump` and its source), any input (`input.txt`) and options (`args.txt`), and the
expected stdout, exit status, FAULT or LIMIT line and trace. CP1 tests run your
`--disasm` and compare it with objdump's listing in `expected.objdump`. For any other
test you can paste `prog.dump` and `input.txt` into `refiss` to see the same result.

The script needs Python 3.8 or later and nothing else.

## Release 1.1 on November 3, 2026

Use the included handout and refiss-v1.1.html together. The required subset has
43 instructions, including ADR. Both extensions are required. The public suite
contains 45 cases: 3 disassembly cases and 42 execution cases.

New regression cases cover ADC/SBC overflow, non-ASCII output bytes, ADR, BLX LR,
WRITE to stderr, sequential-target branch timing on both cores, and TRACE_ON.
DUMP_REGS and DUMP_MEM are checked against expected.debug.json by value, allowing
the formatting variations specified in the handout. expected.stderr, when present,
is compared byte for byte. A faulting instruction has no trace line, EXIT is traced
when enabled, TRACE_ON includes itself, and TRACE_OFF excludes itself. READ memory
writes do not appear in the trace.

Deadlines are Tuesdays at 23:59 Cairo time: CP1 November 10, CP2 November 17,
CP3 November 24, and final December 1, 2026. Submit the repository URL and checkpoint
tag on Canvas. Keep source code and CONTRIBUTIONS.md in each tagged commit.

Build instructions and tested template links: see [BUILDING.md](BUILDING.md).

C target programs use the supplied bare-metal startup and direct SVC wrappers,
with no standard library or libgcc. Both C and assembly build in Compiler Explorer.
