#!/usr/bin/env python3
"""
Простой тест для проверки работоспособности модулей.
"""

import sys
import os


def test_imports():
    """Тестирует импорт всех модулей."""
    try:
        from core.route_collector import collect_routes
        from core.bird_manager import apply_bird_configuration
        from fetchers.bgp_fetcher import get_routes_from_bgptools
        from fetchers.tor_fetcher import get_routes_from_tor
        from fetchers.github_fetcher import get_routes_from_github
        from fetchers.antifilter_fetcher import get_routes_from_antifilter
        from fetchers.twitter_fetcher import get_routes_from_twitter
        from network.processor import process_networks_in_memory
        from utils.cache import ensure_cache_dir, get_cached_data, save_to_cache
        from utils.file_utils import get_file_hash, read_as_list

        print("✓ Все модули успешно импортированы")
        return True
    except ImportError as e:
        print(f"✗ Ошибка импорта: {e}")
        return False


def test_basic_functionality():
    """Тестирует базовую функциональность."""
    try:
        from utils.cache import ensure_cache_dir
        from utils.file_utils import get_file_hash

        # Тест создания кэш директории
        ensure_cache_dir()
        if os.path.exists(".cache"):
            print("✓ Кэш директория создана успешно")
        else:
            print("✗ Кэш директория не создана")
            return False

        # Тест хеширования файла
        test_content = "test content"
        with open("test_file.txt", "w") as f:
            f.write(test_content)

        hash_result = get_file_hash("test_file.txt")
        if hash_result:
            print("✓ Хеширование файла работает")
        else:
            print("✗ Хеширование файла не работает")
            return False

        # Очистка
        os.remove("test_file.txt")
        return True

    except Exception as e:
        print(f"✗ Ошибка тестирования: {e}")
        return False


def main():
    """Основная функция тестирования."""
    print("Тестирование модулей antibl...")
    print("-" * 40)

    # Тест импортов
    if not test_imports():
        print("Тест импортов не пройден")
        return False

    # Тест базовой функциональности
    if not test_basic_functionality():
        print("Тест базовой функциональности не пройден")
        return False

    print("-" * 40)
    print("✓ Все тесты пройдены успешно!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
