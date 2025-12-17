#!/usr/bin/env bash

# Demo script showing network logging in action
# This runs a quick subset of tests and shows the results

echo "🎬 Network Logging Demo"
echo "======================"
echo ""
echo "This will:"
echo "1. Prepare the noi demo site"
echo "2. Run tests with network logging enabled"
echo "3. Show a summary of captured requests"
echo ""
read -p "Press Enter to continue..."

# Set up
export LOG_NETWORK=1
export BASE_SITE=noi

# Change to react repository root
cd "$(dirname "$0")/../.."

# Clean old logs
rm -f network-testing/logs/*.json

echo ""
echo "🔧 Preparing demo site..."
python puppeteers/noi/manage.py prep --noinput

if [ $? -ne 0 ]; then
    echo "❌ Failed to prepare demo site"
    exit 1
fi

echo ""
echo "▶️  Running tests with network logging..."
npm run itest

if [ $? -ne 0 ]; then
    echo "⚠️  Tests had issues, but logs should still be captured"
fi

echo ""
echo "📊 Analyzing captured network traffic..."
echo ""

# Check for log file
LATEST_LOG="network-testing/logs/network-log-noi.json"

if [ ! -f "$LATEST_LOG" ]; then
    echo "❌ No log file found!"
    exit 1
fi

echo "Found log file: $LATEST_LOG"
echo ""

# Show summary
python analyze_network_logs.py "$LATEST_LOG"

echo ""
echo "✅ Demo complete!"
echo ""
echo "📁 Full log available at: $LATEST_LOG"
echo "💡 Tip: Open the JSON file in a text editor or JSON viewer for detailed inspection"
