import torch
from sentence_transformers import SentenceTransformer

# Global variables
_embedding_model = None
device = None

def get_device():
    """Get the device being used for embeddings (cuda or cpu)"""
    global device
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return device

def get_embedding_client():
    global _embedding_model, device
    
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
