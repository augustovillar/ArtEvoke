import os
import time
import torch
import faiss
import random
import pickle
import open_clip
import numpy as np
import pandas as pd
from PIL import Image
from sentence_transformers import SentenceTransformer

# Set Recall@K values
K_values = [1, 3, 6, 10]

# Directory and files
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FAISS_DIR = os.path.join(SCRIPT_DIR, "FAISS")

# Directory of the images
DATA_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "SemArt"
)
IMAGE_DIR = os.path.join(DATA_DIR, "Images")

# LMMs results file
DESCRIPTION_FILE = os.path.join(SCRIPT_DIR, "..", "LMMs", "qwen", "qwen_output2000.csv")

# Model name
model_name = "Qwen2_5_7B_512"

# Embeddings models names:
model_names = {
    "bge-large-en-v1.5": "BAAI/bge-large-en-v1.5",
    "MiniLM-L6-v2": "sentence-transformers/all-MiniLM-L6-v2",
    "gte-large": "thenlper/gte-large",
    "e5-large-v2": "intfloat/e5-large-v2",
    "Qwen3 0.6B": "Qwen/Qwen3-Embedding-0.6B",
    "Qwen3 4B": "Qwen/Qwen3-Embedding-4B",
    "ViT-G/14": ("ViT-g-14", "laion2b_s34b_b88k"),
    "ViT-H-14-378-quickgelu (DFN)": ("ViT-H-14-378-quickgelu", "dfn5b"),
    "ConvNeXt-Large_320px": ("convnext_large_d_320", "laion2b_s29b_b131k_ft_soup"),
    "ConvNeXt-XXLarge": ("convnext_xxlarge", "laion2b_s34b_b82k_augreg_soup"),
}

print_results_of = {
    "project_assets/data/SemArt/Images/15281-111geric.jpg": 254,
    "project_assets/data/SemArt/Images/06684-village.jpg": 1,
    "project_assets/data/SemArt/Images/28363-1market.jpg": 49,
}


def load_your_descriptions():
    df = pd.read_csv(DESCRIPTION_FILE)
    df = df[["IMAGE_FILE", "DESCRIPTION", "description_" + model_name]]
    df = df.rename(
        columns={
            "IMAGE_FILE": "image_file",
            "DESCRIPTION": "original_description",
            "description_" + model_name: "generated_description",
        }
    )

    return df


def load_embedding_model(name):
    device = torch.device("cuda:1" if torch.cuda.is_available() else "cpu")

    if name in [
        "ViT-G/14",
        "ViT-H-14-378-quickgelu (DFN)",
        "ConvNeXt-XXLarge",
        "ConvNeXt-Large_320px",
    ]:
        model_name, pretrained = model_names[name]
        model, _, transform = open_clip.create_model_and_transforms(
            model_name, pretrained=pretrained
        )
        tokenizer = open_clip.get_tokenizer(model_name)

        class OpenCLIPWrapper:
            def __init__(self, model, tokenizer, transform, device):
                self.model = model.to(device)
                self.tokenizer = tokenizer
                self.transform = transform
                self.device = device

            def encode(self, texts, normalize_embeddings=True):
                with torch.no_grad():
                    tokens = self.tokenizer(texts).to(self.device)
                    features = self.model.encode_text(tokens)
                    if normalize_embeddings:
                        features = features / features.norm(dim=-1, keepdim=True)
                    return features.cpu().numpy().astype("float32")

            def encode_images(
                self, image_paths, normalize_embeddings=True, batch_size=120
            ):
                all_embeddings = []
                with torch.no_grad():
                    for i in range(0, len(image_paths), batch_size):
                        batch_paths = image_paths[i : i + batch_size]
                        imgs = [
                            self.transform(Image.open(p).convert("RGB")).unsqueeze(0)
                            for p in batch_paths
                        ]
                        imgs = torch.cat(imgs).to(self.device)

                        features = self.model.encode_image(imgs)
                        if normalize_embeddings:
                            features = features / features.norm(dim=-1, keepdim=True)
                        all_embeddings.append(features.cpu())

                return torch.cat(all_embeddings).numpy().astype("float32")

        return OpenCLIPWrapper(model, tokenizer, transform, device)
    elif name in ["Qwen3 0.6B", "Qwen3 4B"]:
        return SentenceTransformer(
            model_names[name],
            model_kwargs={
                "attn_implementation": "flash_attention_2",
                "device_map": device,
                "dtype": torch.float16,
            },
            tokenizer_kwargs={"padding_side": "left"},
        )
    elif name in model_names:
        return SentenceTransformer(model_names[name])


def generate_embeddings(df, model, generate_faiss):
    print("Generating embeddings...")
    original_description = df["original_description"].tolist()
    generated_descriptions = df["generated_description"].tolist()
    df["IMAGE_FILE_FULLPATH"] = IMAGE_DIR + "/" + df["image_file"]
    image_paths = df["IMAGE_FILE_FULLPATH"].tolist()

    # Step 1: Get unnormalized embeddings
    original_emb = model.encode(original_description, normalize_embeddings=True)
    time2 = time.time()
    generated_embs = None
    if generate_faiss:
        generated_embs = model.encode(generated_descriptions, normalize_embeddings=True)
    time3 = time.time()

    image_emb = None
    image_emb_time = None
    if hasattr(model, "encode_images") and generate_faiss:
        image_emb = model.encode_images(image_paths, normalize_embeddings=True)
        image_emb_time = time.time() - time3

    generated_emb_time = time3 - time2

    print(
        f"Time taken to generate generated embeddings: {generated_emb_time:.2f} seconds"
    )
    if image_emb_time is not None:
        print(f"Time taken to generate image embeddings: {image_emb_time:.2f} seconds")

    return original_emb, generated_embs, image_emb


def create_faiss(model, generated_embs, image_embs, df, name, image_emb_together):
    os.makedirs(os.path.join(FAISS_DIR, "index"), exist_ok=True)
    os.makedirs(os.path.join(FAISS_DIR, "metadata"), exist_ok=True)

    name = name.replace("/", "_")
    image_paths = df["image_file"].tolist()

    text_metadata = [{"image_file": f, "tag": "text"} for f in image_paths]

    if image_emb_together and hasattr(model, "encode_images"):
        # Stack text and image embeddings
        combined_embs = np.vstack([image_embs, generated_embs]).astype("float32")
        image_metadata = [{"image_file": f, "tag": "img"} for f in image_paths]
        combined_metadata = text_metadata + image_metadata

        index = faiss.IndexFlatIP(combined_embs.shape[1])
        index.add(combined_embs)
        faiss.write_index(
            index, os.path.join(FAISS_DIR, f"index/combined_embeddings_{name}.index")
        )

        with open(
            os.path.join(FAISS_DIR, f"metadata/combined_embeddings_{name}.pkl"), "wb"
        ) as f:
            pickle.dump(combined_metadata, f)

    else:
        # Text-only index
        text_embs = generated_embs.astype("float32")
        index_text = faiss.IndexFlatIP(text_embs.shape[1])
        index_text.add(text_embs)
        faiss.write_index(
            index_text, os.path.join(FAISS_DIR, f"index/text_embeddings_{name}.index")
        )

        with open(
            os.path.join(FAISS_DIR, f"metadata/text_embeddings_{name}.pkl"), "wb"
        ) as f:
            pickle.dump(text_metadata, f)

        print(f"Text-only FAISS index created and saved for {name}.")
        if hasattr(model, "encode_images"):
            # Image-only index
            image_embs_f32 = image_embs.astype("float32")
            image_metadata = [{"image_file": f, "tag": "img"} for f in image_paths]
            index_img = faiss.IndexFlatIP(image_embs_f32.shape[1])
            index_img.add(image_embs_f32)
            faiss.write_index(
                index_img,
                os.path.join(FAISS_DIR, f"index/image_embeddings_{name}.index"),
            )

            with open(
                os.path.join(FAISS_DIR, f"metadata/image_embeddings_{name}.pkl"), "wb"
            ) as f:
                pickle.dump(image_metadata, f)


def compute_recall(I, k_values, metadata, df, verbose=False):
    recalls = {}
    tag_counter = {k: {"text": 0, "img": 0} for k in k_values}

    for k in k_values:
        correct = 0
        for i in range(len(I)):
            gt_file = df.iloc[i]["image_file"]
            for j in range(k):
                idx = I[i, j]
                retrieved = metadata[idx]
                if retrieved["image_file"] == gt_file:
                    correct += 1
                    tag = retrieved.get("tag", "unknown")
                    tag_counter[k][tag] += 1
                    if verbose:
                        print(f"✔️ Query {i} → Correct at rank {j+1}: {gt_file} [{tag}]")
                    break
        recalls[f"Recall@{k}"] = correct / len(I)

    print("\n📊 Correct retrievals by tag:")
    for k in k_values:
        print(
            f"Recall@{k}: Text = {tag_counter[k]['text']}, Image = {tag_counter[k]['img']}"
        )

    return recalls


def open_faiss(type, name):
    index = faiss.read_index(
        os.path.join(FAISS_DIR, f"index/{type}_embeddings_{name}.index")
    )
    with open(
        os.path.join(FAISS_DIR, f"metadata/{type}_embeddings_{name}.pkl"), "rb"
    ) as f:
        metadata = list(pickle.load(f))
    return index, metadata


def interleave_results_no_duplicates(
    I_text, D_text, metadata_text, I_img, D_img, metadata_img, k, original_emb_len
):
    combined_I, combined_D = [], []
    offset = len(metadata_text)

    for i in range(original_emb_len):
        ids, scores, seen = [], [], set()
        text_r = img_r = 0

        while len(ids) < k:
            is_image = random.random() < 0.5  # randomly choose modality at each step

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


def calculate_recall(
    model, name, original_emb, df, image_emb_together, force_text_only=False
):
    print(f"\n🔍 Evaluating model: {name}")
    name = name.replace("/", "_")

    if not hasattr(model, "encode_images") or force_text_only:
        index, metadata = open_faiss("text", name)
        D, I = index.search(original_emb, max(K_values))
        recalls = compute_recall(I, K_values, metadata, df)

        print("\nOriginal ➝ Generated (text-only index):")
        for k, v in recalls.items():
            print(f"{k}: {v:.3f}")

        combined_I, combined_D = I, D
        combined_metadata = metadata

    elif image_emb_together:
        index, metadata = open_faiss("combined", name)
        D, I = index.search(original_emb, max(K_values))
        recalls = compute_recall(I, K_values, metadata, df)

        print("\nOriginal ➝ Generated (combined index):")
        for k, v in recalls.items():
            print(f"{k}: {v:.3f}")

        combined_I, combined_D = I, D
        combined_metadata = metadata
    else:
        # Separate image and text indices
        index_text, metadata_text = open_faiss("text", name)
        index_img, metadata_img = open_faiss("image", name)

        D_text, I_text = index_text.search(original_emb, max(K_values))
        D_img, I_img = index_img.search(original_emb, max(K_values))

        combined_metadata = metadata_text + metadata_img
        combined_I, combined_D = interleave_results_no_duplicates(
            I_text,
            D_text,
            metadata_text,
            I_img,
            D_img,
            metadata_img,
            k=max(K_values),
            original_emb_len=len(original_emb),
        )

        recalls = compute_recall(combined_I, K_values, combined_metadata, df)

        print("\nOriginal ➝ Generated (interleaved image + text index):")
        for k, v in recalls.items():
            print(f"{k}: {v:.3f}")

    # Sample output
    indices = list(print_results_of.values())
    print("\n📌 Sample top-k metadata for selected queries:")
    for i in indices:
        print(f"\nQuery {i}:")
        print(f"Description: {df.iloc[i]['original_description']}")
        print(
            f"Ground truth image: {df.iloc[i]['image_file'].replace(
                "test_LMMs/SemArt_sample2000/", "project_assets/data/SemArt/Images/"
            )}"
        )
        for rank in range(min(10, len(combined_I[i]))):
            idx = combined_I[i][rank]
            retrieved_item = combined_metadata[idx]
            retrieved_image = retrieved_item["image_file"].replace(
                "test_LMMs/SemArt_sample2000/", "project_assets/data/SemArt/Images/"
            )
            tag = retrieved_item.get("tag", "N/A")
            ground_truth_image = df.iloc[i]["image_file"].replace(
                "test_LMMs/SemArt_sample2000/", "project_assets/data/SemArt/Images/"
            )
            mark = "✅" if retrieved_image == ground_truth_image else "❌"
            print(
                f"  Rank {rank+1}: {retrieved_image} [{tag}] (Score: {combined_D[i][rank]:.4f}) {mark}"
            )


if __name__ == "__main__":
    df = load_your_descriptions()

    for name, _ in model_names.items():
        print(f"\n🔍 Processing with {name}")
        image_emb_together = False
        generate_faiss = True
        model = load_embedding_model(name)
        original_emb, generated_embs, image_emb = generate_embeddings(
            df, model, generate_faiss
        )

        if generate_faiss:
            create_faiss(model, generated_embs, image_emb, df, name, image_emb_together)

        # Calculate recall of the unique vector database
        calculate_recall(model, name, original_emb, df, False)

        if hasattr(model, "encode_images"):
            # forces text-only index
            calculate_recall(model, name, original_emb, df, False, True)
            # uses image and text separately
            calculate_recall(model, name, original_emb, df, True)

        torch.cuda.empty_cache()
