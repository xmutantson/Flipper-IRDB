"""Synthetic parser checks; no devices, network or repository mutations."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from verify_contributions import payloads, records

HEADER = "Filetype: IR signals file\nVersion: 1\n#\n"
SIGNAL = "name: Power\ntype: parsed\nprotocol: NEC\naddress: 01 00 00 00\ncommand: 02 00 00 00\n"


class ContributionParserTests(unittest.TestCase):
    def test_labels_comments_and_hex_case_do_not_change_payload(self):
        source = HEADER + SIGNAL.replace("02", "AB")
        renamed = source.replace("Power", "POWER").replace("AB", "ab") + "# note\n"
        self.assertEqual(payloads(records(source)), payloads(records(renamed)))

    def test_duplicate_payload_multiplicity_is_preserved(self):
        single = payloads(records(HEADER + SIGNAL))
        double = payloads(records(HEADER + SIGNAL + SIGNAL.replace("Power", "Other")))
        self.assertNotEqual(single, double)
        self.assertEqual(sum((double - single).values()), 1)

    def test_changed_command_is_detected(self):
        self.assertNotEqual(payloads(records(HEADER + SIGNAL)),
                            payloads(records(HEADER + SIGNAL.replace("02", "03"))))

    def test_record_order_is_not_a_payload_change(self):
        other = SIGNAL.replace("Power", "Other").replace("02", "03")
        self.assertEqual(payloads(records(HEADER + SIGNAL + other)),
                         payloads(records(HEADER + other + SIGNAL)))

    def test_missing_field_is_rejected(self):
        with self.assertRaises(ValueError):
            records(HEADER + SIGNAL.replace("command: 02 00 00 00\n", ""))

    def test_duplicate_field_is_rejected(self):
        with self.assertRaises(ValueError):
            records(HEADER + SIGNAL + "command: 02 00 00 00\n")

    def test_invalid_byte_width_is_rejected(self):
        with self.assertRaises(ValueError):
            records(HEADER + SIGNAL.replace("02 00 00 00", "02 00"))

    def test_wrong_header_is_rejected(self):
        with self.assertRaises(ValueError):
            records(HEADER.replace("Version: 1", "Version: 2") + SIGNAL)

    def test_empty_file_is_rejected(self):
        with self.assertRaises(ValueError):
            records(HEADER)

    def test_unknown_fields_are_not_silently_discarded(self):
        with self.assertRaises(ValueError):
            records(HEADER + SIGNAL + "extra: data\n")


if __name__ == "__main__":
    unittest.main()
