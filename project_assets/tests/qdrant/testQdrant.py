import time, os, sys
os.environ["CUDA_VISIBLE_DEVICES"] = "1"
import pandas as pd
import numpy as np
from PIL import Image
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, SearchParams

# Configuration
K_values = [1, 3, 6]
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_PATH = os.path.join(SCRIPT_DIR, "..", "..","scripts", "outputs", "descriptions", "output_merged_semart.csv")
RETRIEVAL_DIR = os.path.join(SCRIPT_DIR, "retrieval_examples")
os.makedirs(RETRIEVAL_DIR, exist_ok=True)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..",  "data", "SemArt")
IMAGE_DIR = os.path.join(DATA_DIR, "Images")

# Set up local cache directory for HuggingFace models
CACHE_DIR = os.path.join(SCRIPT_DIR, "model_cache")
os.makedirs(CACHE_DIR, exist_ok=True)
os.environ['HF_HOME'] = CACHE_DIR
os.environ['TRANSFORMERS_CACHE'] = CACHE_DIR

print("Loading model...")
print(f"Using cache directory: {CACHE_DIR}")
model = SentenceTransformer("thenlper/gte-large", cache_folder=CACHE_DIR)

subset_sizes = [1000, 5000, 10000, 15000]

# Multiple HNSW configurations to test (like different FAISS indices)
# Each configuration trades off speed vs accuracy
hnsw_configs = [
    {"name": "HNSW-High-Recall", "m": 32, "ef_construct": 200, "ef_search": 128, "color": "blue"},
    {"name": "HNSW-Balanced", "m": 16, "ef_construct": 100, "ef_search": 64, "color": "red"},
]

print_results_of = {
    (IMAGE_DIR+"/"+ "06684-village.jpg"): 0,
    (IMAGE_DIR+"/"+ "28363-1market.jpg"): 1
}


def compute_recall(search_results, df_subset, size):
    """
    Compute recall@k metrics.
    search_results: list of lists of point IDs from Qdrant
    """
    recalls = {}
    for k in K_values:
        if k > size:
            continue
        
        correct = 0
        for i in range(size):
            # Get the original image file for query i
            original_file = df_subset.iloc[i]["image_file"]
            
            # Check if any of the top-k results match the original
            for j in range(min(k, len(search_results[i]))):
                retrieved_id = search_results[i][j].id
                retrieved_file = df_subset.iloc[retrieved_id]["image_file"]
                if retrieved_file == original_file:
                    correct += 1
                    break
        
        recalls[f"Recall@{k}"] = correct / size
    
    return recalls


def test_qdrant_config(client, collection_name, original_emb, generated_emb, df_subset, config, save_examples=False):
    """
    Test Qdrant with specific HNSW configuration.
    """
    size = len(df_subset)
    dimension = generated_emb.shape[1]
    
    m = config["m"]
    ef_construct = config["ef_construct"]
    ef_search = config["ef_search"]
    config_name = config["name"]
    
    print(f"Creating collection '{collection_name}' with {config_name} (m={m}, ef_construct={ef_construct})...")
    
    # Delete collection if it exists
    try:
        client.delete_collection(collection_name=collection_name)
    except Exception:
        pass
    
    # Create collection with HNSW parameters
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=dimension,
            distance=Distance.COSINE
        ),
        hnsw_config={
            "m": m,
            "ef_construct": ef_construct
        }
    )
    
    # Prepare and upload points in batches to avoid timeout
    print(f"Uploading {size} vectors...")
    
    upload_start = time.time()
    batch_size = 100  # Upload 100 vectors at a time
    
    for batch_start in range(0, size, batch_size):
        batch_end = min(batch_start + batch_size, size)
        batch_points = [
            PointStruct(
                id=i,
                vector=generated_emb[i].tolist(),
                payload={"image_file": df_subset.iloc[i]["image_file"]}
            )
            for i in range(batch_start, batch_end)
        ]
        
        client.upsert(
            collection_name=collection_name,
            points=batch_points,
            wait=True  # Wait for the operation to complete
        )
        
        if (batch_end % 1000 == 0) or (batch_end == size):
            print(f"  Uploaded {batch_end}/{size} vectors...")
    
    upload_time = time.time() - upload_start
    
    print(f"Searching {size} queries with ef={ef_search}...")
    
    # Measure query latency
    search_results = []
    total_query_time = 0
    
    for i in range(size):
        query_start = time.time()
        results = client.query_points(
            collection_name=collection_name,
            query=original_emb[i].tolist(),
            limit=max(K_values),
            search_params=SearchParams(
                hnsw_ef=ef_search  # Search-time parameter
            )
        )
        query_time = time.time() - query_start
        total_query_time += query_time
        search_results.append(results.points)
    
    avg_latency = total_query_time / size
    
    # Compute recall
    recall = compute_recall(search_results, df_subset, size)
    
    # Estimate memory: vectors + HNSW overhead
    # HNSW memory overhead depends on m parameter
    # Formula: base_vectors + (m * 2 * 4 bytes per connection * num_vectors)
    vector_memory_mb = (generated_emb.nbytes / (1024 * 1024))
    hnsw_overhead_mb = (m * 2 * 4 * size) / (1024 * 1024)  # Approximate
    estimated_total_mb = vector_memory_mb + hnsw_overhead_mb
    
    # Save retrieval examples if requested
    if save_examples:
        top_k_dir = os.path.join(RETRIEVAL_DIR, f"qdrant_{config_name}_{size}")
        os.makedirs(top_k_dir, exist_ok=True)
        
        for i in print_results_of.values():
            try:
                original_path = os.path.join(IMAGE_DIR, df_subset.iloc[i]["image_file"])
                Image.open(original_path).save(os.path.join(top_k_dir, f"{i}_original.jpg"))
            except Exception as e:
                print(f"[Error] Original image {original_path}: {e}")
            
            for rank, result in enumerate(search_results[i][:6]):
                try:
                    retrieved_idx = result.id
                    retrieved_path = os.path.join(IMAGE_DIR, df_subset.iloc[retrieved_idx]["image_file"])
                    Image.open(retrieved_path).save(os.path.join(top_k_dir, f"{i}_{rank+1}.jpg"))
                except Exception as e:
                    print(f"[Error] Retrieved image: {e}")
    
    return {
        "Config": config_name,
        "Latency (s/query)": round(avg_latency, 6),
        "Latency (ms/query)": round(avg_latency * 1000, 3),
        "Upload Time (s)": round(upload_time, 2),
        "Memory (MB)": round(estimated_total_mb, 2),
        **{k: round(v, 3) for k, v in recall.items()}
    }


if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print("Usage: python testQdrant_multiple_configs.py <mode>")
        print("  mode: 'local' (Docker on localhost:6333) or 'memory' (in-memory mode)")
        sys.exit(1)
    
    mode = sys.argv[1]
    
    # Initialize Qdrant client with increased timeout
    if mode == "local":
        print("Connecting to Qdrant on localhost:6333...")
        client = QdrantClient(host="localhost", port=6333, timeout=120)  # 120 second timeout
    elif mode == "memory":
        print("Using Qdrant in-memory mode...")
        client = QdrantClient(":memory:")
    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)
    
    print("Loading generated descriptions...")
    df_gen = pd.read_csv(DATA_PATH)
    print("Loading original descriptions from SemArt.csv...")
    semart_path = os.path.join(SCRIPT_DIR, "..", "..", "data", "SemArt", "SemArt.csv")
    df_orig = pd.read_csv(semart_path)
    df = pd.merge(df_gen, df_orig[['id', 'description']], on='id', suffixes=('_gen', '_orig'))
    df['original_description'] = df['description_orig']
    df['generated_description'] = df['description_gen']
    df['image_file'] = df['image_file_gen'] if 'image_file_gen' in df.columns else df['image_file']
    print(f"Loaded {len(df)} samples after merge")

    print("Encoding descriptions...")
    original_emb_all = model.encode(df["original_description"].tolist(), normalize_embeddings=True).astype("float32")
    generated_emb_all = model.encode(df["generated_description"].tolist(), normalize_embeddings=True).astype("float32")
    
    global_results = []
    
    for size in subset_sizes:
        print(f"\n{'='*80}")
        print(f"Testing with {size} samples")
        print(f"{'='*80}")
        
        df_subset = df.iloc[:size].reset_index(drop=True)
        original_emb = original_emb_all[:size]
        generated_emb = generated_emb_all[:size]
        
        for config in hnsw_configs:
            collection_name = f"semart_{size}_{config['name'].lower().replace('-', '_')}"
            
            # Test with this configuration
            save_examples = (size == subset_sizes[-1] and config["name"] == "HNSW-Balanced")
            result = test_qdrant_config(
                client, 
                collection_name, 
                original_emb, 
                generated_emb, 
                df_subset,
                config,
                save_examples=save_examples
            )
            
            result["# Samples"] = size
            result["m"] = config["m"]
            result["ef_construct"] = config["ef_construct"]
            result["ef_search"] = config["ef_search"]
            result["TikZ_color"] = config["color"]
            
            global_results.append(result)
            
            # Clean up
            try:
                client.delete_collection(collection_name=collection_name)
            except Exception:
                pass
    
    df_results = pd.DataFrame(global_results)
    print("\n" + "="*80)
    print("QDRANT RESULTS - MULTIPLE CONFIGURATIONS")
    print("="*80)
    print(df_results[["Config", "# Samples", "Latency (ms/query)", "Memory (MB)", "Recall@1", "Recall@3", "Recall@6"]])
    
    # Save results to CSV
    output_file = os.path.join(SCRIPT_DIR, f"qdrant_results_{mode}_multi_config.csv")
    df_results.to_csv(output_file, index=False)
    print(f"\nResults saved to: {output_file}")
    
    # Generate LaTeX TikZ code for plotting
    print("\n" + "="*80)
    print("LATEX TIKZ COORDINATES")
    print("="*80)
    
    print("\n% Recall@1 coordinates:")
    for config in hnsw_configs:
        config_name = config["name"]
        color = config["color"]
        data = df_results[df_results["Config"] == config_name]
        coords = " ".join([f"({row['# Samples']/1000}, {row['Recall@1']:.3f})" 
                          for _, row in data.iterrows()])
        print(f"\\addplot[color={color}, mark=*] coordinates {{{coords}}};")
        print(f"\\addlegendentry{{{config_name}}}")
    
    print("\n% Latency coordinates:")
    for config in hnsw_configs:
        config_name = config["name"]
        color = config["color"]
        data = df_results[df_results["Config"] == config_name]
        coords = " ".join([f"({row['# Samples']/1000}, {row['Latency (s/query)']:.6f})" 
                          for _, row in data.iterrows()])
        print(f"\\addplot[color={color}, mark=*] coordinates {{{coords}}};")
    
    print("\n% Memory coordinates:")
    for config in hnsw_configs:
        config_name = config["name"]
        color = config["color"]
        data = df_results[df_results["Config"] == config_name]
        coords = " ".join([f"({row['# Samples']/1000}, {row['Memory (MB)']:.2f})" 
                          for _, row in data.iterrows()])
        print(f"\\addplot[color={color}, mark=*] coordinates {{{coords}}};")

