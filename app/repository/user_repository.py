import uuid
from psycopg2.extras import RealDictCursor
from app.core.db_connection import get_db_connection

class UserRepository:
    @staticmethod
    def create(email: str, username: str, hashed_password: str):
        """Create a new user in database"""
        user_id = str(uuid.uuid4())
        query = """
            INSERT INTO users (id, email, username, hashed_password, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, TRUE, NOW(), NOW())
            RETURNING id, email, username, is_active, created_at, updated_at
        """
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(query, (user_id, email, username, hashed_password))
            result = cursor.fetchone()
            conn.commit()
            return dict(result) if result else None
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_by_id(user_id: str):
        """Get user by id from database"""
        query = "SELECT id, email, username, is_active, created_at, updated_at FROM users WHERE id = %s"
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            return dict(result) if result else None
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_by_email(email: str):
        """Get user by email from database"""
        query = "SELECT id, email, username, hashed_password, is_active, created_at, updated_at FROM users WHERE email = %s"
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(query, (email,))
            result = cursor.fetchone()
            return dict(result) if result else None
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_by_username(username: str):
        """Get user by username from database"""
        query = "SELECT id, email, username, is_active, created_at, updated_at FROM users WHERE username = %s"
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            return dict(result) if result else None
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_all(skip: int = 0, limit: int = 10):
        """Get all users from database with pagination"""
        query = "SELECT id, email, username, is_active, created_at, updated_at FROM users ORDER BY created_at DESC OFFSET %s LIMIT %s"
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(query, (skip, limit))
            results = cursor.fetchall()
            return [dict(row) for row in results]
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def update(user_id: str, **kwargs):
        """Update user in database"""
        allowed_fields = {'email', 'username', 'is_active'}
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return UserRepository.get_by_id(user_id)
        
        set_clause = ", ".join([f"{k} = %s" for k in updates.keys()])
        query = f"UPDATE users SET {set_clause}, updated_at = NOW() WHERE id = %s RETURNING id, email, username, is_active, created_at, updated_at"
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(query, (*updates.values(), user_id))
            result = cursor.fetchone()
            conn.commit()
            return dict(result) if result else None
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def delete(user_id: str):
        """Delete user from database"""
        query = "DELETE FROM users WHERE id = %s RETURNING id"
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            conn.commit()
            return result is not None
        finally:
            cursor.close()
            conn.close()
