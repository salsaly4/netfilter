#!/bin/bash

# Script for setting up cron job for antibl
# Author: Alexander Bulanov

# Set strict mode
set -euo pipefail

# Project directory path (absolute path)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_SCRIPT="$SCRIPT_DIR/run_antibl.sh"

# Check that run script exists
if [[ ! -f "$RUN_SCRIPT" ]]; then
    echo "Error: run_antibl.sh not found in $SCRIPT_DIR" >&2
    exit 1
fi

# Check that script is executable
if [[ ! -x "$RUN_SCRIPT" ]]; then
    echo "Error: run_antibl.sh is not executable" >&2
    exit 1
fi

echo "Setting up cron job for antibl..."
echo "Project directory: $SCRIPT_DIR"
echo "Run script: $RUN_SCRIPT"
echo ""

echo "Note: On macOS, cron setup requires manual configuration due to system restrictions."
echo ""
echo "To manually set up cron job:"
echo "1. Open crontab for editing:"
echo "   crontab -e"
echo ""
echo "2. Add this line (replace with your actual path):"
echo "   0 * * * * $RUN_SCRIPT"
echo ""
echo "3. Save and exit the editor"
echo ""
echo "Alternative: Use launchd (macOS native scheduler)"
echo "1. Create a plist file in ~/Library/LaunchAgents/"
echo "2. Use launchctl to load and start the job"
echo ""
echo "For more details, see CRON_README.md"

echo ""
echo "For manual testing run:"
echo "  $RUN_SCRIPT"
echo ""
echo "For removing cron job run:"
echo "  crontab -e"
echo "  (delete line with run_antibl.sh)"
