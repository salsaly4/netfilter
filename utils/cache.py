"""
Модуль для работы с кэшем файлов.
"""

import os
import sys
from typing import List


def ensure_cache_dir():
    """Создает директорию .cache, если она не существует."""
    if not os.path.exists(".cache"):
        try:
            os.makedirs(".cache")
        except (IOError, OSError) as e:
            print(f"Warning: Could not create cache directory: {e}", file=sys.stderr)


def get_cached_data(source: str) -> List[str]:
    """Получает кэшированные данные для указанного источника."""
    cache_file = os.path.join(".cache", f"{source}.txt")
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                return [line.strip() for line in f.readlines() if line.strip()]
        except (IOError, OSError) as e:
            print(
                f"Warning: Could not read cache file {cache_file}: {e}", file=sys.stderr
            )
    return []


def save_to_cache(source: str, data: List[str]):
    """Сохраняет данные в кэш для указанного источника."""
    if not data:
        print(f"Warning: No data to cache for {source}", file=sys.stderr)
        return

    cache_file = os.path.join(".cache", f"{source}.txt")
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            for item in data:
                if item.strip():
                    f.write(f"{item}\n")
    except (IOError, OSError) as e:
        print(f"Warning: Could not write cache file {cache_file}: {e}", file=sys.stderr)
