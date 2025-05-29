import time, os, psutil
import faiss, sys
import pandas as pd
from PIL import Image
from sentence_transformers import SentenceTransformer
from pynvml import nvmlInit, nvmlDeviceGetHandleByIndex, nvmlDeviceGetMemoryInfo, nvmlDeviceGetCount



nvmlInit()
K_values = [1, 3, 6]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_PATH = os.path.join(SCRIPT_DIR, "..", "..", "descriptions", "output_merged_semart.csv")
RETRIEVAL_DIR = os.path.join(SCRIPT_DIR, "retrieval_examples")
os.makedirs(RETRIEVAL_DIR, exist_ok=True)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..",  "data", "SemArt")
IMAGE_DIR = os.path.join(DATA_DIR, "Images")

print("Loading model...")
model = SentenceTransformer("thenlper/gte-large")

subset_sizes = [1000, 5000, 10000, 15000]

# Predefine parameters to avoid FAISS clustering warnings
param_config = {
    1000:  {"nlist": 25,  "m_pq": 8,  "nbits_pq": 8},
    5000:  {"nlist": 50,  "m_pq": 16, "nbits_pq": 8},
    10000: {"nlist": 100, "m_pq": 16, "nbits_pq": 8},
    15000: {"nlist": 100, "m_pq": 16, "nbits_pq": 8}
}

print_results_of = {
    # (IMAGE_DIR+"/"+ "15281-111geric.jpg"): 254,
    (IMAGE_DIR+"/"+ "06684-village.jpg"): 0,
    (IMAGE_DIR+"/"+ "28363-1market.jpg"): 1
}


def get_memory_mb():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)

def get_total_gpu_memory_mb():
    total_used = 0
    device_count = nvmlDeviceGetCount()
    for i in range(device_count):
        handle = nvmlDeviceGetHandleByIndex(i)
        info = nvmlDeviceGetMemoryInfo(handle)
        total_used += info.used
    return total_used / (1024 * 1024)  # MB

def compute_recall(I, size):
    recalls = {}
    for k in K_values:
        if k > size:
            continue 
        correct = sum(
            metadata[I[i, j]]["image_file"] == df_subset.iloc[i]["image_file"]
            for i in range(size) for j in range(k)
        )
        recalls[f"Recall@{k}"] = correct / size
    return recalls

def test_faiss_index(index, name, train_data=None, gpu=False):
    import gc
    gc.collect() 
    if gpu:
        mem_before = get_total_gpu_memory_mb()
    else:
        mem_before = get_memory_mb()

    print(f"Training {name}...")
    if train_data is not None and index.is_trained is False:
        index.train(train_data)
    index.add(generated_emb)

    gc.collect()
    if gpu:
        mem_after = get_total_gpu_memory_mb()
    else:
        mem_after = get_memory_mb()
    index_mem_MB = mem_after - mem_before

    print(f"Searching {name}...")
    start = time.time()
    D, I = index.search(original_emb, max(K_values))
    latency = (time.time() - start) / len(original_emb)

    recall = compute_recall(I, len(df_subset))
    total_mem_MB = generated_emb.nbytes / (1024 * 1024) + index_mem_MB

    if name == "IndexFlatIP":
        top_k_dir = os.path.join(RETRIEVAL_DIR, f"flatip_{len(df_subset)}")
        os.makedirs(top_k_dir, exist_ok=True)

        for i in print_results_of.values():
            try:
                original_path = os.path.join(IMAGE_DIR, df_subset.iloc[i]["image_file"])
                Image.open(original_path).save(os.path.join(top_k_dir, f"{i}_original.jpg"))
            except Exception as e:
                print(f"[Error] Original image {original_path}: {e}")

            for rank, idx in enumerate(I[i][:6]):
                try:
                    retrieved_path = os.path.join(IMAGE_DIR, metadata[idx]["image_file"])
                    Image.open(retrieved_path).save(os.path.join(top_k_dir, f"{i}_{rank+1}.jpg"))
                except Exception as e:
                    print(f"[Error] Retrieved image {retrieved_path}: {e}")

    return {
        "Index": name,
        "Latency (s/query)": round(latency, 6),
        "Memory (MB)": round(total_mem_MB, 2),  # includes embeddings + index
        **{k: round(v, 3) for k, v in recall.items()}
    }

if __name__ == "__main__":

    print("Loading data...")

    df = pd.read_csv(DATA_PATH)[["IMAGE_FILE", "DESCRIPTION", "description"]]
    df.columns = ["image_file", "original_description", "generated_description"]

    global_results = []
    mode = sys.argv[1]

    print("Encondding descriptions...")
    original_emb_all = model.encode(df["original_description"].tolist(), normalize_embeddings=True).astype("float32")
    generated_emb_all = model.encode(df["generated_description"].tolist(), normalize_embeddings=True).astype("float32")
    
    if mode == "cpu":
        for size in subset_sizes:
            print(f"\n===== Testing with {size} samples =====")
            config = param_config[size]
            nlist = config["nlist"]
            m_pq = config["m_pq"]
            nbits_pq = config["nbits_pq"]

            df_subset = df.iloc[:size].reset_index(drop=True)
            original_emb = original_emb_all[:size]
            generated_emb = generated_emb_all[:size]
            metadata = [{"image_file": f} for f in df_subset["image_file"]]

            dimension = generated_emb.shape[1]
            results = []

            # IndexFlatIP
            results.append(test_faiss_index(faiss.IndexFlatIP(generated_emb.shape[1]), "IndexFlatIP"))

            # IndexIVF
            quantizer = faiss.IndexFlatIP(generated_emb.shape[1])
            ivf = faiss.IndexIVFFlat(quantizer, generated_emb.shape[1], nlist)
            results.append(test_faiss_index(ivf, "IndexIVF", train_data=generated_emb))

            # IndexIVFPQ
            quantizer_pq = faiss.IndexFlatIP(generated_emb.shape[1])
            ivfpq = faiss.IndexIVFPQ(quantizer_pq, generated_emb.shape[1], nlist, m_pq, nbits_pq)
            results.append(test_faiss_index(ivfpq, "IndexIVFPQ", train_data=generated_emb))

            for r in results:
                r["# Samples"] = size
                r["nlist"] = nlist
                r["m_pq"] = m_pq if r["Index"] == "IndexIVFPQ" else "N/A"
                r["nbits_pq"] = nbits_pq if r["Index"] == "IndexIVFPQ" else "N/A"

            global_results.extend(results)
    elif mode == "gpu":
        res = faiss.StandardGpuResources()

        for size in subset_sizes:
            print(f"\n===== Testing with {size} samples (GPU) =====")
            config = param_config[size]
            nlist = config["nlist"]
            m_pq = config["m_pq"]
            nbits_pq = config["nbits_pq"]

            df_subset = df.iloc[:size].reset_index(drop=True)
            original_emb = original_emb_all[:size]
            generated_emb = generated_emb_all[:size]
            metadata = [{"image_file": f} for f in df_subset["image_file"]]

            results = []

            # IndexFlatIP on GPU
            index_flat = faiss.IndexFlatIP(generated_emb.shape[1])
            gpu_flat = faiss.index_cpu_to_gpu(res, 0, index_flat)
            results.append(test_faiss_index(gpu_flat, "IndexFlatIP", gpu=True))

            # IVF on GPU
            cpu_ivf = faiss.IndexIVFFlat(faiss.IndexFlatIP(generated_emb.shape[1]), generated_emb.shape[1], nlist)
            gpu_ivf = faiss.index_cpu_to_gpu(res, 0, cpu_ivf)
            results.append(test_faiss_index(gpu_ivf, "IndexIVF", train_data=generated_emb, gpu=True))

            # IVFPQ on GPU
            cpu_ivfpq = faiss.IndexIVFPQ(faiss.IndexFlatIP(generated_emb.shape[1]), generated_emb.shape[1], nlist, m_pq, nbits_pq)
            gpu_ivfpq = faiss.index_cpu_to_gpu(res, 0, cpu_ivfpq)
            results.append(test_faiss_index(gpu_ivfpq, "IndexIVFPQ", train_data=generated_emb, gpu=True))

            for r in results:
                r["# Samples"] = size
                r["nlist"] = nlist
                r["m_pq"] = m_pq if r["Index"] == "IndexIVFPQ" else "N/A"
                r["nbits_pq"] = nbits_pq if r["Index"] == "IndexIVFPQ" else "N/A"

            global_results.extend(results)

    df_results = pd.DataFrame(global_results)
    print(df_results)