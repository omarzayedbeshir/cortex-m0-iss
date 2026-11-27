import io
import unittest
from contextlib import ExitStack
from unittest.mock import patch

import iss
import Memory
from cpu import CPU


class CP3IOTests(unittest.TestCase):
    def setUp(self):
        address = Memory.RAM_BASE + Memory.RAM_SIZE - 3
        self.address = address
        self.addCleanup(Memory.ram.__setitem__, slice(-3, None), Memory.ram[-3:])
        patches = ExitStack()
        self.addCleanup(patches.close)
        patches.enter_context(patch.object(iss, "cpu", CPU()))
        patches.enter_context(patch.object(iss, "stdin_data", None))
        patches.enter_context(patch.object(iss, "std_pointer", 0))

    def call(self, service, descriptor, address, count):
        iss.cpu.r[:3] = [descriptor, address, count]
        iss.svc(service)
        return iss.cpu.r[0]

    def test_read_shares_input_cursor_and_only_validates_bytes_read(self):
        stdin = io.TextIOWrapper(io.BytesIO(b"Axyz"))
        with patch("sys.stdin", stdin):
            self.assertEqual(self.call(0x22, 1, 0, 4), 0xFFFFFFF7)
            self.assertEqual(self.call(0x22, 0, 0, 0), 0)
            self.assertIsNone(iss.stdin_data)
            iss.svc(0x14)
            self.assertEqual(iss.cpu.r[0], ord("A"))
            self.assertEqual(self.call(0x22, 0, self.address, 4), 3)
            self.assertEqual(Memory.ram[-3:], b"xyz")
            self.assertEqual(self.call(0x22, 0, 0, 4), 0)

    def test_read_into_rom_faults(self):
        stdin = io.TextIOWrapper(io.BytesIO(b"A"))
        with patch("sys.stdin", stdin):
            with self.assertRaisesRegex(Memory.MemError, "^BUS$"):
                self.call(0x22, 0, Memory.ROM_BASE, 1)
        self.assertEqual(iss.std_pointer, 0)

    def test_write_validates_entire_buffer_before_emitting_bytes(self):
        Memory.ram[-3:] = b"A\x00\xff"
        stdout = io.TextIOWrapper(io.BytesIO())
        stderr = io.TextIOWrapper(io.BytesIO())
        with patch("sys.stdout", stdout), patch("sys.stderr", stderr):
            self.assertEqual(self.call(0x23, 0, 0xFFFFFFFF, 3), 0xFFFFFFF7)
            self.assertEqual(self.call(0x23, 1, 0xFFFFFFFF, 0), 0)
            with self.assertRaisesRegex(Memory.MemError, "^BUS$"):
                self.call(0x23, 1, self.address, 4)
            self.assertEqual(self.call(0x23, 1, self.address, 3), 3)
            self.assertEqual(self.call(0x23, 2, self.address + 2, 1), 1)
        self.assertEqual(stdout.buffer.getvalue(), b"A\x00\xff")
        self.assertEqual(stderr.buffer.getvalue(), b"\xff")
