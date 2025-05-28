# 🦙 LLaMA Evaluation - SemArt Dataset

This module evaluates the performance of the LLaMA model using outputs stored in CSV format. It assumes that the SemArt dataset has already been downloaded and prepared.

## 📁 Project Structure

```
llama/
├── llama_env/ # (Optional) Virtual environment
├── llama_output.csv # Main output CSV from LLaMA evaluation
├── llama_output copy.csv # Backup or variant of the output CSV
├── README.md # This file
├── requirements.txt # Python dependencies
└── testLlama.py # Script to run the LLaMA output evaluation
```

## ✅ Requirements

Make sure you have Python 3.8+ installed. You will also need to have the **SemArt dataset** available locally and preprocessed.

## 🛠️ Installation

It's recommended to use a virtual environment:

```bash
# Create virtual environment
python -m venv llama_env
source llama_env/bin/activate  # On Windows use: llama_env\Scripts\activate

pip install -r requirements.txt
```

## ▶️ Running the Evaluation

To run the evaluation on the LLaMA outputs:

```bash
python testLlama.py
```