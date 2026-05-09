import json
import time
import threading
from calendar import timegm
from datetime import datetime, timezone

from flask import Flask, render_template

import feedparser

app = Flask(__name__)

FEED_SOURCES = [
    {
        "url": "https://news.google.com/rss/search?q=artificial+intelligence+enterprise&hl=en-US&gl=US&ceid=US:en",
        "label": "Google News · AI in enterprise",
    },
    {
        "url": "https://news.google.com/rss/search?q=AI+regulation+Europe&hl=en-US&gl=US&ceid=US:en",
        "label": "Google News · EU AI regulation",
    },
    {
        "url": "https://news.google.com/rss/search?q=AI+healthcare+technology&hl=en-US&gl=US&ceid=US:en",
        "label": "Google News · AI & healthcare",
    },
]

_cache = {"items": [], "last_fetch": 0, "last_refresh_utc": ""}
_lock = threading.Lock()
CACHE_TTL = 3600


def _time_ago(published_parsed):
    if not published_parsed:
        return ""
    ts = timegm(published_parsed)
    delta = time.time() - ts
    if delta < 3600:
        return f"{int(delta // 60)}m ago"
    if delta < 86400:
        return f"{int(delta // 3600)}h ago"
    return f"{int(delta // 86400)}d ago"


def _fetch():
    items = []
    for src in FEED_SOURCES:
        try:
            d = feedparser.parse(src["url"])
            for entry in d.entries[:3]:
                items.append({
                    "title": entry.get("title", ""),
                    "link": entry.get("link", "#"),
                    "source": src["label"],
                    "ago": _time_ago(entry.get("published_parsed")),
                })
        except Exception:
            pass
    return items[:8]


def get_feeds():
    now = time.time()
    with _lock:
        if now - _cache["last_fetch"] > CACHE_TTL or not _cache["items"]:
            _cache["items"] = _fetch()
            _cache["last_fetch"] = now
            _cache["last_refresh_utc"] = datetime.now(timezone.utc).strftime(
                "%Y-%m-%d %H:%M UTC"
            )
    return _cache["items"], _cache["last_refresh_utc"]


PLOTLY_TEASER = {
    "data": [
        {
            "type": "treemap",
            "labels": [
                "Trauma & Orthopaedics", "General Surgery", "Ear Nose & Throat",
                "Ophthalmology", "Gynaecology", "Cardiology", "Neurology",
                "Dermatology", "Urology", "Gastroenterology", "Plastic Surgery",
                "Rheumatology", "Cardiothoracic Surgery", "Oral Surgery", "Other",
            ],
            "parents": [""] * 15,
            "values": [
                841000, 460000, 604000, 637000, 555000, 439000, 244000,
                411000, 341000, 434000, 170000, 163000, 24000, 231000, 1580000,
            ],
            "textinfo": "label+value",
            "marker": {
                "colors": [
                    16.8, 13.9, 15.1, 13.2, 16.4, 12.7, 15.9, 10.8,
                    12.1, 13.6, 18.4, 12.8, 11.2, 17.5, 13.0,
                ],
                "colorscale": [
                    [0.0, "#0F172A"], [0.25, "#78350F"],
                    [0.55, "#D97706"], [0.8, "#FBBF24"], [1.0, "#F59E0B"],
                ],
                "showscale": True,
                "colorbar": {
                    "title": "Median weeks",
                    "tickfont": {"color": "#9CA3AF"},
                },
                "line": {"color": "#0A0B0D", "width": 1},
            },
            "hovertemplate": (
                "<b>%{label}</b><br>Waiting list: %{value:,.0f}"
                "<br>Median weeks: %{color:.1f}<extra></extra>"
            ),
        }
    ],
    "layout": {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {
            "family": "Inter, system-ui, sans-serif",
            "color": "#CBD5E1",
            "size": 13,
        },
        "margin": {"l": 0, "r": 0, "t": 30, "b": 0},
        "title": {
            "text": "NHS England waiting list · treemap by specialty",
            "font": {"color": "#F8FAFC", "size": 15},
            "x": 0.02,
        },
    },
}


@app.route("/")
def index():
    feeds, last_refresh = get_feeds()
    return render_template(
        "index.html",
        feeds=feeds,
        last_refresh=last_refresh,
        plotly_teaser=json.dumps(PLOTLY_TEASER),
    )


@app.route("/team")
def team_page():
    return render_template("team.html", active_page="team")


@app.route("/contact")
def contact_page():
    return render_template("contact.html", active_page="contact")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
