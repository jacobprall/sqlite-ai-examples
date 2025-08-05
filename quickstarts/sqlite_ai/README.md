# SQLite-AI Tutorial

Learn SQLite-AI through hands-on examples! This tutorial shows you how SQLite-AI brings artificial intelligence directly into your database with text generation, embeddings, and semantic search.

## 🎯 What You'll Learn

- **AI Model Integration** - Load and use AI models directly in SQLite
- **Text Generation** - Chat and completion capabilities in your database
- **Semantic Search** - Find documents by meaning, not just keywords
- **Embeddings** - Generate and use vector representations of text
- **Model Management** - Switch between different AI models

## 🚀 Quick Start

### One-Command Setup

Run our interactive setup script that handles everything:

```bash
./setup.sh
```

This will:
- 🔍 Auto-detect your platform (macOS, Linux, Windows)
- 📥 Download the SQLite-AI extension from GitHub
- 🧠 Optionally download sample AI models
- 🐍 Create a Python virtual environment
- 📦 Install all dependencies
- 📁 Set up the project structure

### Manual Setup (Alternative)

If you prefer manual setup:

1. **Get the extension**: Download from [SQLite-AI Releases](https://github.com/sqliteai/sqlite-ai/releases)
2. **Install dependencies**: `pip install click`
3. **Add AI models**: Place `.gguf` model files in `./models/` directory

**Note:** The tutorial works without the extension in "demo mode" for learning!

### Start the Tutorial

**Basic Tutorial:**
```bash
source venv/bin/activate
python ai.py --client-id my-app --interactive
```

**With AI Model:**
```bash
source venv/bin/activate
python ai.py --client-id chatbot --model-path ./models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf --interactive
```

## 📝 Tutorial Commands

```
chat <message>         - Chat with AI
doc <title> <content>  - Add a document
search <query>         - Search documents semantically
list                   - Show all documents
history                - Show chat history
load <model_path>      - Load AI model
status                 - Show app status
quit                   - Exit
```

## 🧪 Try These Experiments

### Experiment 1: Document Management
```bash
[my-app] doc "Python Tutorial" "Python is a programming language"
[my-app] doc "AI Guide" "Artificial intelligence and machine learning"
[my-app] list
[my-app] search "programming"
```

### Experiment 2: AI Chat (with model)
```bash
[chatbot] load ./models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
[chatbot] chat "What is Python?"
[chatbot] chat "Explain machine learning"
[chatbot] history
```

### Experiment 3: Semantic Search
```bash
[my-app] doc "Database Guide" "SQLite is a lightweight database engine"
[my-app] doc "Web Development" "HTML, CSS, and JavaScript for websites"
[my-app] search "data storage"  # Should find the database guide
[my-app] search "frontend"      # Should find web development
```

## ✨ What's Happening?

When you run the tutorial:

1. **SQLite Database**: Your app gets a local SQLite database with AI capabilities
2. **Model Loading**: AI models run locally for privacy and performance
3. **Embeddings**: Text is converted to vectors for semantic understanding
4. **Chat Integration**: Natural language interfaces built into your database

## 🤔 Common Questions

**Q: Do I need the extension to try this?**  
A: No! The tutorial works in "demo mode" to teach the concepts.

**Q: What AI models can I use?**  
A: Any GGUF format models (Llama, Phi, Mistral, etc.). Place them in `./models/`

**Q: How does semantic search work?**  
A: SQLite-AI generates embeddings (vectors) that capture meaning, enabling similarity search.

**Q: Can I use this in my own app?**  
A: Yes! Check out the `AIClient` class in `ai.py` for integration patterns.

## 🧠 AI Model Sources

Models available in setup script:
- **TinyLlama 1.1B Chat** (~637MB) - Fast, good for testing
- **Phi-3.5 Mini Instruct** (~2.2GB) - High quality, compact
- **Qwen2.5 0.5B Instruct** (~394MB) - Ultra-fast, tiny

More models available from:
- [Hugging Face](https://huggingface.co/models?library=gguf)
- [LM Studio Models](https://lmstudio.ai/models)
- [Ollama Models](https://ollama.ai/library)

## 🔗 Learn More

- [SQLite-AI Documentation](https://github.com/sqliteai/sqlite-ai)
- [GGUF Model Format](https://github.com/ggerganov/ggml/blob/master/docs/gguf.md)
- [Vector Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)

---

**Ready to build intelligent databases?** Run `python ai.py --client-id my-app --interactive` and start exploring! 🚀