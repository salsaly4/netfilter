"""
Модуль для получения данных из BGP.
"""

import json
import requests
import sys
from typing import Dict, List

from utils.cache import ensure_cache_dir, get_cached_data, save_to_cache


def get_routes_from_bgptools(as_list: Dict[int, str]) -> List[str]:
    """Получает список маршрутов AS от bgp.tools."""
    ensure_cache_dir()
    url = "https://bgp.tools/table.jsonl"
    headers = {"User-Agent": "Alexander Bulanov bgp.tools - bgp@abulanov.com"}
    try:
        print("Fetching routes from bgp.tools...")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        routes = []
        for line in response.text.splitlines():
            data = json.loads(line)
            asn = data.get("ASN")  # ASN is already an integer
            cidr = data.get("CIDR", "")
            if asn in as_list and cidr and ":" not in cidr and "." in cidr:
                routes.append(cidr)
        print(f"Successfully fetched {len(routes)} routes from bgp.tools.")
        save_to_cache("bgptools", routes)
        return routes
    except requests.RequestException as e:
        print(f"Error fetching routes from bgp.tools: {e}", file=sys.stderr)
        cached_routes = get_cached_data("bgptools")
        if cached_routes:
            print(f"Using cached data for bgp.tools: {len(cached_routes)} routes.")
            return cached_routes
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from bgp.tools: {e}", file=sys.stderr)
        cached_routes = get_cached_data("bgptools")
        if cached_routes:
            print(f"Using cached data for bgp.tools: {len(cached_routes)} routes.")
            return cached_routes
        return []
