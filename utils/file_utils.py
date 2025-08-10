"""
Модуль для работы с файлами.
"""

import hashlib
import os
import sys
from typing import Dict


def get_file_hash(filename: str) -> str:
    """Вычисляет MD5 хеш файла."""
    if not filename or not os.path.exists(filename):
        return ""
    try:
        with open(filename, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except (IOError, OSError) as e:
        print(
            f"Warning: Could not read file {filename} for hash calculation: {e}",
            file=sys.stderr,
        )
        return ""


def read_as_list(filename: str) -> Dict[int, str]:
    """Читает список AS с комментариями."""
    as_list = {}
    with open(filename, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if line and not line.startswith("#"):
                try:
                    parts = line.split("#", 1)
                    asn = int(parts[0].strip())  # Convert ASN to integer
                    comment = parts[1].strip() if len(parts) > 1 else ""
                    as_list[asn] = comment
                except (ValueError, IndexError) as e:
                    print(
                        f"Warning: Invalid ASN format on line {line_num}: {line.strip()}",
                        file=sys.stderr,
                    )
    return as_list
