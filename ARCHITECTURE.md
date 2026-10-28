# Architecture — modelarena

## 1. Scope
Sports-style coverage of model launches: box scores, records, standings, title reigns, recaps.
**MVP:** launch feed (JSON) → box score vs. prior best, standings with days-at-#1, template recap generator.
**Product:** live ingestion pipeline, verified results, a media surface (site, newsletter, video, push alerts), fantasy league.

## 2. System context
```mermaid
flowchart LR
  Sources[Lab blogs / arXiv / leaderboards] --> Ingest[Ingest + extraction]
  Ingest --> Review[Editor verification]
  Review --> Feed[(Launch feed)]
  Feed --> Engine[Stats engine]
  Engine --> Recap[Recap writer]
  Recap --> Channels[Site / newsletter / X / video]
```

## 3. Components
| Module | Responsibility | Status |
|---|---|---|
| `load_feed` | Parse and sort launches by date | MVP |
| `box_score` | Per benchmark: score, previous best and holder, delta, record flag; first-ever marks | MVP |
| `standings` | Title holder per benchmark and reign history → days at #1 per lab up to `as_of` | MVP |
| `recap` | Deterministic headline + play-by-play from the box score | MVP |
| Extraction | LLM-assisted table extraction from launch posts, with human verification | Roadmap |

## 4. Design decisions
- **The stats engine is pure and deterministic.** The same feed always gives the same standings, so
  coverage is auditable and corrections are a re-run.
- **A record is strictly greater than the prior best.** Ties don't steal titles.
- **Template recaps first.** An LLM rewrite layer can add voice later, but numbers always come
  from the engine (no hallucinated scores).
- **Self-reported vs. independently verified scores** become a schema field (`source`), and
  standings can filter on it.

## 5. Production architecture
Postgres (launches, scores with source and provenance URL), a nightly standings materialisation,
and a static site generator + email (Resend) + social posting workers. Push alerts on "record broken" events.

## 6. Risks
Benchmark contamination and self-reporting. Mitigate by showing provenance badges and running
independent eval partners. Brand and trademark: the name and visuals must not imply ESPN affiliation.

## 7. Limitations (sell-ready audit, 2026-10-28)
- No feature gating by plan: every API key unlocks the same software. Publisher's
  embeddable standings are not built — the web app sends `X-Frame-Options:
  DENY`, so it cannot be framed into another site — and were removed from sales
  copy. Media's unlimited outlets are not enforced (no outlet accounts).
- The sample feed in examples/launches.json is illustrative, not real results
  (README already says this); a buyer must supply their own feed, and scores
  are taken at face value — there is no verification, provenance, or source
  field in the current feed schema, despite the roadmap mentioning it.
- Live ingest, video recaps, push alerts, fantasy league, and prediction
  markets are roadmap, not shipped.
- Docker build and a live Render/Fly deployment were not verified in the audit
  environment (no Docker binary there); Dockerfile, render.yaml, and fly.toml are
  the same template shape as vibe-lube, but a deployment claim remains
  "not verified" until one is made.
- Stripe prices were not verified against a live Stripe account in this run;
  checkout and revocation are covered in tests with mocked Stripe calls, and the
  README example now uses creator/publisher/media plan keys to match the plan names.
