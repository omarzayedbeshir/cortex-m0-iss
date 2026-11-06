#!/usr/bin/env python3
"""Run the public tests against your simulator.

    python3 run_tests.py --iss "./iss" cp2
    python3 run_tests.py --iss "python3 iss.py" all
    python3 run_tests.py --iss "./iss" cp3/fnptr          (one test)

--iss is the command that starts your simulator; the options and the program are
added after it. CP1 tests run `iss --disasm prog.dump` and compare the listing with
objdump's, using the rules in section 6 of the handout. All other tests run
`iss [args] --trace FILE prog.dump < input.txt` and compare stdout, the exit status,
the FAULT/LIMIT line on stderr and, where expected.trace exists, the trace.
Standard library only; Python 3.8 or later.
"""
import argparse, json, os, re, shlex, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TIMEOUT = 120

# ---- CP1: disassembly listings -------------------------------------------------
def norm_disasm(text):
    text = text.split('@')[0]                    # objdump's comments
    text = re.sub(r'<[^>]*>', '', text)          # <label> names
    text = text.lower().replace('\t', ' ').strip()
    parts = text.split(None, 1)
    if not parts: return ''
    mnem = re.sub(r'\.(n|w)$', '', parts[0])     # .n and .w suffixes
    rest = parts[1] if len(parts) > 1 else ''
    return mnem + re.sub(r'\s+', '', rest)       # spacing is ignored

def objdump_instructions(path):
    want = {}
    for line in open(path, encoding='latin1'):
        m = re.match(r'^\s*([0-9a-f]+):\s+[0-9a-f]{4}(?: [0-9a-f]{4})?\s+\t(.*)$', line.rstrip('\n'))
        if not m or m.group(2).lstrip().startswith('.'): continue   # .word / .short are skipped
        want[int(m.group(1), 16)] = (norm_disasm(m.group(2)), m.group(2).strip())
    return want

def check_disasm(iss, d):
    r = subprocess.run(iss + ['--disasm', os.path.join(d, 'prog.dump')], capture_output=True, timeout=TIMEOUT)
    if r.returncode != 0:
        return f'--disasm exited with status {r.returncode}: {r.stderr.decode(errors="replace").strip()[:200]}'
    got = {}
    for line in r.stdout.decode(errors='replace').splitlines():
        # BL's encoding may be written f000f803 or, as objdump does, f000 f803
        m = re.match(r'^\s*([0-9a-fA-F]{8}):\s+[0-9a-fA-F]+(?: [0-9a-fA-F]{4}(?=\s))?\s+(.*)$', line)
        if m: got[int(m.group(1), 16)] = m.group(2)
    want = objdump_instructions(os.path.join(d, 'expected.objdump'))
    for addr in sorted(want):
        exp_norm, exp_text = want[addr]
        if addr not in got: return f'no line for address {addr:08x} (objdump: {exp_text})'
        if norm_disasm(got[addr]) != exp_norm:
            return f'at {addr:08x}: yours "{got[addr].strip()}", objdump "{exp_text}"'
    return None

# ---- everything else: running programs -------------------------------------------
def clean_trace(text):
    return [re.sub(r'\s+', ' ', l.split(';')[0]).strip() for l in text.splitlines() if l.split(';')[0].strip()]

def parse_debug(text):
    """Parse labelled register values and address-prefixed hex bytes.

    Whitespace, case, optional 0x prefixes, register aliases, and '=' versus ':'
    separators are ignored. DUMP_REGS register order and line wrapping are free.
    Multiple dumps retain their order for each register and each memory byte.
    """
    regs = {}
    pattern = r'\b(r(?:1[0-5]|[0-9])|sp|lr|pc)\s*[:=]\s*(?:0x)?([0-9a-f]{8})\b'
    for name, value in re.findall(pattern, text, re.I):
        name = {'r13': 'sp', 'r14': 'lr', 'r15': 'pc'}.get(name.lower(), name.lower())
        regs.setdefault(name, []).append(int(value, 16))
    flags = re.findall(r'\bNZCV\s*[:=]\s*([01]{4})\b', text, re.I)
    if flags: regs['NZCV'] = flags
    memory = []
    for line in text.splitlines():
        m = re.match(r'^\s*(?:0x)?([0-9a-f]{8})\s*:\s*(.*)$', line, re.I)
        if not m: continue
        address = int(m.group(1), 16)
        for token in m.group(2).split():
            if not re.fullmatch(r'(?:0x)?[0-9a-f]{2}', token, re.I): break
            memory.append([address, int(token, 16)])
            address += 1
    return {'registers': regs, 'memory': memory}

def check_run(iss, d):
    stdin = open(os.path.join(d, 'input.txt'), 'rb').read() if os.path.exists(os.path.join(d, 'input.txt')) else b''
    extra = open(os.path.join(d, 'args.txt')).read().split() if os.path.exists(os.path.join(d, 'args.txt')) else []
    want_trace = os.path.exists(os.path.join(d, 'expected.trace'))
    with tempfile.TemporaryDirectory() as tmp:
        tfile = os.path.join(tmp, 'trace.txt')
        cmd = iss + extra + (['--trace', tfile] if want_trace else []) + [os.path.join(d, 'prog.dump')]
        try:
            r = subprocess.run(cmd, input=stdin, capture_output=True, timeout=TIMEOUT)
        except subprocess.TimeoutExpired:
            return f'timed out after {TIMEOUT} s'
        exp_out = open(os.path.join(d, 'expected.out'), 'rb').read()
        if r.stdout != exp_out:
            a, b = r.stdout, exp_out
            i = next((k for k in range(min(len(a), len(b))) if a[k] != b[k]), min(len(a), len(b)))
            return f'stdout differs at byte {i}: yours {a[max(0, i-20):i+20]!r}, expected {b[max(0, i-20):i+20]!r}'
        exp_exit = int(open(os.path.join(d, 'expected.exit')).read())
        if r.returncode != exp_exit:
            return f'exit status {r.returncode}, expected {exp_exit}'
        stderr_path = os.path.join(d, 'expected.stderr')
        if os.path.exists(stderr_path):
            if r.stderr != open(stderr_path, 'rb').read():
                return 'stderr bytes differ from expected.stderr'
        debug_path = os.path.join(d, 'expected.debug.json')
        if os.path.exists(debug_path):
            expected = json.load(open(debug_path))
            actual = parse_debug(r.stderr.decode(errors='replace'))
            for kind in ('registers', 'memory'):
                if actual[kind] != expected[kind]:
                    return f'stderr debug {kind} differ from expected.debug.json'
        fpath = os.path.join(d, 'expected.fault')
        if os.path.exists(fpath):
            exp_fault = open(fpath).read().strip()
            mine = [l.strip() for l in r.stderr.decode(errors='replace').splitlines() if l.startswith(('FAULT ', 'LIMIT '))]
            if not mine or mine[-1] != exp_fault:
                return f'stderr should end with "{exp_fault}", yours has {mine[-1] if mine else "no FAULT/LIMIT line"!r}'
        if want_trace:
            if not os.path.exists(tfile): return 'no trace file was written'
            mine = clean_trace(open(tfile, encoding='latin1').read())
            ref = clean_trace(open(os.path.join(d, 'expected.trace')).read())
            for k in range(min(len(mine), len(ref))):
                if mine[k] != ref[k]:
                    return f'trace line {k + 1}: yours "{mine[k]}", expected "{ref[k]}"'
            if len(mine) != len(ref):
                return f'trace has {len(mine)} lines, expected {len(ref)}'
    return None

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--iss', required=True, help='command that runs your simulator, e.g. "./iss" or "python3 iss.py"')
    ap.add_argument('which', nargs='*', default=['all'], help='cp1, cp2, cp3, final, all, or CHECKPOINT/TEST')
    a = ap.parse_args()
    iss = shlex.split(a.iss)
    tests = []
    for w in a.which:
        groups = ['cp1', 'cp2', 'cp3', 'final'] if w == 'all' else [w]
        for g in groups:
            p = os.path.join(HERE, g)
            if os.path.exists(os.path.join(p, 'prog.dump')): tests.append(p)
            elif os.path.isdir(p): tests += sorted(os.path.join(p, t) for t in os.listdir(p) if os.path.isdir(os.path.join(p, t)))
            else: sys.exit(f'no such test or group: {w}')
    passed = 0
    for d in tests:
        name = os.path.relpath(d, HERE)
        try:
            err = check_disasm(iss, d) if os.path.exists(os.path.join(d, 'expected.objdump')) else check_run(iss, d)
        except subprocess.TimeoutExpired:
            err = f'timed out after {TIMEOUT} s'
        except FileNotFoundError as e:
            sys.exit(f'cannot start your simulator ({e}); check --iss')
        print(f'{"PASS" if err is None else "FAIL"}  {name}' + ('' if err is None else f'\n      {err}'))
        passed += err is None
    print(f'\n{passed} of {len(tests)} tests passed')
    sys.exit(0 if passed == len(tests) else 1)

if __name__ == '__main__':
    main()
