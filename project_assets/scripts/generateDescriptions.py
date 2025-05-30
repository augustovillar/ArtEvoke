import os
import sys
import torch
import pandas as pd
import random
import multiprocessing as mp
from tqdm import tqdm
from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info
import json

random.seed(42)

# Global settings
MODEL_NAME = "Qwen/Qwen2.5-VL-7B-Instruct"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_PATH = os.path.join(SCRIPT_DIR, "..", "data")

DESCRIPTION_PATH = os.path.join(SCRIPT_DIR,  "outputs", "descriptions")

MUESUEM_DATA_PATH = "/DATA/public/siamese/dataset_mrbab/art-foto"

MAX_PIXELS = 512 * 512
DESC_COL_BASE = "description_Qwen2_5"


BASE_QUERY = """Task: Describe the visual content of the following artwork in detail.
Your description should focus only on what is visible in the image — such as people, objects, colors, emotions, actions, setting, and atmosphere.
Do not include the title, artist, art movement, or historical context.

Example of a good description:
“The lunette on the back wall of the loggia depicts a colorful fruit and vegetable market. The scene is split in two: women run their stalls beneath a tall arcade supported by a striking red pillar. Besides produce, other goods hang from a molding along the back wall.”

Now, describe the current image following the same style.
Be accurate, descriptive, and grounded in what can be seen.

{subject_hint}
"""

def build_prompt(dataset, info):
    if dataset == "semart":
        if info:
            return BASE_QUERY.format(subject_hint="\n\nYou may consider the following information:\n" + info)
    elif dataset == "wikiart":
        if info:
            return BASE_QUERY.format(subject_hint="\n\nYou may consider the following terms as visual hints:\n" + info)
    elif dataset == "museum":
        if isinstance(info, dict) and any(info.values()):
            hint = "; ".join(f"{k}: {v}" for k, v in info.items() if v)
            return BASE_QUERY.format(subject_hint="\n\nYou may consider the following terms as visual hints:\n" + hint)
    return BASE_QUERY.format(subject_hint="")

def load_data(dataset):
    if dataset == "semart":
        path = os.path.join(DATA_PATH, "SemArt", "semart_info", "SemArt15000.csv")
        df = pd.read_csv(path)
        return df.to_dict(orient="records")
    elif dataset == "wikiart":
        path = os.path.join(DATA_PATH, "WikiArt", "WikiArt15000.csv")
        df = pd.read_csv(path)
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)
        return df.to_dict(orient="records")
    elif dataset == "museum":
        path = os.path.join(DATA_PATH, "Museum", "input_data_museum.json")
        with open(path, "r", encoding="utf-8") as f:
            return list(json.load(f).values())
    else:
        raise ValueError("Unknown dataset")

SEMART_PATH = os.path.join(DATA_PATH, "SemArt", "Images")
WIKI_PATH = os.path.join(DATA_PATH, "WikiArt",  "Images")

def get_image_path(dataset, row):
    if dataset == "semart":
        return os.path.join(SEMART_PATH, row.get("IMAGE_FILE", ""))
    elif dataset == "wikiart":
        return os.path.join(WIKI_PATH, row.get("filename", ""))
    elif dataset == "museum":
        return row.get("imageLinkHigh", "")
    return ""

def get_info(dataset, row):
    if dataset == "semart":
        return row.get("DESCRIPTION", "")
    elif dataset == "wikiart":
        return row.get("description", "")
    elif dataset == "museum":
        return row.get("subjectMatter", "")
    return ""

def process_partition(dataset, data_items, gpu_id, output_file, desc_col_base):
    torch.cuda.set_device(gpu_id)
    desc_col = f"{desc_col_base}_gpu{gpu_id}"

    if os.path.exists(output_file):
        df_saved = pd.read_csv(output_file)
        df_saved[desc_col] = df_saved[desc_col].astype("string")
        print(f"[GPU {gpu_id}] Resuming from {output_file} with {df_saved[desc_col].notna().sum()} done")
    else:
        df_saved = pd.DataFrame(data_items)
        df_saved[desc_col] = pd.NA

    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(MODEL_NAME, torch_dtype=torch.bfloat16, device_map={"" : f"cuda:{gpu_id}"})
    processor = AutoProcessor.from_pretrained(MODEL_NAME)

    for idx, row in tqdm(df_saved.iterrows(), total=len(df_saved), desc=f"GPU {gpu_id}", position=gpu_id):
        desc_val = row.get(desc_col)

        if pd.notna(desc_val):
            continue

        image_path = get_image_path(dataset, row)
        if not os.path.exists(image_path):
            df_saved.at[idx, desc_col] = "Image not found"
            continue

        try:
            prompt = build_prompt(dataset, get_info(dataset, row))

            messages = [{
                "role": "user", "content": [
                    {"type": "image", "image": image_path, "max_pixels": MAX_PIXELS},
                    {"type": "text", "text": prompt},
            ],}]

            text = processor.apply_chat_template(messages, add_generation_prompt=True)
            image_inputs, _ = process_vision_info(messages)
            inputs = processor(text=[text], images=image_inputs, padding=True, return_tensors="pt").to(f"cuda:{gpu_id}")

            output_ids = model.generate(**inputs, max_new_tokens=1000)
            output_text = processor.batch_decode(output_ids, skip_special_tokens=True)[0]

            if "assistant" in output_text.lower():
                parts = output_text.rsplit("assistant", 1)
                description = parts[-1].strip(": \n")
            else:
                description = output_text.strip()

            df_saved.at[idx, desc_col] = description.replace("\n", " ")
            df_saved.to_csv(output_file, index=False)

        except Exception as e:
            df_saved.at[idx, desc_col] = f"Error: {str(e)}"
            df_saved.to_csv(output_file, index=False)
            continue

if __name__ == "__main__":
    dataset = sys.argv[1]  # "semart", "wikiart", or "museum"
    valid_datasets = {"semart", "wikiart", "museum"}
    if dataset not in valid_datasets:
        print(f"❌ Invalid dataset '{dataset}'. Choose one of: {', '.join(valid_datasets)}.")
        sys.exit(1)

    desc_col_base = f"description_Qwen2_5_{dataset}"
    output0 = os.path.join(DESCRIPTION_PATH, f"{dataset}_output_gpu0.csv")
    output1 = os.path.join(DESCRIPTION_PATH, f"{dataset}_output_gpu1.csv")
    output_merged = os.path.join(DESCRIPTION_PATH, f"output_merged_{dataset}.csv")

    records = load_data(dataset)

    records = records[:10]

    mid = len(records) // 2
    part0, part1 = records[:mid], records[mid:]

    p0 = mp.Process(target=process_partition, args=(dataset, part0, 0, output0, desc_col_base))
    p1 = mp.Process(target=process_partition, args=(dataset, part1, 1, output1, desc_col_base))

    p0.start()
    p1.start()
    p0.join()
    p1.join()

    df0 = pd.read_csv(output0)
    df1 = pd.read_csv(output1)

    df0 = df0.rename(columns={f"{desc_col_base}_gpu0": "description"})
    df1 = df1.rename(columns={f"{desc_col_base}_gpu1": "description"})

    merged_df = pd.concat([df0, df1], ignore_index=True)
    merged_df.to_csv(output_merged, index=False)
    print(f"✅ Merged output saved to {output_merged}")