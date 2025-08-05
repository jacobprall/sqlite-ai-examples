import sqlite3
import os
import sys
import click
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple


class DatabaseError(Exception):
    """Custom exception for database operations"""
    pass

class DatabaseManager:
    """Handles all SQLite database operations for chat history"""
    def __init__(self, database_path="./data/chatbot.db"):
        self.current_model_path = None
        try:
            os.makedirs(os.path.dirname(os.path.abspath(database_path)), exist_ok=True)
    
            db = sqlite3.connect(database_path)
            # Use Row factory to access columns by name instead of index (e.g., row['message'] vs row[1])
            db.row_factory = sqlite3.Row
            self.db = db
        except Exception as e:
            raise DatabaseError(f"Failed to connect to Database: {e}")

    def sql(self, sql, parameters=None):
        """Pass-through execute function to the underlying database."""
        if not self.db:
            raise DatabaseError("Database not connected")
        try:
            if parameters:
                result = self.db.execute(sql, parameters)
            else:
                result = self.db.execute(sql)
            self.db.commit()
            return result
        except Exception as e:
            raise DatabaseError(f"SQL execution failed: {str(e)}")
