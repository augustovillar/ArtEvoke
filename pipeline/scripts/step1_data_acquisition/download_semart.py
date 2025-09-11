"""
SemArt Dataset Download and Processing
Step 1a: Download SemArt dataset from official source
"""
import os
import sys
import requests
import zipfile
import pandas as pd
import shutil
from pathlib import Path
import logging

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from config import DATASETS, ensure_directories
from utils.logging_setup import setup_logging

logger = setup_logging("semart_download")

def download_semart():
    """Download SemArt dataset from official source"""
    dataset_config = DATASETS["semart"]
    raw_dir = dataset_config["raw_dir"]
    download_url = dataset_config["download_url"]
    
    zip_file = raw_dir / "SemArt.zip"
    temp_extract_dir = raw_dir / "SemArt"
    
    logger.info(f"📥 Starting SemArt download to {raw_dir}")
    
    # Create directories
    ensure_directories()
    
    # Download dataset
    logger.info(f"⬇️ Downloading from {download_url}")
    response = requests.get(download_url, stream=True)
    response.raise_for_status()
    
    with open(zip_file, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    
    logger.info(f"✅ Download complete: {zip_file}")
    
    # Extract dataset
    logger.info("📂 Extracting archive...")
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(raw_dir)
    
    logger.info("✅ Extraction complete")
    
    # Cleanup zip file
    zip_file.unlink()
    logger.info("🗑️ Cleaned up zip file")
    
    return temp_extract_dir

def process_semart_metadata(extract_dir):
    """Process and merge SemArt CSV files"""
    dataset_config = DATASETS["semart"]
    metadata_dir = dataset_config["metadata_dir"]
    metadata_dir.mkdir(exist_ok=True)
    
    logger.info("📊 Processing SemArt metadata...")
    
    # Merge train/val/test CSV files
    csv_files = ["semart_train.csv", "semart_val.csv", "semart_test.csv"]
    dfs = []
    
    for csv_file in csv_files:
        csv_path = extract_dir / csv_file
        if csv_path.exists():
            df = pd.read_csv(csv_path, sep="\t", encoding="latin1")
            dfs.append(df)
            logger.info(f"📄 Loaded {csv_file}: {len(df)} records")
        else:
            logger.warning(f"⚠️ File not found: {csv_file}")
    
    if not dfs:
        raise FileNotFoundError("No CSV files found in extracted data")
    
    # Merge all dataframes
    merged_df = pd.concat(dfs, ignore_index=True)
    
    # Save original merged file
    original_file = metadata_dir / "semart_original.csv"
    merged_df.to_csv(original_file, index=False)
    logger.info(f"💾 Saved original merged file: {original_file}")
    
    return merged_df

def create_semart_subsets(merged_df):
    """Create different sized subsets of SemArt"""
    dataset_config = DATASETS["semart"]
    metadata_dir = dataset_config["metadata_dir"]
    
    logger.info("🎯 Creating SemArt subsets...")
    
    # SemArt500 - 50 images per genre (10 genres = 500 total)
    genres = ["genre", "historical", "interior", "landscape", "mythological",
              "portrait", "religious", "still-life", "study", "other"]
    
    df_500_parts = []
    for genre in genres:
        genre_df = merged_df[merged_df["TYPE"] == genre]
        if len(genre_df) >= 50:
            sample = genre_df.sample(n=50, random_state=42)
            df_500_parts.append(sample)
        else:
            logger.warning(f"⚠️ Genre '{genre}' has only {len(genre_df)} images (< 50)")
            df_500_parts.append(genre_df)
    
    df_500 = pd.concat(df_500_parts, ignore_index=True)
    df_500.to_csv(metadata_dir / "SemArt500.csv", index=False)
    logger.info(f"💾 Created SemArt500.csv: {len(df_500)} images")
    
    # SemArt2000 - Add 1500 more random images
    remaining = merged_df[~merged_df["IMAGE_FILE"].isin(df_500["IMAGE_FILE"])]
    df_1500 = remaining.sample(n=min(1500, len(remaining)), random_state=42)
    df_2000 = pd.concat([df_500, df_1500], ignore_index=True)
    df_2000.to_csv(metadata_dir / "SemArt2000.csv", index=False)
    logger.info(f"💾 Created SemArt2000.csv: {len(df_2000)} images")
    
    # SemArt15000 - Exclude some genres for variety
    excluded_genres = {"portrait", "study", "still-life", "interior", "other"}
    df_15000 = merged_df[~merged_df["TYPE"].str.lower().isin(excluded_genres)]
    df_15000.to_csv(metadata_dir / "SemArt15000.csv", index=False)
    logger.info(f"💾 Created SemArt15000.csv: {len(df_15000)} images")
    
    # Return set of all used image files
    all_used = set(df_500["IMAGE_FILE"]) | set(df_2000["IMAGE_FILE"]) | set(df_15000["IMAGE_FILE"])
    return all_used

def organize_semart_images(extract_dir, used_image_files):
    """Move and organize SemArt images"""
    dataset_config = DATASETS["semart"]
    target_images_dir = dataset_config["images_dir"] 
    source_images_dir = extract_dir / "Images"
    
    logger.info("🖼️ Organizing SemArt images...")
    
    # Create target directory
    target_images_dir.mkdir(exist_ok=True)
    
    # Move only used images
    moved_count = 0
    for image_file in used_image_files:
        source_path = source_images_dir / image_file
        target_path = target_images_dir / image_file
        
        if source_path.exists():
            shutil.move(str(source_path), str(target_path))
            moved_count += 1
        else:
            logger.warning(f"⚠️ Image not found: {image_file}")
    
    logger.info(f"✅ Moved {moved_count} images to {target_images_dir}")
    
    # Cleanup extraction directory
    shutil.rmtree(extract_dir)
    logger.info("🗑️ Cleaned up temporary extraction directory")

def main():
    """Main execution function"""
    try:
        logger.info("🚀 Starting SemArt download and processing")
        
        # Step 1: Download and extract
        extract_dir = download_semart()
        
        # Step 2: Process metadata
        merged_df = process_semart_metadata(extract_dir)
        
        # Step 3: Create subsets
        used_images = create_semart_subsets(merged_df)
        
        # Step 4: Organize images
        organize_semart_images(extract_dir, used_images)
        
        logger.info("🎉 SemArt processing completed successfully!")
        logger.info(f"📊 Total images processed: {len(used_images)}")
        
    except Exception as e:
        logger.error(f"❌ Error processing SemArt: {str(e)}")
        raise

if __name__ == "__main__":
    main()
