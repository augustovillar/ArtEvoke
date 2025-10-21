from qdrant_client import QdrantClient
import time
from ..utils.types import Dataset
from ..utils.embedding_utils import get_embedding

# Global variables
_qdrant_client = None

AVAILABLE_DATASETS = [Dataset.wikiart, Dataset.semart, Dataset.ipiranga]


def get_qdrant_client():
    """Initialize Qdrant client with retries and host fallback"""
    global _qdrant_client
    
    if _qdrant_client is None:
        for attempt in range(3): 
            try:
                print(f"Attempting to connect to Qdrant at qdrant:6333 (attempt {attempt + 1})")
                _qdrant_client = QdrantClient(host="qdrant", port=6333)
            except Exception as e:
                print(f"❌ Failed to connect to qdrant:6333 (attempt {attempt + 1}): {e}")
                time.sleep(1)
        
        raise ConnectionError("Failed to connect to Qdrant after 3 attempts")
    return _qdrant_client

def get_available_collections():
    collections = get_qdrant_client().get_collections()
    available_collections = [c.name for c in collections.collections]
    return available_collections


def search_similar_vectors(text: str, dataset: Dataset, k: int = 3) -> list:
    if dataset not in AVAILABLE_DATASETS:
        raise ValueError(f"Dataset {dataset} not available. Available: {AVAILABLE_DATASETS}")
    
    query_embedding = get_embedding(text)
    
    collection_name = dataset.value
    
    if collection_name not in available_collections:
        raise ValueError(f"Collection {collection_name} not found in Qdrant")
    
    try:
        search_results = get_qdrant_client().search(
            collection_name=collection_name,
            query_vector=query_embedding[0].tolist(),
            limit=k,
            with_payload=True
        )
        return search_results
    except Exception as e:
        print(f"❌ Error searching Qdrant collection {collection_name}: {e}")
        return []

def search_similar_vectors_batch(texts: list[str], dataset: Dataset, k: int = 3) -> list:
    """
    Search for similar vectors for multiple texts
    
    Returns:
        List of search results for each text
    """
    results = []
    for text in texts:
        results.append(search_similar_vectors(text, dataset, k))
    return results