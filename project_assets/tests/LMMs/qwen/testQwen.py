from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor, AutoModelForCausalLM
from qwen_vl_utils import process_vision_info
import time
import pandas as pd
from tqdm import tqdm
import os
import torch

query = """
Task: Describe the visual content of the following artwork in detail.
Your description should focus only on what is visible in the image — such as people, objects, colors, emotions, actions, setting, and atmosphere.
Do not include the title, artist, art movement, or historical context.

Example of a good description:

“The lunette on the back wall of the loggia depicts a colorful fruit and vegetable market. The scene is split in two: women run their stalls beneath a tall arcade supported by a striking red pillar. Besides produce, other goods hang from a molding along the back wall.”

Now, describe the current image following the same style.
Be accurate, descriptive, and grounded in what can be seen.
"""

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "data", "SemArt")
IMAGE_DIR = os.path.join(DATA_DIR, "Images")

SAMPLE500 = os.path.join(DATA_DIR, "semart_info", "SemArt500.csv")

def process_image(max_pixels, image_path):
    messages = [{
        "role": "user",
        "content": [
            {"type": "image", "image": image_path, "max_pixels": max_pixels},

            {"type": "text", "text": query},
        ],
    }]

    start_time = time.time()
    # Preparation for inference
    text = processor.apply_chat_template(messages, add_generation_prompt=True)
    image_inputs, _ = process_vision_info(messages)
    inputs = processor(
        text=[text],
        images=image_inputs,
        padding=True,
        return_tensors="pt",
    ).to("cuda")
    # Inference
    generated_ids = model.generate(**inputs, max_new_tokens=1000)
    output_text = processor.batch_decode(
        generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False
    )
    if isinstance(output_text, list):
        output_text = output_text[0]

    if "assistant" in output_text.lower():
        parts = output_text.rsplit("assistant", 1)
        clean_description = parts[-1].strip(": \n")
    else:
        clean_description = output_text.strip()

    elapsed_time = time.time() - start_time

    allocated = 0
    reserved = 0
    for i in range(torch.cuda.device_count()):
        allocated += torch.cuda.memory_allocated(i) / (1024**2)
        reserved += torch.cuda.memory_reserved(i) / (1024**2)

    return clean_description.replace("\n", ""), elapsed_time, allocated, reserved

def getImagesFileNames():
    df = pd.read_csv(SAMPLE500)
    df["IMAGE_FILE_FULLPATH"] = IMAGE_DIR + "/"+ df["IMAGE_FILE"]
    return df, df["IMAGE_FILE_FULLPATH"].tolist()


def addDataToTheDataFrame(model_name, df, outputs, times, allocate_total, reserved_total, pixel_limit):
    desc_col = f"description_{model_name.split('/')[-1]}_{str(pixel_limit)}"
    time_col = f"time_{model_name.split('/')[-1]}_{str(pixel_limit)}"
    allocate_col = f"allocated_{model_name.split('/')[-1]}_{str(pixel_limit)}"
    reserved_col = f"reserved_{model_name.split('/')[-1]}_{str(pixel_limit)}"

    if len(df) != len(outputs):
        raise ValueError(
            f"Mismatch between DataFrame rows ({len(df)}) and outputs ({len(outputs)})."
        )

    df[desc_col] = outputs
    df[time_col] = times
    df[allocate_col] = allocate_total
    df[reserved_col] = reserved_total

    return df


models_name = [
    "Qwen/Qwen2.5-VL-3B-Instruct", 
    "Qwen/Qwen2.5-VL-7B-Instruct",
    "Qwen/Qwen2.5-VL-7B-Instruct",
    "Qwen/Qwen2.5-VL-7B-Instruct",
    "Qwen/Qwen2.5-VL-7B-Instruct",
    "Qwen/Qwen2.5-VL-7B-Instruct",
    "Qwen/Qwen2.5-VL-7B-Instruct",
]

max_pixels =[
    512*512,
    512*512,
    512 * 640,
    512 * 896,
    512 * 1024,
    1024 * 1024,
]

if __name__ == "__main__":
    df, images_files = getImagesFileNames()

    for model_name, pixel_limit in zip(models_name, max_pixels):
        model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            model_name,
            torch_dtype=torch.bfloat16,
            device_map="auto"
        )
        processor = AutoProcessor.from_pretrained(model_name)

        descriptions = []
        times = []
        allocate_total = []
        reserved_total = []

        for image_path in tqdm(images_files, desc=f"Processing with {model_name} @ {pixel_limit} px", unit="image"):
            description, elapsed_time, allocated, reserved = process_image(pixel_limit, image_path)
            descriptions.append(description)
            times.append(elapsed_time)
            allocate_total.append(allocated)
            reserved_total.append(reserved)

        df = addDataToTheDataFrame(model_name, df, descriptions, times, allocate_total, reserved_total, pixel_limit)

        df.to_csv(os.path.join(SCRIPT_DIR, f"qwen_output.csv"), index=False)

    df = df.drop(columns=["IMAGE_FILE_FULLPATH"])
    df.to_csv(os.path.join(SCRIPT_DIR, f"qwen_output.csv"), index=False)
    torch.cuda.empty_cache()
