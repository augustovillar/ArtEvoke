import faiss, os
import pandas as pd
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

DESCRIPTION_PATH = os.path.join(SCRIPT_DIR, "..",  "outputs", "descriptions")

PATH_OUTPUT = os.path.join(SCRIPT_DIR, "..", "outputs", "faiss")

os.makedirs(PATH_OUTPUT, exist_ok=True)

OUTPUT_FILES = {
    "museum": "output_merged_museum.csv",
    "semart": "output_merged_semart.csv",
    "wikiart": "output_merged_wikiart.csv"
}

COLUMNS = {
    "museum": {
        "desc": "description",
        "meta": ["recordID", "titleText", "imageLinkHigh", "creatorDescription", "subjectMatter", "description"],
        "renaming": {"imageLinkHigh": "file_name", "titleText": "title", "creatorDescription": "author"}
    },
    "semart": {
        "desc": "description",
        "meta": ["IMAGE_FILE", "DESCRIPTION", "AUTHOR", "TITLE", "TECHNIQUE", "DATE", "TYPE", "SCHOOL", "description"],
        "renaming": {"IMAGE_FILE": "file_name", "TITLE": "title", "AUTHOR": "author", "TYPE": "genre"}
    },
    "wikiart": {
        "desc": "description",
        "meta": ["filename", "artist", "genre", "description"],
        "renaming": {"filename": "file_name", "artist": "author", "genre": "genre"}
    }
}


print("Loading model...")
model0 = SentenceTransformer("thenlper/gte-large", device="cuda:0")
model1 = SentenceTransformer("thenlper/gte-large", device="cuda:1")

def generate_faiss_datasets(df, dataset_name, column_description, column_metadata):
    descriptions = df[column_description].tolist()
    descriptions_part0 = descriptions[:len(descriptions)//2]
    descriptions_part1 = descriptions[len(descriptions)//2:]

    part0_embeddings = model0.encode(descriptions_part0, normalize_embeddings=True).astype("float32")
    part1_embeddings = model1.encode(descriptions_part1, normalize_embeddings=True).astype("float32")
    embeddings = np.concatenate((part0_embeddings, part1_embeddings), axis=0)

    index_flat = faiss.IndexFlatIP(embeddings.shape[1])
    index_flat.add(embeddings)

    # Save FAISS index
    faiss.write_index(index_flat, os.path.join(PATH_OUTPUT, f"{dataset_name}_index.faiss"))

    # Save metadata
    metadata = df[column_metadata].copy().reset_index(drop=True)
    renaming_dict = COLUMNS[dataset_name].get("renaming", {})
    metadata.rename(columns=renaming_dict, inplace=True)

    if "file_name" in metadata.columns:
        prefix_to_strip = "/DATA/public/siamese/dataset_mrbab/art-foto/"
        metadata["file_name"] = metadata["file_name"].str.replace(prefix_to_strip, "", regex=False)
    

    with open(os.path.join(PATH_OUTPUT, f"{dataset_name}_metadata.pkl"), "wb") as f:
        pickle.dump(metadata, f)

    # print(f"{dataset_name} done: {len(embeddings)} embeddings, index + metadata saved.")

# Process each dataset
for name, file_name in OUTPUT_FILES.items():
    print(f"Processing {name}...")
    df = pd.read_csv(os.path.join(DESCRIPTION_PATH, file_name))
    generate_faiss_datasets(df, name, COLUMNS[name]["desc"], COLUMNS[name]["meta"])