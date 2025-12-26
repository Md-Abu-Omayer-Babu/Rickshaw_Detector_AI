"""
Database configuration and connection management.
Handles SQLite database initialization and connection pooling.
"""
import sqlite3
from contextlib import contextmanager
from typing import Generator
from app.core.config import settings


def init_database():
    """
    Initialize the SQLite database and create tables if they don't exist.
    """
    conn = sqlite3.connect(settings.database_path)
    cursor = conn.cursor()
    
    # Create detections table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_type TEXT NOT NULL,
            file_name TEXT NOT NULL,
            rickshaw_count INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    
    print(f"✓ Database initialized at {settings.database_path}")


@contextmanager
def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager for database connections.
    Ensures proper connection cleanup.
    
    Yields:
        sqlite3.Connection: Database connection
        
    Example:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM detections")
            results = cursor.fetchall()
    """
    conn = sqlite3.connect(settings.database_path)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def insert_detection(file_type: str, file_name: str, rickshaw_count: int) -> int:
    """
    Insert a new detection record into the database.
    
    Args:
        file_type: Type of file ('image' or 'video')
        file_name: Name of the processed file
        rickshaw_count: Number of rickshaws detected
        
    Returns:
        int: ID of the inserted record
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO detections (file_type, file_name, rickshaw_count) VALUES (?, ?, ?)",
            (file_type, file_name, rickshaw_count)
        )
        return cursor.lastrowid


def get_all_detections() -> list[dict]:
    """
    Retrieve all detection records from the database.
    
    Returns:
        list[dict]: List of detection records
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, file_type, file_name, rickshaw_count, created_at
            FROM detections
            ORDER BY created_at DESC
        """)
        rows = cursor.fetchall()
        
        # Convert Row objects to dictionaries
        return [dict(row) for row in rows]
