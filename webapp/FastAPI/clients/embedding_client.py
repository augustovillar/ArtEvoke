import torch
import numpy as np
from sentence_transformers import SentenceTransformer
import os

# Global variables
_embedding_model = None
device = None
_disable_model = os.getenv('DISABLE_EMBEDDING_MODEL', 'false').lower() == 'true'

def get_embedding_client():
    global _embedding_model, device
    
    if _disable_model:
        print("⚠️ Embedding model disabled via DISABLE_EMBEDDING_MODEL environment variable")
        return None
    
    if _embedding_model is None:
        device = torch.device("cuda:1" if torch.cuda.is_available() else "cpu")
        print(f"Loading embedding model on {device}...")
        
        model_kwargs = {
            "attn_implementation": "sdpa",
            "dtype": torch.float16,
        }
        
        _embedding_model = SentenceTransformer(
            "Qwen/Qwen3-Embedding-4B",
            model_kwargs=model_kwargs,
            tokenizer_kwargs={"padding_side": "left"},
            device=str(device),  
        )
        print(f"✅ Embedding model loaded on {device}")
    
    return _embedding_model

def encode_text(texts, convert_to_numpy=True):
    """Encode text(s) to embeddings, with fallback for disabled model"""
    if _disable_model:
        if isinstance(texts, str):
            texts = [texts]
        
        np.random.seed(42)
        embeddings = np.random.rand(len(texts), 2560).astype(np.float32)
        
        if convert_to_numpy:
            return embeddings
        else:
            return torch.from_numpy(embeddings)
    
    model = get_embedding_client()
    return model.encode(texts, convert_to_numpy=convert_to_numpy)


_embedding_model = get_embedding_client()