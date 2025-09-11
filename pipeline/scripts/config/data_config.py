"""
ArtEvoke Data Configuration
Centralized paths and dataset parameters
"""
import os
from pathlib import Path

# Project root directory (now under pipeline/)
PROJECT_ROOT = Path(__file__).parent.parent.parent
PIPELINE_ROOT = PROJECT_ROOT  # Same as project root in new structure
DATA_ROOT = PROJECT_ROOT / "data"
SCRIPTS_ROOT = PROJECT_ROOT / "scripts"

# Data directories
RAW_DATA_DIR = DATA_ROOT / "raw"
PROCESSED_DATA_DIR = DATA_ROOT / "processed"

# Dataset-specific paths
DATASETS = {
    "semart": {
        "raw_dir": RAW_DATA_DIR / "SemArt",
        "images_dir": RAW_DATA_DIR / "SemArt" / "Images", 
        "metadata_dir": RAW_DATA_DIR / "SemArt" / "metadata",
        "csv_file": "SemArt15000.csv",
        "download_url": "https://researchdata.aston.ac.uk/id/eprint/380/1/SemArt.zip"
    },
    "wikiart": {
        "raw_dir": RAW_DATA_DIR / "WikiArt",
        "images_dir": RAW_DATA_DIR / "WikiArt" / "Images",
        "csv_file": "WikiArt15000.csv", 
        "kaggle_dataset": "steubk/wikiart"
    },
    "museum": {
        "raw_dir": RAW_DATA_DIR / "Museum",
        "json_file": "input_data_museum.json"
    }
}

# Processing output directories
OUTPUT_DIRS = {
    "descriptions": PROCESSED_DATA_DIR / "descriptions",
    "embeddings": PROCESSED_DATA_DIR / "embeddings",
    "intermediate": PROCESSED_DATA_DIR / "descriptions" / "intermediate"
}

# Create directories if they don't exist
def ensure_directories():
    """Create all necessary directories"""
    for dataset_info in DATASETS.values():
        for key, path in dataset_info.items():
            if "dir" in key and isinstance(path, Path):
                path.mkdir(parents=True, exist_ok=True)
    
    for output_dir in OUTPUT_DIRS.values():
        output_dir.mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    ensure_directories()
    print("✅ All directories created successfully!")
