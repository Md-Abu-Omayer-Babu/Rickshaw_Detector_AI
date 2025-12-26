"""
Database configuration and connection management.
Handles SQLite database initialization and connection pooling.
"""
import sqlite3
from contextlib import contextmanager
from typing import Generator, Optional
from datetime import datetime
from app.core.config import settings, logger


def init_database():
    """
    Initialize the SQLite database and create tables if they don't exist.
    """
    # Ensure database directory exists
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(settings.database_path)
    cursor = conn.cursor()
    
    # Create detections table (legacy compatibility)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_type TEXT NOT NULL,
            file_name TEXT NOT NULL,
            rickshaw_count INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create rickshaw_logs table for entry/exit tracking
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rickshaw_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            camera_id TEXT DEFAULT 'default',
            rickshaw_id TEXT,
            confidence REAL NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            frame_number INTEGER,
            bounding_box TEXT,
            crossing_line TEXT,
            notes TEXT
        )
    """)
    
    # Create analytics_summary table for cached statistics
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analytics_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            camera_id TEXT DEFAULT 'default',
            total_entry INTEGER DEFAULT 0,
            total_exit INTEGER DEFAULT 0,
            net_count INTEGER DEFAULT 0,
            peak_hour INTEGER,
            peak_hour_count INTEGER,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(date, camera_id)
        )
    """)
    
    # Create camera_streams table for RTSP stream management
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS camera_streams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            camera_id TEXT UNIQUE NOT NULL,
            camera_name TEXT NOT NULL,
            rtsp_url TEXT NOT NULL,
            status TEXT DEFAULT 'inactive',
            last_active TIMESTAMP,
            total_frames_processed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes for better query performance
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_rickshaw_logs_timestamp 
        ON rickshaw_logs(timestamp)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_rickshaw_logs_event_type 
        ON rickshaw_logs(event_type)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_rickshaw_logs_camera 
        ON rickshaw_logs(camera_id)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_analytics_date 
        ON analytics_summary(date)
    """)
    
    conn.commit()
    conn.close()
    
    logger.info(f"Database initialized at {settings.database_path}")
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
        logger.error(f"Database error: {str(e)}")
        raise e
    finally:
        conn.close()


# ============================================================
# Legacy Functions (for backward compatibility)
# ============================================================

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
        record_id = cursor.lastrowid
        logger.info(f"Inserted detection record: {file_type} - {file_name} - {rickshaw_count} rickshaws")
        return record_id


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


# ============================================================
# Entry-Exit Logging Functions
# ============================================================

def log_rickshaw_event(
    event_type: str,
    confidence: float,
    camera_id: str = "default",
    rickshaw_id: Optional[str] = None,
    frame_number: Optional[int] = None,
    bounding_box: Optional[str] = None,
    crossing_line: Optional[str] = None,
    notes: Optional[str] = None
) -> int:
    """
    Log a rickshaw entry or exit event.
    
    Args:
        event_type: 'entry' or 'exit'
        confidence: Detection confidence score
        camera_id: Camera identifier
        rickshaw_id: Unique rickshaw tracking ID
        frame_number: Frame number in video
        bounding_box: Bounding box coordinates as JSON string
        crossing_line: Line that was crossed
        notes: Additional notes
        
    Returns:
        int: ID of the inserted log record
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO rickshaw_logs 
            (event_type, camera_id, rickshaw_id, confidence, frame_number, 
             bounding_box, crossing_line, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (event_type, camera_id, rickshaw_id, confidence, frame_number,
              bounding_box, crossing_line, notes))
        record_id = cursor.lastrowid
        logger.info(f"Logged {event_type} event: camera={camera_id}, confidence={confidence:.2f}")
        return record_id


def get_rickshaw_logs(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    event_type: Optional[str] = None,
    camera_id: Optional[str] = None,
    limit: int = 1000
) -> list[dict]:
    """
    Retrieve rickshaw event logs with optional filters.
    
    Args:
        start_date: Filter by start date (YYYY-MM-DD)
        end_date: Filter by end date (YYYY-MM-DD)
        event_type: Filter by event type ('entry' or 'exit')
        camera_id: Filter by camera ID
        limit: Maximum number of records to return
        
    Returns:
        list[dict]: List of log records
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        query = "SELECT * FROM rickshaw_logs WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND date(timestamp) >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND date(timestamp) <= ?"
            params.append(end_date)
        
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)
        
        if camera_id:
            query += " AND camera_id = ?"
            params.append(camera_id)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]


# ============================================================
# Analytics Functions
# ============================================================

def get_daily_counts(date: str, camera_id: str = "default") -> dict:
    """
    Get entry/exit counts for a specific date.
    
    Args:
        date: Date in YYYY-MM-DD format
        camera_id: Camera identifier
        
    Returns:
        dict: Dictionary with entry_count, exit_count, net_count
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Get entry count
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM rickshaw_logs
            WHERE date(timestamp) = ? AND event_type = 'entry' AND camera_id = ?
        """, (date, camera_id))
        entry_count = cursor.fetchone()['count']
        
        # Get exit count
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM rickshaw_logs
            WHERE date(timestamp) = ? AND event_type = 'exit' AND camera_id = ?
        """, (date, camera_id))
        exit_count = cursor.fetchone()['count']
        
        return {
            "date": date,
            "entry_count": entry_count,
            "exit_count": exit_count,
            "net_count": entry_count - exit_count
        }


def get_hourly_distribution(date: str, camera_id: str = "default") -> list[dict]:
    """
    Get hourly distribution of rickshaw events.
    
    Args:
        date: Date in YYYY-MM-DD format
        camera_id: Camera identifier
        
    Returns:
        list[dict]: List of hourly counts
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                strftime('%H', timestamp) as hour,
                event_type,
                COUNT(*) as count
            FROM rickshaw_logs
            WHERE date(timestamp) = ? AND camera_id = ?
            GROUP BY hour, event_type
            ORDER BY hour
        """, (date, camera_id))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_total_counts(camera_id: str = "default") -> dict:
    """
    Get total entry/exit counts across all time.
    
    Args:
        camera_id: Camera identifier
        
    Returns:
        dict: Dictionary with total counts
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN event_type = 'entry' THEN 1 ELSE 0 END) as total_entry,
                SUM(CASE WHEN event_type = 'exit' THEN 1 ELSE 0 END) as total_exit
            FROM rickshaw_logs
            WHERE camera_id = ?
        """, (camera_id,))
        
        row = cursor.fetchone()
        
        return {
            "total_entry": row['total_entry'] or 0,
            "total_exit": row['total_exit'] or 0,
            "net_count": (row['total_entry'] or 0) - (row['total_exit'] or 0)
        }
