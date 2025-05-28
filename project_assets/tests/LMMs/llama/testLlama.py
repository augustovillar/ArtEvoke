import os
from PIL import Image
from transformers import MllamaForConditionalGeneration, AutoProcessor
import torch
import time
import pandas as pd
from tqdm import tqdm

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

# Load the model and processor
model_id = "meta-llama/Llama-3.2-11B-Vision-Instruct"
model = MllamaForConditionalGeneration.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)
processor = AutoProcessor.from_pretrained(model_id)


def process_image(image_path):
    image = Image.open(image_path).convert("RGB")
    messages = [
        {
            "role": "user",
            "content": [{"type": "image"}, {"type": "text", "text": query}],
        },
    ]

    start_time = time.time()

    input_text = processor.apply_chat_template(messages, add_generation_prompt=True)
    inputs = processor(
        image,
        input_text,
        add_special_tokens=False,
        return_tensors="pt",
    ).to(model.device)

    output = model.generate(**inputs, max_new_tokens=1000)
    full_text = processor.decode(output[0], skip_special_tokens=True)

    if "assistant" in full_text.lower():
        parts = full_text.split("assistant", 1)
        clean_description = parts[-1].strip(": \n")
    else:
        clean_description = full_text

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


def addDataToTheDataFrame(model_name, df, outputs, times, allocate_total, reserved_total):
    desc_col = f"description_{model_name}"
    time_col = f"time_{model_name}"
    allocate_col = f"allocated_{model_name}"
    reserved_col = f"reserved_{model_name}"

    if len(df) != len(outputs):
        raise ValueError(
            f"Mismatch between DataFrame rows ({len(df)}) and outputs ({len(outputs)})."
        )

    df[desc_col] = outputs
    df[time_col] = times
    df[allocate_col] = allocate_total
    df[reserved_col] = reserved_total

    return df


if __name__ == "__main__":
    model_name = "Llama-3.2-11B-Vision-Instruct"
    df, images_files = getImagesFileNames()
    descriptions = []
    times = []
    allocate_total = []
    reserved_total = []

    for image_path in tqdm(images_files, desc="Processing images", unit="image"):
        description, elapsed_time, allocated, reserved = process_image(image_path)
        descriptions.append(description)
        times.append(elapsed_time)
        allocate_total.append(allocated)
        reserved_total.append(reserved)

    df = addDataToTheDataFrame(model_name, df, descriptions, times, allocate_total, reserved_total)
    
    df = df.drop(columns=["IMAGE_FILE_FULLPATH"])
    df.to_csv(os.path.join(SCRIPT_DIR, "llama_output.csv"), index=False)

    torch.cuda.empty_cache()
