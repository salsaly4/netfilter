#!/usr/bin/env python3
"""
Модуль для проверки и обработки списков IP-адресов и подсетей.
Предоставляет функциональность для работы с файлами, содержащими IP-адреса,
подсети и другие сетевые данные.
"""

import argparse
import os
import sys

from core.route_collector import collect_routes
from core.bird_manager import apply_bird_configuration
from utils.file_utils import get_file_hash


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
        help="Применить изменения в BIRD после обновления маршрутов",
    )
    parser.add_argument(
        "--summarize",
        action="store_true",
        help="Рекурсивно суммаризовать маршруты для минимизации размера списка",
    )
    args = parser.parse_args()

    if not args.output or not args.output.strip():
        print("Error: Output file not specified", file=sys.stderr)
        sys.exit(1)

    # Проверяем, что директория для выходного файла существует
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except (IOError, OSError) as e:
            print(
                f"Error: Could not create output directory {output_dir}: {e}",
                file=sys.stderr,
            )
            sys.exit(1)

    try:
        print(f"Collecting routes and writing to {args.output}...")
        collect_routes(
            args.as_list if args.as_list and args.as_list.strip() else None,
            args.output,
            args.exclude if args.exclude and args.exclude.strip() else None,
            args.summarize,
        )
        print("Routes collection completed successfully.")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error during route collection: {e}", file=sys.stderr)
        sys.exit(1)

    # Проверяем, что файл создан и не пустой
    if os.path.exists(args.output) and os.path.getsize(args.output) > 0:
        print(f"Output file {args.output} created successfully.")

        # Применяем BIRD конфигурацию, если запрошено
        if args.apply:
            if not apply_bird_configuration():
                sys.exit(1)
    else:
        print(
            f"Warning: Output file {args.output} is empty or was not created",
            file=sys.stderr,
        )
        if args.apply:
            print(
                "Cannot apply BIRD configuration - output file is invalid",
                file=sys.stderr,
            )


if __name__ == "__main__":
    main()
