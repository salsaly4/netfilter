"""
Основной модуль для сбора маршрутов.
"""

import os
import sys

from fetchers.bgp_fetcher import get_routes_from_bgptools
from fetchers.tor_fetcher import get_routes_from_tor
from fetchers.github_fetcher import (
    get_routes_from_github,
    get_exclude_list,
    get_as_list,
)
from fetchers.antifilter_fetcher import get_routes_from_antifilter
from fetchers.twitter_fetcher import get_routes_from_twitter
from network.processor import process_networks_in_memory


def collect_routes(
    as_list_file: str,
    output_file: str,
    exclude_file: str = None,
    summarize: bool = False,
):
    """Собирает маршруты из разных источников и применяет фильтрацию."""
    as_list = get_as_list(as_list_file)

    all_routes = set()

    routes = get_routes_from_bgptools(as_list)
    all_routes.update(routes)
    print(f"Added {len(routes)} routes from bgp.tools.")

    routes = get_routes_from_tor()
    all_routes.update(routes)
    print(f"Added {len(routes)} routes from Tor.")

    routes = get_routes_from_github()
    all_routes.update(routes)
    print(f"Added {len(routes)} routes from GitHub.")

    routes = get_routes_from_antifilter()
    all_routes.update(routes)
    print(f"Added {len(routes)} routes from antifilter.")

    routes = get_routes_from_twitter()
    all_routes.update(routes)
    print(f"Added {len(routes)} routes from Twitter.")

    print(f"Total routes collected: {len(all_routes)}")

    if not all_routes:
        print("Warning: No routes collected from any source", file=sys.stderr)
        return

    excludes = get_exclude_list(exclude_file)

    print("Applying exclusion filter...")
    process_networks_in_memory(sorted(all_routes), excludes, output_file, summarize)
    print("Successfully applied exclusion filter.")

    print("Processing output file for BIRD configuration...")
    try:
        if not os.path.exists(output_file):
            print(
                f"Warning: Output file {output_file} does not exist after processing",
                file=sys.stderr,
            )
            return

        with open(output_file, "r", encoding="utf-8") as f:
            routes = f.readlines()
        with open(output_file, "w", encoding="utf-8") as f:
            for route in routes:
                f.write(f"route {route.strip()} reject;\n")
        print("Successfully processed output file for BIRD configuration.")
        print(f"Final number of routes: {len(routes)}")
    except (IOError, OSError) as e:
        print(f"Error processing output file {output_file}: {e}", file=sys.stderr)
        raise
