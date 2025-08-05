#!/usr/bin/env python3
"""
Unit tests for AIClient service
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


class TestAIClient(unittest.TestCase):
    """Test AIClient functionality with real database and mocked AI calls"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.model_path = os.path.join(self.temp_dir, 'test_model.gguf')
        
        # Create a fake model file
        with open(self.model_path, 'w') as f:
            f.write('fake model content')
    
    def tearDown(self):
        """Clean up test files"""
        for file in [self.db_path, self.model_path]:
            if os.path.exists(file):
                os.remove(file)
        os.rmdir(self.temp_dir)
    
    def test_ai_client_initialization(self):
        """Test AIClient initialization"""
        client = AIClient(client_id='test-client', database_path=self.db_path)
        
        # Check basic attributes
        self.assertEqual(client.session_id, 'test-client')
        self.assertIsNone(client.current_model_path)
        self.assertIsNotNone(client.database_manager)
    
    def test_session_id_generation(self):
        """Test automatic session ID generation"""
        client = AIClient(database_path=self.db_path)
        
        # Should generate an 8-character session ID
        self.assertIsNotNone(client.session_id)
        self.assertEqual(len(client.session_id), 8)
    
    def test_load_model_nonexistent_file(self):
        """Test loading non-existent model file"""
        client = AIClient(database_path=self.db_path)
        
        result = client.load_model('/nonexistent/model.gguf')
        self.assertFalse(result)
        self.assertIsNone(client.current_model_path)
    
    def test_load_model_success(self):
        """Test successful model loading"""
        client = AIClient(database_path=self.db_path)
        
        # Mock the entire database connection
        with patch.object(client.database_manager, 'db') as mock_db:
            mock_execute = MagicMock()
            mock_db.execute = mock_execute
            mock_execute.return_value = MagicMock()
            
            result = client.load_model(self.model_path)
            
            self.assertTrue(result)
            self.assertEqual(client.current_model_path, self.model_path)
            mock_execute.assert_called_with("SELECT llm_model_load(?)", (self.model_path,))
    
    def test_load_model_failure(self):
        """Test model loading failure"""
        client = AIClient(database_path=self.db_path)
        
        # Mock the entire database connection
        with patch.object(client.database_manager, 'db') as mock_db:
            mock_execute = MagicMock()
            mock_db.execute = mock_execute
            mock_execute.side_effect = Exception("Model loading failed")
            
            result = client.load_model(self.model_path)
            
            self.assertFalse(result)
            self.assertIsNone(client.current_model_path)
    
    def test_complete_no_model(self):
        """Test completion without loaded model"""
        client = AIClient(database_path=self.db_path)
        
        response = client.complete("Hello")
        
        self.assertEqual(response, "No model loaded. Please load a model first.")
    
    def test_complete_with_model(self):
        """Test completion with loaded model"""
        client = AIClient(database_path=self.db_path)
        client.current_model_path = self.model_path
        
        # Mock successful completion
        with patch.object(client.database_manager, 'db') as mock_db:
            mock_execute = MagicMock()
            mock_db.execute = mock_execute
            mock_result = MagicMock()
            mock_result.fetchone.return_value = ['Generated response']
            mock_execute.return_value = mock_result
            
            response = client.complete("Hello")
            
            self.assertEqual(response, "Generated response")
            mock_execute.assert_called_with("SELECT llm_text_generate(?)", ("Hello",))
    
    def test_complete_empty_response(self):
        """Test completion with empty response"""
        client = AIClient(database_path=self.db_path)
        client.current_model_path = self.model_path
        
        # Mock empty response
        with patch.object(client.database_manager, 'db') as mock_db:
            mock_execute = MagicMock()
            mock_db.execute = mock_execute
            mock_result = MagicMock()
            mock_result.fetchone.return_value = None
            mock_execute.return_value = mock_result
            
            response = client.complete("Hello")
            
            self.assertEqual(response, "Sorry, I couldn't generate a response.")
    
    def test_complete_exception(self):
        """Test completion with exception"""
        client = AIClient(database_path=self.db_path)
        client.current_model_path = self.model_path
        
        # Mock exception
        with patch.object(client.database_manager, 'db') as mock_db:
            mock_execute = MagicMock()
            mock_db.execute = mock_execute
            mock_execute.side_effect = Exception("AI generation failed")
            
            response = client.complete("Hello")
            
            self.assertEqual(response, "Error generating response: AI generation failed")


if __name__ == '__main__':
    unittest.main()