"""
Модуль для получения данных от antifilter.
"""

import requests
import sys
from typing import List

from utils.cache import ensure_cache_dir, get_cached_data, save_to_cache


def get_routes_from_antifilter() -> List[str]:
    """Получает списки ipsum.lst и subnet.lst с antifilter.download."""
    ensure_cache_dir()
    urls = [
        "https://antifilter.download/list/ipsum.lst",
        "https://antifilter.download/list/subnet.lst",
    ]
    routes = []
    for url in urls:
        try:
            print(f"Fetching list from {url}...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            url_routes = []
            for line in response.text.splitlines():
                if line.strip():
                    url_routes.append(line.strip())
            routes.extend(url_routes)
            print(f"Successfully fetched {len(url_routes)} routes from {url}.")
        except requests.RequestException as e:
            print(f"Error fetching list from {url}: {e}", file=sys.stderr)
    if routes:
        save_to_cache("antifilter", routes)
        return routes
    cached_routes = get_cached_data("antifilter")
    if cached_routes:
        print(f"Using cached data for antifilter: {len(cached_routes)} routes.")
        return cached_routes
    return []
