# 🧠 LLM-Based Story Generation and Evaluation

This script evaluates the **generative quality** of large language models (LLMs) in crafting coherent short stories from visual art scene descriptions.

---

## 📁 Directory Structure

```
LLMs/
├── llm_env/                           # Virtual environment
├── llm_stories.csv                   # Automatically generated stories and metrics
├── llm_manual_evaluation_summary.csv # Manual evaluation results (optional)
├── testLlm.py                        # Main evaluation script
└── requirements.txt
```

---

## 🛠️ Installation

Create and activate a virtual environment:

```bash
python -m venv llm_env
source llm_env/bin/activate  # On Windows use: llm_env\Scripts\activate

pip install -r requirements.txt
```

---

## ⚙️ Script Overview (`testLlm.py`)

This script has two main modes:

### `run`
- Loads visual descriptions of artworks
- Prompts selected LLMs to generate short stories based on the descriptions
- Automatically assesses fluency and coherence (basic checks)
- Saves generated stories, generation time, and success flag to `llm_stories.csv`

### `evaluate`
- Loads the generated stories
- Asks the user to manually judge each story:
  - Is it successful? (y/n)
  - Rate its quality (1–5)
- Summarizes manual success rate and average score in `llm_manual_evaluation_summary.csv`

---

## ▶️ How to Run

Run automatic generation:
```bash
python testLlm.py run
```

Run manual evaluation:
```bash
python testLlm.py evaluate
```

---

## 📌 Prompt Format

The script compiles a few detailed visual descriptions of paintings and prompts the model to write a **2–3 paragraph story**, with:
- A clear start, middle, and end
- Sequential, connected ideas

---

## 📚 Models Used

The models can be adjusted, but currently include:

- `Qwen/Qwen3-1.7B`
- `Qwen/Qwen3-4B`
- `microsoft/Phi-4-mini-instruct`

Each run repeats generation multiple times (`REPEAT = 10` by default) for each model.

---

## 📦 Output

Generated stories and evaluation results are saved as CSV files for analysis and reproducibility.
