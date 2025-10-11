"""
Database configuration for ArtEvoke application.
This module handles database connection setup for the Docker MySQL instance.
"""

import os
from orm import init_db

# Default Docker MySQL configuration (from .env.mysql)
DEFAULT_DB_CONFIG = {
    "user": "appuser",
    "password": "changeme_app",
    "host": "localhost",
    "port": 3306,
    "database": "appdb",
}


def get_database_url(
    user: str = None,
    password: str = None,
    host: str = None,
    port: int = None,
    database: str = None,
) -> str:
    """
    Build database URL from components.
    """
    user = user or os.getenv("DB_USER", DEFAULT_DB_CONFIG["user"])
    password = password or os.getenv("DB_PASSWORD", DEFAULT_DB_CONFIG["password"])
    host = host or os.getenv("DB_HOST", DEFAULT_DB_CONFIG["host"])
    port = port or int(os.getenv("DB_PORT", DEFAULT_DB_CONFIG["port"]))
    database = database or os.getenv("DB_NAME", DEFAULT_DB_CONFIG["database"])

    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"


def setup_database(echo: bool = False):
    """
    Initialize database connection with default Docker MySQL settings
    """
    database_url = get_database_url()
    engine = init_db(database_url, echo=echo)
    return engine


def get_connection_info():
    """
    Get current database connection information (for display purposes).
    """
    return {
        "user": os.getenv("DB_USER", DEFAULT_DB_CONFIG["user"]),
        "host": os.getenv("DB_HOST", DEFAULT_DB_CONFIG["host"]),
        "port": int(os.getenv("DB_PORT", DEFAULT_DB_CONFIG["port"])),
        "database": os.getenv("DB_NAME", DEFAULT_DB_CONFIG["database"]),
        "url": get_database_url().replace(
            os.getenv("DB_PASSWORD", DEFAULT_DB_CONFIG["password"]), "***"
        ),
    }


if __name__ == "__main__":
    # Test database configuration
    print("Database Configuration")
    print("=" * 60)

    info = get_connection_info()
    print(f"User:     {info['user']}")
    print(f"Host:     {info['host']}")
    print(f"Port:     {info['port']}")
    print(f"Database: {info['database']}")
    print(f"URL:      {info['url']}")

    print("\n" + "=" * 60)
    print("Testing connection...")

    try:
        engine = setup_database(echo=False)
        print("✓ Database connection successful!")

        # Test query
        from orm import get_db, Patient

        db = next(get_db())
        count = db.query(Patient).count()
        print(f"✓ Found {count} patients in database")
        db.close()

    except Exception as e:
        print(f"✗ Connection failed: {e}")
        print("\nMake sure Docker MySQL is running:")
        print("  cd /home/augustovillar/ArtEvoke/webapp/data/db")
        print("  docker-compose up -d")
