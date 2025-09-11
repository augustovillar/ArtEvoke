import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import re
import pickle
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

SAVE_DIR = os.path.join(SCRIPT_DIR, "test_text_seg/")
os.makedirs(SAVE_DIR, exist_ok=True)

DATA_PATH = os.path.join(SCRIPT_DIR, "..", "..", "descriptions", "output_merged_semart.csv")

DATA_DIR = os.path.join(SCRIPT_DIR, "..", "..", "..", "data", "SemArt")
IMAGE_DIR = os.path.join(DATA_DIR, "Images")

story = """
I remember arriving in a small village by train while it was raining. The station was quiet, just a couple of people waiting, and a bike leaning against the wall. I had a small bag with me and a letter in my pocket with an address. A dog was sleeping under the bench, and the only sound was the soft hum of the engine as the train pulled away.

Instead of going straight to the house, I took a walk through the village. The streets were narrow and made of stones. I passed a small shop with flowers in front, and a boy kicking a ball by himself. There was a little church with a bell that rang as I walked by. Everything felt calm, like time moved slower there.

When I got to the house, no one was home yet. I sat on the front step and opened the envelope I had brought. Inside was a postcard from my girlfriend at the time. She was smiling in the photo, standing in a wide field with hills in the background and flowers all around. On the back, she had written, 'Wish you were here. Enjoy your vacations in your uncle house.'
"""

model = SentenceTransformer("thenlper/gte-large", device="cuda:1")
res = faiss.StandardGpuResources()


def do_faiss_database():
    df = pd.read_csv(DATA_PATH)[["IMAGE_FILE", "description"]]
    df.columns = ["image_file", "generated_description"]
    descriptions = df["generated_description"].tolist()
    image_files = df["image_file"].tolist()

    print("Generating embeddings...")
    db_embeddings = model.encode(descriptions, convert_to_numpy=True, normalize_embeddings=True)

    with open(os.path.join(SAVE_DIR, "image_files.pkl"), "wb") as f:
        pickle.dump(image_files, f)

    print("Creating and saving FAISS CPU index...")
    cpu_index = faiss.IndexFlatIP(db_embeddings.shape[1])
    cpu_index.add(db_embeddings)
    faiss.write_index(cpu_index, os.path.join(SAVE_DIR, "index_flatip.faiss"))

def load_faiss_database(use_gpu=True):
    with open(os.path.join(SAVE_DIR, "image_files.pkl"), "rb") as f:
        image_files = pickle.load(f)
    cpu_index = faiss.read_index(os.path.join(SAVE_DIR, "index_flatip.faiss"))

    if use_gpu:
        index = faiss.index_cpu_to_gpu(res, 1, cpu_index)
    else:
        index = cpu_index

    return index, image_files

def split_into_sentences(text):
    pattern = r'(?<=[.!?])\s+(?=[A-Z])'
    return re.split(pattern, text.strip())


def save_results(name, segments, retrieved_paths, image_base_path="SemArt/Images/"):
    method_dir = os.path.join(SCRIPT_DIR, "retrieved_results", name)
    os.makedirs(method_dir, exist_ok=True)

    try:
        font = ImageFont.truetype("DejaVuSans.ttf", size=18)
    except:
        font = ImageFont.load_default()

    for i, (segment, img_file) in enumerate(zip(segments, retrieved_paths)):
        img_path = os.path.join(IMAGE_DIR, img_file)
        save_path = os.path.join(method_dir, f"{i:02d}_image.jpg")
        save_path_with_text = os.path.join(method_dir, f"{i:02d}_image_with_text.jpg")

        if os.path.exists(img_path):
            try:
                img = Image.open(img_path).convert("RGB")
                img.save(save_path)
                draw = ImageDraw.Draw(img)

                w, h = img.size
                strip_height = 50
                new_img = Image.new("RGB", (w, h + strip_height), "black")
                new_img.paste(img, (0, 0))

                draw = ImageDraw.Draw(new_img)
                text = segment[:200] + ("..." if len(segment) > 200 else "")
                draw.text((10, h + 10), text, fill="white", font=font)

                new_img.save(save_path_with_text)
            except Exception as e:
                print(f"Error processing image {img_file}: {e}")
        else:
            print(f"Image not found: {img_path}")

if __name__ == "__main__":
    if not os.path.exists(os.path.join(SAVE_DIR, "index_flatip.faiss")):
        do_faiss_database()
    index, image_files = load_faiss_database()

    paragraphs = [p.strip() for p in story.split('\n') if p.strip()]
    sentences = split_into_sentences(story)

    def get_segments(sentences, size, step=None):
        if step is None:
            step = 1 if size > 1 else size
        return [
            " ".join(sentences[i:i+size])
            for i in range(0, len(sentences) - size + 1, step)
        ]

    segmentation_strategies = {
        "paragraph": paragraphs,
        "1sent_nonoverlap": get_segments(sentences, 1, step=1),
        "2sent_nonoverlap": get_segments(sentences, 2, step=2),
        "3sent_nonoverlap": get_segments(sentences, 3, step=3),
        "2sent_step1_overlap": get_segments(sentences, 2, step=1),
        "3sent_step1_overlap": get_segments(sentences, 3, step=1),
        "3sent_step2_overlap": get_segments(sentences, 3, step=2),
    }


    results = {}

    for name, segments in segmentation_strategies.items():
        print(f"Processing: {name}")
        segment_embeddings = model.encode(segments, convert_to_numpy=True, normalize_embeddings=True)
        D, I = index.search(segment_embeddings, k=1)

        retrieved = [image_files[i[0]] for i in I]
        similarities = [d[0] for d in D]

        results[name] = {
            "retrieved_images": retrieved,
            "cosine_similarities": similarities,
            "total_retrieved": len(retrieved),
            "diversity_score": len(set(retrieved)),
            "average_similarity": np.mean(similarities),
        }

        save_results(name=name, segments=segments, retrieved_paths=retrieved)

    for key, value in results.items():
        print(f"\nStrategy: {key}")
        print(f"  Total Retrieved: {value['total_retrieved']}")
        print(f"  Avg. Cosine Similarity: {value['average_similarity']:.4f}")
        print(f"  Diversity (unique images): {value['diversity_score']}")
