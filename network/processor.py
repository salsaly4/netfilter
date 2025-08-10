"""
Модуль для обработки сетей и IP-адресов.
"""

import ipaddress
import sys
from typing import List


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
                try:
                    result.append(ipaddress.IPv4Network(line))
                except ValueError as e:
                    print(
                        f"Warning: Invalid network format: {line.strip()}",
                        file=sys.stderr,
                    )
    return result


def exclude_subnets(network: ipaddress.IPv4Network, excludes: list) -> list:
    """Рекурсивно исключает все подсети из excludes из network."""
    if not isinstance(network, ipaddress.IPv4Network):
        print(f"Warning: Invalid network type: {type(network)}", file=sys.stderr)
        return [network]

    for ex in excludes:
        if not isinstance(ex, ipaddress.IPv4Network):
            print(f"Warning: Invalid exclude type: {type(ex)}", file=sys.stderr)
            continue

        if ex.subnet_of(network):
            result = []
            try:
                for sub in network.subnets(new_prefix=network.prefixlen + 1):
                    if ex == sub:
                        continue  # полностью совпадает — не добавляем!
                    if ex.overlaps(sub):
                        result.extend(exclude_subnets(sub, [ex]))
                    else:
                        result.append(sub)
                return result
            except ValueError as e:
                print(
                    f"Warning: Error processing subnet {network}: {e}", file=sys.stderr
                )
                return [network]
    return [network]


def summarize_networks(
    networks: List[ipaddress.IPv4Network],
) -> List[ipaddress.IPv4Network]:
    """
    Рекурсивно суммаризует список сетей для получения минимального размера.
    Объединяет соседние подсети в более крупные сети.
    """
    if not networks:
        return []

    # Сортируем сети по адресу и префиксу
    sorted_networks = sorted(networks, key=lambda x: (x.network_address, x.prefixlen))

    result = []
    i = 0

    while i < len(sorted_networks):
        current = sorted_networks[i]

        # Ищем соседние сети, которые можно объединить
        j = i + 1
        candidates = [current]

        while j < len(sorted_networks):
            next_net = sorted_networks[j]

            # Проверяем, можно ли объединить текущую сеть с следующей
            if (
                current.prefixlen == next_net.prefixlen
                and current.supernet(new_prefix=current.prefixlen - 1).network_address
                == next_net.supernet(new_prefix=next_net.prefixlen - 1).network_address
            ):

                # Проверяем, что объединенная сеть не содержит других сетей из списка
                supernet = current.supernet(new_prefix=current.prefixlen - 1)
                can_merge = True

                for k in range(len(sorted_networks)):
                    if k != i and k != j:
                        other_net = sorted_networks[k]
                        if supernet.overlaps(other_net) and not other_net.subnet_of(
                            supernet
                        ):
                            can_merge = False
                            break

                if can_merge:
                    candidates.append(next_net)
                    j += 1
                else:
                    break
            else:
                break

        if len(candidates) > 1:
            # Объединяем сети
            merged = candidates[0].supernet(new_prefix=candidates[0].prefixlen - 1)
            result.append(merged)
            i = j
        else:
            # Не можем объединить, добавляем как есть
            result.append(current)
            i += 1

    # Рекурсивно применяем суммаризацию, если что-то изменилось
    if len(result) < len(networks):
        return summarize_networks(result)

    return result


def process_networks_in_memory(
    networks: List[str], excludes: List[str], output_file: str, summarize: bool = False
):
    """Обрабатывает списки сетей в памяти и создает результирующий файл."""
    if not networks:
        print("Warning: No networks to process", file=sys.stderr)
        return

    networks_list = read_networks_from_list(networks)
    exclude_networks = read_networks_from_list(excludes)

    if not networks_list:
        print("Warning: No valid networks found after parsing", file=sys.stderr)
        return

    result_networks = set()

    for net in networks_list:
        # Находим все исключения, которые попадают в эту сеть
        relevant_excludes = [ex for ex in exclude_networks if ex.subnet_of(net)]
        result_networks.update(exclude_subnets(net, relevant_excludes))

    if not result_networks:
        print("Warning: No networks after processing", file=sys.stderr)
        return

    # Применяем суммаризацию, если запрошено
    if summarize:
        print("Applying network summarization...")
        original_count = len(result_networks)
        result_networks = set(summarize_networks(list(result_networks)))
        final_count = len(result_networks)
        print(
            f"Summarization reduced networks from {original_count} to {final_count} (saved {original_count - final_count} entries)"
        )

    # Сортируем сети по возрастанию
    sorted_networks = sorted(
        result_networks, key=lambda x: (x.network_address, x.prefixlen)
    )

    # Записываем результат, обеспечивая уникальность строк
    seen_networks = set()
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            for net in sorted_networks:
                net_str = str(net)
                if net_str not in seen_networks:
                    f.write(f"{net_str}\n")
                    seen_networks.add(net_str)
    except (IOError, OSError) as e:
        print(f"Error writing output file {output_file}: {e}", file=sys.stderr)
        raise
