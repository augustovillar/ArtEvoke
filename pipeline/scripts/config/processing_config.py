"""
ArtEvoke Processing Configuration
General processing parameters and settings
"""

# Processing limits (for development/testing)
PROCESSING_LIMITS = {
    "semart_limit": None,      # None = process all, int = limit for testing
    "wikiart_limit": None,     # e.g., 100 for quick testing
    "museum_limit": None,
    "test_mode": False         # Set to True for small sample processing
}

# If test_mode is True, use these limits
TEST_MODE_LIMITS = {
    "semart_limit": 50,
    "wikiart_limit": 50,
    "museum_limit": 20
}

# Parallel processing settings
PARALLEL_CONFIG = {
    "use_multiprocessing": True,
    "num_processes": 2,        # Should match number of GPUs
    "chunk_size": None         # None = auto-calculate based on dataset size
}

# File naming conventions
FILE_NAMING = {
    "description_column_base": "description_Qwen2_5",
    "intermediate_suffix": "_gpu{gpu_id}",
    "final_suffix": "_merged",
    "backup_suffix": "_backup"
}

# Logging configuration  
LOGGING_CONFIG = {
    "level": "INFO",           # DEBUG, INFO, WARNING, ERROR
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "log_to_file": True,
    "log_dir": "logs"
}

# Data validation settings
VALIDATION_CONFIG = {
    "check_image_integrity": True,
    "min_image_size": (64, 64),      # Minimum image dimensions
    "max_image_size": (4096, 4096),  # Maximum image dimensions  
    "allowed_extensions": [".jpg", ".jpeg", ".png", ".bmp"],
    "check_csv_encoding": True
}

def get_processing_limits():
    """Get current processing limits based on test mode"""
    if PROCESSING_LIMITS["test_mode"]:
        return TEST_MODE_LIMITS
    return PROCESSING_LIMITS
