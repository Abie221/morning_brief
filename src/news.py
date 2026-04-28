import concurrent.futures
import re
from typing import Optional

import feedparser
import requests

HN_TOP_STORIES = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM = "https://hacker-news.firebaseio.com/v0/item/{}.json"

RSS_FEEDS = [
    ("TLDR AI", "https://tldr.tech/api/rss/ai"),
    ("Import AI", "https://importai.substack.com/feed"),
]

FETCH_TIMEOUT = 10


def _fetch_hn_item(item_id: int) -> Optional[dict]:
    try:
        r = requests.get(HN_ITEM.format(item_id), timeout=5)
        data = r.json()
        if data.get("type") != "story" or not data.get("url"):
            return None
        return {
            "title": data.get("title", ""),
            "summary": data.get("title", ""),
            "url": data.get("url", ""),
            "source": "Hacker News",
        }
    except Exception:
        return None


def _fetch_hn(max_items: int = 30) -> list:
    try:
        r = requests.get(HN_TOP_STORIES, timeout=5)
        ids = r.json()[:60]
    except Exception:
        return []

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        futures = [ex.submit(_fetch_hn_item, i) for i in ids]
        for fut in concurrent.futures.as_completed(futures, timeout=FETCH_TIMEOUT):
            try:
                item = fut.result()
            except Exception:
                continue
            if item:
                results.append(item)
            if len(results) >= max_items:
                break

    return results[:max_items]


def _fetch_rss(name: str, url: str) -> list:
    try:
        feed = feedparser.parse(url)
        items = []
        for entry in feed.entries[:10]:
            summary = entry.get("summary", entry.get("description", entry.get("title", "")))
            summary = re.sub(r"<[^>]+>", "", summary).strip()[:400]
            items.append({
                "title": entry.get("title", ""),
                "summary": summary,
                "url": entry.get("link", ""),
                "source": name,
            })
        return items
    except Exception:
        return []


def fetch_news() -> list:
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        hn_fut = ex.submit(_fetch_hn, 30)
        rss_futs = [ex.submit(_fetch_rss, name, url) for name, url in RSS_FEEDS]

        try:
            results.extend(hn_fut.result(timeout=FETCH_TIMEOUT))
        except Exception:
            pass

        for fut in rss_futs:
            try:
                results.extend(fut.result(timeout=FETCH_TIMEOUT))
            except Exception:
                pass

    return results
