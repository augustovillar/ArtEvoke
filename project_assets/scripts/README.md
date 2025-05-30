# 🔍 Visual Description and FAISS Embedding Pipeline

This repository contains scripts to generate visual descriptions from art datasets using Qwen2.5-VL and build FAISS indices for retrieval based on sentence-transformer embeddings.

## 📁 Structure

```
.
├── scripts/
... ├── generateDescriptions.py       # Generate image descriptions using Qwen2.5-VL on multiple GPUs
    ├── generateFAISSDatabases.py     # Build FAISS vector index and save metadata
    ├── requirements.txt                 # Python dependencies
    ├── README.md
    └── outputs/
        ├── descriptions/                 # Contains generated descriptions (intermediate + merged CSVs)
        └── faiss/                        # Contains FAISS index and metadata (PKL)

```

## ⚙️ Environment Setup

```bash
# Create virtual environment (optional but recommended)
cd scripts
python -m venv main_env
source main_env/bin/activate  # On Windows use `main_env\Scripts\activate`

# Install dependencies
pip install -r requirements.txt
```

## 🖼️ Description Generation

To generate descriptions from images using the Qwen2.5-VL model (run on 2 GPUs):

```bash
python generateDescriptions.py [dataset_name]
```

- `[dataset_name]` must be one of: `semart`, `wikiart`, `museum`
- Outputs are saved as CSVs under `outputs/descriptions/`.

### Description Fields

- Output includes a column `description` with the final text generated.
- Original metadata is preserved in the output.

## 🧠 FAISS Database Creation

After descriptions are generated, you can build the FAISS vector index:

```bash
python generateFAISSDatabases.py
```

- This reads the merged description CSVs.
- Builds a FAISS index with `gte-large` sentence transformer using 2 GPUs.
- Saves:
  - `*.faiss`: FAISS index
  - `*.pkl`: metadata file with renamed & normalized fields

## 📂 Datasets

Expected dataset structure (update `DATA_PATH` in script if needed):

```
data/
├── SemArt/
│   ├── semart_info/SemArt15000.csv
│   └── Images/
├── WikiArt/
│   ├── WikiArt15000.csv
│   └── Images/
├── Museum/
│   └── input_data_museum.json
```

## 🚀 Notes

- Descriptions are generated in parallel using `torch.multiprocessing` on two GPUs.
- Output CSVs for each GPU are merged automatically.
- For museum data, full image paths are trimmed for consistency.