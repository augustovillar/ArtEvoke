import pandas as pd
import os
import torch
from tqdm import tqdm
from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info
import multiprocessing as mp

MODEL_NAME = "Qwen/Qwen2.5-VL-7B-Instruct"
PIXEL_LIMIT = 512 * 512


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "..", "..", "data", "SemArt")
CSV_PATH = os.path.join(DATA_DIR, "semart_info", "SemArt2000.csv")
IMAGE_DIR = os.path.join(DATA_DIR, "Images")
DESC_COL = "description_Qwen2_5_7B_512"
OUTPUT_TEMPLATE = os.path.join(SCRIPT_DIR, "qwen_output_gpu{}.csv")

query = """
Task: Describe the visual content of the following artwork in detail.
Your description should focus only on what is visible in the image — such as people, objects, colors, emotions, actions, setting, and atmosphere.
Do not include the title, artist, art movement, or historical context.

Example of a good description:

“The lunette on the back wall of the loggia depicts a colorful fruit and vegetable market. The scene is split in two: women run their stalls beneath a tall arcade supported by a striking red pillar. Besides produce, other goods hang from a molding along the back wall.”

Now, describe the current image following the same style.
Be accurate, descriptive, and grounded in what can be seen.
"""


def process_partition(df, gpu_id, output_file):
    torch.cuda.set_device(gpu_id)

    # Carrega progresso anterior se existir
    if os.path.exists(output_file):
        df_saved = pd.read_csv(output_file)
        print(f"[GPU {gpu_id}] Resuming from existing file: {output_file}")
    else:
        df[DESC_COL] = pd.NA
        df_saved = df.copy()

    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        MODEL_NAME, torch_dtype=torch.bfloat16, device_map={"" : f"cuda:{gpu_id}"}
    )
    processor = AutoProcessor.from_pretrained(MODEL_NAME)

    for idx, row in tqdm(df_saved.iterrows(), total=len(df_saved), desc=f"[GPU {gpu_id}] Processing", position=gpu_id):
        if pd.notna(row.get(DESC_COL)) and "Error" not in str(row.get(DESC_COL)):
            continue

        image_path = row["IMAGE_FILE_PATH"]
        try:
            messages = [{
                "role": "user",
                "content": [
                    {"type": "image", "image": image_path, "max_pixels": PIXEL_LIMIT},
                    {"type": "text", "text": query},
                ],
            }]
            text = processor.apply_chat_template(messages, add_generation_prompt=True)
            image_inputs, _ = process_vision_info(messages)
            inputs = processor(text=[text], images=image_inputs, padding=True, return_tensors="pt").to(f"cuda:{gpu_id}")
            output_ids = model.generate(**inputs, max_new_tokens=1000)
            output_text = processor.batch_decode(output_ids, skip_special_tokens=True)[0]
            description = output_text.rsplit("assistant", 1)[-1].strip(": \n") if "assistant" in output_text.lower() else output_text.strip()
            df_saved.at[idx, DESC_COL] = description.replace("\n", " ")
        except Exception as e:
            df_saved.at[idx, DESC_COL] = f"Error: {str(e)}"

        df_saved.to_csv(output_file, index=False)

def get_images_df():
    df = pd.read_csv(CSV_PATH)
    df["IMAGE_FILE_PATH"] = df["IMAGE_FILE"].apply(lambda x: os.path.join(IMAGE_DIR, str(x)))
    return df

if __name__ == "__main__":
    df = get_images_df()
    df = df[:10]
    half = len(df) // 2
    df0 = df.iloc[:half].copy()
    df1 = df.iloc[half:].copy()

    p0 = mp.Process(target=process_partition, args=(df0, 0, OUTPUT_TEMPLATE.format(0)))
    p1 = mp.Process(target=process_partition, args=(df1, 1, OUTPUT_TEMPLATE.format(1)))

    p0.start()
    p1.start()
    p0.join()
    p1.join()

    # Merge final
    df0_out = pd.read_csv(OUTPUT_TEMPLATE.format(0))
    df1_out = pd.read_csv(OUTPUT_TEMPLATE.format(1))
    merged = pd.concat([df0_out, df1_out], ignore_index=True)
    merged = merged.drop(columns=["IMAGE_FILE_PATH"])
    merged.to_csv(os.path.join(SCRIPT_DIR, "qwen_output2000.csv"), index=False)

    os.remove(OUTPUT_TEMPLATE.format(0))
    os.remove(OUTPUT_TEMPLATE.format(1))
