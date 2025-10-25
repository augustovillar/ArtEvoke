from sqlalchemy.orm import sessionmaker
import sys
import os

# Add parent directory to path to import database_config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from database_config import setup_database

# Global variables
_db_engine = None
_SessionLocal = None


def get_database_engine():
    """Return a SQLAlchemy Engine singleton, creating it if necessary."""
    global _db_engine
    if _db_engine is None:
        print("Connecting to database engine...")
        _db_engine = setup_database(echo=False)
        print("✅ Database engine ready")
    return _db_engine


def get_database_client():
    """Return a sessionmaker (SessionLocal). Creates engine and sessionmaker lazily."""
    global _SessionLocal
    if _SessionLocal is None:
        engine = get_database_engine()
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        print("✅ SessionLocal (sessionmaker) ready")
    return _SessionLocal