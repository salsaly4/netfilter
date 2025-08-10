"""
Модуль для получения Tor-узлов.
"""

import ipaddress
import re
import requests
import sys
from typing import List

from utils.cache import ensure_cache_dir, get_cached_data, save_to_cache


def get_routes_from_tor() -> List[str]:
    """Получает список Tor-узлов."""
    ensure_cache_dir()
    url = "https://www.dan.me.uk/torlist/"
    try:
        print("Fetching Tor node list...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        routes = []
        for line in response.text.splitlines():
            line = line.strip()
            if re.match(r"\b([0-9]{1,3}\.){3}[0-9]{1,3}\b", line):
                try:
                    # Проверяем, что это действительно валидный IP адрес
                    ipaddress.IPv4Address(line)
                    routes.append(f"{line}/32")
                except ipaddress.AddressValueError:
                    print(
                        f"Warning: Invalid IP address in Tor list: {line}",
                        file=sys.stderr,
                    )
        print(f"Successfully fetched {len(routes)} Tor nodes.")
        save_to_cache("tor", routes)
        return routes
    except requests.RequestException as e:
        print(f"Error fetching Tor node list: {e}", file=sys.stderr)
        cached_routes = get_cached_data("tor")
        if cached_routes:
            print(f"Using cached data for Tor nodes: {len(cached_routes)} routes.")
            return cached_routes
        return []
