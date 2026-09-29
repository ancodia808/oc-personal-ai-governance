import copy
import json
import unittest
from scripts.build_demo import FIXTURE, summarize


class DemoTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_expected_totals(self):
        result = summarize(self.data)
        self.assertEqual(result["total"], 153000)
        self.assertEqual(result["daily"], {"2026-09-28": 87000, "2026-09-29": 66000})
        self.assertEqual(result["projects"]["Delivery playbook"], 39000)

    def test_duplicate_rejected(self):
        self.data["turns"].append(copy.deepcopy(self.data["turns"][0]))
        with self.assertRaises(ValueError):
            summarize(self.data)

    def test_private_input_rejected(self):
        self.data["synthetic"] = False
        with self.assertRaises(ValueError):
            summarize(self.data)

    def test_missing_or_invalid_tokens_rejected(self):
        self.data["turns"][0]["input_tokens"] = -1
        with self.assertRaises(ValueError):
            summarize(self.data)


if __name__ == "__main__":
    unittest.main()
