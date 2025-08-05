from typing import List, Dict, Any, Tuple
from db import DatabaseManager, DatabaseError
from ai import AIClient

class ChatService:
    """Handles chat functionality, model management, and history"""
    
    def __init__(self, db: DatabaseManager, ai: AIClient):
        """Initialize chat service with database manager."""
        self.ai = ai
        self.db = db

    def setup_schema(self) -> None:
        """Create chat history table if it doesn't exist."""
        try:
            self.db.db.execute('''
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    message TEXT NOT NULL,
                    model_used TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    session_id TEXT NOT NULL DEFAULT ''
                )
            ''')
            self.db.db.commit()
        except Exception as e:
            raise DatabaseError(f"Failed to setup database schema: {e}")
    
    def chat(self, session_id: str, message: str) -> str:
        """Process a chat message using loaded AI model."""
        try:
            response = self.ai.complete(message)
        except Exception as e:
            response = f"Error generating response: {str(e)}"
        
        # Store in database if available
        if self.db:
            try:
                model_used = self.ai.current_model_path
                # Store user message  
                self.db.db.execute('''
                    INSERT INTO chat_history (role, message, model_used, session_id)
                    VALUES (?, ?, ?, ?)
                ''', ('user', message, model_used, session_id))

                # Store assistant response
                self.db.db.execute('''
                    INSERT INTO chat_history (role, message, model_used, session_id)
                    VALUES (?, ?, ?, ?)
                ''', ('assistant', response, model_used, session_id))

                self.db.db.commit()
            except Exception:
                # Chat can continue even if storage fails
                pass
        
        return response
    
    def get_history(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get chat history for a session."""
        if not self.db:
            return []
        
        try:
            messages = self.db.db.execute('''
                SELECT role, message, created_at FROM chat_history 
                WHERE session_id = ?
                ORDER BY id DESC
                LIMIT ?
            ''', (session_id, limit)).fetchall()
            
            return [dict(msg) for msg in messages]
        except Exception:
            return []
    
    def clear_history(self, session_id: str) -> int:
        """Clear chat history for a session."""
        if not self.db:
            return 0
        
        try:
            cursor = self.db.db.execute(
                "DELETE FROM chat_history WHERE session_id = ?", 
                (session_id,)
            )
            deleted_count = cursor.rowcount
            self.db.db.commit()
            return deleted_count
        except Exception:
            return 0
    
    def get_message_stats(self, session_id: str) -> Tuple[int, int]:
        """Get message statistics for a session."""
        if not self.db:
            return 0, 0
        
        try:
            total_result = self.db.db.execute(
                "SELECT COUNT(*) FROM chat_history WHERE session_id = ?", 
                (session_id,)
            ).fetchone()
            total_messages = total_result[0] if total_result else 0
            
            user_result = self.db.db.execute(
                "SELECT COUNT(*) FROM chat_history WHERE session_id = ? AND role = 'user'", 
                (session_id,)
            ).fetchone()
            user_messages = user_result[0] if user_result else 0
            
            return total_messages, user_messages
        except Exception:
            return 0, 0

