#!/bin/bash
# Demo Start Script - Clean slate for AI demonstrations

echo "🎬 Starting Fresh SQLite-AI Demo"
echo "================================="

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
if [[ -f "sqlite-ai.so" || -f "sqlite-ai.dylib" || -f "sqlite-ai.dll" ]]; then
    extension_status="🤖 SQLite-AI: Ready for AI magic!"
else
    extension_status="📱 SQLite-AI: Demo mode (run ./setup.sh to get extension)"
fi

# Check for models
model_count=$(find models/ -name "*.gguf" 2>/dev/null | wc -l | tr -d ' ')
model_status=""
if [[ "$model_count" -gt 0 ]]; then
    model_status="🧠 AI Models: $model_count model(s) available"
    echo "   Available models:"
    find models/ -name "*.gguf" -exec basename {} \; | sed 's/^/     • /'
else
    model_status="🧠 AI Models: No models (add to ./models/ directory)"
fi

echo ""
echo "✅ Demo environment ready!"
echo "$extension_status"
echo "$model_status"
echo ""
echo "🎯 Demo Commands:"
echo ""
echo "Basic Demo:"
echo "   python ai.py --client-id my-app --interactive"
echo ""
if [[ "$model_count" -gt 0 ]]; then
    # Show example with the smallest/fastest model first
    if [[ -f "models/qwen2.5-0.5b-instruct-q4_k_m.gguf" ]]; then
        echo "With AI Model (Ultra-fast):"
        echo "   python ai.py --client-id chatbot --model-path ./models/qwen2.5-0.5b-instruct-q4_k_m.gguf --interactive"
    elif [[ -f "models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf" ]]; then
        echo "With AI Model (Fast):"
        echo "   python ai.py --client-id chatbot --model-path ./models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf --interactive"
    elif [[ -f "models/Phi-3.5-mini-instruct-Q4_K_M.gguf" ]]; then
        echo "With AI Model (High-quality):"
        echo "   python ai.py --client-id chatbot --model-path ./models/Phi-3.5-mini-instruct-Q4_K_M.gguf --interactive"
    else
        first_model=$(find models/ -name "*.gguf" -exec basename {} \; | head -1)
        echo "With AI Model:"
        echo "   python ai.py --client-id chatbot --model-path ./models/$first_model --interactive"
    fi
    echo ""
fi
echo "🎭 Demo Flow Suggestions:"
echo "1. Start the interactive mode"
echo "2. Add some documents with 'doc' command"
echo "3. Try semantic search with 'search' command"
echo "4. Chat with AI using 'chat' command"
echo "5. Load different models with 'load' command"
echo "6. Show chat history and status"
echo ""
echo "🌟 Ready to demo intelligent databases!"