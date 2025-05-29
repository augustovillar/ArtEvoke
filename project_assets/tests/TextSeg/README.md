# ✂️ Text Segmentation-Based Image Retrieval

This module explores the effect of **text segmentation strategies** on retrieving semantically relevant artworks from a visual database using FAISS.

---

## 📁 Directory Structure

```
TextSeg/
├── retrieved_results/           # Output folders with retrieved image matches and overlays
├── test_text_seg/               # Saved FAISS index and image metadata
├── textSeg_env/                 # Virtual environment (optional)
├── testTextSeg.py               # Main script
└── requirements.txt             # Dependency list
```

---

## 🛠️ Installation

```bash
python -m venv textSeg_env
source textSeg_env/bin/activate  # On Windows: textSeg_env\Scripts\activate

pip install -r requirements.txt
```

---

## ⚙️ Script Overview (`testTextSeg.py`)

This script evaluates the retrieval performance of various segmentation strategies applied to a short narrative text. It:

- Loads a pretrained SentenceTransformer (`gte-large`)
- Splits the story into sentences and paragraphs
- Applies segmentation strategies (non-overlapping and overlapping windows)
- Encodes segments and searches a FAISS image embedding index
- Saves results and overlayed matches per segment
- Computes metrics:
  - 🔁 Number of retrieved items
  - 📊 Cosine similarity average
  - 🎨 Diversity (unique images retrieved)

---

## ✂️ Segmentation Strategies Tested

- `paragraph`: raw paragraph blocks
- `1sent_nonoverlap`: one sentence at a time
- `2sent_nonoverlap`, `3sent_nonoverlap`: groups of 2/3 sentences without overlap
- `2sent_step1_overlap`, `3sent_step1_overlap`, `3sent_step2_overlap`: overlapping sliding windows

---

## ▶️ How to Run

```bash
python testTextSeg.py
```

If the FAISS index doesn’t exist yet, it will be created from the SemArt dataset descriptions.

---

## 📦 Output

- Results with overlayed text per segment are saved under `retrieved_results/<strategy>/`
- Images are annotated with the segment that triggered their retrieval
- Printed summary includes average cosine similarity and diversity scores per strategy
