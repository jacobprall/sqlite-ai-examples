#!/usr/bin/env python3
"""
Unit tests for ChatService
"""

import unittest
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add services to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'services'))

from chat import ChatService
from db import DatabaseManager, DatabaseError
from ai import AIClient


class TestChatService(unittest.TestCase):
    """Test ChatService functionality with real database operations"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        
        # Create real database manager
        self.db_manager = DatabaseManager(self.db_path)
        
        # Create mock AI client
        self.ai_client = MagicMock(spec=AIClient)
        self.ai_client.current_model_path = '/fake/model.gguf'
        
        # Add missing methods to database manager
        self.db_manager.execute = self.db_manager.db.execute
        self.db_manager.commit = self.db_manager.db.commit
        self.db_manager.fetchall = lambda sql, params=None: self.db_manager.db.execute(sql, params).fetchall()
        self.db_manager.fetchone = lambda sql, params=None: self.db_manager.db.execute(sql, params).fetchone()
        
        self.chat_service = ChatService(self.db_manager, self.ai_client)
    
    def tearDown(self):
        """Clean up test files"""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)
    
    def test_setup_schema(self):
        """Test database schema setup"""
        self.chat_service.setup_schema()
        
        # Verify table was created
        cursor = self.db_manager.db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='chat_history'"
        )
        table = cursor.fetchone()
        self.assertIsNotNone(table)
        
        # Verify table structure
        cursor = self.db_manager.db.execute("PRAGMA table_info(chat_history)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        expected_columns = {
            'id': 'INTEGER',
            'role': 'TEXT',
            'message': 'TEXT',
            'model_used': 'TEXT',
            'created_at': 'TEXT',
            'session_id': 'TEXT'
        }
        
        for name, type_ in expected_columns.items():
            self.assertIn(name, columns)
            self.assertEqual(columns[name], type_)
    
    def test_chat_with_response(self):
        """Test chat functionality with AI response"""
        self.chat_service.setup_schema()
        
        # Mock AI completion
        self.ai_client.complete.return_value = "Hello! How can I help you?"
        
        response = self.chat_service.chat('test-session', 'Hello')
        
        self.assertEqual(response, "Hello! How can I help you?")
        
        # Verify messages were stored in database
        cursor = self.db_manager.db.execute(
            "SELECT role, message FROM chat_history WHERE session_id = ? ORDER BY id",
            ('test-session',)
        )
        messages = cursor.fetchall()
        
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]['role'], 'user')
        self.assertEqual(messages[0]['message'], 'Hello')
        self.assertEqual(messages[1]['role'], 'assistant')
        self.assertEqual(messages[1]['message'], 'Hello! How can I help you?')
    
    def test_get_history_empty(self):
        """Test getting history when no messages exist"""
        self.chat_service.setup_schema()
        
        history = self.chat_service.get_history('test-session')
        
        self.assertEqual(history, [])
    
    def test_get_history_with_messages(self):
        """Test getting chat history with existing messages"""
        self.chat_service.setup_schema()
        
        # Add test messages
        self.ai_client.complete.return_value = "Response 1"
        self.chat_service.chat('test-session', 'Message 1')
        
        self.ai_client.complete.return_value = "Response 2"
        self.chat_service.chat('test-session', 'Message 2')
        
        # Get history
        history = self.chat_service.get_history('test-session')
        
        # Should be in reverse chronological order (newest first)
        self.assertEqual(len(history), 4)  # 2 user + 2 assistant messages
        self.assertEqual(history[0]['message'], 'Response 2')  # Most recent
        self.assertEqual(history[1]['message'], 'Message 2')
        self.assertEqual(history[2]['message'], 'Response 1')
        self.assertEqual(history[3]['message'], 'Message 1')  # Oldest
    
    def test_get_history_with_limit(self):
        """Test getting history with limit"""
        self.chat_service.setup_schema()
        
        # Add multiple messages
        for i in range(5):
            self.ai_client.complete.return_value = f"Response {i}"
            self.chat_service.chat('test-session', f'Message {i}')
        
        # Get limited history
        history = self.chat_service.get_history('test-session', limit=3)
        
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0]['message'], 'Response 4')  # Most recent
    
    def test_clear_history(self):
        """Test clearing chat history"""
        self.chat_service.setup_schema()
        
        # Add messages
        self.ai_client.complete.return_value = "Response"
        self.chat_service.chat('test-session', 'Message')
        
        # Clear history
        count = self.chat_service.clear_history('test-session')
        
        self.assertEqual(count, 2)  # 1 user + 1 assistant message
        
        # Verify history is empty
        history = self.chat_service.get_history('test-session')
        self.assertEqual(history, [])
    
    def test_get_message_stats(self):
        """Test getting message statistics"""
        self.chat_service.setup_schema()
        
        # Add messages
        self.ai_client.complete.return_value = "Response"
        self.chat_service.chat('test-session', 'Message 1')
        self.chat_service.chat('test-session', 'Message 2')
        
        total, user = self.chat_service.get_message_stats('test-session')
        
        self.assertEqual(total, 4)  # 2 user + 2 assistant
        self.assertEqual(user, 2)   # 2 user messages
    
    def test_session_isolation(self):
        """Test that different sessions are isolated"""
        self.chat_service.setup_schema()
        
        # Add messages to different sessions
        self.ai_client.complete.return_value = "Response A"
        self.chat_service.chat('session-a', 'Message A')
        
        self.ai_client.complete.return_value = "Response B"
        self.chat_service.chat('session-b', 'Message B')
        
        # Verify session isolation
        history_a = self.chat_service.get_history('session-a')
        history_b = self.chat_service.get_history('session-b')
        
        self.assertEqual(len(history_a), 2)
        self.assertEqual(len(history_b), 2)
        
        # Verify content is different
        self.assertIn('Message A', [msg['message'] for msg in history_a])
        self.assertIn('Message B', [msg['message'] for msg in history_b])
        self.assertNotIn('Message B', [msg['message'] for msg in history_a])
        self.assertNotIn('Message A', [msg['message'] for msg in history_b])


if __name__ == '__main__':
    unittest.main()