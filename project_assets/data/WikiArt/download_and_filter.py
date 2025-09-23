import os
import pandas as pd
import kagglehub
import shutil

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PATH_DATASET = os.path.join(SCRIPT_DIR, "Images")
INPUT_CSV = os.path.join(SCRIPT_DIR, "WikiArt.csv")

genres_selected = {
    "New_Realism", "Realism", "Baroque", "Impressionism", "Northern_Renaissance",
    "Romanticism", "Mannerism_Late_Renaissance", "Pointillism", "Contemporary_Realism",
    "Early_Renaissance", "High_Renaissance", "Naive_Art_Primitivism",
    "Post_Impressionism", "Ukiyo_e"
}

def download_and_unzip():
    print("Downloading WikiArt dataset...")
    path = kagglehub.dataset_download("steubk/wikiart")
    print(f"Dataset downloaded to: {path}")

    if os.path.exists(PATH_DATASET):
        print(f"Removing existing folder: {PATH_DATASET}")
        shutil.rmtree(PATH_DATASET)

    shutil.move(path, PATH_DATASET)
    print(f"Moved dataset to: {PATH_DATASET}")

def remove_unwanted_files():
    for item in os.listdir(PATH_DATASET):
        item_path = os.path.join(PATH_DATASET, item)

        if os.path.isdir(item_path) and item not in genres_selected:
            print(f"Deleting unwanted genre folder: {item_path}")
            shutil.rmtree(item_path)

    os.remove(os.path.join(PATH_DATASET, "wclasses.csv"))
    shutil.move(os.path.join(PATH_DATASET, "classes.csv"), os.path.join(SCRIPT_DIR, "classes.csv"))

def filter_dataset():
    df1 = pd.read_csv(os.path.join(SCRIPT_DIR, "classes.csv"))

    df1 = df1[df1["filename"].apply(lambda f: any(g in f for g in genres_selected))]

    df1["file_exists"] = df1["filename"].apply(lambda f: os.path.exists(os.path.join(PATH_DATASET, f)))
    df1 = df1[df1["file_exists"]]

    df1["basename"] = df1["filename"].apply(lambda x: x.split("/")[-1])
    df_keep = df1.drop_duplicates(subset="basename", keep="first")
    df_duplicates = df1[~df1.index.isin(df_keep.index)]

    deleted_count = 0
    for _, row in df_duplicates.iterrows():
        full_path = os.path.join(PATH_DATASET, row["filename"])
        if os.path.exists(full_path):
            os.remove(full_path)
            deleted_count += 1

    df_keep.drop(columns=["file_exists", "basename"], errors="ignore") \
        .drop(columns=["subset", "genre_count"], errors="ignore") \
        .to_csv(INPUT_CSV, index=False)
    
    os.remove(os.path.join(SCRIPT_DIR, "classes.csv"))

    print(f"Final dataset size: {len(df_keep)}")
    print(f"Deleted {deleted_count} duplicated files.")

if __name__ == "__main__":
    download_and_unzip()
    remove_unwanted_files()
    filter_dataset()