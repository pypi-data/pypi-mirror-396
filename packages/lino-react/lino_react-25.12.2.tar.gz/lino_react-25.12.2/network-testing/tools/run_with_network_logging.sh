#!/usr/bin/env bash

# Script to run Jest tests with network request logging enabled
# Usage: ./run_with_network_logging.sh [site] [options]
#
# Examples:
#   ./run_with_network_logging.sh noi
#   ./run_with_network_logging.sh avanti
#   ./run_with_network_logging.sh noi skipprep

SITE=${1:-noi}
SKIP_PREP=$2

# Change to react repository root
cd "$(dirname "$0")/../.."

echo "🧪 Running ${SITE} tests with network logging enabled..."
echo "📁 Network logs will be saved to: ./network-testing/logs/"
echo ""

# Prepare demo site unless skipprep is specified
if [ "$SKIP_PREP" != "skipprep" ] ; then
    echo "🔧 Preparing demo site..."
    python puppeteers/${SITE}/manage.py prep --noinput
    if [ $? -ne 0 ]; then
        echo "❌ Failed to prepare demo site"
        exit 1
    fi
    echo ""
fi

# Run tests with network logging
echo "▶️  Running tests..."
LOG_NETWORK=1 BASE_SITE=${SITE} npm run itest

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Tests completed successfully"
    echo "📝 Check ./network-testing/logs/ for the generated JSON file"
else
    echo ""
    echo "❌ Tests failed"
    exit 1
fi
