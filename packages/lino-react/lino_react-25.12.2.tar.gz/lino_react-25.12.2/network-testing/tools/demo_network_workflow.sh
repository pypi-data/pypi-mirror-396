#!/usr/bin/env bash

# Complete workflow demonstrating network logging and mocking
# This script shows:
# 1. Running Puppeteer tests with network logging
# 2. Running RTL tests with network mocking from captured logs

echo "🎬 Network Logging & Mocking Workflow Demo"
echo "==========================================="
echo ""
echo "This demonstrates the complete workflow:"
echo "1. Capture network traffic from Puppeteer tests"
echo "2. Use captured responses to mock RTL tests"
echo ""

SITE=${1:-noi}

cd "$(dirname "$0")/../.."

echo "🔧 Step 1: Preparing demo site..."
python puppeteers/${SITE}/manage.py prep --noinput

if [ $? -ne 0 ]; then
    echo "❌ Failed to prepare demo site"
    exit 1
fi

echo ""
echo "📡 Step 2: Running Puppeteer tests with network logging..."
echo "   This will capture all network requests and responses"
echo ""
LOG_NETWORK=1 BASE_SITE=${SITE} npm run itest

if [ $? -ne 0 ]; then
    echo "⚠️  Puppeteer tests had issues, but logs should still be captured"
fi

LOG_FILE="network-testing/logs/network-log-${SITE}.json"

if [ ! -f "$LOG_FILE" ]; then
    echo ""
    echo "❌ Network log file was not created!"
    exit 1
fi

echo ""
echo "✅ Network log captured: $LOG_FILE"
echo ""
echo "📊 Quick analysis of captured requests:"
python analyze_network_logs.py "$LOG_FILE" | head -30

echo ""
echo ""
echo "🎭 Step 3: Running RTL tests with network mocking..."
echo "   This will use the captured responses to mock all network calls"
echo ""

MOCK_NETWORK=1 BASE_SITE=${SITE} BABEL=1 npm run rtltest

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ RTL tests completed successfully with mocked network!"
else
    echo ""
    echo "⚠️  RTL tests had issues"
fi

echo ""
echo "🎉 Workflow Demo Complete!"
echo ""
echo "Summary:"
echo "  1. ✅ Captured network traffic from Puppeteer tests"
echo "  2. ✅ Saved to: $LOG_FILE"
echo "  3. ✅ Used mocked responses in RTL tests"
echo ""
echo "💡 Key Commands:"
echo "   Capture:  LOG_NETWORK=1 BASE_SITE=${SITE} npm run itest"
echo "   Mock RTL: MOCK_NETWORK=1 BASE_SITE=${SITE} BABEL=1 npm run rtltest"
echo "   Analyze:  python analyze_network_logs.py $LOG_FILE"
echo "   View:     python view_network_log.py $LOG_FILE"
