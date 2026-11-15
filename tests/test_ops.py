import contextlib
import io
import json
import os
import tempfile
import unittest

from modelarena.__main__ import main

SRC = ["--source", "https://example.com/paper"]


def run(*argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        code = main(list(argv))
    return code, out.getvalue()


class DeskOpsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.s = ["--store", os.path.join(self.tmp.name, "feed.json")]
        self.ok("launch-add", "Atlas-1", "--lab", "Helix", "--date", "2026-01-10", "--score", "SWE-bench=61.2", *SRC)

    def tearDown(self):
        self.tmp.cleanup()

    def ok(self, *argv):
        code, out = run(*argv, *self.s)
        self.assertEqual(code, 0, out)
        return out

    def test_a_new_launch_takes_the_title_and_the_story_cites_its_source(self):
        out = self.ok(
            "launch-add", "Nova-2", "--lab", "Orbit", "--date", "2026-03-02", "--score", "SWE-bench=64.8", *SRC
        )
        self.assertIn("1 record(s) of 1", out)
        story = self.ok("story", "Nova-2")
        self.assertIn("steals the crown from Atlas-1", story)
        self.assertIn("Source: https://example.com/paper", story)
        league = self.ok("league", "--as-of", "2026-04-01")
        self.assertIn("Nova-2", league)
        self.assertEqual([i["model"] for i in json.loads(self.ok("export"))], ["Atlas-1", "Nova-2"])

    def test_retraction_restores_the_previous_holder(self):
        self.ok("launch-add", "Nova-2", "--lab", "Orbit", "--date", "2026-03-02", "--score", "SWE-bench=64.8", *SRC)
        self.ok("launch-remove", "nova-2")
        self.assertIn("Atlas-1", self.ok("league", "--as-of", "2026-04-01"))
        self.assertNotIn("Nova-2", self.ok("launches"))

    def test_refusals(self):
        base = ["--lab", "L", "--date", "2026-05-01"]
        for argv in (
            ["launch-add", "atlas-1", *base, "--score", "x=1", *SRC],  # duplicate, case-insensitive
            ["launch-add", "M", *base, "--score", "x=abc", *SRC],
            ["launch-add", "M", *base, "--score", "x=nan", *SRC],
            ["launch-add", "M", "--lab", "L", "--date", "May", "--score", "x=1", *SRC],
            ["launch-add", "M", *base, "--score", "x=1", "--source", "trust me"],
            ["story", "Ghost"],
            ["launch-remove", "Ghost"],
        ):
            with self.subTest(argv=argv):
                self.assertEqual(run(*argv, *self.s)[0], 1)


if __name__ == "__main__":
    unittest.main()
