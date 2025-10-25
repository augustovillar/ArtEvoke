from sqlalchemy.orm import sessionmaker
import sys
import os

# Add parent directory to path to import database_config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from database_config import setup_database

# Global variables
_db_engine = None
_SessionLocal = None

def get_database_client():
    """Initialize the database connection"""
    global _db_engine
    
    if _db_engine is None:
        print("Connecting to database...")
        _db_engine = setup_database(echo=False)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
        print("✅ Database connection established")
    
    return _db_engine

def get_database_engine():
    db_engine = get_database_client()
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    return _SessionLocal