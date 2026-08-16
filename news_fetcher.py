"""
news_fetcher.py
-----------------
Pulls recent crypto headlines from free public RSS feeds.
No API key or signup required - RSS feeds are open by design.

If you later want richer news (more sources, full articles),
you can swap this out for a paid API like CryptoPanic or
NewsAPI by adding a key as a GitHub Secret.
"""

import feedparser
import time

# Free, no-key-required crypto news RSS feeds
RSS_FEEDS = [
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://cointelegraph.com/rss",
    "https://decrypt.co/feed",
]


def get_recent_headlines(query: str, hours: int = 12, max_items: int = 30):
    """
    Fetch headlines from all feeds that mention `query`
    (case-insensitive) and were published within `hours`.
    Returns a list of headline strings.
    """
    cutoff = time.time() - (hours * 3600)
    matches = []

    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
        except Exception:
            continue  # skip a feed if it's temporarily down

        for entry in feed.entries:
            title = getattr(entry, "title", "")
            if query.lower() not in title.lower():
                continue

            # Try to respect the time window; if no timestamp, include it anyway
            published = getattr(entry, "published_parsed", None)
            if published:
                entry_time = time.mktime(published)
                if entry_time < cutoff:
                    continue

            matches.append(title)
            if len(matches) >= max_items:
                break

    return matches
