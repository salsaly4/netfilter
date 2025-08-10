"""
Модуль для получения данных Twitter.
"""

import requests
import sys
from typing import List

from utils.cache import ensure_cache_dir, get_cached_data, save_to_cache


def get_routes_from_twitter() -> List[str]:
    """Получает список IP-адресов Twitter."""
    ensure_cache_dir()
    url = (
        "https://raw.githubusercontent.com/SecOps-Institute/"
        "TwitterIPLists/master/twitter_ip_list.lst"
    )
    try:
        print("Fetching Twitter IP list...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        routes = []
        for line in response.text.splitlines():
            if line.strip():
                routes.append(line.strip())
        print(f"Successfully fetched {len(routes)} Twitter IPs.")
        save_to_cache("twitter", routes)
        return routes
    except requests.RequestException as e:
        print(f"Error fetching Twitter IP list: {e}", file=sys.stderr)
        cached_routes = get_cached_data("twitter")
        if cached_routes:
            print(f"Using cached data for Twitter IPs: {len(cached_routes)} routes.")
            return cached_routes
        return []
