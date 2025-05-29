# 📊 FAISS-Based Recall Evaluation for Embedding Models

This repository evaluates the **semantic alignment** between original artwork descriptions and generated captions from vision-language models by computing **Recall@K** over FAISS indices.

---

## 📁 Directory Structure

```
faiss/
├── faiss_env/                # Virtual environment
├── retrieval_examples/       # Folder storing retrieved image results
├── testFaiss.py              # Main FAISS testing script
└── requirements.txt
```

---

## 🛠️ Installation

It's recommended to use a virtual environment:

```bash
# Create and activate virtual environment
python -m venv faiss_env
source faiss_env/bin/activate  # On Windows use: faiss_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## ⚙️ Script Overview (`testFaiss.py`)

This script evaluates the retrieval quality of embedding models by computing Recall@K between original and generated descriptions. It:

- Loads original and generated descriptions from CSV
- Generates text embeddings via `SentenceTransformer`
- Creates FAISS indices (`FlatIP`, `IVF`, and `IVFPQ`)
- Calculates Recall@1, 3, 6
- Measures latency and memory usage (CPU/GPU)
- Saves retrieval examples of top-6 results for selected test cases

---

## ▶️ How to Run

Use one of the following commands:

```bash
python testFaiss.py cpu
```

```bash
python testFaiss.py gpu
```

---

## 💾 Output

- Retrieval examples for selected images are saved to:
  ```
  retrieval_examples/flatip_<sample_size>/
  ```
- A summary table with latency, memory, and recall scores is printed and saved as a DataFrame
