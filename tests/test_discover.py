"""discover: new launches from Hugging Face, scores from model cards when published (no network)."""

import contextlib
import io
import json
import os
import tempfile
import unittest
from unittest import mock

from modelarena.__main__ import main
from modelarena.hf import card_scores, discover

LISTING = {
    "acme-ai": [
        {
            "id": "acme-ai/Acme-2",
            "createdAt": "2026-11-10T09:00:00.000Z",
            "likes": 900,
            "pipeline_tag": "text-generation",
        },
        {
            "id": "acme-ai/Acme-2-GGUF",
            "createdAt": "2026-11-11T09:00:00.000Z",
            "likes": 4,
            "pipeline_tag": "text-generation",
        },
        {
            "id": "acme-ai/Acme-Vision",
            "createdAt": "2026-11-12T09:00:00.000Z",
            "likes": 50,
            "pipeline_tag": "image-classification",
        },
        {
            "id": "acme-ai/Acme-1",
            "createdAt": "2026-06-01T09:00:00.000Z",
            "likes": 2000,
            "pipeline_tag": "text-generation",
        },
    ]
}
CARDS = {
    "acme-ai/Acme-2": {
        "model-index": [
            {
                "name": "Acme-2",
                "results": [
                    {"dataset": {"name": "MMLU-Pro"}, "metrics": [{"type": "accuracy", "value": 71.25}]},
                    {"dataset": {"name": "GPQA"}, "metrics": [{"type": "accuracy", "value": 48.0}]},
                ],
            }
        ]
    }
}


def fake_get(url):
    if "?author=" in url:
        author = url.split("author=")[1].split("&")[0]
        return LISTING.get(author, [])
    model = url.split("/api/models/")[1].split("?")[0].replace("%2F", "/")
    return {"id": model, "cardData": CARDS.get(model, {})}


def run(*argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        code = main(list(argv))
    return code, out.getvalue()


class DiscoverTests(unittest.TestCase):
    def test_filters_and_card_scores(self):
        found = discover(["acme-ai"], "2026-11-01", set(), min_likes=10, get=fake_get)
        self.assertEqual([f["model"] for f in found], ["acme-ai/Acme-2"])  # old, low-like and non-text dropped
        self.assertEqual(found[0]["scores"], {"MMLU-Pro": 71.25, "GPQA": 48.0})
        self.assertEqual(found[0]["source"], "https://huggingface.co/acme-ai/Acme-2")
        self.assertEqual(len(discover(["acme-ai"], "2026-11-01", set(), any_task=True, get=fake_get)), 3)
        self.assertEqual(discover(["acme-ai"], "2026-11-01", {"acme-2", "acme-2-gguf"}, get=fake_get), [])
        with self.assertRaises(ValueError):
            discover(["../etc"], "2026-11-01", set(), get=fake_get)

    def test_card_scores_ignores_junk(self):
        card = {
            "model-index": [
                {
                    "results": [
                        {"dataset": {}, "metrics": [{"value": 1}]},
                        {"dataset": {"name": "X"}, "metrics": [{"value": "n/a"}, {"value": True}]},
                    ]
                }
            ]
        }
        self.assertEqual(card_scores(card), {})
        self.assertEqual(card_scores({}), {})

    def test_cli_adds_scored_launches_and_prints_the_rest(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = os.path.join(tmp, "feed.json")
            with (
                mock.patch("modelarena.hf._get", fake_get),
                mock.patch("modelarena.hf.discover.__defaults__", (0, False, fake_get, 50)),
            ):
                code, out = run(
                    "discover", "--labs", "acme-ai", "--since", "2026-11-01", "--add-scored", "--store", store
                )
            self.assertEqual(code, 0, out)
            self.assertIn("added   2026-11-10  acme-ai/Acme-2", out)
            self.assertIn('launch-add "acme-ai/Acme-2-GGUF" --lab acme-ai --date 2026-11-11', out)
            with open(store, encoding="utf-8") as fh:
                feed = json.load(fh)
            self.assertEqual(feed[0]["scores"]["GPQA"], 48.0)
            _, out = run("story", "acme-ai/Acme-2", "--store", store)
            self.assertIn("huggingface.co/acme-ai/Acme-2", out)
            self.assertEqual(run("discover", "--labs", "acme-ai", "--since", "yesterday", "--store", store)[0], 1)


if __name__ == "__main__":
    unittest.main()
