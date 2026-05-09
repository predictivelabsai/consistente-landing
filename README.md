# Consistente Landing Site

Landing site for [consistente.tech](https://consistente.tech). Built with FastHTML, styled with Tailwind CSS (CDN), and deployed via Docker on Coolify.

## Local Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

The app starts on [http://localhost:5037](http://localhost:5037).

## Docker

```bash
docker build -t consistente-landing .
docker run -p 5037:5037 consistente-landing
```

## Deploy on Coolify

1. Create a new resource in Coolify, select your GitHub repo
2. Choose **Dockerfile** as the build pack
3. Set **FQDN** to `https://consistente.tech`
4. Set **Exposed Port** to `5037`
5. Make sure DNS for `consistente.tech` points to your Coolify server IP (A record)
6. Deploy — Coolify handles the reverse proxy and SSL via Let's Encrypt

## Tests

```bash
pip install playwright pytest
python -m playwright install chromium
python -m pytest tests/test_pages.py -v
```

## Project Structure

```
main.py              Entrypoint (imports app from app.py)
app.py               FastHTML routes (/, /team, /contact)
components.py        Shared UI components and layout
content/
  team.py            Team member data
  case_studies.py    Case study content
  news.py            RSS feed fetcher (background refresh)
  signal.py          Plotly chart builder from CSV data
  data/*.csv         Public dataset CSVs for signal charts
static/
  site.css           Custom styles (slate + amber theme)
  three-hero.js      Three.js globe animation
  signal.js          Plotly chart renderer
tests/
  test_pages.py      Playwright smoke tests
```
