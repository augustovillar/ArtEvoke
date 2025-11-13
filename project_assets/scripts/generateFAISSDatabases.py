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

# Set local cache directory to avoid permission issues
LOCAL_CACHE_DIR = os.path.join(SCRIPT_DIR, ".cache", "huggingface")
os.makedirs(LOCAL_CACHE_DIR, exist_ok=True)
os.environ['HF_HOME'] = LOCAL_CACHE_DIR
os.environ['TRANSFORMERS_CACHE'] = LOCAL_CACHE_DIR
os.environ['HF_DATASETS_CACHE'] = LOCAL_CACHE_DIR

DESCRIPTION_PATH = os.path.join(SCRIPT_DIR, "outputs", "descriptions")
ORIGINAL_DATA_PATH = os.path.join(SCRIPT_DIR, "..", "data")

PATH_OUTPUT = os.path.join(SCRIPT_DIR, "outputs", "faiss")

os.makedirs(PATH_OUTPUT, exist_ok=True)

OUTPUT_FILES = {
    "semart": "output_merged_semart.csv",
    "wikiart": "output_merged_wikiart.csv",
    "ipiranga": "output_merged_ipiranga.csv",
}

ORIGINAL_FILES = {
    "semart": "SemArt/SemArt.csv",
    "wikiart": "WikiArt/WikiArt.csv",
    "ipiranga": "Ipiranga/Ipiranga.csv",
}


COLUMNS = {
    "semart": {
        "desc": "description",
        "meta": ["id", "image_file", "description", "type"],
        "renaming": {
            "image_file": "file_name",
        },
    },
    "wikiart": {
        "desc": "description",
        "meta": ["id", "image_file", "description", "type"],
        "renaming": {
            "image_file": "file_name",
        },
    },
    "ipiranga": {
        "desc": "description",
        "meta": ["id", "inventory_code", "description", "type"],
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
    parser.add_argument(
        "--model",
        choices=["qwen-4b", "qwen-0.6b"],
        default="qwen-4b",
        help="Embedding model to use (default: qwen-4b)"
    )
    parser.add_argument(
        "--split-phrases",
        action="store_true",
        help="Split descriptions by phrases (sentences) - each phrase becomes a separate vector pointing to the same item"
    )
    return parser.parse_args()


print("Loading model...")
# Model will be loaded later based on command-line argument
model0 = None
model1 = None


def load_models(model_name):
    """Load embedding models based on the selected model name"""
    global model0, model1
    
    model_map = {
        "qwen-4b": "Qwen/Qwen3-Embedding-4B",
        "qwen-0.6b": "Qwen/Qwen3-Embedding-0.6B"
    }
    
    model_path = model_map.get(model_name)
    if not model_path:
        raise ValueError(f"Unknown model: {model_name}")
    
    print(f"Loading model: {model_path}...")
    print(f"Using cache directory: {LOCAL_CACHE_DIR}")
    
    model0 = SentenceTransformer(
        model_path,
        cache_folder=LOCAL_CACHE_DIR,
        model_kwargs={
            "attn_implementation": "flash_attention_2",
            "device_map": "cuda:0",
            "dtype": torch.float16,
        },
        tokenizer_kwargs={"padding_side": "left"},
    )
    # Commenting out model1 to avoid simultaneous downloads
    # model1 = SentenceTransformer(
    #     model_path,
    #     model_kwargs={
    #         "attn_implementation": "flash_attention_2",
    #         "device_map": "cuda:1",
    #         "dtype": torch.float16,
    #     },
    #     tokenizer_kwargs={"padding_side": "left"},
    # )
    model1 = model0  # Use the same model for both
    print(f"Models loaded successfully!")


def split_description_into_phrases(description):
    """Split a description into phrases by periods, cleaning and filtering empty ones"""
    if pd.isna(description) or description == "":
        return []
    
    # Split by period and clean up
    phrases = description.split('.')
    # Strip whitespace and filter out empty phrases
    phrases = [phrase.strip() for phrase in phrases if phrase.strip()]
    
    return phrases


def expand_dataframe_by_phrases(df, column_description, column_metadata):
    """
    Expand dataframe so each phrase becomes a row, but keeps all original metadata.
    Each phrase will reference the same original item.
    """
    expanded_rows = []
    
    for idx, row in df.iterrows():
        description = row[column_description]
        phrases = split_description_into_phrases(description)
        
        if not phrases:
            # If no phrases, keep the original row
            expanded_rows.append(row.to_dict())
            continue
        
        # Create a row for each phrase
        for phrase_idx, phrase in enumerate(phrases):
            new_row = row.to_dict()
            new_row[column_description] = phrase
            new_row['phrase_index'] = phrase_idx
            new_row['total_phrases'] = len(phrases)
            new_row['original_description'] = description
            expanded_rows.append(new_row)
    
    expanded_df = pd.DataFrame(expanded_rows)
    print(f"Expanded from {len(df)} items to {len(expanded_df)} phrase vectors")
    
    return expanded_df


def setup_qdrant_collection(client, collection_name, vector_size, use_named_vectors=False):
    """Create or recreate a Qdrant collection"""
    try:
        # Delete collection if it exists
        client.delete_collection(collection_name)
        print(f"Deleted existing collection: {collection_name}")
    except Exception:
        print(f"Collection {collection_name} doesn't exist, creating new one")
    
    # Create collection with named vectors if using phrase splitting
    if use_named_vectors:
        # For named vectors, create a dict with the full_description vector
        # Additional phrase vectors will be added dynamically when uploading points
        vectors_config = {
            "full_description": VectorParams(size=vector_size, distance=Distance.COSINE)
        }
        print(f"Creating collection with support for named vectors (full_description + phrases)")
    else:
        vectors_config = VectorParams(size=vector_size, distance=Distance.COSINE)
    
    # Create new collection
    client.create_collection(
        collection_name=collection_name,
        vectors_config=vectors_config
    )
    
    print(f"Created collection: {collection_name}")


def generate_qdrant_dataset(client, df, dataset_name, column_description, column_metadata, split_phrases=False):
    """Generate and upload data to Qdrant"""
    
    if split_phrases:
        print(f"Using Named Vectors approach for phrase splitting in {dataset_name}...")
        # With named vectors, we keep the original dataframe structure
        # but create multiple vectors per point
        generate_qdrant_with_named_vectors(client, df, dataset_name, column_description, column_metadata)
    else:
        # Original single-vector approach
        generate_qdrant_single_vector(client, df, dataset_name, column_description, column_metadata)


def generate_qdrant_single_vector(client, df, dataset_name, column_description, column_metadata):
    """Generate and upload data to Qdrant with single vector per item"""
    
    # Filter out rows with missing descriptions first
    df_filtered = df[df[column_description].notna()].copy()
    df_filtered = df_filtered[df_filtered[column_description] != ""].copy()
    
    print(f"Processing {len(df_filtered)} items (filtered from {len(df)} total)...")
    
    descriptions = df_filtered[column_description].tolist()
    descriptions = [str(d) for d in descriptions]  # Ensure all are strings
    
    print(f"Encoding {len(descriptions)} descriptions...")
    
    # Encode all descriptions using only model0
    embeddings = model0.encode(descriptions, normalize_embeddings=True, show_progress_bar=True).astype("float32")
    
    # Setup collection
    setup_qdrant_collection(client, dataset_name, embeddings.shape[1], use_named_vectors=False)
    
    # Prepare metadata from filtered dataframe
    metadata = df_filtered[column_metadata].copy().reset_index(drop=True)
    renaming_dict = COLUMNS[dataset_name.replace("_phrases", "")].get("renaming", {})
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


def generate_qdrant_with_named_vectors(client, df, dataset_name, column_description, column_metadata):
    """Generate and upload data to Qdrant with named vectors for phrases"""
    
    # Filter out rows with missing descriptions first
    df_filtered = df[df[column_description].notna()].copy()
    df_filtered = df_filtered[df_filtered[column_description] != ""].copy()
    
    print(f"Processing {len(df_filtered)} items (filtered from {len(df)} total)...")
    
    # First, encode the full descriptions
    full_descriptions = df_filtered[column_description].tolist()
    full_descriptions = [str(d) for d in full_descriptions]  # Ensure all are strings
    
    # Encode full descriptions using only model0
    print(f"Encoding {len(full_descriptions)} full descriptions...")
    full_embeddings = model0.encode(full_descriptions, normalize_embeddings=True, show_progress_bar=True).astype("float32")
    
    # Setup collection with named vectors support
    setup_qdrant_collection(client, dataset_name, full_embeddings.shape[1], use_named_vectors=True)
    
    # Now process each item and create phrase embeddings
    print(f"Processing phrases for each item...")
    points = []
    
    for idx, (_, row) in enumerate(df_filtered.iterrows()):
        # Prepare metadata
        metadata_dict = {col: row[col] for col in column_metadata if col in row}
        
        # Apply renaming
        renaming_dict = COLUMNS[dataset_name.replace("_phrases", "")].get("renaming", {})
        if renaming_dict:
            for old_name, new_name in renaming_dict.items():
                if old_name in metadata_dict:
                    metadata_dict[new_name] = metadata_dict.pop(old_name)
        
        # Clean file_name if present
        if "file_name" in metadata_dict:
            prefix_to_strip = "/DATA/public/siamese/dataset_mrbab/art-foto/"
            metadata_dict["file_name"] = metadata_dict["file_name"].replace(prefix_to_strip, "")
        
        # Split description into phrases
        description = row[column_description]
        phrases = split_description_into_phrases(description)
        
        # Add metadata about phrases
        metadata_dict['total_phrases'] = len(phrases)
        metadata_dict['original_description'] = description
        
        # Encode each phrase
        if phrases:
            phrase_embeddings = model0.encode(phrases, normalize_embeddings=True).astype("float32")
        else:
            phrases = [description]  # Fallback to full description
            phrase_embeddings = model0.encode(phrases, normalize_embeddings=True).astype("float32")
        
        # Create named vectors dictionary
        named_vectors = {
            "full_description": full_embeddings[idx].tolist()
        }
        
        # Add each phrase as a named vector
        for phrase_idx, phrase_emb in enumerate(phrase_embeddings):
            named_vectors[f"phrase_{phrase_idx}"] = phrase_emb.tolist()
        
        # Create point with named vectors
        point = PointStruct(
            id=idx,
            vector=named_vectors,
            payload=metadata_dict
        )
        points.append(point)
        
        if (idx + 1) % 100 == 0:
            print(f"Processed {idx + 1}/{len(df_filtered)} items...")
    
    # Upload to Qdrant in batches
    batch_size = 100
    for i in range(0, len(points), batch_size):
        batch = points[i:i + batch_size]
        client.upsert(
            collection_name=dataset_name,
            points=batch
        )
        print(f"Uploaded batch {i//batch_size + 1}/{(len(points) + batch_size - 1)//batch_size} for {dataset_name}")
    
    print(f"Successfully uploaded {len(points)} points with named vectors to collection {dataset_name}")


def generate_faiss_datasets(df, dataset_name, column_description, column_metadata):
    """Generate FAISS datasets (original functionality)"""
    
    # Filter out rows with missing descriptions first
    df_filtered = df[df[column_description].notna()].copy()
    df_filtered = df_filtered[df_filtered[column_description] != ""].copy()
    
    print(f"Processing {len(df_filtered)} items (filtered from {len(df)} total)...")
    
    descriptions = df_filtered[column_description].tolist()
    descriptions = [str(d) for d in descriptions]  # Ensure all are strings
    
    print(f"Encoding {len(descriptions)} descriptions...")
    
    # Encode all descriptions using only model0
    embeddings = model0.encode(descriptions, normalize_embeddings=True, show_progress_bar=True).astype("float32")

    index_flat = faiss.IndexFlatIP(embeddings.shape[1])
    index_flat.add(embeddings)

    # Save FAISS index
    faiss.write_index(
        index_flat, os.path.join(PATH_OUTPUT, f"{dataset_name}_index.faiss")
    )

    # Save metadata from filtered dataframe
    metadata = df_filtered[column_metadata].copy().reset_index(drop=True)
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
    
    # Load models based on selected model argument
    load_models(args.model)
    
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
        
        # Add suffix to collection name if splitting by phrases
        collection_name = f"{name}_phrases" if args.split_phrases else name
        
        print(f"Processing {name}..." + (" (with phrase splitting)" if args.split_phrases else ""))
        
        # Load the generated descriptions
        file_path = os.path.join(DESCRIPTION_PATH, file_name)
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue
            
        df_descriptions = pd.read_csv(file_path)
        
        # Load the original dataset to get the type column
        original_file_path = os.path.join(ORIGINAL_DATA_PATH, ORIGINAL_FILES[name])
        if os.path.exists(original_file_path):
            print(f"Loading original data from {original_file_path}...")
            df_original = pd.read_csv(original_file_path)
            # Merge on 'id' to get the 'type' column
            df = df_descriptions.merge(df_original[['id', 'type']], on='id', how='left')
            print(f"Merged type column from original dataset")
        else:
            print(f"Warning: Original file not found at {original_file_path}, proceeding without 'type' column")
            df = df_descriptions
        
        if args.use_qdrant:
            generate_qdrant_dataset(
                client, df, collection_name, COLUMNS[name]["desc"], COLUMNS[name]["meta"],
                split_phrases=args.split_phrases
            )
        else:
            generate_faiss_datasets(
                df, name, COLUMNS[name]["desc"], COLUMNS[name]["meta"]
            )
    
    print("Processing complete!")


if __name__ == "__main__":
    main()
