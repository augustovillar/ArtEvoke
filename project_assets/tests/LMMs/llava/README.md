# 🤖 LLaVA Evaluation - SemArt Dataset

This module evaluates the performance of a LLaVA-based model on the SemArt dataset. It generates visual descriptions and stores the results in CSV format. It assumes the SemArt dataset is already available and preprocessed.

## 📁 Project Structure

```
llava/
├── LLaVA/ # Cloned or modified LLaVA repository (actual model files)
│   ├── ...
├── llava_output.csv # Main output CSV
├── llavaMod.py # modifications of the LLVA files
├── README.md 
├── requirements.txt
└── testLlava.py # Main script to run the evaluation
```


## ✅ Requirements

Make sure you have **Python 3.10+** installed. You will also need to have the **SemArt dataset** locally available and preprocessed.



## 🛠️ Installation

1. It is recommended to use a virtual environment:

```bash
cd llava
python -m venv llava_env
source llava_env/bin/activate  # On Windows: llava_env\Scripts\activate

pip install -r requirements.txt
```
2. Clone and install the original LLaVA package (mandatory):

```bash
git clone https://github.com/haotian-liu/LLaVA.git
cd LLaVA
pip install --upgrade pip
pip install -e .
```


## ▶️ Running the Evaluation
To run the evaluation and generate image descriptions using the LLaVA model:

```bash
python testLlava.py
```


## 📊 Output

The final CSV file (`llava_output.csv`) will include:

- **Original image filename**
- **Description** per model combination
- **Inference time** per image (in seconds)
- **Allocated GPU memory** (in MB) during generation
- **Reserved GPU memory** (in MB) during generation
- Cleaned metadata for each image