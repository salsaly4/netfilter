"""
Модуль для управления BIRD.
"""

import subprocess
import sys


def apply_bird_configuration():
    """Применяет изменения в конфигурации BIRD."""
    print("Applying changes to BIRD configuration...")
    try:
        # Проверяем, существует ли команда birdc
        result = subprocess.run(["which", "birdc"], capture_output=True, text=True)
        if result.returncode != 0:
            print(
                "Warning: birdc command not found. Skipping BIRD configuration reload.",
                file=sys.stderr,
            )
            return False

        subprocess.run(["birdc", "configure"], check=True)
        print("Successfully reloaded BIRD configuration.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error reloading BIRD configuration: {e}", file=sys.stderr)
        return False
    except FileNotFoundError:
        print(
            "Error: birdc command not found. Please install BIRD routing daemon.",
            file=sys.stderr,
        )
        return False
