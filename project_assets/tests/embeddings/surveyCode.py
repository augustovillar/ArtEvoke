import os
import random
import numpy as np
import pandas as pd
from PIL import Image
from testEmbeddings import load_embedding_model, interleave_results_no_duplicates, open_faiss


random.seed(42)
np.random.seed(42)

# Directory and files
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

FAISS_DIR = os.path.join(SCRIPT_DIR, "FAISS")
IMAGE_DIR = os.path.join(SCRIPT_DIR, "..", "..", "data", "SemArt", "Images") 
OUTPUT_BASE = os.path.join(SCRIPT_DIR, "images")


# Embedding model names
model_1 = "gte-large"
model_2 = "ConvNeXt-Large_320px"

# Descriptive phrases
phrases = [
    "A grand mansion stands by the water, filled with lights and music, as elegantly dressed guests arrive under the moonlight.",
    "At its highest point, a great castle looms over the rooftops, as the king's procession winds through streets lined with watchful citizens.",
    "On a hillside, peasants gather in quiet clusters, their tools resting beside them as guards ride past toward the distant walls.",
    "A dusty path approaches a village, where chickens scatter and children pause their play to watch him pass.",
    "A wide rye field stretches toward the edge of a cliff, as children run through the grass while a figure watches over them from a distance.",
    "A firefighter stands before a wall of burning books, the orange glow lighting up his soot-covered face as ash rains down in a quiet suburban street.",
]

def interleave_results_no_duplicates(I_text, D_text, metadata_text, I_img, D_img, metadata_img, k, original_emb_len):
    combined_I, combined_D = [], []
    offset = len(metadata_text)

    for i in range(original_emb_len):
        ids, scores, seen = [], [], set()
        text_r = img_r = 0

        while len(ids) < k:
            is_image = random.random() < 0.5 

            if is_image and img_r < len(I_img[i]):
                idx = I_img[i][img_r]
                file = metadata_img[idx]["image_file"]
                if file not in seen:
                    ids.append(idx + offset)
                    scores.append(D_img[i][img_r])
                    seen.add(file)
                img_r += 1
            elif not is_image and text_r < len(I_text[i]):
                idx = I_text[i][text_r]
                file = metadata_text[idx]["image_file"]
                if file not in seen:
                    ids.append(idx)
                    scores.append(D_text[i][text_r])
                    seen.add(file)
                text_r += 1
            else:
                # If chosen modality is exhausted, fall back to the other
                if img_r < len(I_img[i]):
                    idx = I_img[i][img_r]
                    file = metadata_img[idx]["image_file"]
                    if file not in seen:
                        ids.append(idx + offset)
                        scores.append(D_img[i][img_r])
                        seen.add(file)
                    img_r += 1
                elif text_r < len(I_text[i]):
                    idx = I_text[i][text_r]
                    file = metadata_text[idx]["image_file"]
                    if file not in seen:
                        ids.append(idx)
                        scores.append(D_text[i][text_r])
                        seen.add(file)
                    text_r += 1
                else:
                    break  # both modalities exhausted

        combined_I.append(ids)
        combined_D.append(scores)

    return np.array(combined_I), np.array(combined_D)

def search_text_model(embeddings, model_name):
    index_text, metadata_text = open_faiss("text", model_name)

    D_text, I_text = index_text.search(embeddings, 5)

    return D_text, I_text, metadata_text

def search_text_and_iamge_model(embeddings, model_name):
    index_text, metadata_text = open_faiss("text", model_name)
    index_img, metadata_img = open_faiss("image", model_name)

    D_text, I_text = index_text.search(embeddings, 5)
    D_img, I_img = index_img.search(embeddings, 5)

    combined_metadata = metadata_text + metadata_img
    combined_I, combined_D = interleave_results_no_duplicates(
        I_text, D_text, metadata_text,
        I_img, D_img, metadata_img,
        k=5,
        original_emb_len=len(embeddings)
    )

    return combined_D, combined_I, combined_metadata

def save_image_pair(phrase_idx, comparison_idx, comparison_type, img1_path, img2_path, rank1, rank2, flip_order):
    phrase_folder = os.path.join(OUTPUT_BASE, f"phrase{phrase_idx+1}")
    os.makedirs(phrase_folder, exist_ok=True)

    # Open and resize images
    img1_path = os.path.join(IMAGE_DIR, os.path.basename(img1_path))
    img2_path = os.path.join(IMAGE_DIR, os.path.basename(img2_path))

    img1 = Image.open(img1_path).convert("RGB")
    img2 = Image.open(img2_path).convert("RGB")

    target_height = min(img1.height, img2.height)
    img1 = img1.resize((int(img1.width * target_height / img1.height), target_height))
    img2 = img2.resize((int(img2.width * target_height / img2.height), target_height))

    # Flip image order if requested
    if flip_order:
        img1, img2 = img2, img1
        rank1, rank2 = rank2, rank1
        model_left, model_right = "model_2", "model_1"
    else:
        model_left, model_right = "model_1", "model_2"

    combined_width = img1.width + img2.width
    combined_img = Image.new("RGB", (combined_width, target_height))
    combined_img.paste(img1, (0, 0))
    combined_img.paste(img2, (img1.width, 0))

    filename = f"{comparison_idx+1}_{comparison_type.replace(' ', '_')}_ranks_{rank1+1}_{rank2+1}.jpg"
    full_path = os.path.join(phrase_folder, filename)
    combined_img.save(full_path)

    return filename, model_left, model_right


if __name__ == "__main__":
    gte_large = load_embedding_model(model_1)
    conv1Next = load_embedding_model(model_2)

    phrases_gte = gte_large.encode(phrases)
    phrases_conv1Next = conv1Next.encode(phrases)

    D1, I1, meta1 = search_text_model(phrases_gte, model_1)
    D2, I2, meta2 = search_text_and_iamge_model(phrases_conv1Next, model_2)

    # Build results: 3 comparisons per phrase
    results = []
    for i, phrase in enumerate(phrases):
        results.append({
            "phrase": phrase,
            "comparison_type": "Top 1 vs Top 1",
            "model_1_image": meta1[I1[i][0]]["image_file"],
            "model_2_image": meta2[I2[i][0]]["image_file"]
        })
        # Get top-5 without duplicates for model 1
        top5_model1 = list(I1[i])
        top5_model2 = list(I2[i])

        used1 = {I1[i][0]}
        used2 = {I2[i][0]}

        for j in range(4):
            rand1 = next(idx for idx in top5_model1[1:] if idx not in used1)
            rand2 = next(idx for idx in top5_model2[1:] if idx not in used2)
            used1.add(rand1)
            used2.add(rand2)

            results.append({
                "phrase": phrase,
                "comparison_type": f"Random Top-5 Sample {j+1}",
                "model_1_image": meta1[rand1]["image_file"],
                "model_2_image": meta2[rand2]["image_file"]
            })

    organized_info = []
    for i, phrase in enumerate(phrases):
        for j in range(5):
            base_idx = i * 5 + j
            comp = results[base_idx]
            m1_path = comp["model_1_image"]
            m2_path = comp["model_2_image"]
            comp_type = comp["comparison_type"]
            
            m1_rank = list(I1[i]).index(next(idx for idx in I1[i] if meta1[idx]["image_file"] == m1_path))
            m2_rank = list(I2[i]).index(next(idx for idx in I2[i] if meta2[idx]["image_file"] == m2_path))
            
            flip = random.random() < 0.5
            new_img_combined, model_left, model_right = save_image_pair(i, j, comp_type, m1_path, m2_path, m1_rank, m2_rank, flip)

            organized_info.append({
                "phrase": f"Phrase {i+1}",
                "comparison": comp_type,
                "combined_image": new_img_combined,
                "model_1_rank": m1_rank + 1,
                "model_2_rank": m2_rank + 1,
                "model_on_left": model_left,
                "model_on_right": model_right
            })


    organized_df = pd.DataFrame(organized_info)
    print(organized_df)