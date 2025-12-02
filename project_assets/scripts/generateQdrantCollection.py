import faiss, os
import pandas as pd
import pickle
import torch
import numpy as np
import argparse
import uuid
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

OUTPUT_FILES = {
    "semart": "output_merged_semart.csv",
    "wikiart": "output_merged_wikiart.csv",
    "ipiranga": "output_merged_ipiranga.csv",
}

# Model will be loaded later based on command-line argument
model = None


def parse_args():
    parser = argparse.ArgumentParser(description="Generate Qdrant collections from descriptions with phrase-level embeddings")
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
        "--split-phrases",
        action="store_true",
        help="Split descriptions into phrases - each phrase becomes a separate point pointing to the same item"
    )
    return parser.parse_args()


def load_model():
    """Load Qwen3-Embedding-4B model on cuda:1"""
    global model
    
    model_path = "Qwen/Qwen3-Embedding-4B"
    device = "cuda:1"
    
    print(f"Loading model: {model_path}...")
    print(f"Using cache directory: {LOCAL_CACHE_DIR}")
    print(f"Using device: {device}")
    
    model = SentenceTransformer(
        model_path,
        cache_folder=LOCAL_CACHE_DIR,
        device=device,
        model_kwargs={
            "attn_implementation": "flash_attention_2",
            "device_map": device,
            "dtype": torch.float16,
        },
        tokenizer_kwargs={"padding_side": "left"},
    )
    
    # Explicitly ensure model is on the correct device
    if hasattr(model, 'to'):
        model = model.to(device)
    
    print(f"Model loaded successfully on {device}!")


def split_description_into_phrases(description):
    """Split a description into phrases by periods, cleaning and filtering empty ones"""
    if pd.isna(description) or description == "":
        return []
    
    phrases = description.split('.')
    phrases = [phrase.strip() for phrase in phrases if phrase.strip()]
    
    return phrases


def setup_qdrant_collection(client, collection_name, vector_size):
    """Create or recreate a Qdrant collection"""
    try:
        client.delete_collection(collection_name)
        print(f"Deleted existing collection: {collection_name}")
    except Exception:
        print(f"Collection {collection_name} doesn't exist, creating new one")
    
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
    )
    
    print(f"Created collection: {collection_name}")


def generate_qdrant_collection(client, df, dataset_name, split_phrases=False):
    """Generate and upload data to Qdrant with phrase-level embeddings"""
    
    # Filter out rows with missing descriptions
    df_filtered = df[df['description'].notna()].copy()
    df_filtered = df_filtered[df_filtered['description'] != ""].copy()
    
    print(f"Processing {len(df_filtered)} items (filtered from {len(df)} total)...")
    
    points = []
    all_texts_to_encode = []
    point_metadata = []
    
    for idx, row in df_filtered.iterrows():
        item_id = row['id']
        item_type = row['type'] if 'type' in row else None
        full_description = str(row['description'])
        
        if split_phrases:
            texts_to_encode = split_description_into_phrases(full_description)
            if not texts_to_encode:
                texts_to_encode = [full_description]
        else:
            texts_to_encode = [full_description]
        
        for text in texts_to_encode:
            all_texts_to_encode.append(text)
            point_metadata.append({
                'id': item_id,
                'type': item_type,
                'description': full_description  # Always store the full original description
            })
    
    print(f"Encoding {len(all_texts_to_encode)} texts...")
    
    embeddings = model.encode(all_texts_to_encode, normalize_embeddings=True, show_progress_bar=True).astype("float32")
    
    setup_qdrant_collection(client, dataset_name, embeddings.shape[1])
    
    for embedding, metadata in zip(embeddings, point_metadata):
        point = PointStruct(
            id=str(uuid.uuid4()),  
            vector=embedding.tolist(),
            payload={
                'id': metadata['id'],  
                'type': metadata['type'],
                'description': metadata['description']  
            }
        )
        points.append(point)
    
    batch_size = 100
    for i in range(0, len(points), batch_size):
        batch = points[i:i + batch_size]
        client.upsert(
            collection_name=dataset_name,
            points=batch
        )
        print(f"Uploaded batch {i//batch_size + 1}/{(len(points) + batch_size - 1)//batch_size} for {dataset_name}")
    
    print(f"Successfully uploaded {len(points)} points to collection {dataset_name}")
    print(f"  - {len(df_filtered)} unique items")
    print(f"  - {len(points)} total points (phrases/descriptions)")


def main():
    args = parse_args()
    
    load_model()
    
    print(f"Connecting to Qdrant at {args.qdrant_host}:{args.qdrant_port}")
    client = QdrantClient(host=args.qdrant_host, port=args.qdrant_port)
    
    try:
        collections = client.get_collections()
        print(f"Successfully connected to Qdrant. Current collections: {[c.name for c in collections.collections]}")
    except Exception as e:
        print(f"Failed to connect to Qdrant: {e}")
        return
    
    for name in args.datasets:
        if name not in OUTPUT_FILES:
            print(f"Unknown dataset: {name}")
            continue
            
        file_name = OUTPUT_FILES[name]
        
        collection_name = f"{name}" if args.split_phrases else name
        
        print(f"\n{'='*60}")
        print(f"Processing {name}...")
        if args.split_phrases:
            print("  Mode: Split descriptions into phrases")
        else:
            print("  Mode: Use full descriptions")
        print(f"{'='*60}\n")
        
        # Load the generated descriptions
        file_path = os.path.join(DESCRIPTION_PATH, file_name)
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue
            
        df = pd.read_csv(file_path)
        
        # Ensure required columns exist
        required_columns = ['id', 'description']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"Warning: Missing required columns {missing_columns} in {file_name}")
            continue
        
        # Generate Qdrant collection
        generate_qdrant_collection(
            client, 
            df, 
            collection_name,
            split_phrases=args.split_phrases
        )
    
    print("\n" + "="*60)
    print("Processing complete!")
    print("="*60)


if __name__ == "__main__":
    main()

