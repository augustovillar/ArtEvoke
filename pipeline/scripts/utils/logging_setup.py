"""
Logging Setup Utilities
Centralized logging configuration for all scripts
"""
import logging
import sys
from pathlib import Path
from config.processing_config import LOGGING_CONFIG

def setup_logging(script_name: str, log_level: str = None):
    """
    Setup logging configuration for a script
    
    Args:
        script_name: Name of the script (used for log file naming)
        log_level: Override default log level
    
    Returns:
        logger: Configured logger instance
    """
    # Use config or override
    level = log_level or LOGGING_CONFIG["level"]
    
    # Create logger
    logger = logging.getLogger(script_name)
    logger.setLevel(getattr(logging, level))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level))
    
    # Formatter
    formatter = logging.Formatter(LOGGING_CONFIG["format"])
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    # File handler (if enabled)
    if LOGGING_CONFIG["log_to_file"]:
        log_dir = Path(LOGGING_CONFIG["log_dir"])
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"{script_name}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level))
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
    
    return logger
