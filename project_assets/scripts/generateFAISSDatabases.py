import faiss, os
import pandas as pd
import pickle
import torch
import numpy as np
import argparse
from sentence_transformers import SentenceTransformer
from concurrent.futures import ThreadPoolExecutor
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

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


def parse_args():
    parser = argparse.ArgumentParser(description="Generate FAISS or Qdrant databases from descriptions")
    parser.add_argument(
        "--use-qdrant", 
        action="store_true", 
        help="Use Qdrant instead of FAISS"
    )
    parser.add_argument(
        "--qdrant-host", 
        default="localhost", 
        help="Qdrant host (default: localhost)"
    )
    parser.add_argument(
        "--qdrant-port", 
        type=int, 
        default=6333, 
        help="Qdrant port (default: 6333)"
    )
    parser.add_argument(
        "--datasets",
        nargs="+",
        choices=["semart", "wikiart", "ipiranga"],
        default=["semart", "wikiart", "ipiranga"],
        help="Datasets to process (default: all)"
    )
    return parser.parse_args()


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


def setup_qdrant_collection(client, collection_name, vector_size):
    """Create or recreate a Qdrant collection"""
    try:
        # Delete collection if it exists
        client.delete_collection(collection_name)
        print(f"Deleted existing collection: {collection_name}")
    except Exception:
        print(f"Collection {collection_name} doesn't exist, creating new one")
    
    # Create new collection
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
    )
    print(f"Created collection: {collection_name}")


def generate_qdrant_dataset(client, df, dataset_name, column_description, column_metadata):
    """Generate and upload data to Qdrant"""
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
    
    # Setup collection
    setup_qdrant_collection(client, dataset_name, embeddings.shape[1])
    
    # Prepare metadata
    metadata = df[column_metadata].copy().reset_index(drop=True)
    renaming_dict = COLUMNS[dataset_name].get("renaming", {})
    if renaming_dict:
        metadata.rename(columns=renaming_dict, inplace=True)

    if "file_name" in metadata.columns:
        prefix_to_strip = "/DATA/public/siamese/dataset_mrbab/art-foto/"
        metadata["file_name"] = metadata["file_name"].str.replace(
            prefix_to_strip, "", regex=False
        )

    # Create points for Qdrant
    points = []
    for idx, (embedding, (_, row)) in enumerate(zip(embeddings, metadata.iterrows())):
        point = PointStruct(
            id=idx,
            vector=embedding.tolist(),
            payload=row.to_dict()
        )
        points.append(point)
    
    # Upload to Qdrant in batches
    batch_size = 100
    for i in range(0, len(points), batch_size):
        batch = points[i:i + batch_size]
        client.upsert(
            collection_name=dataset_name,
            points=batch
        )
        print(f"Uploaded batch {i//batch_size + 1}/{(len(points) + batch_size - 1)//batch_size} for {dataset_name}")
    
    print(f"Successfully uploaded {len(points)} points to collection {dataset_name}")


def generate_faiss_datasets(df, dataset_name, column_description, column_metadata):
    """Generate FAISS datasets (original functionality)"""
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


def generate_faiss_datasets(df, dataset_name, column_description, column_metadata):
    """Generate FAISS datasets (original functionality)"""
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


def main():
    args = parse_args()
    
    if args.use_qdrant:
        print(f"Connecting to Qdrant at {args.qdrant_host}:{args.qdrant_port}")
        client = QdrantClient(host=args.qdrant_host, port=args.qdrant_port)
        
        # Test connection
        try:
            collections = client.get_collections()
            print(f"Successfully connected to Qdrant. Current collections: {[c.name for c in collections.collections]}")
        except Exception as e:
            print(f"Failed to connect to Qdrant: {e}")
            return
    
    # Process each dataset
    for name in args.datasets:
        if name not in OUTPUT_FILES:
            print(f"Unknown dataset: {name}")
            continue
            
        file_name = OUTPUT_FILES[name]
        print(f"Processing {name}...")
        
        file_path = os.path.join(DESCRIPTION_PATH, file_name)
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue
            
        df = pd.read_csv(file_path)
        
        if args.use_qdrant:
            generate_qdrant_dataset(
                client, df, name, COLUMNS[name]["desc"], COLUMNS[name]["meta"]
            )
        else:
            generate_faiss_datasets(
                df, name, COLUMNS[name]["desc"], COLUMNS[name]["meta"]
            )
    
    print("Processing complete!")


if __name__ == "__main__":
    main()
