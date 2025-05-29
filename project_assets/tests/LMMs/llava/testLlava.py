from llavaMod import eval_model
import pandas as pd
import warnings
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


pd.set_option("display.max_colwidth", None)
warnings.filterwarnings("ignore", message=".*copying from a non-meta parameter.*")
warnings.filterwarnings("ignore", message=".*resume_download.*deprecated.*")
warnings.filterwarnings("ignore", message=".*model of type llava.*")

# === Constants and Paths ===
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "..", "..", "data", "SemArt")
CSV_PATH = os.path.join(DATA_DIR, "semart_info", "SemArt500.csv")
IMAGE_DIR = os.path.join(DATA_DIR, "Images")
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "llava_output.csv")

# === Settings ===
model_paths = [
    "liuhaotian/llava-v1.5-7b",
    "liuhaotian/llava-v1.5-13b",
    "liuhaotian/llava-v1.6-vicuna-7b",
    "liuhaotian/llava-v1.6-vicuna-13b",
    "liuhaotian/llava-v1.6-mistral-7b",
]


# Load image
def getImagesFileNames():
    df = pd.read_csv(CSV_PATH)
    df["IMAGE_FILE_FULLPATH"] = IMAGE_DIR + "/"+ df["IMAGE_FILE"]
    return df, df["IMAGE_FILE_FULLPATH"].tolist()


def addDataToTheDataFrame(model_name, df, outputs, times, allocate_total, reserved_total):
    desc_col = f"description_{model_name.split('/')[-1]}"
    time_col = f"time_{model_name.split('/')[-1]}"
    allocate_col = f"allocated_{model_name.split('/')[-1]}"
    reserved_col = f"reserved_{model_name.split('/')[-1]}"

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
    df, file_names = getImagesFileNames()
    descriptions = []
    times_appended = []
    df, file_names = df[:10], file_names[:10]
    for model_path in model_paths:
        print(f"\n=== Running model: {model_path} ===\n")

        args = type(
            "Args",
            (),
            {
                "model_path": model_path,
                "model_base": None,
                "query": query,
                "image_files": file_names,
                "sep": ",",
                "conv_mode": None,
                "temperature": 0,
                "top_p": None,
                "num_beams": 1,
                "max_new_tokens": 512,
            },
        )()
        descriptions, times, allocated, reserved = eval_model(args)

        df = addDataToTheDataFrame(model_path, df, descriptions, times, allocated, reserved)

        df.to_csv(OUTPUT_PATH, index=False)

    df = df.drop(columns=["IMAGE_FILE_FULLPATH"])
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"\n✅ DataFrame saved to {OUTPUT_PATH}")
    torch.cuda.empty_cache()
