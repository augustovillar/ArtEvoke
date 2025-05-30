# 🎨 ArtEvoke Platform

ArtEvoke is an AI-powered platform that connects personal stories to visual artworks, helping trigger memories in people living with Alzheimer's disease. 🖥️ [Access the platform here](https://artevoke.com.br). It leverages large multimodal models (LMMs), language models (LLMs), and FAISS-based similarity search to retrieve contextually relevant images.

📄 **Full Thesis Report**: [Master Thesis - ArtEvoke](link_here)

---

## 📁 Project Structure

```
ArtEvoke/
├── project_assets/
│   ├── data/                    # Raw dataset inputs and metadata
│   │   ├── Museum/
│   │   ├── SemArt/
│   │   ├── WikiArt/
│   ├── scripts/                 # Core processing scripts
│   │   ├── generateDescriptions.py
│   │   ├── generateFAISSDatabases.py
│   └── tests/                   # Evaluation and model selection
│       ├── embeddings/
│       ├── faiss/
│       ├── LLMs/
│       ├── LMMs/
│       └── TextSeg/
├── website/                 # Web platform frontend/backend
├── .gitignore
└── README.md                
```

---

## 🚀 How It Works

Each subfolder has a description to help run all the tests and preprocessing.

### 1. 🔍 Description Generation (Qwen2.5-VL)
Generate detailed visual descriptions from artwork images across datasets (`semart`, `wikiart`, `museum`) using:
```bash
python generateDescriptions.py semart
```
Runs in parallel on 2 GPUs and saves descriptions as CSV.

### 2. 🧠 FAISS Embedding and Indexing
After description generation, build FAISS-compatible vector embeddings using `gte-large`:
```bash
python generateFAISSDatabases.py
```

---

## 🧪 Testing Suite

The `tests/` folder includes validation scripts for:
- 🔠 `embeddings/`: Sentence embedding benchmarks
- 🧮 `faiss/`: FAISS performance evaluation and recall metrics
- 🧾 `LLMs/`: Story generation and summary evaluation
- 🖼️ `LMMs/`: Visual captioning comparison (e.g., Qwen vs. LLaVA)
- ✂️ `TextSeg/`: Phrase segmentation strategies and analysis

---

## 📂 Data Sources

- `SemArt15000.csv` with realistic subset of SemArt images
- `WikiArt15000.csv` randomly sampled and filtered
- Royal Museum dataset 
- Output folders:
  - `outputs/descriptions/`: Description CSVs from LMMs
  - `outputs/faiss/`: FAISS indices and associated metadata

---

## 📎 Requirements


Python ≥ 3.10 and CUDA-enabled GPU required for full inference pipeline.

---

## 📘 Citation

If you use this project, please cite the associated master's thesis:
> Augusto Silva & Marc Bejjani. “ArtEvoke: AI-powered platform to trigger memories in Alzheimer’s patients using art imagery.” École polytechnique de Louvain, 2025.

---