#!/bin/bash
# Demo Start Script - Clean slate for demonstrations

echo "🎬 Starting Fresh SQLite-Sync Demo"
echo "==================================="

# Check if virtual environment exists
if [[ ! -d "venv" ]]; then
    echo "❌ Virtual environment not found. Please run ./setup.sh first"
    exit 1
fi

# Clean up previous demo data
echo "🧹 Cleaning previous demo data..."
rm -rf data/
mkdir -p data/

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source venv/bin/activate

# Check for extension
extension_status=""
if [[ -f "cloudsync.so" || -f "cloudsync.dylib" || -f "cloudsync.dll" ]]; then
    extension_status="🔄 SQLite-Sync: Ready for real sync!"
else
    extension_status="📱 SQLite-Sync: Local-only mode (run ./setup.sh to get extension)"
fi

echo ""
echo "✅ Demo environment ready!"
echo "$extension_status"
echo ""
echo "🎯 Demo Commands:"
echo ""
echo "Terminal 1 (Device A):"
echo "   python sync.py --client-id device-a --interactive"
echo ""
echo "Terminal 2 (Device B):"
echo "   python sync.py --client-id device-b --interactive"
echo ""
echo "🎭 Demo Flow Suggestions:"
echo "1. Start both terminals"
echo "2. Add todos on Device A, show list"
echo "3. Set up cloud connection (if extension available)"
echo "4. Sync from Device A"
echo "5. Sync to Device B, show list"
echo "6. Add todos on Device B"
echo "7. Sync back to Device A"
echo "8. Show both devices have identical data!"
echo ""
echo "🌟 Ready to demo!"