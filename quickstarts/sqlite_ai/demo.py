#!/usr/bin/env python3
"""
SQLite-AI Tutorial Demo

Automated demonstration of AI database concepts.

Usage:
    python demo.py
    python demo.py --with-model "./models/tinyllama.gguf"
"""

import argparse
import time
from ai import AIClient


def tutorial_demo(use_model=False, model_path=None):
    """Simple demo showing SQLite-AI basics."""
    print("🎯 SQLite-AI Tutorial Demo")
    print("=" * 40)
    
    # Create AI client
    client = AIClient("demo-app")
    
    try:
        # Load model if provided
        if use_model and model_path:
            print(f"\n🧠 Loading AI model...")
            if client.load_model(model_path):
                print("✅ Model loaded successfully")
            else:
                print("❌ Model loading failed - continuing in demo mode")
                use_model = False
        
        # Add sample documents
        print("\n📚 Adding sample documents...")
        client.add_document("Python Guide", "Python is a high-level programming language known for its simplicity and readability. It's widely used in web development, data science, and AI.")
        client.add_document("SQLite Tutorial", "SQLite is a lightweight, serverless database that stores data in a single file. It's perfect for applications that need a simple, reliable database.")
        client.add_document("AI Overview", "Artificial Intelligence involves creating systems that can perform tasks typically requiring human intelligence, such as learning, reasoning, and perception.")
        
        client.list_documents()
        
        # Demonstrate search
        print("\n🔍 Searching documents...")
        client.search_documents("database")
        
        print("\n🔍 Searching for AI content...")
        client.search_documents("artificial intelligence")
        
        # Demonstrate chat if model is available
        if use_model:
            print("\n💬 Chatting with AI...")
            client.chat("What is Python programming language?")
            client.chat("Explain SQLite in simple terms")
            
            print("\n📜 Chat history:")
            client.show_chat_history()
        else:
            print("\n💬 Chat demo (demo mode)...")
            client.chat("Hello, can you help me with programming?")
            client.chat("What are databases used for?")
        
        # Show final status
        print("\n📊 Final status:")
        client.show_status()
        
        print("\n✨ Demo complete!")
        if use_model:
            print("🎉 AI-powered search and chat demonstrated!")
        else:
            print("💡 Try with --with-model to see real AI in action!")
    
    finally:
        client.close()


def main():
    """Run the tutorial demo."""
    parser = argparse.ArgumentParser(
        description="SQLite-AI Tutorial Demo",
        epilog="""
Examples:
  python demo.py                                                              # Auto-detect mode
  python demo.py --with-model "./models/qwen2.5-0.5b-instruct-q4_k_m.gguf"  # With specific model
        """
    )
    
    parser.add_argument('--with-model', metavar='MODEL_PATH',
                        help='Enable AI with specified model path')
    
    args = parser.parse_args()
    
    try:
        if args.with_model:
            tutorial_demo(True, args.with_model)
        else:
            # Check if we have any downloaded models to use
            import os
            model_files = [
                "./models/qwen2.5-0.5b-instruct-q4_k_m.gguf",           # Fastest
                "./models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",       # Good balance  
                "./models/Phi-3.5-mini-instruct-Q4_K_M.gguf"           # Highest quality
            ]
            
            available_model = None
            for model_path in model_files:
                if os.path.exists(model_path):
                    available_model = model_path
                    break
            
            if available_model:
                print(f"🧠 Found model: {os.path.basename(available_model)}")
                tutorial_demo(True, available_model)
            else:
                tutorial_demo(False)
    
    except KeyboardInterrupt:
        print("\n\n👋 Demo stopped!")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")


if __name__ == '__main__':
    main()