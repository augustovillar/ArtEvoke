import faiss, os
import pandas as pd
import pickle
import torch
import numpy as np
from sentence_transformers import SentenceTransformer
from concurrent.futures import ThreadPoolExecutor

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

DESCRIPTION_PATH = os.path.join(SCRIPT_DIR, "outputs", "descriptions")

PATH_OUTPUT = os.path.join(SCRIPT_DIR, "outputs", "faiss")

os.makedirs(PATH_OUTPUT, exist_ok=True)

OUTPUT_FILES = {
    "semart": "output_merged_semart.csv",
    "wikiart": "output_merged_wikiart.csv",
    "ipiranga": "output_merged_ipiranga.csv",
}

COLUMNS = {
    "semart": {
        "desc": "description",
        "meta": ["id", "image_file", "description"],
        "renaming": {
            "image_file": "file_name",
        },
    },
    "wikiart": {
        "desc": "description",
        "meta": ["id", "image_file", "description"],
        "renaming": {
            "image_file": "file_name",
        },
    },
    "ipiranga": {
        "desc": "description",
        "meta": ["id", "inventory_code", "description"],
        "renaming": {
            "inventory_code": "code",
        },
    },
}


print("Loading model...")
model0 = SentenceTransformer(
    "Qwen/Qwen3-Embedding-4B",
    model_kwargs={
        "attn_implementation": "flash_attention_2",
        "device_map": "cuda:0",
        "dtype": torch.float16,
    },
    tokenizer_kwargs={"padding_side": "left"},
)
model1 = SentenceTransformer(
    "Qwen/Qwen3-Embedding-4B",
    model_kwargs={
        "attn_implementation": "flash_attention_2",
        "device_map": "cuda:1",
        "dtype": torch.float16,
    },
    tokenizer_kwargs={"padding_side": "left"},
)


def generate_faiss_datasets(df, dataset_name, column_description, column_metadata):
    descriptions = df[column_description].tolist()
    descriptions_part0 = descriptions[: len(descriptions) // 2]
    descriptions_part1 = descriptions[len(descriptions) // 2 :]

    def encode_part(model, descs):
        return model.encode(descs, normalize_embeddings=True).astype("float32")

    with ThreadPoolExecutor(max_workers=2) as executor:
        future0 = executor.submit(encode_part, model0, descriptions_part0)
        future1 = executor.submit(encode_part, model1, descriptions_part1)
        part0_embeddings = future0.result()
        part1_embeddings = future1.result()

    embeddings = np.concatenate((part0_embeddings, part1_embeddings), axis=0)

    index_flat = faiss.IndexFlatIP(embeddings.shape[1])
    index_flat.add(embeddings)

    # Save FAISS index
    faiss.write_index(
        index_flat, os.path.join(PATH_OUTPUT, f"{dataset_name}_index.faiss")
    )

    # Save metadata
    metadata = df[column_metadata].copy().reset_index(drop=True)
    renaming_dict = COLUMNS[dataset_name].get("renaming", {})
    if renaming_dict:
        metadata.rename(columns=renaming_dict, inplace=True)

    if "file_name" in metadata.columns:
        prefix_to_strip = "/DATA/public/siamese/dataset_mrbab/art-foto/"
        metadata["file_name"] = metadata["file_name"].str.replace(
            prefix_to_strip, "", regex=False
        )

    with open(os.path.join(PATH_OUTPUT, f"{dataset_name}_metadata.pkl"), "wb") as f:
        pickle.dump(metadata, f)


# Process each dataset
for name, file_name in OUTPUT_FILES.items():
    print(f"Processing {name}...")
    df = pd.read_csv(os.path.join(DESCRIPTION_PATH, file_name))
    generate_faiss_datasets(df, name, COLUMNS[name]["desc"], COLUMNS[name]["meta"])
