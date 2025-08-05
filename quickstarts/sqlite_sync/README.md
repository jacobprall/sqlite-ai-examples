# SQLite-Sync Tutorial

Learn SQLite-Sync through a simple multi-device todo app! This tutorial shows you how SQLite-Sync enables automatic synchronization between devices with conflict-free data merging.

## 🎯 What You'll Learn

- **Multi-device sync** - See data automatically sync between devices
- **Offline-first behavior** - Work offline, sync when reconnected
- **Conflict resolution** - Watch CRDT technology resolve conflicts automatically  
- **Simple integration** - How easy it is to add sync to your SQLite app

## 🚀 Quick Start

### One-Command Setup

Run our interactive setup script that handles everything:

```bash
./setup.sh
```

This will:
- 🔍 Auto-detect your platform (macOS, Linux, Windows)
- 📥 Download the SQLite-Sync extension from GitHub
- 🐍 Create a Python virtual environment
- 📦 Install all dependencies
- 📁 Set up the project structure

### Manual Setup (Alternative)

If you prefer manual setup:

1. **Get the extension**: Download from [SQLite-Sync Releases](https://github.com/sqliteai/sqlite-sync/releases)
2. **Install dependencies**: `pip install click`

**Note:** The tutorial works without the extension in "local-only mode" for learning!

### Start the Tutorial

**Terminal 1:**
```bash
source venv/bin/activate
python sync.py --client-id device-a --interactive
```

**Terminal 2:**
```bash  
source venv/bin/activate
python sync.py --client-id device-b --interactive
```

## 📝 Tutorial Commands

```
add <title>          - Add a todo
list                 - Show all todos
complete <id>        - Complete a todo  
sync                 - Sync with other devices
status               - Show device info
cloud <url> <key>    - Connect to SQLite Cloud
quit                 - Exit
```

## 🧪 Try These Experiments

### Experiment 1: Local-Only Mode
```bash
# Device A
[device-a]> add "Learn SQLite-Sync"
[device-a]> list
[device-a]> status
```

### Experiment 2: Multi-Device Sync (with SQLite Cloud)
```bash
# First, get a free account at sqlitecloud.io
# Then connect both devices:

[device-a]> cloud "sqlitecloud://your-project.sqlite.cloud/db.sqlite" "your-api-key"
[device-a]> add "Todo from Device A"
[device-a]> sync

[device-b]> cloud "sqlitecloud://your-project.sqlite.cloud/db.sqlite" "your-api-key"  
[device-b]> sync
[device-b]> list    # See the todo from Device A!
[device-b]> add "Todo from Device B"
[device-b]> sync

[device-a]> sync
[device-a]> list    # See both todos!
```

## ✨ What's Happening?

When you run the tutorial:

1. **SQLite Database**: Each device gets its own local SQLite database
2. **CRDT Magic**: SQLite-Sync tracks changes using conflict-free data structures  
3. **Automatic Sync**: Changes sync between devices without conflicts
4. **Offline-First**: Works offline, syncs when reconnected

## 🤔 Common Questions

**Q: Do I need the extension to try this?**  
A: No! The tutorial works in "local-only mode" to teach the concepts.

**Q: How do I enable real sync between devices?**  
A: Get a free account at [sqlitecloud.io](https://sqlitecloud.io), then use the `cloud` command.

**Q: What if both devices change the same todo?**  
A: SQLite-Sync uses CRDT algorithms to automatically merge changes - no conflicts!

**Q: Can I use this in my own app?**  
A: Yes! Check out the `SyncClient` class in `sync.py` for integration patterns.

## 🔗 Learn More

- [SQLite-Sync Documentation](https://github.com/sqliteai/sqlite-sync)
- [SQLite Cloud Platform](https://sqlitecloud.io)
- [CRDT Concepts](https://en.wikipedia.org/wiki/Conflict-free_replicated_data_type)

---

**Ready to explore sync?** Run `python sync.py --client-id my-device --interactive` and start learning! 🚀
