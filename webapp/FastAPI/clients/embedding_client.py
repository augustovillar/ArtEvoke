import torch
import numpy as np
from sentence_transformers import SentenceTransformer
from openai import OpenAI
import os

# Global variables
_embedding_model = None
_openai_client = None
device = None
_use_local_model = os.getenv('LOCAL_EMBEDDING_MODEL', 'false').lower() == 'true'

def get_embedding_client():
    """Get local embedding model client"""
    global _embedding_model, device
    
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

def get_openai_client():
    """Get DeepInfra OpenAI client for API-based embeddings"""
    global _openai_client
    
    if _openai_client is None:
        api_key = os.getenv('DEEPINFRA_API_KEY')
        if not api_key:
            raise ValueError("DEEPINFRA_API_KEY environment variable is required when LOCAL_EMBEDDING_MODEL=false")
        
        _openai_client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepinfra.com/v1/openai",
        )
        print("✅ DeepInfra OpenAI client initialized")
    
    return _openai_client

def encode_text(texts, convert_to_numpy=True):
    """Encode text(s) to embeddings using local model or DeepInfra API"""
    if isinstance(texts, str):
        texts = [texts]
    
    if _use_local_model:
        # Use local model
        model = get_embedding_client()
        embeddings = model.encode(texts, convert_to_numpy=convert_to_numpy)
    else:
        # Use DeepInfra API
        client = get_openai_client()
        
        response = client.embeddings.create(
            model="Qwen/Qwen3-Embedding-4B",
            input=texts,
            encoding_format="float"
        )
        
        if len(texts) == 1:
            embeddings = np.array([response.data[0].embedding], dtype=np.float32)
        else:
            embeddings = np.array([item.embedding for item in response.data], dtype=np.float32)
        
        if not convert_to_numpy:
            embeddings = torch.from_numpy(embeddings)
    
    return embeddings


if _use_local_model:
    _embedding_model = get_embedding_client()
else:
    print("🌐 Using DeepInfra API for embeddings (LOCAL_EMBEDDING_MODEL=false)")