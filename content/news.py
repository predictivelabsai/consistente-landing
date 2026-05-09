"""
News module. Pulls from a curated set of RSS/Atom feeds and serves a cached
list of items per category.

- One module-level in-memory cache keyed by category.
- A background daemon thread refreshes every hour so page renders never block.
- Per-feed fetch timeout is aggressive (6s) so a slow feed can't hold up
  the whole refresh. Per-feed failures are silently dropped.
"""

from __future__ import annotations

import html
import re
import socket
import threading
import time
from datetime import datetime, timezone
from typing import Any

import feedparser


_GNEWS = "https://news.google.com/rss/search?hl=en-GB&gl=GB&ceid=GB:en&q="

FEEDS: dict[str, list[tuple[str, str]]] = {
    "ai": [
        ("Google News · AI in enterprise",
         _GNEWS + "%22artificial+intelligence%22+enterprise+OR+%22public+sector%22+when:14d"),
        ("Google News · EU AI Act & regulation",
         _GNEWS + "%22EU+AI+Act%22+OR+%22AI+regulation%22+Europe+when:30d"),
        ("Google News · Generative AI enterprise",
         _GNEWS + "%22generative+AI%22+enterprise+deployment+when:14d"),
    ],
    "healthcare": [
        ("Google News · AI & healthcare",
         _GNEWS + "NHS+AI+OR+%22digital+health%22+UK+when:14d"),
        ("Google News · European health data",
         _GNEWS + "%22European+Health+Data+Space%22+OR+%22health+data%22+EU+AI+when:30d"),
    ],
    "financial": [
        ("Google News · Financial services + AI",
         _GNEWS + "%22financial+services%22+AI+regulation+UK+OR+FCA+when:14d"),
        ("Google News · FinTech AI Europe",
         _GNEWS + "FinTech+AI+Europe+when:14d"),
    ],
}

HOME_MIX_ORDER = ["ai", "healthcare", "financial"]


REFRESH_SECONDS = 60 * 60
FETCH_TIMEOUT_SECONDS = 6
MAX_ITEMS_PER_FEED = 10
MAX_ITEMS_PER_CATEGORY = 6
MAX_ITEMS_HOME = 8

_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Consistente-NewsFetcher/1.0"
)

_cache: dict[str, list[dict[str, Any]]] = {k: [] for k in FEEDS}
_cache["home"] = []
_cache_lock = threading.Lock()
_last_refresh = 0.0


_DROP_PATTERNS = [
    r"accessibility\s+statement",
    r"how\s+to\s+use\s+(these|this|the)\s+guidelines?",
    r"terms?\s+of\s+reference",
    r"fatality\s+investigation",
    r"investigation\s+into\s+the\s+deaths?",
    r"\bcorrigendum\b",
    r"privacy\s+notice",
    r"cookie\s+policy",
]
_DROP_RE = re.compile("|".join(_DROP_PATTERNS), re.IGNORECASE)


def _parse_entry(source_label: str, entry: Any) -> dict[str, Any] | None:
    title = (entry.get("title") or "").strip()
    link = entry.get("link") or ""
    if not title or not link:
        return None
    published_struct = entry.get("published_parsed") or entry.get("updated_parsed")
    if published_struct:
        try:
            published = datetime(*published_struct[:6], tzinfo=timezone.utc)
        except (TypeError, ValueError):
            published = None
    else:
        published = None
    return {
        "title": html.unescape(title),
        "url": link,
        "source": source_label,
        "published": published,
    }


def _fetch_feed(source_label: str, url: str) -> list[dict[str, Any]]:
    old_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(FETCH_TIMEOUT_SECONDS)
    try:
        parsed = feedparser.parse(url, agent=_USER_AGENT)
    except Exception:
        return []
    finally:
        socket.setdefaulttimeout(old_timeout)

    out: list[dict[str, Any]] = []
    for entry in (parsed.entries or [])[:MAX_ITEMS_PER_FEED]:
        item = _parse_entry(source_label, entry)
        if item and not _DROP_RE.search(item["title"]):
            out.append(item)
    return out


def _dedupe(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for item in items:
        key = item["title"].lower()[:120]
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def _sort_by_recency(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    undated_pos = len(items)

    def key(item):
        p = item.get("published")
        if p is None:
            nonlocal undated_pos
            undated_pos -= 1
            return (0, undated_pos)
        return (1, p.timestamp())

    return sorted(items, key=key, reverse=True)


def _refresh_category(key: str) -> list[dict[str, Any]]:
    gathered: list[dict[str, Any]] = []
    for source_label, url in FEEDS.get(key, []):
        gathered.extend(_fetch_feed(source_label, url))
    gathered = _dedupe(gathered)
    gathered = _sort_by_recency(gathered)
    return gathered[:MAX_ITEMS_PER_CATEGORY]


def _build_home_mix() -> list[dict[str, Any]]:
    mixed: list[dict[str, Any]] = []
    for cat in HOME_MIX_ORDER:
        for item in _cache.get(cat, [])[:3]:
            mixed.append(item)
    mixed = _dedupe(mixed)
    return mixed[:MAX_ITEMS_HOME]


def refresh_all():
    global _last_refresh
    for key in FEEDS:
        items = _refresh_category(key)
        with _cache_lock:
            _cache[key] = items
    with _cache_lock:
        _cache["home"] = _build_home_mix()
        _last_refresh = time.time()


def _refresher_loop():
    while True:
        try:
            refresh_all()
        except Exception:
            pass
        time.sleep(REFRESH_SECONDS)


def start_background_refresh():
    if getattr(start_background_refresh, "_started", False):
        return
    start_background_refresh._started = True
    t = threading.Thread(target=_refresher_loop, daemon=True, name="news-refresher")
    t.start()


def items_for(category: str) -> list[dict[str, Any]]:
    with _cache_lock:
        return list(_cache.get(category, []))


def last_refresh_iso() -> str | None:
    if _last_refresh <= 0:
        return None
    return datetime.fromtimestamp(_last_refresh, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def format_published(p: datetime | None) -> str:
    if p is None:
        return ""
    now = datetime.now(tz=timezone.utc)
    delta = now - p
    hours = int(delta.total_seconds() // 3600)
    if hours < 1:
        return "just now"
    if hours < 24:
        return f"{hours}h ago"
    days = hours // 24
    if days < 7:
        return f"{days}d ago"
    return p.strftime("%d %b %Y")
