#!/usr/bin/env python3
import ipaddress
from typing import List
import argparse


def read_networks(filename: str) -> List[ipaddress.IPv4Network]:
    """Читает список сетей из файла."""
    networks = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                networks.append(ipaddress.IPv4Network(line))
    return networks


def exclude_subnets(network: ipaddress.IPv4Network, excludes: list) -> list:
    """Рекурсивно исключает все подсети из excludes из network."""
    for ex in excludes:
        if ex.subnet_of(network):
            result = []
            for sub in network.subnets(new_prefix=network.prefixlen + 1):
                if ex == sub:
                    continue  # полностью совпадает — не добавляем!
                elif ex.overlaps(sub):
                    result.extend(exclude_subnets(sub, [ex]))
                else:
                    result.append(sub)
            return result
    return [network]


def process_networks(netlist_file: str, exclude_file: str, output_file: str):
    """Обрабатывает списки сетей и создает результирующий файл."""
    networks = read_networks(netlist_file)
    exclude_networks = read_networks(exclude_file)

    result_networks = set()

    for net in networks:
        # Находим все исключения, которые попадают в эту сеть
        relevant_excludes = [
            ex for ex in exclude_networks
            if ex.subnet_of(net)
        ]
        result_networks.update(exclude_subnets(net, relevant_excludes))

    # Сортируем сети по возрастанию
    sorted_networks = sorted(
        result_networks,
        key=lambda x: (x.network_address, x.prefixlen)
    )

    # Записываем результат, обеспечивая уникальность строк
    seen_networks = set()
    with open(output_file, 'w') as f:
        for net in sorted_networks:
            net_str = str(net)
            if net_str not in seen_networks:
                f.write(f"{net_str}\n")
                seen_networks.add(net_str)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Обработка сетей с исключениями.'
    )
    parser.add_argument(
        '-i', '--input', default='networks.txt',
        help='Входной файл со списком сетей (по умолчанию: networks.txt)'
    )
    parser.add_argument(
        '-x', '--exclude', default='exclude.txt',
        help='Файл исключений (по умолчанию: exclude.txt)'
    )
    parser.add_argument(
        '-o', '--output', default='result.txt',
        help='Выходной файл (по умолчанию: result.txt)'
    )
    args = parser.parse_args()

    process_networks(args.input, args.exclude, args.output)
