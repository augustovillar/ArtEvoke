"""
Database configuration and initialization for ArtEvoke application.
This module handles MySQL database connection using SQLAlchemy ORM.
"""

import logging
from database_config import setup_database, get_connection_info
from orm import create_all_tables

logging.basicConfig(level=logging.INFO)

engine = None


async def connect_to_mysql():
    """Initialize MySQL database connection and create tables."""
    global engine
    try:
        engine = setup_database(echo=False)
        logging.info("Connected to MySQL")

        # Create all tables if they don't exist
        create_all_tables()
        logging.info("Database tables ready")

        # Log connection info
        info = get_connection_info()
        logging.info(f"Database: {info['database']} at {info['host']}:{info['port']}")

    except Exception as e:
        logging.error(f"Could not connect to MySQL: {e}")
        engine = None
        raise


async def disconnect_from_mysql():
    """Close MySQL database connection."""
    global engine
    if engine:
        engine.dispose()
        engine = None
        logging.info("Disconnected from MySQL")
