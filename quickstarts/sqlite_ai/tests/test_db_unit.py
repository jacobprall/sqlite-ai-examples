#!/usr/bin/env python3
"""
Unit tests for DatabaseManager service
"""

import unittest
import sqlite3
import tempfile
import os
import sys
import shutil
from pathlib import Path

# Add services to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'services'))

from db import DatabaseManager, DatabaseError


class TestDatabaseManager(unittest.TestCase):
    """Test DatabaseManager functionality with real SQLite databases"""
    
    def setUp(self):
        """Set up test database for each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        
    def tearDown(self):
        """Clean up test database"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_database_creation(self):
        """Test that database is created successfully"""
        db_manager = DatabaseManager(self.db_path)
        
        # Verify database file exists
        self.assertTrue(os.path.exists(self.db_path))
        
        # Verify connection is active
        self.assertIsNotNone(db_manager.db)
        
        # Verify row factory is set
        self.assertEqual(db_manager.db.row_factory, sqlite3.Row)
    
    def test_database_directory_creation(self):
        """Test that parent directories are created"""
        nested_path = os.path.join(self.temp_dir, 'nested', 'deep', 'test.db')
        
        db_manager = DatabaseManager(nested_path)
        
        # Verify directory structure was created
        self.assertTrue(os.path.exists(os.path.dirname(nested_path)))
        self.assertTrue(os.path.exists(nested_path))
    
    def test_in_memory_database(self):
        """Test in-memory database creation"""
        db_manager = DatabaseManager(':memory:')
        
        # Should work without creating files
        self.assertIsNotNone(db_manager.db)
        
        # Can execute queries
        cursor = db_manager.db.execute("SELECT 1 as test")
        result = cursor.fetchone()
        self.assertEqual(result['test'], 1)
    
    def test_database_operations(self):
        """Test basic database operations"""
        db_manager = DatabaseManager(self.db_path)
        
        # Create a test table
        db_manager.db.execute('''
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT,
                value INTEGER
            )
        ''')
        
        # Insert data
        db_manager.db.execute(
            "INSERT INTO test_table (name, value) VALUES (?, ?)",
            ('test_item', 42)
        )
        db_manager.db.commit()
        
        # Query data
        cursor = db_manager.db.execute("SELECT * FROM test_table")
        row = cursor.fetchone()
        
        # Verify row factory works
        self.assertEqual(row['name'], 'test_item')
        self.assertEqual(row['value'], 42)
    
    def test_sql_method(self):
        """Test the sql helper method"""
        db_manager = DatabaseManager(self.db_path)
        
        # Create test table using sql method
        db_manager.sql('''
            CREATE TABLE test_sql (
                id INTEGER PRIMARY KEY,
                data TEXT
            )
        ''')
        
        # Insert using sql method with parameters
        db_manager.sql(
            "INSERT INTO test_sql (data) VALUES (?)",
            ('test data',)
        )
        db_manager.db.commit()
        
        # Query using sql method
        cursor = db_manager.sql("SELECT * FROM test_sql")
        row = cursor.fetchone()
        
        self.assertEqual(row['data'], 'test data')
    
    def test_current_model_path_initialization(self):
        """Test that current_model_path is initialized correctly"""
        db_manager = DatabaseManager(self.db_path)
        self.assertIsNone(db_manager.current_model_path)


if __name__ == '__main__':
    unittest.main()