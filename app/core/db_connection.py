import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    """Create a new database connection"""
    return psycopg2.connect(DATABASE_URL)

def get_db():
    """Dependency for FastAPI to get database connection"""
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()

def execute_query(query: str, params: tuple = None):
    """Execute a query and return results"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.commit()
        return results
    finally:
        cursor.close()
        conn.close()

def execute_insert(query: str, params: tuple = None):
    """Execute an insert query and return last inserted id"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()
