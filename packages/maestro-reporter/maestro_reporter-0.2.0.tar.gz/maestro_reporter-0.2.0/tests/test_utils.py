import unittest
from reporter.parser import _safe_float, _set_default_status, _truncate_message


class TestParserUtilities(unittest.TestCase):
    def test_safe_float_valid_numbers(self):
        self.assertEqual(_safe_float("10"), 10.0)
        self.assertEqual(_safe_float("0"), 0.0)

    def test_safe_float_invalid_numbers(self):
        self.assertEqual(_safe_float("abc"), 0.0)  # default value
        self.assertEqual(_safe_float(None, 10.0), 10.0)

    def test_default_status_value(self):
        self.assertEqual(_set_default_status(status=None, has_failure=True), "Failed")
        self.assertEqual(
            _set_default_status(status="PASSED", has_failure=False), "Passed"
        )
        self.assertEqual(
            _set_default_status(status="error", has_failure=False), "Error"
        )
        self.assertEqual(
            _set_default_status(status=None, has_failure=False), "Passed"
        )  # default status

    def test_truncate_message(self):
        text = "Hello World from maestro-reporter"
        truncated_words = "Hello W..."
        self.assertEqual(_truncate_message(""), "-")
        self.assertEqual(_truncate_message(text=text, max_chars=10), truncated_words)
        self.assertEqual(_truncate_message(text=text, max_chars=36), text)


if __name__ == "__main__":
    unittest.main()
