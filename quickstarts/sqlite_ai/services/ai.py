#!/usr/bin/env python3
"""
SQLite-AI Tutorial - Simple AI Chatbot

Learn SQLite-AI through a focused chatbot example that demonstrates:
• AI model integration with SQLite
• Text generation and conversation
• Chat history management
• Model loading and switching

Usage:
    python ai.py --client-id my-chatbot --interactive
    python ai.py --model-path ./models/llama.gguf --interactive  
"""

import os
from db import DatabaseManager
from uuid import uuid4

class AIClient:
    """
    A simple local chatbot powered by SQLite.
    
    Shows how to:
    • Connect to SQLite with AI capabilities
    • Load and manage AI models
    • Generate chat responses
    • Store conversation history
    """
    
    def __init__(self, database_path="./data/chatbot.db", client_id=None):
        """Create a new AI chatbot client."""
        self.session_id = str(uuid4())[:8] if client_id is None else client_id
        
        # Initialize components
        self.database_manager = DatabaseManager(database_path)
        self.current_model_path = None

    def load_model(self, model_path: str) -> bool:
        """Load an AI model using SQLite-AI extension."""
        if not os.path.exists(model_path):
            return False

        try:
            # Use SQLite-AI extension to load the model
            self.database_manager.db.execute("SELECT llm_model_load(?)", (model_path,))
            self.current_model_path = model_path
            return True
        except Exception as e:
            return False

    def complete(self, message: str) -> str:
        """Generate a chat response using the loaded model."""
        if not self.current_model_path:
            return "No model loaded. Please load a model first."
            
        try:
            # Use SQLite-AI extension to generate text completion
            result = self.database_manager.db.execute("SELECT llm_text_generate(?)", (message,)).fetchone()
            return result[0] if result and result[0] else "Sorry, I couldn't generate a response."
        except Exception as e:
            return f"Error generating response: {str(e)}"