from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from routes import get_db, correct_grammer_and_translate, doTextSegmentation
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import torch
import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer
from PIL import Image
from io import BytesIO
import logging
import re
import os
import pandas

router = APIRouter()
logger = logging.getLogger(__name__)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

MODEL_NAME = "Qwen/Qwen3-1.7B"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME, torch_dtype="auto", device_map="cuda:0"
)

# Load the model **once** at startup
print("Loading embedding model...")
embedding_model = SentenceTransformer("thenlper/gte-large")

# Load FAISS index and metadata once
print("Loading FAISS index and metadata...")
wikiIndexImages = faiss.read_index("./embeddingsCLIP/index/wikiart_index.faiss")
with open("./embeddingsCLIP/metadata/wikiart_metadata.pkl", "rb") as f:
    wikiMetadataImages = pickle.load(f)

semArtIndexImages = faiss.read_index("./embeddingsCLIP/index/semart_index.faiss")
with open("./embeddingsCLIP/metadata/semart_metadata.pkl", "rb") as f:
    semArtMetadataImages = pickle.load(f)

museumIndexImages = faiss.read_index("./embeddingsCLIP/index/museum_index.faiss")
with open("./embeddingsCLIP/metadata/museum_metadata.pkl", "rb") as f:
    museumMetadataImages = pickle.load(f)
print("FAISS index and metadata loaded successfully!")

index_by_dataset = {
    "wikiart": wikiIndexImages,
    "semart": semArtIndexImages,
    "museum": museumIndexImages,
}

metadata_by_dataset = {
    "wikiart": wikiMetadataImages,
    "semart": semArtMetadataImages,
    "museum": museumMetadataImages
}

filename_columns = {
    "wikiart": "filename",
    "semart": "IMAGE_FILE",
    "museum": "imageLinkHigh"
}

art_name_columns = {
    "wikiart": "filename",
    "semart": "TITLE",
    "museum": "imageLinkHigh"
}

prefix_1 = "/DATA/public/siamese/dataset_mrbab/art-foto/mod/intranet/"
prefix_2 = "/DATA/public/siamese/dataset_mrbab/art-foto/old/intranet/"
prefix_3 = "/DATA/public/siamese/dataset_mrbab/art-foto/sculpt19/intranet/"

def get_gte_embedding(text):
    embedding = embedding_model.encode([text], convert_to_numpy=True)
    embedding = embedding / np.linalg.norm(embedding, axis=1, keepdims=True)  # Normalize
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
        if idx < len(metadataImages):
            image_url = (metadataImages.iloc[idx][filename]).removeprefix(prefix_1).removeprefix(prefix_2)
            image_name = (metadataImages.iloc[idx][name]).removeprefix(prefix_1).removeprefix(prefix_2)
            images.append({'image_url': f"/art-images/{dataset}/{image_url}", "art_name": image_name})
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
        section_images = get_top_k_images_from_text(section, body["dataset"], k=int(body['k']))
        results.append({"section": section, "images": section_images})

    return {"sections": results}

@router.post("/generate-story")
async def generate_story(body: dict):
    data = body["selectedImagesByDataset"]

    cleaned_filenames_by_dataset = {}

    for key, urls in data.items():
        prefix = f"/art-images/{key}/"
        cleaned_filenames_by_dataset[key] = [
            url.replace(prefix, '') for url in urls
        ]

    art_descriptions = []

    for dataset, filenames in cleaned_filenames_by_dataset.items():
        df = metadata_by_dataset[dataset]
        filename_col = filename_columns[dataset]

        for name in filenames:
            if dataset == 'museum':
                # Try first prefix
                full_name_1 = prefix_1 + name
                match = df.loc[df[filename_col] == full_name_1, 'description']

                # If no match, try second prefix
                if match.empty:
                    full_name_2 = prefix_2 + name
                    match = df.loc[df[filename_col] == full_name_2, 'description']

                if not match.empty:
                    art_descriptions.append(match.values[0])
                else:
                    print(f"[Warning] No description found for museum filename (tried both prefixes): {name}")

            else:
                # Regular matching for wikiart and semart
                match = df.loc[df[filename_col] == name, 'description']
                if not match.empty:
                    art_descriptions.append(match.values[0])
                else:
                    print(f"[Warning] No description found for {dataset} filename: {name}")

    base_prompt = (
        "Descriptions:\n"
        + "\n".join(f"- {desc}" for desc in art_descriptions)
        + "\n\n"
        "Write a story that takes inspiration on these scenes. Use 2–3 short paragraphs (approximately). "
        "Tell it like a simple, flowing story with a start, middle and an end. The paragraphs have to be conneced and follow a sequence of events."
    )

    messages = [{"role": "user", "content": base_prompt}]

    text = tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True, enable_thinking=False
            )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    generated_ids = model.generate(
                    **model_inputs,
                    max_new_tokens=1024,
                    do_sample=True,
                    temperature=0.9,
                )

    output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()
    story = tokenizer.decode(output_ids, skip_special_tokens=True).strip()

    return {"text": story}
