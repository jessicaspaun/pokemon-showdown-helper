"""
Database connection and utility functions for the Pokémon Showdown Helper.
"""
import sqlite3
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager

# Create the engine with connection pooling
def create_db_engine(db_path: Path):
    """Create a SQLAlchemy engine with connection pooling."""
    return create_engine(
        f'sqlite:///{db_path}',
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800
    )

# Create a thread-safe session factory
def create_session_factory(engine):
    """Create a thread-safe session factory."""
    return scoped_session(sessionmaker(bind=engine))

# Initialize the engine and session factory
db_path = Path(__file__).parent.parent / "database" / "pokemon_showdown.db"
if not db_path.exists():
    raise FileNotFoundError(f"Database file not found at {db_path}")

engine = create_db_engine(db_path)
SessionFactory = create_session_factory(engine)

@contextmanager
def get_db_session():
    """Get a database session using a context manager."""
    session = SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def get_db_connection():
    """Get a connection to the SQLite database (legacy method)."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn

def close_db_connection(conn):
    """Close the database connection (legacy method)."""
    if conn:
        conn.close() 