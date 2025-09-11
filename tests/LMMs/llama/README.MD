# 🦙 LLaMA Evaluation - SemArt Dataset

This module evaluates the performance of the LLaMA model using outputs stored in CSV format. It assumes that the SemArt dataset has already been downloaded and prepared.

## 📁 Project Structure

```
llama/
├── llama_env/
├── llama_output.csv 
├── README.md # This file
├── requirements.txt # Python dependencies
└── testLlama.py # Script to run the LLaMA output evaluation
```

## ✅ Requirements

Make sure you have Python 3.10+ installed. You will also need to have the **SemArt dataset** available locally and preprocessed.

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

## 📊 Output

The final CSV (`llama_output.csv`) will include:

- **Original image filename**
- **Generated description** for each artwork, produced by the LLaMA model
- **Inference time** per image (in seconds)
- **Allocated GPU memory** (in MB) during generation
- **Reserved GPU memory** (in MB) during generation
- Cleaned metadata used for analysis
