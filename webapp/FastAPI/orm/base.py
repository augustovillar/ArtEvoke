"""
Base configuration for SQLAlchemy ORM models.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

# Base class for all ORM models
Base = declarative_base()

# Database engine (to be configured with actual connection string)
engine = None
SessionLocal = None


def init_db(database_url: str, **engine_kwargs):
    """
    Initialize the database engine and session factory.

    Args:
        database_url: Database connection string (e.g., "mysql+pymysql://user:pass@host/db")
        **engine_kwargs: Additional arguments to pass to create_engine
    """
    global engine, SessionLocal

    engine = create_engine(database_url, poolclass=NullPool, **engine_kwargs)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    return engine


def get_db():
    """
    Dependency function for FastAPI to get database sessions.
    Yields a database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_all_tables():
    """
    Create all tables in the database.
    Should be called after all models are imported.
    """
    Base.metadata.create_all(bind=engine)


def drop_all_tables():
    """
    Drop all tables in the database.
    Use with caution - this will delete all data!
    """
    Base.metadata.drop_all(bind=engine)
