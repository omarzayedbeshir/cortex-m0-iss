import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import iss
from cpu import CPU


class CP3StateTests(unittest.TestCase):
    def test_instret_counts_current_svc_and_returns_both_words(self):
        cpu = CPU()
        cpu.instret = 0xFFFFFFFF
        with patch.object(iss, "cpu", cpu), patch.object(iss, "read_mem", return_value=0xDF30):
            iss.step()
        self.assertEqual(cpu.r[:2], [0, 1])
        self.assertEqual(cpu.instret, 0x100000000)

    def test_dump_regs_labels_values_and_reports_svc_address(self):
        cpu = CPU()
        cpu.r[:] = range(16)
        cpu.r[15] = 0x100
        cpu.N = cpu.C = True
        stderr = io.TextIOWrapper(io.BytesIO())
        with patch.object(iss, "cpu", cpu), patch.object(iss, "read_mem", return_value=0xDF40):
            with patch("sys.stderr", stderr):
                iss.step()
        registers = [f"r{i}={i:08x}" for i in range(13)]
        registers.extend(["sp=0000000d", "lr=0000000e", "pc=00000100", "NZCV=1010"])
        self.assertEqual(stderr.buffer.getvalue(), (" ".join(registers) + "\n").encode("ascii"))
        self.assertEqual(cpu.r[15], 0x102)

    def test_invalid_reset_creates_empty_trace(self):
        with tempfile.TemporaryDirectory() as directory:
            dump = Path(directory) / "reset.dump"
            trace = Path(directory) / "reset.trace"
            dump.write_text("Hex dump of section '.vectors':\n  0x00000000 00000420 00010000\n", encoding="ascii")
            result = subprocess.run(
                [sys.executable, iss.__file__, "--trace", str(trace), str(dump)],
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 255)
            self.assertEqual(result.stderr, b"FAULT INVSTATE at pc=0x00000100\n")
            self.assertEqual(trace.read_bytes(), b"")
