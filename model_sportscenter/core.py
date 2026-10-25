"""Box scores, records, standings and recaps for model launches."""

from __future__ import annotations

from collections import defaultdict
from datetime import date

__all__ = ["load_feed", "box_score", "standings", "recap"]


def load_feed(items: list[dict]) -> list[dict]:
    if not isinstance(items, list) or not all(isinstance(i, dict) for i in items):
        raise ValueError("feed must be a JSON list of launch objects")
    feed = [{**i, "date": date.fromisoformat(i["date"])} for i in items]
    return sorted(feed, key=lambda i: i["date"])


def _find(feed, model):
    for i in feed:
        if i["model"].lower() == model.lower():
            return i
    raise KeyError(f"model {model!r} not in feed")


def box_score(feed: list[dict], model: str) -> dict:
    """Compare a launch with the best previous score on each benchmark."""
    launch = _find(feed, model)
    prior = [i for i in feed if i["date"] < launch["date"]]
    rows = []
    for bench, score in launch["scores"].items():
        prev = [(i["scores"][bench], i) for i in prior if bench in i["scores"]]
        if prev:
            best, holder = max(prev, key=lambda p: p[0])
            rows.append(
                {
                    "benchmark": bench,
                    "score": score,
                    "prev_best": best,
                    "prev_holder": holder["model"],
                    "prev_lab": holder["lab"],
                    "delta": round(score - best, 2),
                    "record": score > best,
                }
            )
        else:
            rows.append(
                {
                    "benchmark": bench,
                    "score": score,
                    "prev_best": None,
                    "prev_holder": None,
                    "prev_lab": None,
                    "delta": None,
                    "record": True,
                }
            )
    return {
        "model": launch["model"],
        "lab": launch["lab"],
        "date": launch["date"].isoformat(),
        "rows": rows,
        "records": sum(r["record"] for r in rows),
    }


def standings(feed: list[dict], as_of: date | None = None) -> dict:
    """Title holders per benchmark and total days-at-#1 per lab."""
    as_of = as_of or date.today()
    benches = sorted({b for i in feed for b in i["scores"]})
    holders, days = {}, defaultdict(int)
    for bench in benches:
        best, reign = None, []
        for i in feed:
            if bench in i["scores"] and i["date"] <= as_of and (best is None or i["scores"][bench] > best[0]):
                best = (i["scores"][bench], i)
                reign.append((i["date"], i))
        for (start, holder), nxt in zip(reign, [*reign[1:], (as_of, None)]):
            days[holder["lab"]] += (nxt[0] - start).days
        if best:
            holders[bench] = {
                "model": best[1]["model"],
                "lab": best[1]["lab"],
                "score": best[0],
                "since": reign[-1][0].isoformat(),
            }
    return {
        "as_of": as_of.isoformat(),
        "titles": holders,
        "days_at_one": dict(sorted(days.items(), key=lambda kv: -kv[1])),
    }


def recap(feed: list[dict], model: str) -> str:
    bs = box_score(feed, model)
    records = [r for r in bs["rows"] if r["record"] and r["delta"] is not None]
    misses = [r for r in bs["rows"] if not r["record"]]
    if records:
        big = max(records, key=lambda r: r["delta"])
        headline = f"{bs['lab'].upper()} STRIKES: {bs['model']} smashes {big['benchmark']} record by {big['delta']:.1f}"
    elif misses:
        headline = f"{bs['model']} comes up short as {misses[0]['prev_lab']} holds on"
    else:
        headline = f"{bs['model']} opens the season for {bs['lab']}"
    lines = [headline, ""]
    plays = []
    for r in records:
        steal = "steals the crown from" if r["prev_lab"] != bs["lab"] else "breaks its own lab's record held by"
        plays.append(
            f"On {r['benchmark']}, {bs['model']} posts {r['score']:g}, {steal} {r['prev_holder']} ({r['prev_best']:g})."
        )
    for r in misses:
        plays.append(
            f"{r['benchmark']} stays with {r['prev_holder']}: {r['score']:g} falls {abs(r['delta']):.1f} short."
        )
    for r in bs["rows"]:
        if r["delta"] is None:
            plays.append(f"First-ever {r['benchmark']} mark on the board: {r['score']:g}.")
    lines.append(" ".join(plays))
    lines.append("")
    lines.append(f"Final tally: {bs['records']} record(s) of {len(bs['rows'])} benchmarks entered. ({bs['date']})")
    return "\n".join(lines)
