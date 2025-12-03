import numpy as np
from openai import OpenAI
import os

# Global variables
_openai_client = None

def get_openai_client():
    """Get DeepInfra OpenAI client for API-based embeddings"""
    global _openai_client
    
    if _openai_client is None:
        api_key = os.getenv('DEEPINFRA_API_KEY')
        if not api_key:
            raise ValueError("DEEPINFRA_API_KEY environment variable is required")
        
        _openai_client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepinfra.com/v1/openai",
        )
        print("✅ DeepInfra OpenAI client initialized")
    
    return _openai_client

def encode_text(texts, convert_to_numpy=True):
    """Encode text(s) to embeddings using DeepInfra API"""
    if isinstance(texts, str):
        texts = [texts]
    
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
    
    return embeddings


print("🌐 Using DeepInfra API for embeddings")