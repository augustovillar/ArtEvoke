## 📊 FAISS-Based Recall Evaluation for Embedding Models

This script evaluates the **semantic alignment** between original artwork descriptions and generated descriptions from vision-language models (LMMs) by computing **Recall@K** over FAISS indices.

---

## 📁 Directory Structure
```
embeddings/
├── FAISS/
│   ├── index/          # FAISS index files
│   └── metadata/       # Corresponding metadata (image filename + tag)
├── emb_env/            # Python virtual environment
├── testEmbeddings.py   # Main script for evaluation
├── surveyCode.py       # Script that uses results from above (optional)
├── requirements.txt
└── README.md
```

---
## 🛠️ Installation

It's recommended to use a virtual environment:

```bash
# Create virtual environment
python -m venv emb_env
source emb_env/bin/activate  # On Windows use: emb_env\Scripts\activate

pip install -r requirements.txt
```
---
## ⚙️ Script Overview (`testEmbeddings.py`)

This script evaluates the retrieval quality of embedding models by computing Recall@K from original to generated image descriptions. It includes:

- 📥 Loading original and generated descriptions from a CSV
- 🧠 Generating text/image embeddings via SentenceTransformer or OpenCLIP
- 📦 Creating FAISS indices (text-only, image-only, or combined)
- 📈 Calculating Recall@1, 3, 6, and 10
- 🧪 Optional interleaved retrieval from both modalities
- 🔍 Printing top-k results for selected test cases
---

## ▶️ How to Run
Run the script with:
```bash
python testEmbeddings.py
```
It will:
- Load the descriptions and models
- Generate FAISS indices
- Calculate recall metrics


---

## 📦 Output Structure
```
FAISS/
├── index/
│   ├── text_embeddings_MODEL.index
│   ├── image_embeddings_MODEL.index
│   └── combined_embeddings_MODEL.index
├── metadata/
│   ├── text_embeddings_MODEL.pkl
│   ├── image_embeddings_MODEL.pkl
│   └── combined_embeddings_MODEL.pkl
```

Each FAISS index is paired with a metadata file that maps FAISS vectors to their source images.

---

## 📚 Dependencies
Install required packages with:
```bash
pip install -r requirements.txt