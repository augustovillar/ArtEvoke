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
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print("Loading embedding model...")
        _embedding_model = SentenceTransformer(
            "Qwen/Qwen3-Embedding-4B",
            model_kwargs={
                "attn_implementation": "sdpa",
                "device_map": torch.device("cuda" if torch.cuda.is_available() else "cpu"),
                "dtype": torch.float16,
            },
            tokenizer_kwargs={"padding_side": "left"},
        )
        print(f"✅ Embedding model loaded on {device}")
    
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
