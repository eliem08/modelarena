"""Operating commands: keep your own launch feed and publish from it (also served by the web app).

Every launch carries the source it was taken from, so a published number can always be traced.
"""

import json
import math
import os
from datetime import date

from .core import box_score, load_feed, recap, standings

OPS = ("launch-add", "launch-remove", "launches", "story", "league", "export")


class DeskError(ValueError):
    pass


def load(path: str) -> list[dict]:
    try:
        with open(path, encoding="utf-8-sig") as fh:
            items = json.load(fh)
    except FileNotFoundError:
        return []
    if not isinstance(items, list):
        raise DeskError(f"{path}: not a modelarena feed")
    return items


def save(items: list[dict], path: str):
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(sorted(items, key=lambda i: i["date"]), fh, indent=2)
    os.replace(tmp, path)


def scores(items) -> dict:
    out = {}
    for item in items:
        bench, sep, value = item.partition("=")
        try:
            out[bench.strip()] = float(value)
        except ValueError:
            raise DeskError(f"--score must look like benchmark=number, got {item!r}") from None
        if not sep or not bench.strip() or not math.isfinite(out[bench.strip()]):
            raise DeskError(f"--score must look like benchmark=number, got {item!r}")
    return out


def add_ops(sub):
    store = os.environ.get("MODELARENA_STORE", "feed.json")
    p = sub.add_parser("launch-add", help="record a model launch and its benchmark scores")
    p.add_argument("model")
    p.add_argument("--lab", required=True)
    p.add_argument("--date", required=True, help="launch day, YYYY-MM-DD")
    p.add_argument("--score", action="append", required=True, help="benchmark=score (repeatable)")
    p.add_argument("--source", required=True, help="where the numbers come from (URL of the paper or post)")
    sub.add_parser("launch-remove", help="take a launch off the feed (a retraction)").add_argument("model")
    sub.add_parser("launches", help="everything on the feed, oldest first")
    sub.add_parser(
        "story", help="the game-night write-up for a launch: headline, plays, box score, source"
    ).add_argument("model")
    sub.add_parser("league", help="title holders per benchmark and days at number one").add_argument("--as-of")
    sub.add_parser("export", help="the feed as JSON, for syndication")
    for name in OPS:
        sub.choices[name].add_argument("--store", default=store)


def run_ops(a) -> int:
    try:
        items = load(a.store)
        _run(items, a)
        return 0
    except (ValueError, KeyError) as e:
        print(f"refused: {e.args[0] if e.args else e}")
        return 1


def _run(items: list[dict], a):
    c = a.cmd
    if c == "launch-add":
        if any(i["model"].lower() == a.model.lower() for i in items):
            raise DeskError(f"{a.model} is already on the feed; remove it first to correct it")
        try:
            day = date.fromisoformat(a.date)
        except ValueError:
            raise DeskError(f"{a.date!r} is not a date like 2026-12-01") from None
        if not a.source.startswith(("https://", "http://")):
            raise DeskError("--source must be a link to where the numbers were published")
        item = {"model": a.model, "lab": a.lab, "date": day.isoformat(), "scores": scores(a.score), "source": a.source}
        items.append(item)
        save(items, a.store)
        bs = box_score(load_feed(items), a.model)
        print(f"{a.model} ({a.lab}) on the feed: {bs['records']} record(s) of {len(bs['rows'])} benchmarks")
    elif c == "launch-remove":
        keep = [i for i in items if i["model"].lower() != a.model.lower()]
        if len(keep) == len(items):
            raise DeskError(f"{a.model} is not on the feed")
        save(keep, a.store)
        print(f"{a.model} removed")
    elif c == "launches":
        for i in sorted(items, key=lambda i: i["date"]):
            marks = ", ".join(f"{b} {s:g}" for b, s in i["scores"].items())
            print(f"{i['date']}  {i['model']:<16}{i['lab']:<18}{marks}")
        if not items:
            print("feed is empty: add a launch with launch-add")
    elif c == "story":
        feed = load_feed(items)
        print(recap(feed, a.model))
        bs = box_score(feed, a.model)
        print(f"\n{'benchmark':<14}{'score':>8}{'prev best':>11}{'delta':>8}  holder")
        for r in bs["rows"]:
            prev = "-" if r["prev_best"] is None else f"{r['prev_best']:g}"
            delta = "-" if r["delta"] is None else f"{r['delta']:+.1f}"
            flag = "  RECORD" if r["record"] else ""
            print(f"{r['benchmark']:<14}{r['score']:>8g}{prev:>11}{delta:>8}  {r['prev_holder'] or '-'}{flag}")
        source = next(i for i in items if i["model"].lower() == a.model.lower()).get("source")
        if source:
            print(f"\nSource: {source}")
    elif c == "league":
        if not items:
            raise DeskError("feed is empty: add a launch with launch-add")
        try:
            as_of = date.fromisoformat(a.as_of) if a.as_of else None
        except ValueError:
            raise DeskError(f"{a.as_of!r} is not a date like 2026-12-01") from None
        st = standings(load_feed(items), as_of)
        print(f"Standings as of {st['as_of']}")
        for b, h in st["titles"].items():
            print(f"  {b:<14}{h['model']:<16}{h['lab']:<18}{h['score']:g} (since {h['since']})")
        print("Days at #1, summed across benchmarks:")
        for lab, d in st["days_at_one"].items():
            print(f"  {lab:<18}{d}")
    else:
        print(json.dumps(sorted(items, key=lambda i: i["date"]), indent=2))
