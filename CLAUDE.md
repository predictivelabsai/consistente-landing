# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Marketing/landing site for [consistente.tech](https://consistente.tech) — a static-feeling, server-rendered FastHTML app. There is no database, build step, or JS bundler: pages are Python functions returning HTML, styled with Tailwind via CDN.

## Commands

```bash
# Run locally (serves on http://localhost:5037)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py

# Tests (Playwright smoke tests — boot the app in a subprocess, screenshot each route, assert the h1)
pip install playwright pytest
python -m playwright install chromium      # one-time
python -m pytest tests/test_pages.py -v

# Single route: tests are parametrized over ROUTES via test_route
python -m pytest "tests/test_pages.py::test_route[/team-team-small group]" -v

# Docker (parity with deploy; Coolify builds from this Dockerfile)
docker build -t consistente-landing . && docker run -p 5037:5037 consistente-landing
```

Port **5037** is deliberate (avoids clashing with a sibling `predictivelabs` app). `python main.py` uses FastHTML's `serve()`; the Docker `CMD` runs `uvicorn main:app` — `main.py` is only a thin shim re-exporting `app` from `app.py`.

## Architecture

Three layers, kept strictly separated — keep routes thin and push content/data outward:

- **`app.py`** — route handlers (`/`, `/team`, `/contact`) registered with `@rt(...)`. Each is a thin composition of `components.py` primitives fed by `content/*` data. App is created with `fast_app(live=False, static_path=".", pico=False)` — `pico=False` means **no PicoCSS**; all styling is Tailwind. `static_path="."` serves the repo root, so assets are referenced as `/static/...`.
- **`components.py`** — the design system and the `page(...)` wrapper. `page()` builds the full `<html>`: Tailwind CDN + an inline `TAILWIND_CONFIG` that defines the palette (slate `bg.*` / `ink.*` / `line.*` + amber `accent.*`) and fonts (Inter / JetBrains Mono), plus `static/site.css`, then wraps content in `Navbar` + `Main` + `Footer_`. Reusable primitives: `Heading`, `Eyebrow`, `Button_`, `Pill`, `Hero`, `Pillar`, `MetricTile`, `CaseStudyCard`, `NewsSection`, `CTASection`, `Section_`. Site-wide constants (`SITE_NAME`, `CONTACT_EMAIL`, `NAV_ITEMS`) live at the top of this file.
- **`content/`** — data and content-generation logic, no markup beyond what helpers build:
  - `team.py` / `case_studies.py` — plain Python data (`TEAM`, `ALL`, `BID_DERIVED`, `NAMED_PRECEDENTS`).
  - `news.py` — RSS/Atom fetcher. Holds an **in-memory cache keyed by category**, refreshed by a **background daemon thread every hour** that is started at import time via `news_mod.start_background_refresh()` in `app.py` (an import side effect). Per-feed timeout is 6s; per-feed failures are silently dropped so a slow feed never blocks a render.
  - `signal.py` + `data/*.csv` — reads the public-dataset CSVs and returns **Plotly trace dicts** (dark theme, amber scale). The server serializes these to JSON and injects them into a `window.PLOTLY_*` global; `static/signal.js` renders them client-side. Each CSV has a paired `*.SOURCE.md` documenting provenance.

**Client-side assets** (`static/`) load over CDN, not bundled: `three-hero.js` (decorative Three.js globe, loaded as `type="module"`), `signal.js` (Plotly renderer reading the injected window globals), `site.css` (canvas container + scroll-reveal), `favicon.svg`. Plotly and Three.js come from CDNs added per-page via the `body_extra=` argument to `page()`.

### Adding content
New section → add data to `content/*.py`, build markup with `components.py` primitives, compose it in the relevant `app.py` route. Reuse `Heading`/`Section_`/`Eyebrow` rather than hand-writing Tailwind classes so the palette and type scale stay consistent. To pull in a JS/CSS library, pass it through `head_extra=`/`body_extra=` on `page()`.

## Note on SKILLS.md

`SKILLS.md` is an **operations handoff** for an in-progress domain/registrar + IONOS email migration of `consistente.tech` — it is unrelated to the application code. Credentials referenced there live only in `.secrets/` (gitignored), never in the repo.
