#!/bin/bash

# Script for running antibl via cron
# Author: Alexander Bulanov
# Description: Updates the list of blocked routes

# Set strict mode
set -euo pipefail

# Project directory path (absolute path)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check that we are in the correct directory
if [[ ! -f "main.py" ]]; then
    echo "Error: main.py not found in current directory" >&2
    exit 1
fi

# Check virtual environment existence
if [[ ! -d "venv" ]]; then
    echo "Error: virtual environment not found" >&2
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check that Python is available
if ! command -v python &> /dev/null; then
    echo "Error: Python not found in virtual environment" >&2
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python --version 2>&1)
echo "Using: $PYTHON_VERSION"

# Запускаем antibl с параметрами
echo "Starting antibl at $(date)"
echo "Directory: $SCRIPT_DIR"

# Запускаем с параметром --summarize для автоматического обновления
python main.py --summarize --output routes.txt

# Проверяем результат выполнения
if [[ $? -eq 0 ]]; then
    echo "antibl completed successfully at $(date)"
    
    # Проверяем размер выходного файла
    if [[ -f "routes.txt" ]]; then
        FILE_SIZE=$(wc -l < routes.txt)
        echo "Created routes.txt file with $FILE_SIZE lines"
    fi
    
    exit 0
else
    echo "Error running antibl at $(date)"
    exit 1
fi
