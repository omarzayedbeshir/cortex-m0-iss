import io
import unittest
from unittest.mock import patch

import iss
from cpu import CPU


class CP2ServicesTests(unittest.TestCase):
    def setUp(self):
        self.cpu_patch = patch.object(iss, "cpu", CPU())
        self.cpu_patch.start()
        self.addCleanup(self.cpu_patch.stop)
        iss.stdin_data = None
        iss.std_pointer = 0

    def test_output_services_format_values(self):
        output = io.TextIOWrapper(io.BytesIO(), encoding="ascii")
        with patch("sys.stdout", output):
            iss.cpu.r[0] = 0x141
            iss.svc(0x10)
            iss.cpu.r[0] = 0xFFFFFFFF
            iss.svc(0x12)
            iss.svc(0x13)
            output.flush()
            self.assertEqual(output.buffer.getvalue(), b"A-10xFFFFFFFF")

    def test_input_services_share_position_and_report_eof(self):
        input_stream = io.TextIOWrapper(io.BytesIO(b" -42 Z"), encoding="ascii")
        with patch("sys.stdin", input_stream):
            iss.svc(0x15)
            self.assertEqual(iss.cpu.r[0], 0xFFFFFFD6)
            iss.svc(0x14)
            self.assertEqual(iss.cpu.r[0], ord(" "))
            iss.svc(0x14)
            self.assertEqual(iss.cpu.r[0], ord("Z"))
            iss.svc(0x14)
            self.assertEqual(iss.cpu.r[0], 0xFFFFFFFF)
            iss.svc(0x15)
            self.assertEqual(iss.cpu.r[0], 0)

    def test_exit_uses_low_byte(self):
        iss.cpu.r[0] = 0x1234
        self.assertEqual(iss.svc(0x00), 0x34)


if __name__ == "__main__":
    unittest.main()
