import torch
import numpy as np
from sentence_transformers import SentenceTransformer
import os

# Global variables
_embedding_model = None
device = None
_disable_model = os.getenv('DISABLE_EMBEDDING_MODEL', 'false').lower() == 'true'

def get_device():
    """Get the device being used for embeddings (cuda or cpu)"""
    global device
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return device

def get_embedding_client():
    global _embedding_model, device
    
    if _disable_model:
        print("⚠️ Embedding model disabled via DISABLE_EMBEDDING_MODEL environment variable")
        return None
    
    if _embedding_model is None:
        # Check available GPUs
        num_gpus = torch.cuda.device_count()

        model_kwargs = {
            "attn_implementation": "sdpa",
            "dtype": torch.float16,
        }
        
        if num_gpus > 1:
            model_kwargs["device_map"] = "balanced"
        elif num_gpus == 1:
            model_kwargs["device_map"] = "cuda:0"
        else:
            model_kwargs["device_map"] = "cpu"
        
        _embedding_model = SentenceTransformer(
            "Qwen/Qwen3-Embedding-4B",
            model_kwargs=model_kwargs,
            tokenizer_kwargs={"padding_side": "left"},
        )
        
        # Print device allocation details
        if num_gpus > 0:
            print(f"✅ Embedding model loaded and distributed across {num_gpus} GPU(s)")
            for i in range(num_gpus):
                mem_allocated = torch.cuda.memory_allocated(i) / 1024**3  # Convert to GB
                mem_reserved = torch.cuda.memory_reserved(i) / 1024**3
                print(f"   GPU {i} ({torch.cuda.get_device_name(i)}): {mem_allocated:.2f}GB allocated, {mem_reserved:.2f}GB reserved")
        else:
            print(f"✅ Embedding model loaded on CPU")
    
    return _embedding_model

def encode_text(texts, convert_to_numpy=True):
    """Encode text(s) to embeddings, with fallback for disabled model"""
    if _disable_model:
        # Return random embeddings as fallback
        if isinstance(texts, str):
            texts = [texts]
        
        # Use a fixed seed for consistent "random" embeddings
        np.random.seed(42)
        # Assuming 2560-dimensional embeddings (common for Qwen models)
        embeddings = np.random.rand(len(texts), 2560).astype(np.float32)
        
        if convert_to_numpy:
            return embeddings
        else:
            return torch.from_numpy(embeddings)
    
    # Normal model encoding
    model = get_embedding_client()
    return model.encode(texts, convert_to_numpy=convert_to_numpy)

def get_device():
    """Get the device being used for the embedding model"""
    global device
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return device


# start embedding system
_embedding_model = get_embedding_client()