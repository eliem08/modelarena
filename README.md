# model-sportscenter

[![CI](https://github.com/eliem08/model-sportscenter/actions/workflows/ci.yml/badge.svg)](https://github.com/eliem08/model-sportscenter/actions/workflows/ci.yml)

> **ESPN for AI** — every model launch covered like a big game.

Model launches are the Super Bowl of tech Twitter, but coverage is a mess of
screenshots and vibes. `model-sportscenter` turns a launch feed into sports
coverage: box scores, records broken, lab standings, title streaks and a
ready-to-post recap.

## What the MVP does

- **Launch feed** (JSON): model, lab, date, benchmark scores
- **Box score** for any launch vs. the previous best on every benchmark
- **Records broken** detection and margin of victory
- **Standings**: for each benchmark, who holds the title, since when, and
  "days at #1" per lab across the season
- **Recap generator**: headline + play-by-play paragraph in a sports voice
- Ships with a small sample feed (illustrative numbers, not real results)

## Quickstart

```bash
pip install -e .
model-sportscenter recap examples/launches.json "Nova-3"
model-sportscenter standings examples/launches.json --as-of 2026-10-24
model-sportscenter boxscore examples/launches.json "Nova-3"
```

## Roadmap

- Live ingest from lab blogs, arXiv, leaderboards (LMArena, SWE-bench, ARC)
- Daily video recap (pairs with hyperframes) and push alerts ("BREAKING: new SOTA")
- Fantasy league: draft models, score points from benchmark wins
- Betting-style prediction markets on next launch (education only)

## Development

Zero runtime dependencies; Python 3.10+.

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python -m unittest discover -s tests -t .           # unit + CLI smoke tests
ruff check . && ruff format --check .               # lint + format
```

```
model_sportscenter/core.py       domain logic (pure, importable, fully tested)
model_sportscenter/__main__.py   CLI (`model-sportscenter ...` / `python -m model_sportscenter ...`)
tests/                unit tests + generated CLI smoke tests
examples/             sample inputs used by the docs and smoke tests
```

CI runs lint and tests on Ubuntu and Windows across Python 3.10, 3.12 and 3.13.
Design, data model, trade-offs and production path: **[ARCHITECTURE.md](ARCHITECTURE.md)**.

Part of the [agent-economy](https://github.com/eliem08/agent-economy) portfolio (idea #11).
