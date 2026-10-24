import argparse
import json
import sys
from datetime import date

from .core import box_score, load_feed, recap, standings


def main(argv=None):
    ap = argparse.ArgumentParser(prog="model-sportscenter")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("recap", "boxscore"):
        p = sub.add_parser(name)
        p.add_argument("feed")
        p.add_argument("model")
    s = sub.add_parser("standings")
    s.add_argument("feed")
    s.add_argument("--as-of")
    a = ap.parse_args(argv)
    with open(a.feed, encoding="utf-8") as fh:
        feed = load_feed(json.load(fh))
    if a.cmd == "recap":
        print(recap(feed, a.model))
    elif a.cmd == "boxscore":
        bs = box_score(feed, a.model)
        print(f"{bs['model']} ({bs['lab']}) - {bs['date']}")
        print(f"{'benchmark':<12}{'score':>8}{'prev best':>11}{'delta':>8}  holder")
        for r in bs["rows"]:
            prev = "-" if r["prev_best"] is None else f"{r['prev_best']:g}"
            delta = "-" if r["delta"] is None else f"{r['delta']:+.1f}"
            print(f"{r['benchmark']:<12}{r['score']:>8g}{prev:>11}{delta:>8}  {r['prev_holder'] or '-'}{'  RECORD' if r['record'] else ''}")
    else:
        st = standings(feed, date.fromisoformat(a.as_of) if a.as_of else None)
        print(f"Standings as of {st['as_of']}")
        for b, h in st["titles"].items():
            print(f"  {b:<12} {h['model']:<12} {h['lab']:<16} {h['score']:g} (since {h['since']})")
        print("Days at #1 (summed across benchmarks):")
        for lab, d in st["days_at_one"].items():
            print(f"  {lab:<16} {d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
