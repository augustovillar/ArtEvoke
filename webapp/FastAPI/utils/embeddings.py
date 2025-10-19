import faiss
import pickle
import torch
import numpy as np
from sentence_transformers import SentenceTransformer
import sqlite3

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load the model **once** at startup
print("Loading embedding model...")
embedding_model = SentenceTransformer(
    "Qwen/Qwen3-Embedding-4B",
    model_kwargs={
        "attn_implementation": "sdpa",
        "device_map": device,
        "dtype": torch.float16,
    },
    tokenizer_kwargs={"padding_side": "left"},
)

# Load FAISS index and metadata once
print("Loading FAISS index and metadata...")
wikiIndexImages = faiss.read_index("/app/data/embeddings/index/wikiart_index.faiss")
with open("/app/data/embeddings/metadata/wikiart_metadata.pkl", "rb") as f:
    wikiMetadataImages = pickle.load(f)

semArtIndexImages = faiss.read_index("/app/data/embeddings/index/semart_index.faiss")
with open("/app/data/embeddings/metadata/semart_metadata.pkl", "rb") as f:
    semArtMetadataImages = pickle.load(f)

ipirangaIndexImages = faiss.read_index(
    "/app/data/embeddings/index/ipiranga_index.faiss"
)
with open("/app/data/embeddings/metadata/ipiranga_metadata.pkl", "rb") as f:
    ipirangaMetadataImages = pickle.load(f)

print("FAISS index and metadata loaded successfully!")

# Connect to ipiranga database
ipiranga_conn = sqlite3.connect("/app/data/db/ipiranga.db")

index_by_dataset = {
    "wikiart": wikiIndexImages,
    "semart": semArtIndexImages,
    "ipiranga": ipirangaIndexImages,
}

metadata_by_dataset = {
    "wikiart": wikiMetadataImages,
    "semart": semArtMetadataImages,
    "ipiranga": ipirangaMetadataImages,
}

filename_columns = {"wikiart": "file_name", "semart": "file_name", "ipiranga": None}

art_name_columns = {"wikiart": "file_name", "semart": "title", "ipiranga": None}


def get_gte_embedding(text):
    embedding = embedding_model.encode([text], convert_to_numpy=True)
    embedding = embedding / np.linalg.norm(
        embedding, axis=1, keepdims=True
    )  # Normalize
    return embedding.astype("float32")


def get_top_k_images_from_text(text, dataset, k=3):
    query_embedding = get_gte_embedding(text)

    indexImages = index_by_dataset[dataset]
    metadataImages = metadata_by_dataset[dataset]
    filename = filename_columns[dataset]
    name = art_name_columns[dataset]

    _, indices = indexImages.search(query_embedding, k)
    images = []
    for idx in indices[0]:
        if dataset == "ipiranga":
            # Query the database for ipiranga
            cursor = ipiranga_conn.cursor()
            cursor.execute(
                "SELECT document, title FROM ipiranga_entries LIMIT 1 OFFSET ?",
                (int(idx),),
            )
            row = cursor.fetchone()
            if row:
                image_url = (
                    "https://acervoonline.mp.usp.br/wp-content/uploads/tainacan-items"
                    + row[0]
                )
                image_name = row[1]
                url = image_url  # Use full URL for ipiranga
            else:
                continue
        else:
            if idx < len(metadataImages):
                image_url = metadataImages.iloc[idx][filename]
                image_name = metadataImages.iloc[idx][name]
                url = f"/art-images/{dataset}/{image_url}"
            else:
                continue
        images.append(
            {
                "image_url": url,
                "art_name": image_name,
            }
        )
    return images
