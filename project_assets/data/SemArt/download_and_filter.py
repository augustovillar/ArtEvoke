import os
import requests
import zipfile
import pandas as pd
import shutil

# --- Constants ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
URL_SEMART = "https://researchdata.aston.ac.uk/id/eprint/380/1/SemArt.zip"
ZIP_FILE = os.path.join(SCRIPT_DIR, "SemArt.zip")
MERGED_CSV = "semart_original.csv"
KEEP_FOLDER = "Images"
SEM_ART_DIR =  os.path.join(SCRIPT_DIR, "SemArt")
IMG_DIR_OLD = os.path.join(SEM_ART_DIR, "Images")
IMG_DIR_NEW = os.path.join(SCRIPT_DIR, "Images")
EXPORT_DIR = os.path.join(SCRIPT_DIR, "semart_info")

# --- Download and extract dataset ---
def download_and_extract():
    print("Downloading...")
    response = requests.get(URL_SEMART, stream=True)
    with open(ZIP_FILE, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    print("Download complete.")

    print("Extracting...")
    with zipfile.ZipFile(ZIP_FILE, 'r') as zip_ref:
        zip_ref.extractall(SCRIPT_DIR)
    print("Extraction complete.")
    os.remove(ZIP_FILE)

# --- Merge train/val/test into a single CSV ---
def merge_csvs():
    os.makedirs(EXPORT_DIR, exist_ok=True)

    csv_files = ["semart_train.csv", "semart_val.csv", "semart_test.csv"]
    dfs = [pd.read_csv(os.path.join(SEM_ART_DIR, f), sep="\t",encoding="latin1") for f in csv_files]
    merged_df = pd.concat(dfs, ignore_index=True)
    merged_df.to_csv(os.path.join(EXPORT_DIR, MERGED_CSV), index=False)
    print(f"Merged CSV saved as {os.path.join(EXPORT_DIR, MERGED_CSV)}")

# --- Cleanup all except merged CSV and Images ---
def clean_directory():
    for item in os.listdir(SCRIPT_DIR):
        print(f"Checking item: {item}")
        if item not in ["SemArt", os.path.basename(IMG_DIR_OLD), os.path.basename(EXPORT_DIR), "download_and_filter.py"]:
            if os.path.isfile(item):
                os.remove(item)
            elif os.path.isdir(item):
                shutil.rmtree(item)

    for item in os.listdir(SEM_ART_DIR):
        full_path = os.path.join(SEM_ART_DIR, item)
        if item != "Images":
            if os.path.isfile(full_path):
                os.remove(full_path)
            elif os.path.isdir(full_path):
                shutil.rmtree(full_path)

    print("Cleanup complete. Only merged CSV and Images folder are kept.")

# --- Generate SemArt500, 2000, and 15000 ---
def create_semart_subsets():
    df = pd.read_csv(os.path.join(EXPORT_DIR, MERGED_CSV))

    # SemArt500
    genres = ["genre", "historical", "interior", "landscape", "mythological",
              "portrait", "religious", "still-life", "study", "other"]
    df_500 = pd.concat([df[df["TYPE"] == g].sample(n=50, random_state=42) for g in genres])
    df_500.to_csv(os.path.join(EXPORT_DIR, "SemArt500.csv"), index=False)

    # SemArt2000
    remaining = df[~df["IMAGE_FILE"].isin(df_500["IMAGE_FILE"])]
    df_1500 = remaining.sample(n=1500, random_state=42)
    df_2000 = pd.concat([df_500, df_1500])
    df_2000.to_csv(os.path.join(EXPORT_DIR, "SemArt2000.csv"), index=False)

    # SemArt15000
    excluded_genres = {"portrait", "study", "still-life", "interior", "other"}
    df_15000 = df[~df["TYPE"].str.lower().isin(excluded_genres)]
    df_15000.to_csv(os.path.join(EXPORT_DIR, "SemArt15000.csv"), index=False)

    print("Subsets SemArt500, SemArt2000, and SemArt15000 saved.")
    return set(df_500["IMAGE_FILE"])| set(df_2000["IMAGE_FILE"]) | set(df_15000["IMAGE_FILE"])

def clean_unused_images(used_files):
    for img_name in os.listdir(IMG_DIR_OLD):
        if img_name not in used_files:
            try:
                os.remove(os.path.join(IMG_DIR_OLD, img_name))
            except Exception as e:
                print(f"Error deleting {img_name}: {e}")
    print("Unused images removed.")

def move_images_and_cleanup():
    os.makedirs(IMG_DIR_NEW, exist_ok=True)

    for img_name in os.listdir(IMG_DIR_OLD):
        src = os.path.join(IMG_DIR_OLD, img_name)
        dst = os.path.join(IMG_DIR_NEW, img_name)
        if os.path.isfile(src):
            shutil.move(src, dst)

    shutil.rmtree(SEM_ART_DIR)
    print("Images moved to root Images/ folder. SemArt/ folder removed.")

# --- Main Execution ---
if __name__ == "__main__":
    print(SEM_ART_DIR)
    download_and_extract()
    merge_csvs()
    clean_directory()
    all_used_images = create_semart_subsets()
    clean_unused_images(all_used_images)
    move_images_and_cleanup()
