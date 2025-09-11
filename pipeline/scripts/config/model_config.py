"""
ArtEvoke Model Configuration
AI model settings and parameters
"""

# Vision-Language Model (Description Generation)
VLM_CONFIG = {
    "model_name": "Qwen/Qwen2.5-VL-7B-Instruct",
    "max_pixels": 512 * 512,
    "batch_size": 1,  # Adjust based on GPU memory
    "num_gpus": 2,    # Number of GPUs to use
    "temperature": 0.7,
    "max_new_tokens": 256
}

# Embedding Model (FAISS Generation)
EMBEDDING_CONFIG = {
    "model_name": "thenlper/gte-large", 
    "normalize_embeddings": True,
    "batch_size": 32,
    "num_gpus": 2,
    "device_map": {
        "gpu_0": "cuda:0",
        "gpu_1": "cuda:1"
    }
}

# FAISS Index Configuration
FAISS_CONFIG = {
    "index_type": "IndexFlatIP",  # Inner Product (cosine similarity)
    "search_k": 6,  # Default number of results
    "nprobe": None  # For IVF indices (not used with Flat)
}

# Base prompt template for description generation
BASE_PROMPT_TEMPLATE = """Task: Describe the visual content of the following artwork in detail.
Your description should focus only on what is visible in the image — such as people, objects, colors, emotions, actions, setting, and atmosphere.
Do not include the title, artist, art movement, or historical context.

Example of a good description:
"The scene depicts a colorful fruit and vegetable market. Women run their stalls beneath a tall arcade supported by a striking red pillar. Besides produce, other goods hang from a molding along the back wall."

Now, describe the current image following the same style.
Be accurate, descriptive, and grounded in what can be seen.

{subject_hint}
"""

# Dataset-specific prompt modifications
DATASET_PROMPT_HINTS = {
    "semart": "\n\nYou may consider the following information:\n{info}",
    "wikiart": "\n\nYou may consider the following terms as visual hints:\n{info}",
    "museum": "\n\nYou may consider the following terms as visual hints:\n{info}"
}
