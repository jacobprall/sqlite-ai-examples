#!/usr/bin/env python3
"""
Integration tests for services working together
"""

import unittest
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add services to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'services'))

from ai import AIClient
from chat import ChatService
from db import DatabaseManager


class TestServicesIntegration(unittest.TestCase):
    """Test services working together with minimal mocking"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.model_path = os.path.join(self.temp_dir, 'test_model.gguf')
        
        # Create fake model file
        with open(self.model_path, 'w') as f:
            f.write('fake model content')
    
    def tearDown(self):
        """Clean up test files"""
        for file in [self.db_path, self.model_path]:
            if os.path.exists(file):
                os.remove(file)
        os.rmdir(self.temp_dir)
    
    def test_full_chat_workflow(self):
        """Test complete workflow: create services, load model, chat"""
        # Create services
        db_manager = DatabaseManager(self.db_path)
        ai_client = AIClient(client_id='test-integration', database_path=self.db_path)
        
        # Add missing methods to database manager for chat service
        db_manager.execute = db_manager.db.execute
        db_manager.commit = db_manager.db.commit
        db_manager.fetchall = lambda sql, params=None: db_manager.db.execute(sql, params).fetchall()
        db_manager.fetchone = lambda sql, params=None: db_manager.db.execute(sql, params).fetchone()
        
        chat_service = ChatService(db_manager, ai_client)
        
        # Setup mock responses for AI operations
        def mock_execute_side_effect(sql, params=None):
            if 'llm_model_load' in sql:
                return MagicMock()  # Model loading
            elif 'llm_text_generate' in sql:
                result = MagicMock()
                result.fetchone.return_value = ['AI generated response']
                return result
            else:
                # For regular SQL operations, use real database
                return self.original_db_execute(sql, params)
        
        # Store original execute method
        self.original_db_execute = ai_client.database_manager.db.execute
        
        # Mock AI client's database connection
        with patch.object(ai_client.database_manager, 'db') as mock_db:
            mock_execute = MagicMock()
            mock_db.execute = mock_execute
            mock_execute.side_effect = mock_execute_side_effect
            
            # Test workflow
            chat_service.setup_schema()
            
            # Load model
            success = ai_client.load_model(self.model_path)
            self.assertTrue(success)
            
            # Chat
            response = chat_service.chat('test-session', 'Hello AI')
            self.assertEqual(response, 'AI generated response')
            
            # Verify history
            history = chat_service.get_history('test-session')
            self.assertEqual(len(history), 2)
            
            # Verify stats
            total, user = chat_service.get_message_stats('test-session')
            self.assertEqual(total, 2)
            self.assertEqual(user, 1)
    
    def test_multiple_sessions(self):
        """Test multiple chat sessions working independently"""
        # Create services
        db_manager = DatabaseManager(self.db_path)
        
        # Add missing methods
        db_manager.execute = db_manager.db.execute
        db_manager.commit = db_manager.db.commit
        db_manager.fetchall = lambda sql, params=None: db_manager.db.execute(sql, params).fetchall()
        db_manager.fetchone = lambda sql, params=None: db_manager.db.execute(sql, params).fetchone()
        
        ai_client1 = AIClient(client_id='user1', database_path=':memory:')
        ai_client2 = AIClient(client_id='user2', database_path=':memory:')
        
        chat_service = ChatService(db_manager, ai_client1)
        chat_service.setup_schema()
        
        # Mock AI responses
        with patch.object(ai_client1, 'complete', return_value='Response to user1'):
            response1 = chat_service.chat('user1', 'Hello from user1')
        
        with patch.object(ai_client2, 'complete', return_value='Response to user2'):
            chat_service.ai = ai_client2  # Switch AI client
            response2 = chat_service.chat('user2', 'Hello from user2')
        
        self.assertEqual(response1, 'Response to user1')
        self.assertEqual(response2, 'Response to user2')
        
        # Verify session isolation
        history1 = chat_service.get_history('user1')
        history2 = chat_service.get_history('user2')
        
        self.assertEqual(len(history1), 2)
        self.assertEqual(len(history2), 2)
        
        # Verify correct messages in each session
        messages1 = [msg['message'] for msg in history1]
        messages2 = [msg['message'] for msg in history2]
        
        self.assertIn('Hello from user1', messages1)
        self.assertIn('Response to user1', messages1)
        self.assertIn('Hello from user2', messages2)
        self.assertIn('Response to user2', messages2)


if __name__ == '__main__':
    unittest.main() 