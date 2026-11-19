"""Discover launches on Hugging Face so nobody has to notice them by hand.

`discover` lists recent public models from the organisations you follow (newest first, via the public
models API) that are not on the feed yet. A model whose card publishes benchmark results (the `model-index`
block) carries those scores, with the model page as the source. Most big labs publish their numbers in a blog
post or paper instead; those come back as candidates with lab, date and source filled in, so a person only
types the scores.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

API = "https://huggingface.co/api/models"
AUTHOR_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,95}$")
TASKS = {"text-generation", "image-text-to-text", "any-to-any", "text2text-generation"}


def _get(url: str, timeout: float = 20):
    req = urllib.request.Request(url, headers={"User-Agent": "modelarena", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        with e:
            raise ValueError(f"Hugging Face answered {e.code} for {url.split('?')[0]}") from None
    except (urllib.error.URLError, OSError) as e:
        raise ValueError(f"could not reach Hugging Face: {e}") from None


def card_scores(card: dict) -> dict:
    """Benchmark -> score from a model card's model-index block (empty if the card publishes none)."""
    out = {}
    for entry in (card or {}).get("model-index") or []:
        for res in entry.get("results") or []:
            ds = res.get("dataset") or {}
            bench = str(ds.get("name") or ds.get("type") or "").strip()
            for m in res.get("metrics") or []:
                v = m.get("value")
                if bench and isinstance(v, (int, float)) and not isinstance(v, bool):
                    name = bench if len(res.get("metrics")) == 1 else f"{bench} ({m.get('type') or m.get('name')})"
                    out.setdefault(name[:60], round(float(v), 2))
    return out


def discover(
    authors: list[str],
    since: str,
    on_feed: set[str],
    min_likes: int = 0,
    any_task: bool = False,
    get=_get,
    limit: int = 50,
) -> list[dict]:
    found = []
    for author in authors:
        if not AUTHOR_RE.match(author):
            raise ValueError(f"{author!r} is not a Hugging Face organisation name")
        q = urllib.parse.urlencode({"author": author, "sort": "createdAt", "direction": -1, "limit": limit})
        for m in get(f"{API}?{q}") or []:
            created = str(m.get("createdAt", ""))[:10]
            model = str(m.get("id", ""))
            if not created or created < since or not model or m.get("private"):
                continue
            if model.lower() in on_feed or model.split("/")[-1].lower() in on_feed:
                continue
            if m.get("likes", 0) < min_likes or (not any_task and m.get("pipeline_tag") not in TASKS):
                continue
            found.append(
                {
                    "model": model,
                    "lab": author,
                    "date": created,
                    "source": f"https://huggingface.co/{model}",
                    "scores": {},
                    "likes": m.get("likes", 0),
                    "task": m.get("pipeline_tag") or "",
                }
            )

    def scores_for(f):
        detail = get(f"{API}/{urllib.parse.quote(f['model'])}?expand%5B%5D=cardData") or {}
        return card_scores(detail.get("cardData") or {})

    # model cards are fetched in parallel so a run with several labs stays inside the hosted API's time limit
    with ThreadPoolExecutor(max_workers=8) as pool:
        for f, s in zip(found, pool.map(scores_for, found)):
            f["scores"] = s
    return sorted(found, key=lambda f: f["date"])
