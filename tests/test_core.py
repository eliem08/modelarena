import json
import pathlib
import unittest
from datetime import date

from model_sportscenter import box_score, load_feed, recap, standings

FEED = load_feed(json.loads((pathlib.Path(__file__).resolve().parent.parent / "examples" / "launches.json").read_text()))


class Tests(unittest.TestCase):
    def test_box_score(self):
        bs = box_score(FEED, "nova-3")
        rows = {r["benchmark"]: r for r in bs["rows"]}
        self.assertTrue(rows["SWE-bench"]["record"])
        self.assertAlmostEqual(rows["SWE-bench"]["delta"], 6.4)
        self.assertFalse(rows["GPQA"]["record"])
        self.assertEqual(rows["GPQA"]["prev_holder"], "Atlas-1.5")
        self.assertEqual(bs["records"], 2)

    def test_first_launch_sets_records(self):
        self.assertEqual(box_score(FEED, "Atlas-1")["records"], 3)

    def test_standings(self):
        st = standings(FEED, date(2026, 10, 24))
        self.assertEqual(st["titles"]["SWE-bench"]["model"], "Nova-3")
        self.assertEqual(st["titles"]["GPQA"]["lab"], "Helix Labs")
        total = sum(st["days_at_one"].values())
        self.assertEqual(total, 3 * (date(2026, 10, 24) - date(2026, 1, 10)).days)

    def test_recap(self):
        text = recap(FEED, "Nova-3")
        self.assertIn("ORBIT AI STRIKES", text)
        self.assertIn("GPQA stays with Atlas-1.5", text)


if __name__ == "__main__":
    unittest.main()
