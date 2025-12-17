# Network Testing - Organization Summary

## ✅ What Was Done

All network logging and mocking functionality has been organized into a dedicated `network-testing/` directory with a clear structure:

```
network-testing/
├── README.md                       # Main documentation & quick start
├── networkLogger.js                # Core: Captures network traffic
├── networkMockLoader.js            # Core: Mocks requests in RTL tests
│
├── docs/                           # All documentation
│   ├── NETWORK_LOGGING.md                 # Complete technical docs
│   ├── NETWORK_LOGGING_QUICKSTART.md      # Quick start guide
│   ├── NETWORK_LOGGING_SUMMARY.md         # Implementation details
│   └── NETWORK_LOGGING_REFERENCE.txt      # Command reference card
│
├── tools/                          # Utility scripts
│   ├── run_with_network_logging.sh        # Run tests with logging
│   ├── demo_network_logging.sh            # Demo logging feature
│   ├── demo_network_workflow.sh           # Complete workflow demo
│   ├── analyze_network_logs.py            # Statistical analysis
│   └── view_network_log.py                # Interactive viewer
│
└── logs/                           # Output directory (gitignored)
    ├── README.md                          # Logs directory docs
    ├── network-log-noi.json              # Generated logs
    └── network-log-*.json                # (per site)
```

## 🔧 What Was Updated

### Code Files
- **`lino_react/react/testSetup/testEnvironment.js`** - Updated import path
- **`lino_react/react/testSetup/setupTests.ts`** - Updated import path and log directory
- **`network-testing/networkLogger.js`** - Updated default output directory
- **`network-testing/networkMockLoader.js`** - Updated log path resolution
- **`.gitignore`** - Updated to ignore `network-testing/logs/*.json`

### Scripts
All shell scripts updated to:
- Change to react root directory automatically
- Use new paths: `network-testing/logs/`, `network-testing/tools/`

### Documentation
All documentation files updated with new paths and structure.

## 📍 Entry Points

### For Users
- **`NETWORK_TESTING.md`** (in react root) - Quick reference pointing to full docs
- **`network-testing/README.md`** - Main documentation with everything you need

### For Developers
- **`network-testing/networkLogger.js`** - Where logging is implemented
- **`network-testing/networkMockLoader.js`** - Where mocking is implemented

## 🚀 How to Use

### Basic Usage
```bash
# From anywhere in the react directory
LOG_NETWORK=1 BASE_SITE=noi npm run itest
MOCK_NETWORK=1 BASE_SITE=noi BABEL=1 npm run rtltest
```

### Using Tools
```bash
# Scripts work from anywhere
network-testing/tools/run_with_network_logging.sh noi
network-testing/tools/demo_network_workflow.sh noi

# Python tools (run from react root)
python network-testing/tools/analyze_network_logs.py \
    network-testing/logs/network-log-noi.json

python network-testing/tools/view_network_log.py \
    network-testing/logs/network-log-noi.json
```

## 📦 Output Location

All logs are saved to: **`network-testing/logs/`**

Files:
- `network-log-noi.json`
- `network-log-avanti.json`
- etc.

(These are gitignored and regenerated on each test run)

## 🎯 Key Improvements

1. **Clear Organization** - All related files in one directory
2. **Logical Structure** - Separate subdirectories for docs, tools, logs
3. **Self-Documenting** - README in main directory and logs subdirectory
4. **Easy to Find** - `NETWORK_TESTING.md` in root points to full docs
5. **Relative Paths** - Scripts work from any location
6. **Clean Root** - React root directory no longer cluttered

## 🔍 Quick Reference

| What You Need | Where to Find It |
|---------------|------------------|
| Quick start guide | `network-testing/README.md` |
| Complete documentation | `network-testing/docs/NETWORK_LOGGING.md` |
| Command reference | `network-testing/docs/NETWORK_LOGGING_REFERENCE.txt` |
| Run tests with logging | `network-testing/tools/run_with_network_logging.sh` |
| Analyze logs | `network-testing/tools/analyze_network_logs.py` |
| View logs interactively | `network-testing/tools/view_network_log.py` |
| Complete demo | `network-testing/tools/demo_network_workflow.sh` |
| Log files | `network-testing/logs/network-log-*.json` |

## ✨ No Breaking Changes

All existing functionality works exactly the same:
- Same environment variables (`LOG_NETWORK=1`, `MOCK_NETWORK=1`)
- Same npm commands (`npm run itest`, `npm run rtltest`)
- Same test code (no changes needed)
- Same JSON output format

Only the file organization changed - everything is now in `network-testing/`.

## 📚 Next Steps

To get started:
1. Read `network-testing/README.md`
2. Try `network-testing/tools/demo_network_workflow.sh noi`
3. Check `network-testing/docs/NETWORK_LOGGING_QUICKSTART.md` for common tasks

For questions or details, see `network-testing/docs/NETWORK_LOGGING.md`.
