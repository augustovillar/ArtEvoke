from fastapi import APIRouter, Depends
from routes import get_db, correct_grammer_and_translate, doTextSegmentation
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import torch
import numpy as np
import openai
import os
import logging
import sqlite3


router = APIRouter()
logger = logging.getLogger(__name__)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Maritaca AI client
client = openai.OpenAI(
    api_key=os.getenv("MARITACA_API_KEY"),
    base_url="https://chat.maritaca.ai/api",
)

# Load the model **once** at startup
print("Loading embedding model...")
embedding_model = SentenceTransformer("thenlper/gte-large")

# Load FAISS index and metadata once
print("Loading FAISS index and metadata...")
DATA_DIR = os.getenv("DATA_DIR", "/data") 

wiki_index_path = os.path.join(DATA_DIR, "embeddings", "index", "wikiart_index.faiss")
wiki_meta_path = os.path.join(DATA_DIR, "embeddings", "metadata", "wikiart_metadata.pkl")
semart_index_path = os.path.join(DATA_DIR, "embeddings", "index", "semart_index.faiss")
semart_meta_path = os.path.join(DATA_DIR, "embeddings", "metadata", "semart_metadata.pkl")
ipiranga_index_path = os.path.join(DATA_DIR, "embeddings", "index", "ipiranga_index.faiss")
ipiranga_meta_path = os.path.join(DATA_DIR, "embeddings", "metadata", "ipiranga_metadata.pkl")

wikiIndexImages = faiss.read_index(wiki_index_path)
with open(wiki_meta_path, "rb") as f:
    wikiMetadataImages = pickle.load(f)

semArtIndexImages = faiss.read_index(semart_index_path)
with open(semart_meta_path, "rb") as f:
    semArtMetadataImages = pickle.load(f)

ipirangaIndexImages = faiss.read_index(ipiranga_index_path)
with open(ipiranga_meta_path, "rb") as f:
    ipirangaMetadataImages = pickle.load(f)

print("FAISS index and metadata loaded successfully!")

# Connect to ipiranga database
ipiranga_db_path = os.path.join(DATA_DIR, "db", "ipiranga.db")
ipiranga_conn = sqlite3.connect(ipiranga_db_path)

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


@router.post("/search-images")
async def search_images(body: dict, db=Depends(get_db)):
    text = correct_grammer_and_translate(body["story"], body["language"])
    listArt = get_top_k_images_from_text(text, body["dataset"], k=6)

    return {"images": listArt}


@router.post("/select-images-per-section")
async def select_images_per_section(body: dict, db=Depends(get_db)):
    story = correct_grammer_and_translate(body["story"], body["language"])

    # Split the Story into Segments
    sections = doTextSegmentation(body["segmentation"], story)
    results = []

    for section in sections:
        section_images = get_top_k_images_from_text(
            section, body["dataset"], k=int(body["k"])
        )
        results.append({"section": section, "images": section_images})

    return {"sections": results}


@router.post("/generate-story")
async def generate_story(body: dict):
    data = body["selectedImagesByDataset"]

    cleaned_filenames_by_dataset = {}

    for key, urls in data.items():
        if key == "ipiranga":
            prefix = "https://acervoonline.mp.usp.br/wp-content/uploads/tainacan-items"
            cleaned_filenames_by_dataset[key] = [
                url.replace(prefix, "") for url in urls
            ]
        else:
            prefix = f"/art-images/{key}/"
            cleaned_filenames_by_dataset[key] = [
                url.replace(prefix, "") for url in urls
            ]

    art_descriptions = []

    for dataset, filenames in cleaned_filenames_by_dataset.items():
        if dataset == "ipiranga":
            cursor = ipiranga_conn.cursor()
            for name in filenames:
                cursor.execute(
                    "SELECT description FROM ipiranga_entries WHERE document = ?",
                    (name,),
                )
                row = cursor.fetchone()
                if row and row[0]:
                    art_descriptions.append(row[0])
                else:
                    print(
                        f"[Warning] No description found for {dataset} document: {name}"
                    )
        else:
            df = metadata_by_dataset[dataset]
            filename_col = filename_columns[dataset]

            for name in filenames:
                # Regular matching for wikiart and semart
                match = df.loc[df[filename_col] == name, "description"]
                if not match.empty:
                    art_descriptions.append(match.values[0])
                else:
                    print(
                        f"[Warning] No description found for {dataset} filename: {name}"
                    )

    base_prompt = (
        "Descriptions:\n" + "\n".join(f"- {desc}" for desc in art_descriptions) + "\n\n"
        "Write a story that takes inspiration on these scenes. Use 2–3 short paragraphs (approximately). "
        "Tell it like a simple, flowing story with a start, middle and an end. The paragraphs have to be conneced and follow a sequence of events."
    )

    messages = [{"role": "user", "content": base_prompt}]

    response = client.chat.completions.create(
        model="sabiazinho-3",
        messages=messages,
        max_tokens=1024,
        temperature=0.9,
    )

    story = response.choices[0].message.content.strip()

    return {"text": story}
