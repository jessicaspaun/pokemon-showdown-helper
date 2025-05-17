"""
Tests for the database connection module.
"""
import os
import tempfile
import pytest
from pathlib import Path
from data_scripts.database import (
    create_db_engine,
    create_session_factory,
    get_db_session,
    get_db_connection,
    close_db_connection
)

@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    db_fd, db_path = tempfile.mkstemp()
    yield Path(db_path)
    os.close(db_fd)
    os.unlink(db_path)

def test_create_db_engine(temp_db):
    """Test creating a database engine."""
    engine = create_db_engine(temp_db)
    assert engine is not None
    assert str(engine.url) == f'sqlite:///{temp_db}'

def test_create_session_factory(temp_db):
    """Test creating a session factory."""
    engine = create_db_engine(temp_db)
    session_factory = create_session_factory(engine)
    assert session_factory is not None

def test_get_db_session(temp_db):
    """Test the database session context manager."""
    engine = create_db_engine(temp_db)
    session_factory = create_session_factory(engine)
    
    # Create a test table
    with get_db_session() as session:
        session.execute("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        """)
        session.commit()
    
    # Test inserting and querying data
    with get_db_session() as session:
        session.execute(
            "INSERT INTO test_table (name) VALUES (?)",
            ("test_name",)
        )
        session.commit()
        
        result = session.execute("SELECT name FROM test_table").fetchone()
        assert result[0] == "test_name"

def test_get_db_session_rollback(temp_db):
    """Test that session rollback works on error."""
    engine = create_db_engine(temp_db)
    session_factory = create_session_factory(engine)
    
    # Create a test table
    with get_db_session() as session:
        session.execute("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        """)
        session.commit()
    
    # Test rollback on error
    with pytest.raises(Exception):
        with get_db_session() as session:
            session.execute(
                "INSERT INTO test_table (name) VALUES (?)",
                ("test_name",)
            )
            raise Exception("Test error")
    
    # Verify the data was not committed
    with get_db_session() as session:
        result = session.execute("SELECT COUNT(*) FROM test_table").fetchone()
        assert result[0] == 0

def test_legacy_connection(temp_db):
    """Test the legacy database connection methods."""
    # Create a test table
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        """)
        conn.commit()
        
        # Test inserting and querying data
        cursor.execute(
            "INSERT INTO test_table (name) VALUES (?)",
            ("test_name",)
        )
        conn.commit()
        
        cursor.execute("SELECT name FROM test_table")
        result = cursor.fetchone()
        assert result[0] == "test_name"
    finally:
        close_db_connection(conn)

def test_connection_pool(temp_db):
    """Test that the connection pool is working."""
    engine = create_db_engine(temp_db)
    session_factory = create_session_factory(engine)
    
    # Create multiple sessions and verify they work
    sessions = []
    for i in range(3):
        session = session_factory()
        sessions.append(session)
        session.execute("""
            CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        """)
        session.execute(
            "INSERT INTO test_table (name) VALUES (?)",
            (f"test_name_{i}",)
        )
        session.commit()
    
    # Verify all sessions can read the data
    for i, session in enumerate(sessions):
        result = session.execute("SELECT name FROM test_table").fetchall()
        assert len(result) == i + 1
    
    # Clean up
    for session in sessions:
        session.close() 