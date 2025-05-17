#!/usr/bin/env python3
"""
Модуль для проверки и обработки списков IP-адресов и подсетей.
Предоставляет функциональность для работы с файлами, содержащими IP-адреса,
подсети и другие сетевые данные.
"""

import argparse
import hashlib
import ipaddress
import json
import os
import re
import subprocess
import sys
from typing import List, Dict

import requests


def get_file_hash(filename: str) -> str:
    """Вычисляет MD5 хеш файла."""
    if not os.path.exists(filename):
        return ""
    with open(filename, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def read_as_list(filename: str) -> Dict[int, str]:
    """Читает список AS с комментариями."""
    as_list = {}
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                parts = line.split("#", 1)
                asn = int(parts[0].strip())  # Convert ASN to integer
                comment = parts[1].strip() if len(parts) > 1 else ""
                as_list[asn] = comment
    return as_list


def ensure_cache_dir():
    """Создает директорию .cache, если она не существует."""
    if not os.path.exists(".cache"):
        os.makedirs(".cache")


def get_cached_data(source: str) -> List[str]:
    """Получает кэшированные данные для указанного источника."""
    cache_file = os.path.join(".cache", f"{source}.txt")
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines()]
    return []


def save_to_cache(source: str, data: List[str]):
    """Сохраняет данные в кэш для указанного источника."""
    cache_file = os.path.join(".cache", f"{source}.txt")
    with open(cache_file, "w", encoding="utf-8") as f:
        for item in data:
            f.write(f"{item}\n")


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
            if asn in as_list and ":" not in data.get("CIDR", ""):
                routes.append(data["CIDR"])
        print(f"Successfully fetched {len(routes)} routes from bgp.tools.")
        save_to_cache("bgptools", routes)
        return routes
    except (requests.RequestException, json.JSONDecodeError) as e:
        print(f"Error fetching routes from bgp.tools: {e}", file=sys.stderr)
        cached_routes = get_cached_data("bgptools")
        if cached_routes:
            print(f"Using cached data for bgp.tools: {len(cached_routes)} routes.")
            return cached_routes
        return []


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
            if re.match(r"\b([0-9]{1,3}\.){3}[0-9]{1,3}\b", line):
                routes.append(f"{line}/32")
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


def read_networks_from_list(networks: List[str]) -> List[ipaddress.IPv4Network]:
    """Преобразует список строк в список сетей."""
    result = []
    for line in networks:
        line = line.strip()
        if line:
            # Если есть комментарий, берём только часть до #
            if "#" in line:
                line = line.split("#")[0].strip()
            if line:
                result.append(ipaddress.IPv4Network(line))
    return result


def exclude_subnets(network: ipaddress.IPv4Network, excludes: list) -> list:
    """Рекурсивно исключает все подсети из excludes из network."""
    for ex in excludes:
        if ex.subnet_of(network):
            result = []
            for sub in network.subnets(new_prefix=network.prefixlen + 1):
                if ex == sub:
                    continue  # полностью совпадает — не добавляем!
                if ex.overlaps(sub):
                    result.extend(exclude_subnets(sub, [ex]))
                else:
                    result.append(sub)
            return result
    return [network]


def process_networks_in_memory(
    networks: List[str], excludes: List[str], output_file: str
):
    """Обрабатывает списки сетей в памяти и создает результирующий файл."""
    networks_list = read_networks_from_list(networks)
    exclude_networks = read_networks_from_list(excludes)

    result_networks = set()

    for net in networks_list:
        # Находим все исключения, которые попадают в эту сеть
        relevant_excludes = [ex for ex in exclude_networks if ex.subnet_of(net)]
        result_networks.update(exclude_subnets(net, relevant_excludes))

    # Сортируем сети по возрастанию
    sorted_networks = sorted(
        result_networks, key=lambda x: (x.network_address, x.prefixlen)
    )

    # Записываем результат, обеспечивая уникальность строк
    seen_networks = set()
    with open(output_file, "w", encoding="utf-8") as f:
        for net in sorted_networks:
            net_str = str(net)
            if net_str not in seen_networks:
                f.write(f"{net_str}\n")
                seen_networks.add(net_str)


def get_exclude_list(exclude_file: str = None) -> List[str]:
    """Получает список исключений из файла или GitHub."""
    ensure_cache_dir()
    if exclude_file and os.path.exists(exclude_file):
        print(f"Reading exclude list from {exclude_file}...")
        with open(exclude_file, "r", encoding="utf-8") as f:
            excludes = [line.strip() for line in f if line.strip()]
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
    if as_list_file and as_list_file.strip():
        print(f"Reading AS list from {as_list_file}...")
        with open(as_list_file, "r", encoding="utf-8") as f:
            as_list = {}
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    parts = line.split("#", 1)
                    asn = int(parts[0].strip())
                    comment = parts[1].strip() if len(parts) > 1 else ""
                    as_list[asn] = comment
        print(f"Successfully read {len(as_list)} AS entries.")
        return as_list

    url = "https://raw.githubusercontent.com/salsaly4/netfilter/refs/heads/master/aslist.txt"
    try:
        print(f"Downloading AS list from {url}...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        as_list = {}
        for line in response.text.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                parts = line.split("#", 1)
                asn = int(parts[0].strip())
                comment = parts[1].strip() if len(parts) > 1 else ""
                as_list[asn] = comment
        print(f"Successfully downloaded {len(as_list)} AS entries.")
        save_to_cache("aslist", list(as_list.keys()))
        return as_list
    except requests.RequestException as e:
        print(f"Failed to download AS list: {e}")
        cached_as_list = get_cached_data("aslist")
        if cached_as_list:
            print(f"Using cached AS list: {len(cached_as_list)} entries.")
            return {int(asn): "" for asn in cached_as_list}
        return {}


def collect_routes(as_list_file: str, output_file: str, exclude_file: str = None):
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

    excludes = get_exclude_list(exclude_file)

    print("Applying exclusion filter...")
    process_networks_in_memory(sorted(all_routes), excludes, output_file)
    print("Successfully applied exclusion filter.")

    print("Processing output file for BIRD configuration...")
    with open(output_file, "r", encoding="utf-8") as f:
        routes = f.readlines()
    with open(output_file, "w", encoding="utf-8") as f:
        for route in routes:
            f.write(f"route {route.strip()} reject;\n")
    print("Successfully processed output file for BIRD configuration.")
    print(f"Final number of routes: {len(routes)}")


def main():
    """
    Основная функция программы.
    Обрабатывает аргументы командной строки и выполняет соответствующие действия.
    """
    parser = argparse.ArgumentParser(description="Сбор и фильтрация маршрутов.")
    parser.add_argument(
        "-a",
        "--as-list",
        default="",
        help="Файл со списком AS (по умолчанию: скачивается из GitHub)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="routes.txt",
        help="Выходной файл (по умолчанию: routes.txt)",
    )
    parser.add_argument(
        "-x",
        "--exclude",
        default="",
        help="Файл исключений (по умолчанию: скачивается из GitHub)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Применить изменения в BIRD при наличии изменений",
    )
    args = parser.parse_args()

    print(f"Checking for changes in {args.output}...")
    old_hash = get_file_hash(args.output)

    collect_routes(
        args.as_list if args.as_list.strip() else None,
        args.output,
        args.exclude if args.exclude.strip() else None,
    )

    new_hash = get_file_hash(args.output)
    if old_hash != new_hash:
        print("Changes detected in routes.")
        if args.apply:
            print("Applying changes to BIRD configuration...")
            try:
                subprocess.run(["birdc", "configure"], check=True)
                print("Successfully reloaded BIRD configuration.")
            except subprocess.CalledProcessError as e:
                print(f"Error reloading BIRD configuration: {e}", file=sys.stderr)
                sys.exit(1)
    else:
        print("No changes detected in routes.")


if __name__ == "__main__":
    main()
