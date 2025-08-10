"""
Модуль для получения данных с GitHub.
"""

import os
import requests
import sys
from typing import List, Dict

from utils.cache import ensure_cache_dir, get_cached_data, save_to_cache


def get_routes_from_github() -> List[str]:
    """Получает список ext-manual.lst с GitHub."""
    ensure_cache_dir()
    url = (
        "https://raw.githubusercontent.com/salsaly4/netfilter/"
        "refs/heads/master/ext-manual.lst"
    )
    try:
        print(f"Fetching manual routes from {url}...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        routes = []
        for line in response.text.splitlines():
            if line.strip():
                routes.append(line.strip())
        print(f"Successfully fetched {len(routes)} manual routes from GitHub.")
        save_to_cache("manual", routes)
        return routes
    except requests.RequestException as e:
        print(f"Error fetching manual routes from {url}: {e}", file=sys.stderr)
        cached_routes = get_cached_data("manual")
        if cached_routes:
            print(f"Using cached data for manual routes: {len(cached_routes)} routes.")
            return cached_routes
        return []


def get_exclude_list(exclude_file: str = None) -> List[str]:
    """Получает список исключений из файла или GitHub."""
    ensure_cache_dir()
    if exclude_file and exclude_file.strip() and os.path.exists(exclude_file):
        print(f"Reading exclude list from {exclude_file}...")
        try:
            with open(exclude_file, "r", encoding="utf-8") as f:
                excludes = [line.strip() for line in f if line.strip()]
        except (IOError, OSError) as e:
            print(f"Error reading exclude file {exclude_file}: {e}", file=sys.stderr)
            return []
        print(f"Successfully read {len(excludes)} exclude entries.")
        return excludes

    url = (
        "https://raw.githubusercontent.com/salsaly4/netfilter/"
        "refs/heads/master/exclude.lst"
    )
    try:
        print(f"Fetching exclude list from {url}...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        excludes = []
        for line in response.text.splitlines():
            if line.strip():
                excludes.append(line.strip())
        print(f"Successfully fetched {len(excludes)} exclude entries.")
        save_to_cache("exclude", excludes)
        return excludes
    except requests.RequestException as e:
        print(f"Error fetching exclude list: {e}", file=sys.stderr)
        cached_excludes = get_cached_data("exclude")
        if cached_excludes:
            print(f"Using cached exclude list: {len(cached_excludes)} entries.")
            return cached_excludes
        return []


def get_as_list(as_list_file: str = None) -> Dict[int, str]:
    """Получает список AS из файла или GitHub, кэширует и использует кэш при ошибке."""
    ensure_cache_dir()
    if as_list_file and as_list_file.strip() and os.path.exists(as_list_file):
        print(f"Reading AS list from {as_list_file}...")
        try:
            with open(as_list_file, "r", encoding="utf-8") as f:
                as_list = {}
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith("#"):
                        try:
                            parts = line.split("#", 1)
                            asn = int(parts[0].strip())
                            comment = parts[1].strip() if len(parts) > 1 else ""
                            as_list[asn] = comment
                        except (ValueError, IndexError) as e:
                            print(
                                f"Warning: Invalid ASN format on line {line_num}: {line.strip()}",
                                file=sys.stderr,
                            )
        except (IOError, OSError) as e:
            print(f"Error reading AS list file {as_list_file}: {e}", file=sys.stderr)
            return {}
        print(f"Successfully read {len(as_list)} AS entries.")
        return as_list

    url = "https://raw.githubusercontent.com/salsaly4/netfilter/refs/heads/master/aslist.txt"
    try:
        print(f"Downloading AS list from {url}...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        as_list = {}
        for line_num, line in enumerate(response.text.splitlines(), 1):
            line = line.strip()
            if line and not line.startswith("#"):
                try:
                    parts = line.split("#", 1)
                    asn = int(parts[0].strip())
                    comment = parts[1].strip() if len(parts) > 1 else ""
                    as_list[asn] = comment
                except (ValueError, IndexError) as e:
                    print(
                        f"Warning: Invalid ASN format on line {line_num}: {line.strip()}",
                        file=sys.stderr,
                    )
        print(f"Successfully downloaded {len(as_list)} AS entries.")
        save_to_cache("aslist", [str(asn) for asn in as_list.keys()])
        return as_list
    except requests.RequestException as e:
        print(f"Failed to download AS list: {e}")
        cached_as_list = get_cached_data("aslist")
        if cached_as_list:
            print(f"Using cached AS list: {len(cached_as_list)} entries.")
            return {int(asn): "" for asn in cached_as_list if str(asn).isdigit()}
        return {}
