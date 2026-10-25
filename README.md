<!-- sell-kit:start -->
# ModelArena

[![CI](https://github.com/eliem08/modelarena/actions/workflows/ci.yml/badge.svg)](https://github.com/eliem08/modelarena/actions/workflows/ci.yml)

> **Every AI model launch covered like a big game: box scores, records and recaps.**

**Who it's for:** AI newsletters, media sites and developer-relations teams.

**The problem:** Model launches are a firehose of benchmark claims with no consistent scorekeeping or history.

**What you get:** Launch box scores, all-time records, title reigns and auto-written recaps from a simple launch feed.

## Quickstart

Customers receive a release archive with the wheel and the examples. Python 3.10+ and no other dependencies.

```bash
pip install modelarena-0.1.0-py3-none-any.whl
modelarena recap examples/launches.json Nova-3
modelarena boxscore examples/launches.json Nova-3
modelarena standings examples/launches.json --as-of 2026-10-24
```

## Web app and API

Every command is also a JSON API endpoint and a browser form, served by the built-in web app.

```bash
modelarena-web --port 8000          # then open http://127.0.0.1:8000
modelarena-web keys create --label "first customer"   # prints an API key (stored hashed)
docker build -t modelarena . && docker run -p 8000:8000 -e API_KEYS=sk_... -v modelarena-data:/data modelarena
```

Every API call needs `Authorization: Bearer <key>` once any key exists; a server on a public address refuses to start without one. Calls are rate-limited per key (60/min, `--rate`) and metered: `modelarena-web usage` prints calls per key for billing.

Endpoints: `POST /api/recap`, `POST /api/boxscore`, `POST /api/standings`, plus `GET /healthz` and `GET /api/spec` (machine-readable field list).
Files are sent as `{"name": ..., "content": ...}`, folders as `{"files": [...]}` or a base64 zip.

## Pricing

Every plan starts with a 14-day free trial. Prices in USD, billed monthly unless noted.

| Plan | Price | Includes |
|---|---|---|
| **Creator** | $19 per month | Recaps and box scores; Standings; Personal use |
| **Publisher** | $99 per month | Commercial use; Embeddable standings; Records and reigns |
| **Media** | $499 per month | Unlimited outlets; Custom metrics; Priority support |

To start a trial or buy a plan, [request access](https://github.com/eliem08/modelarena/issues/new?title=ModelArena%20trial&labels=sales).

## Licence

Proprietary. Copyright (c) 2026 eliem08. All rights reserved. Use requires a paid plan or an active trial; see [LICENSE](LICENSE).
<!-- sell-kit:end -->

## What it does

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
modelarena recap examples/launches.json "Nova-3"
modelarena standings examples/launches.json --as-of 2026-10-24
modelarena boxscore examples/launches.json "Nova-3"
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
modelarena/core.py       domain logic (pure, importable, fully tested)
modelarena/__main__.py   CLI (`modelarena ...` / `python -m modelarena ...`)
tests/                unit tests + generated CLI smoke tests
examples/             sample inputs used by the docs and smoke tests
```

CI runs lint and tests on Ubuntu and Windows across Python 3.10, 3.12 and 3.13.
Design, data model, trade-offs and production path: **[ARCHITECTURE.md](ARCHITECTURE.md)**.

Part of the [agent-economy](https://github.com/eliem08/agent-economy) portfolio (idea #11).
