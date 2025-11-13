import os
import sys
import torch
import pandas as pd
import random
import multiprocessing as mp
from tqdm import tqdm
from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info

random.seed(42)

# Global settings
MODEL_NAME = "Qwen/Qwen2.5-VL-7B-Instruct"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Set local cache directory to avoid permission issues
LOCAL_CACHE_DIR = os.path.join(SCRIPT_DIR, ".cache", "huggingface")
os.makedirs(LOCAL_CACHE_DIR, exist_ok=True)
os.environ['HF_HOME'] = LOCAL_CACHE_DIR
os.environ['TRANSFORMERS_CACHE'] = LOCAL_CACHE_DIR
os.environ['HF_DATASETS_CACHE'] = LOCAL_CACHE_DIR

DATA_PATH = os.path.join(SCRIPT_DIR, "..", "data")

DESCRIPTION_PATH = os.path.join(SCRIPT_DIR, "outputs", "descriptions")

# Ensure output directories exist
os.makedirs(DESCRIPTION_PATH, exist_ok=True)

SQL_OUTPUT_PATH = os.path.join(SCRIPT_DIR, "outputs", "sql_inserts")

MUESUEM_DATA_PATH = "/DATA/public/siamese/dataset_mrbab/art-foto"

MAX_PIXELS = 512 * 512
DESC_COL_BASE = "description_Qwen2_5"


BASE_QUERY = """
Task: Describe the visual content of the following artwork in detail.
Your description should focus only on what is visible in the image — such as people, objects, colors, emotions, actions, setting, and atmosphere.
Do not include the title, artist, art movement, or historical context.

Style:
- Be accurate, descriptive, and grounded in what can be seen.
- Write in flowing prose, not bullet points.
- Avoid speculation unless it is strongly suggested by the visual elements.

Example of a good description:
“The lunette on the back wall of the loggia depicts a colorful fruit and vegetable market. The scene is split in two: women run their stalls beneath a tall arcade supported by a striking red pillar. Besides produce, other goods hang from a molding along the back wall.”

---

Additional Information (may vary across images, use only if useful to enrich the description):
The following information provides metadata fields about the image. Treat them as hints, but **do not override what is visibly seen**. If the metadata conflicts with what you see, prioritize the image.

{metadata}

---

Now, describe the current image following the style and rules above.
"""


def build_prompt(dataset, info):
    if not info:
        return BASE_QUERY.format(metadata="")

    if dataset == "semart":
        return BASE_QUERY.format(
            metadata="\n\nYou may consider the following information:\n" + info
        )
    elif dataset == "wikiart":
        return BASE_QUERY.format(
            metadata="\n\nYou may consider the following terms as visual hints:\n"
            + info
        )
    elif dataset == "ipiranga":
        return BASE_QUERY.format(
            metadata="\n\nYou may consider the following information:\n" + info
        )

    return BASE_QUERY.format(metadata="")


def load_data(dataset):
    if dataset == "semart":
        path = os.path.join(DATA_PATH, "SemArt", "SemArt.csv")
        df = pd.read_csv(path)
        return df.to_dict(orient="records")
    elif dataset == "wikiart":
        path = os.path.join(DATA_PATH, "WikiArt", "WikiArt.csv")
        df = pd.read_csv(path)
        return df.to_dict(orient="records")
    elif dataset == "ipiranga":
        path = os.path.join(DATA_PATH, "Ipiranga", "Ipiranga.csv")
        df = pd.read_csv(path)
        return df.to_dict(orient="records")
    else:
        raise ValueError("Unknown dataset")


SEMART_PATH = os.path.join(DATA_PATH, "SemArt", "Images")
WIKI_PATH = os.path.join(DATA_PATH, "WikiArt", "Images")


def get_image_path(dataset, row):
    if dataset == "semart":
        return os.path.join(SEMART_PATH, row.get("image_file", ""))
    elif dataset == "wikiart":
        return os.path.join(WIKI_PATH, row.get("image_file", ""))
    elif dataset == "ipiranga":
        image_file = row.get("image_file", "")
        if image_file:
            return (
                "https://acervoonline.mp.usp.br/wp-content/uploads/tainacan-items"
                + image_file
            )
        return ""
    return ""


def getValidInformationFromDb(row, exclude_cols=None) -> str:
    info_parts = []
    for col, val in row.items():
        if (
            col not in exclude_cols
            and pd.notna(val)
            and isinstance(val, str)
            and val.strip()
        ):
            info_parts.append(f"{col}: {val.strip()}")
    return "\n".join(info_parts)


def get_info(dataset, row) -> str:
    if dataset == "semart":
        # Include all fields except id, image_file, and description_generated
        return getValidInformationFromDb(
            row,
            [
                "id",
                "image_file",
                "description_generated",
            ],
        )
    elif dataset == "wikiart":
        # Include all fields except id, image_file, and description_generated
        return getValidInformationFromDb(
            row,
            [
                "id",
                "image_file",
                "description_generated",
                "width",
                "height",
            ],
        )
    elif dataset == "ipiranga":
        return getValidInformationFromDb(
            row,
            [
                "id",
                "external_id",
                "image_file",
                "inventory_code",
                "height",
                "width",
                "description_generated",
            ],
        )
    return ""


def escape_sql_string(value):
    """Escape single quotes and backslashes for SQL UPDATE statements"""
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return "NULL"
    if pd.isna(value):
        return "NULL"

    value = str(value)
    # Replace backslashes first, then single quotes
    value = value.replace("\\", "\\\\").replace("'", "''")
    # Remove newlines and normalize whitespace
    value = " ".join(value.split())
    return f"'{value}'"


def generate_update_sql(dataset, merged_csv):
    """Generate SQL UPDATE file for a specific dataset after descriptions are generated"""

    if not os.path.exists(merged_csv):
        print(f"❌ Merged CSV not found: {merged_csv}")
        return False

    df = pd.read_csv(merged_csv)

    if "id" not in df.columns or "description" not in df.columns:
        print("❌ CSV file missing required columns (id, description)")
        return False

    df_valid = df[df["description"].notna() & (df["description"] != "")]
    df_valid = df_valid[~df_valid["description"].str.startswith("Error:", na=False)]
    df_valid = df_valid[df_valid["description"] != "Image not found"]

    valid_rows = len(df_valid)

    if valid_rows == 0:
        print(f"❌ No valid descriptions found for {dataset}")
        return False

    table_name_map = {"ipiranga": "Ipiranga", "wikiart": "WikiArt", "semart": "SemArt"}

    table_name = table_name_map.get(dataset.lower())
    if not table_name:
        print(f"❌ Unknown dataset: {dataset}")
        return False

    output_sql = os.path.join(SQL_OUTPUT_PATH, f"C_{table_name}.sql")

    os.makedirs(SQL_OUTPUT_PATH, exist_ok=True)

    # Generate SQL UPDATE statements
    with open(output_sql, "w", encoding="utf-8") as f:
        batch_size = 100
        total_batches = (valid_rows + batch_size - 1) // batch_size

        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, valid_rows)
            batch = df_valid.iloc[start_idx:end_idx]

            f.write(f"-- Batch {batch_num + 1}/{total_batches}\n")

            for idx, row in batch.iterrows():
                row_id = str(row["id"])
                description = escape_sql_string(row["description"])

                f.write(
                    f"UPDATE {table_name} SET description_generated = {description} "
                    f"WHERE id = '{row_id}';\n"
                )

            f.write("\n")

        # Add verification query at the end
        f.write("-- Verification: Check how many descriptions were updated\n")
        f.write(
            f"SELECT COUNT(*) as updated_count FROM {table_name} WHERE description_generated IS NOT NULL;\n"
        )

    print(f"✅ SQL file generated: {output_sql}")
    print(f"   Total UPDATE statements: {valid_rows}")

    return True


def extract_first_style(type_str):
    """Extract the first style from a list-like string, e.g., "['Abstract Expressionism']" -> "Abstract Expressionism" """
    if pd.isna(type_str) or not isinstance(type_str, str):
        return ""
    try:
        # Remove brackets and quotes, split by comma, take first item
        cleaned = type_str.strip("[]").replace("'", "").replace('"', "")
        first_style = cleaned.split(",")[0].strip()
        return first_style
    except:
        return type_str


def process_partition(dataset, data_items, gpu_id, output_file, desc_col_base):
    torch.cuda.set_device(gpu_id)
    desc_col = f"{desc_col_base}_gpu{gpu_id}"

    if os.path.exists(output_file):
        df_saved = pd.read_csv(output_file)
        df_saved[desc_col] = df_saved[desc_col].astype("string")
        print(
            f"[GPU {gpu_id}] Resuming from {output_file} with {df_saved[desc_col].notna().sum()} done"
        )
    else:
        df_saved = pd.DataFrame(data_items)
        df_saved[desc_col] = pd.NA
        # For WikiArt, extract the first style from the type column and rename it
        if dataset == "wikiart" and "type" in df_saved.columns:
            df_saved["type"] = df_saved["type"].apply(extract_first_style)
        print(f"[GPU {gpu_id}] Starting fresh with {len(df_saved)} items")

    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        MODEL_NAME, 
        dtype=torch.bfloat16, 
        device_map={"": f"cuda:{gpu_id}"},
        cache_dir=LOCAL_CACHE_DIR
    )
    processor = AutoProcessor.from_pretrained(
        MODEL_NAME, 
        use_fast=True,
        cache_dir=LOCAL_CACHE_DIR
    )

    for idx, row in tqdm(
        df_saved.iterrows(), total=len(df_saved), desc=f"GPU {gpu_id}", position=gpu_id
    ):
        desc_val = row.get(desc_col)

        if pd.notna(desc_val):
            continue

        image = get_image_path(dataset, row)
        if not image.startswith("http") and not os.path.exists(image):
            df_saved.at[idx, desc_col] = "Image not found"
            continue

        try:
            prompt = build_prompt(dataset, get_info(dataset, row))

            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "image": image,
                            "max_pixels": MAX_PIXELS,
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ]

            text = processor.apply_chat_template(messages, add_generation_prompt=True)
            image_inputs, _ = process_vision_info(messages)
            inputs = processor(
                text=[text], images=image_inputs, padding=True, return_tensors="pt"
            ).to(f"cuda:{gpu_id}")

            output_ids = model.generate(**inputs, max_new_tokens=1000)
            output_text = processor.batch_decode(output_ids, skip_special_tokens=True)[
                0
            ]

            if "assistant" in output_text.lower():
                parts = output_text.rsplit("assistant", 1)
                description = parts[-1].strip(": \n")
            else:
                description = output_text.strip()

            df_saved.at[idx, desc_col] = description.replace("\n", " ")

            # Save intermediate results with relevant columns only
            if dataset == "ipiranga":
                df_temp = df_saved[["id", "inventory_code", "type", desc_col]]
            elif dataset == "semart":
                df_temp = df_saved[["id", "image_file", "type", desc_col]]
            elif dataset == "wikiart":
                df_temp = df_saved[["id", "image_file", "type", desc_col]]
            else:
                df_temp = df_saved
            df_temp.to_csv(output_file, index=False)

        except Exception as e:
            df_saved.at[idx, desc_col] = f"Error: {str(e)}"
            if dataset == "ipiranga":
                df_temp = df_saved[["id", "inventory_code", "type", desc_col]]
            elif dataset == "semart":
                df_temp = df_saved[["id", "image_file", "type", desc_col]]
            elif dataset == "wikiart":
                df_temp = df_saved[["id", "image_file", "type", desc_col]]
            else:
                df_temp = df_saved
            df_temp.to_csv(output_file, index=False)
            continue

    # Save final results with relevant columns only
    if dataset == "ipiranga":
        df_saved = df_saved[["id", "inventory_code", "type", desc_col]]
    elif dataset == "semart":
        df_saved = df_saved[["id", "image_file", "type", desc_col]]
    elif dataset == "wikiart":
        df_saved = df_saved[["id", "image_file", "type", desc_col]]
    df_saved.to_csv(output_file, index=False)


if __name__ == "__main__":
    # Set multiprocessing start method to 'spawn' for CUDA compatibility
    mp.set_start_method('spawn', force=True)
    
    dataset = sys.argv[1]  # "semart", "wikiart", "museum", or "ipiranga"
    valid_datasets = {"semart", "wikiart", "ipiranga"}
    if dataset not in valid_datasets:
        print(
            f"❌ Invalid dataset '{dataset}'. Choose one of: {', '.join(valid_datasets)}."
        )
        sys.exit(1)

    desc_col_base = f"description_Qwen2_5_{dataset}"
    output0 = os.path.join(DESCRIPTION_PATH, f"{dataset}_output_gpu0.csv")
    output1 = os.path.join(DESCRIPTION_PATH, f"{dataset}_output_gpu1.csv")
    output_merged = os.path.join(DESCRIPTION_PATH, f"output_merged_{dataset}.csv")

    records = load_data(dataset)

    mid = len(records) // 2
    part0, part1 = records[:mid], records[mid:]

    p0 = mp.Process(
        target=process_partition, args=(dataset, part0, 0, output0, desc_col_base)
    )
    p1 = mp.Process(
        target=process_partition, args=(dataset, part1, 1, output1, desc_col_base)
    )

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

    # Generate SQL UPDATE file
    generate_update_sql(dataset, output_merged)
