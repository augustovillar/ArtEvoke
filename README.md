# 🎨 ArtEvoke: AI-Powered Art Description and Retrieval System

**ArtEvoke** is a comprehensive AI platform that processes art datasets to generate semantic descriptions and enable intelligent art retrieval. Originally developed for connecting personal stories to visual artworks to help trigger memories in people with Alzheimer's disease.

🖥️ **[Platform Access](https://artevoke.com.br)** | 📄 **[Full Thesis](link_here)**

---

## 🚀 **Quick Start Pipeline**

This repository contains the **data processing pipeline** that powers the ArtEvoke platform. Follow these steps:

### **Prerequisites**
- Python 3.8+
- CUDA-compatible GPU (recommended for faster processing)
- 50GB+ free disk space

## 🚀 **Quick Start**

This repository is organized into **two main sections** with different virtual environment strategies:

### **🔧 Virtual Environment Strategy**
- **Pipeline**: Single unified environment (`.venv`) for all data processing
- **Tests**: Individual environments per LLM/LMM for isolated testing

### **Installation & Setup**
```bash
# Clone repository
git clone https://github.com/augustovillar/ArtEvoke.git
cd ArtEvoke

# Setup main pipeline environment
cd pipeline
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### **Pipeline Execution**
```bash
# From pipeline directory
cd pipeline

# Step 1: Download datasets
cd scripts/step1_data_acquisition
python download_semart.py && python download_wikiart.py

# Step 2: Generate AI descriptions  
cd ../step2_description_generation
python generate_descriptions.py semart
python generate_descriptions.py wikiart

# Step 3: Build search indices
cd ../step3_embedding_generation
python generate_faiss_databases.py
```

---

## 📁 **Project Structure**

```
ArtEvoke/
├── README.md                     # This guide
├── pipeline/                     # Main data processing pipeline
│   ├── README.md                 # Detailed pipeline documentation
│   ├── requirements.txt          # Pipeline dependencies
│   ├── .venv/                    # Unified virtual environment
│   ├── data/                     # All datasets (raw + processed)
│   │   ├── raw/                  # Original downloaded data
│   │   │   ├── SemArt/          # 21K+ semantic art annotations
│   │   │   ├── WikiArt/         # 15K+ art images by genre
│   │   │   └── Museum/          # Custom museum collections
│   │   └── processed/           # AI-generated outputs
│   │       ├── descriptions/    # VLM-generated descriptions
│   │       └── embeddings/      # FAISS search indices
│   └── scripts/                 # Processing pipeline
│       ├── config/              # Centralized configuration
│       ├── step1_data_acquisition/    # Download & clean datasets
│       ├── step2_description_generation/  # AI description generation
│       ├── step3_embedding_generation/   # Vector search indices
│       └── utils/               # Shared utilities
├── tests/                       # Model testing & evaluation
│   ├── embeddings/              # Embedding model tests (own venv)
│   ├── LLMs/                    # Language model tests (own venv)
│   ├── LMMs/                    # Multimodal model tests (own venv)
│   └── ...                      # Each with isolated environment
├── website/                     # Web platform interface
└── project_assets/              # Legacy structure (for migration)
```

---

## 📖 **Documentation**

### **Main Components**
- **[Pipeline Documentation](pipeline/README.md)**: Complete data processing workflow
- **[Data Organization](pipeline/data/README.md)**: Dataset structure and formats  
- **[Scripts Guide](pipeline/scripts/README.md)**: Step-by-step execution guide
- **[Testing Guide](tests/README.md)**: Model evaluation and benchmarks

### **Quick Navigation**
- **Data Processing**: Start with `pipeline/README.md`
- **Model Testing**: See `tests/README.md` 
- **Configuration**: Check `pipeline/scripts/config/`
- **Web Platform**: Visit `website/` directory

---

## ⚙️ **Environment Management**

### **Pipeline Environment** (Unified)
```bash
cd pipeline
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### **Test Environments** (Isolated per Model)
```bash
cd tests/LLMs
python -m venv llm_env
source llm_env/bin/activate
pip install -r requirements.txt

cd ../LMMs  
python -m venv lmm_env
source lmm_env/bin/activate
pip install -r requirements.txt
```

---

## 🎯 **Supported Workflows**

### **Research & Development**
1. **Data Pipeline**: Process art datasets with AI descriptions
2. **Model Testing**: Evaluate different LLMs/LMMs performance
3. **Search Optimization**: Tune FAISS indices for better retrieval

### **Production Deployment**
1. **Run Full Pipeline**: Generate production-ready search indices
2. **Integration**: Use outputs in the ArtEvoke web platform
3. **Monitoring**: Track processing performance and quality

---

## 🔧 **Development Notes**

- **Modular Design**: Each step can run independently
- **Resumable Processing**: Scripts automatically resume from checkpoints
- **Configurable**: All settings centralized in `pipeline/scripts/config/`
- **Scalable**: GPU parallelization and batch processing support

## 📊 **System Requirements**

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **Python** | 3.8+ | 3.10+ |
| **RAM** | 8GB | 32GB+ |
| **Storage** | 50GB free | 100GB+ SSD |
| **GPU** | Optional | CUDA 8GB+ VRAM |

---

## � **Getting Started**

1. **Choose Your Path**:
   - **Data Processing**: Go to `pipeline/README.md`
   - **Model Testing**: Go to `tests/README.md`
   - **Web Development**: Go to `website/README.md`

2. **Follow Documentation**: Each component has detailed setup instructions

3. **Join Development**: Check issues and contribution guidelines

**Ready to process art with AI? Start with the [Pipeline Guide](pipeline/README.md)!** 🎨✨

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

## 🧪 Testing Suite

The `tests/` folder includes validation scripts for:
- 🔠 `embeddings/`: Sentence embedding benchmarks
- 🧮 `faiss/`: FAISS performance evaluation and recall metrics
- 🧾 `LLMs/`: Story generation and summary evaluation
- 🖼️ `LMMs/`: Visual captioning comparison (e.g., Qwen vs. LLaVA)
- ✂️ `TextSeg/`: Phrase segmentation strategies and analysis


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