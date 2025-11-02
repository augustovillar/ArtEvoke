"""
Database configuration for ArtEvoke application.
This module handles database connection setup for the Docker MySQL instance.
"""

import os
from urllib.parse import quote_plus
from orm import init_db

def get_database_url(
    user: str = None,
    password: str = None,
    host: str = None,
    port: int = None,
    database: str = None,
) -> str:
    """
    Build database URL from components.
    
    Raises ValueError if any required environment variable is missing or matches defaults.
    """
    # Get values from parameters or environment variables
    env_user = user or os.getenv("DB_USER")
    env_password = password or os.getenv("DB_PASSWORD")
    env_host = host or os.getenv("DB_HOST")
    env_port = port or os.getenv("DB_PORT")
    env_database = database or os.getenv("DB_NAME")
    
    # Validate that all required environment variables are set and not using defaults
    missing_vars = []
    if not env_user:
        missing_vars.append("DB_USER")
    if not env_password:
        missing_vars.append("DB_PASSWORD")
    if not env_host:
        missing_vars.append("DB_HOST")
    if not env_database:
        missing_vars.append("DB_NAME")
    
    if missing_vars:
        raise ValueError(
            f"Missing or using default values for required database environment variables: {', '.join(missing_vars)}\n"
            f"Please set these variables in your .env file (./env/.backend.env)"
        )
    
    final_port = int(env_port) if env_port else 3306
    
    # Use validated values
    final_user = env_user
    final_password = env_password
    final_host = env_host
    final_database = env_database

    # URL-encode credentials to handle special characters like @, =, etc.
    encoded_user = quote_plus(final_user)
    encoded_password = quote_plus(final_password)
    
    return f"mysql+pymysql://{encoded_user}:{encoded_password}@{final_host}:{final_port}/{final_database}"


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
        "user": os.getenv("DB_USER", None),
        "host": os.getenv("DB_HOST", None),
        "port": int(os.getenv("DB_PORT", None)),
        "database": os.getenv("DB_NAME", None),
        "url": get_database_url().replace(
            os.getenv("DB_PASSWORD", ""), "***"
        ),
    }

