import numpy as np
from orm import CatalogItem
from api_types.common import Dataset
from clients import get_embedding_client, get_database_client, get_qdrant_client, encode_text

# Lazy client initialization
_embedding_model = None
_SessionLocal = None
_qdrant_client = None

def _get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = get_embedding_client()
    return _embedding_model

def _get_session_local():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = get_database_client()
    return _SessionLocal

def _get_qdrant_client():
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = get_qdrant_client()
    return _qdrant_client


# Available datasets/collections
available_datasets = [Dataset.wikiart, Dataset.semart, Dataset.ipiranga]

filename_columns = {Dataset.wikiart: "file_name", Dataset.semart: "file_name", Dataset.ipiranga: None}

art_name_columns = {Dataset.wikiart: "file_name", Dataset.semart: "file_name", Dataset.ipiranga: None}


def get_embedding(text):
    embedding = encode_text([text], convert_to_numpy=True)
    embedding = embedding / np.linalg.norm(
        embedding, axis=1, keepdims=True
    )  # Normalize
    return embedding.astype("float32")


def format_catalog_item_info(catalog_item: CatalogItem, include_full_metadata: bool = True):
    """
    Format CatalogItem into a standardized dictionary with image URL and metadata.
    
    Args:
        catalog_item: The CatalogItem ORM object to format
        include_full_metadata: If True, includes all available metadata. If False, only basic info.
    
    Returns:
        Dictionary with formatted image information, or None if catalog_item is invalid
    """
    if not catalog_item:
        return None
    
    artwork_data = None
    image_url = None
    art_name = None
    
    # Get source-specific data
    if catalog_item.source == Dataset.semart and catalog_item.semart:
        artwork_data = catalog_item.semart
        image_url = f"/art-images/semart/{artwork_data.image_file}"
        art_name = artwork_data.title or "Untitled"
    elif catalog_item.source == Dataset.wikiart and catalog_item.wikiart:
        artwork_data = catalog_item.wikiart
        image_url = f"/art-images/wikiart/{artwork_data.image_file}"
        art_name = artwork_data.artist_name or "Unknown Artist"
    elif catalog_item.source == Dataset.ipiranga and catalog_item.ipiranga:
        artwork_data = catalog_item.ipiranga
        image_url = f"https://acervoonline.mp.usp.br/wp-content/uploads/tainacan-items{artwork_data.image_file}"
        art_name = artwork_data.title or "Untitled"
    
    if not image_url or not art_name:
        return None
    
    # Base information (always included)
    artwork_info = {
        "id": catalog_item.id,
        "image_url": image_url,
        "art_name": art_name,
        "source": catalog_item.source.value,
    }
    
    # Add full metadata if requested
    if include_full_metadata and artwork_data:
        artwork_info.update({
            "title": None,
            "artist": None,
            "year": None,
            "width": None,
            "height": None,
            "description": None,
            "technique": None
        })
        
        if catalog_item.source == Dataset.semart:
            artwork_info.update({
                "title": artwork_data.title,
                "artist": artwork_data.artist_name,
                "year": artwork_data.date,
                "description": artwork_data.description,
                "technique": artwork_data.technique,
                "type": artwork_data.type,
                "art_school": artwork_data.art_school
            })
        elif catalog_item.source == Dataset.wikiart:
            artwork_info.update({
                "artist": artwork_data.artist_name,
                "width": artwork_data.width,
                "height": artwork_data.height,
                "description": artwork_data.description,
                "type": artwork_data.type,
                "year": artwork_data.description.split("-")[-1] if artwork_data.description else None,
                "title": artwork_data.description.replace("-", " ") if artwork_data.description else None
            })
        elif catalog_item.source == Dataset.ipiranga:
            artwork_info.update({
                "title": artwork_data.title,
                "artist": artwork_data.artist_name,
                "year": artwork_data.date,
                "width": artwork_data.width,
                "height": artwork_data.height,
                "description": artwork_data.description,
                "technique": artwork_data.technique,
                "inventory_code": artwork_data.inventory_code,
                "location": artwork_data.location,
                "period": artwork_data.period,
                "color": artwork_data.color,
                "history": artwork_data.history
            })
    
    return artwork_info


def get_top_k_images_from_text(text: str, dataset: Dataset, k=3):
    """
    Search for top k similar images using Qdrant vector database and return CatalogItem information
    """
    if dataset not in available_datasets:
        raise ValueError(f"Dataset {dataset} not available. Available: {available_datasets}")
    
    # Get query embedding
    query_embedding = get_embedding(text)
    
    # Get collection name for Qdrant
    collection_name = dataset.value
    
    # Search in Qdrant with error handling
    try:
        search_results = _get_qdrant_client().search(
            collection_name=collection_name,
            query_vector=query_embedding[0].tolist(),  # Convert numpy array to list
            limit=k,
            with_payload=True
        )
    except Exception as e:
        print(f"❌ Error searching Qdrant collection {collection_name}: {e}")
        return []
    
    db = _get_session_local()()
    try:
        images = []
        for result in search_results:
            
            payload = result.payload
            
            # Get the artwork ID from the payload
            artwork_id = payload.get('id')
            if not artwork_id:
                continue
            
            # Query CatalogItem based on dataset and artwork ID
            catalog_item = None
            if dataset == Dataset.semart:
                catalog_item = db.query(CatalogItem).filter(
                    CatalogItem.semart_id == artwork_id,
                    CatalogItem.source == Dataset.semart
                ).first()
            elif dataset == Dataset.wikiart:
                catalog_item = db.query(CatalogItem).filter(
                    CatalogItem.wikiart_id == artwork_id,
                    CatalogItem.source == Dataset.wikiart
                ).first()
            elif dataset == Dataset.ipiranga:
                catalog_item = db.query(CatalogItem).filter(
                    CatalogItem.ipiranga_id == artwork_id,
                    CatalogItem.source == Dataset.ipiranga
                ).first()
            
            if not catalog_item:
                continue
            
            # Use the helper function to format the catalog item
            artwork_info = format_catalog_item_info(catalog_item, include_full_metadata=True)
            if artwork_info:
                images.append(artwork_info)
        
        return images
        
    finally:
        db.close()