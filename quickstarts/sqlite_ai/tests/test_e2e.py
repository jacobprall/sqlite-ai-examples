#!/usr/bin/env python3
"""
End-to-end tests for complete user scenarios
"""

import unittest
import tempfile
import os
import sys
import sqlite3
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add services to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'services'))

from ai import AIClient
from chat import ChatService
from db import DatabaseManager


class TestEndToEnd(unittest.TestCase):
    """Test complete user scenarios from start to finish"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'chatbot.db')
        self.model_path = os.path.join(self.temp_dir, 'model.gguf')
        
        # Create fake model file
        with open(self.model_path, 'w') as f:
            f.write('fake model content')
    
    def tearDown(self):
        """Clean up test files"""
        for file in [self.db_path, self.model_path]:
            if os.path.exists(file):
                os.remove(file)
        os.rmdir(self.temp_dir)
    
    def test_complete_chatbot_scenario(self):
        """Test complete chatbot usage scenario"""
        
        # 1. Initialize chatbot
        db_manager = DatabaseManager(self.db_path)
        ai_client = AIClient(client_id='test-user', database_path=self.db_path)
        
        # Add missing methods to database manager
        db_manager.execute = db_manager.db.execute
        db_manager.commit = db_manager.db.commit
        db_manager.fetchall = lambda sql, params=None: db_manager.db.execute(sql, params).fetchall()
        db_manager.fetchone = lambda sql, params=None: db_manager.db.execute(sql, params).fetchone()
        
        chat_service = ChatService(db_manager, ai_client)
        
        # Mock SQLite-AI functions
        def mock_execute(sql, params=None):
            if 'llm_model_load' in sql:
                return MagicMock()
            elif 'llm_text_generate' in sql:
                # Simulate different responses based on input
                message = params[0] if params else ""
                responses = {
                    "Hello": "Hi there! How can I help you today?",
                    "What is Python?": "Python is a high-level programming language known for its simplicity and readability.",
                    "Tell me a joke": "Why do programmers prefer dark mode? Because light attracts bugs!",
                }
                response = responses.get(message, "I'm not sure how to respond to that.")
                
                result = MagicMock()
                result.fetchone.return_value = [response]
                return result
            else:
                # Use real database for other operations
                return self.original_db_execute(sql, params)
        
        # Store original execute method
        self.original_db_execute = ai_client.database_manager.db.execute
        
        # Mock AI client's database execute method for AI operations
        
        # Setup database
        chat_service.setup_schema()
        
        # Verify database file exists
        self.assertTrue(os.path.exists(self.db_path))
        
        # 2. Load AI model
        with patch.object(ai_client.database_manager, 'db') as mock_db:
            mock_db_execute = MagicMock()
            mock_db.execute = mock_db_execute
            mock_db_execute.side_effect = mock_execute
            
            success = ai_client.load_model(self.model_path)
            self.assertTrue(success)
            self.assertEqual(ai_client.current_model_path, self.model_path)
        
        # 3. Have multiple conversations
        with patch.object(ai_client.database_manager, 'db') as mock_db:
            mock_db_execute = MagicMock()
            mock_db.execute = mock_db_execute
            mock_db_execute.side_effect = mock_execute
            
            # First conversation
            response1 = chat_service.chat('test-user', 'Hello')
            self.assertEqual(response1, "Hi there! How can I help you today?")
            
            # Second conversation
            response2 = chat_service.chat('test-user', 'What is Python?')
            self.assertEqual(response2, "Python is a high-level programming language known for its simplicity and readability.")
            
            # Third conversation
            response3 = chat_service.chat('test-user', 'Tell me a joke')
            self.assertEqual(response3, "Why do programmers prefer dark mode? Because light attracts bugs!")
        
        # 4. Check conversation history
        history = chat_service.get_history('test-user')
        self.assertEqual(len(history), 6)  # 3 user + 3 assistant messages
        
        # Verify history order (newest first)
        expected_messages = [
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "Tell me a joke",
            "Python is a high-level programming language known for its simplicity and readability.",
            "What is Python?",
            "Hi there! How can I help you today?",
            "Hello"
        ]
        
        actual_messages = [msg['message'] for msg in history]
        self.assertEqual(actual_messages, expected_messages)
        
        # 5. Check message statistics
        total, user = chat_service.get_message_stats('test-user')
        self.assertEqual(total, 6)
        self.assertEqual(user, 3)
        
        # 6. Clear history
        cleared_count = chat_service.clear_history('test-user')
        self.assertEqual(cleared_count, 6)
        
        # Verify history is empty
        history_after_clear = chat_service.get_history('test-user')
        self.assertEqual(len(history_after_clear), 0)
    
    def test_persistence_across_sessions(self):
        """Test that data persists across different service instances"""
        
        # Create first session
        db_manager1 = DatabaseManager(self.db_path)
        db_manager1.execute = db_manager1.db.execute
        db_manager1.commit = db_manager1.db.commit
        db_manager1.fetchall = lambda sql, params=None: db_manager1.db.execute(sql, params).fetchall()
        db_manager1.fetchone = lambda sql, params=None: db_manager1.db.execute(sql, params).fetchone()
        
        ai_client1 = AIClient(client_id='persistent-user', database_path=self.db_path)
        chat_service1 = ChatService(db_manager1, ai_client1)
        chat_service1.setup_schema()
        
        # Add some messages in first session
        with patch.object(ai_client1, 'complete', return_value='First session response'):
            chat_service1.chat('persistent-user', 'First message')
        
        # Close first session
        db_manager1.db.close()
        
        # Create second session (new instances)
        db_manager2 = DatabaseManager(self.db_path)
        db_manager2.execute = db_manager2.db.execute
        db_manager2.commit = db_manager2.db.commit
        db_manager2.fetchall = lambda sql, params=None: db_manager2.db.execute(sql, params).fetchall()
        db_manager2.fetchone = lambda sql, params=None: db_manager2.db.execute(sql, params).fetchone()
        
        ai_client2 = AIClient(client_id='persistent-user', database_path=self.db_path)
        chat_service2 = ChatService(db_manager2, ai_client2)
        
        # Add more messages in second session
        with patch.object(ai_client2, 'complete', return_value='Second session response'):
            chat_service2.chat('persistent-user', 'Second message')
        
        # Verify all messages are preserved
        history = chat_service2.get_history('persistent-user')
        self.assertEqual(len(history), 4)  # 2 user + 2 assistant messages
        
        messages = [msg['message'] for msg in history]
        self.assertIn('First message', messages)
        self.assertIn('First session response', messages)
        self.assertIn('Second message', messages)
        self.assertIn('Second session response', messages)
    
    def test_error_recovery(self):
        """Test system behavior when errors occur"""
        
        db_manager = DatabaseManager(self.db_path)
        db_manager.execute = db_manager.db.execute
        db_manager.commit = db_manager.db.commit
        db_manager.fetchall = lambda sql, params=None: db_manager.db.execute(sql, params).fetchall()
        db_manager.fetchone = lambda sql, params=None: db_manager.db.execute(sql, params).fetchone()
        
        ai_client = AIClient(client_id='error-test', database_path=self.db_path)
        chat_service = ChatService(db_manager, ai_client)
        chat_service.setup_schema()
        
        # Test AI completion failure
        with patch.object(ai_client, 'complete', side_effect=Exception('AI failed')):
            response = chat_service.chat('error-test', 'This will fail')
            # Should still return something (the exception handling in complete method)
            self.assertIn('Error generating response', response)
        
        # Test database failure recovery
        with patch.object(db_manager, 'execute', side_effect=Exception('DB failed')):
            with patch.object(ai_client, 'complete', return_value='AI response'):
                # Chat should still work even if database storage fails
                response = chat_service.chat('error-test', 'Test message')
                self.assertEqual(response, 'AI response')


if __name__ == '__main__':
    unittest.main() 