# model-sportscenter

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
