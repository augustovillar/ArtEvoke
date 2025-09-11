# 🔧 **ArtEvoke Data Processing Pipeline**

This directory contains the complete data processing pipeline for ArtEvoke - from raw art datasets to AI-powered search indices.

## 🎯 **Pipeline Philosophy**

**Single Environment, Multiple Steps**: This pipeline uses one unified virtual environment for all processing steps, ensuring consistent dependencies and simplified management.

```
Raw Art Images → AI Descriptions → Vector Search → Production Ready
     (Step 1)        (Step 2)        (Step 3)        (Output)
```

---

## ⚙️ **Environment Setup**

### **Prerequisites**
- **Python**: 3.8+ (3.10+ recommended)
- **GPU**: CUDA-compatible with 8GB+ VRAM (optional but highly recommended)
- **Storage**: 50GB+ free space
- **RAM**: 16GB+ for optimal performance

### **Installation**
```bash
# From ArtEvoke/pipeline directory
cd pipeline

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import transformers; print(f'Transformers: {transformers.__version__}')"
```

---

## 🗂️ **Directory Structure**

```
pipeline/
├── README.md                     # This guide
├── requirements.txt              # All dependencies
├── .venv/                        # Virtual environment
├── data/                         # Data storage (no scripts)
│   ├── README.md                 # Data format documentation
│   ├── raw/                      # Original datasets
│   │   ├── SemArt/              # Semantic art dataset
│   │   │   ├── Images/          # 21,000+ art images
│   │   │   └── metadata/        # CSV files with annotations
│   │   ├── WikiArt/             # WikiArt dataset
│   │   │   ├── Images/          # 15,000+ images by art genre
│   │   │   └── WikiArt15000.csv # Metadata file
│   │   └── Museum/              # Museum collections
│   └── processed/               # Generated outputs
│       ├── descriptions/        # AI-generated descriptions
│       │   ├── output_merged_semart.csv
│       │   ├── output_merged_wikiart.csv
│       │   └── intermediate/    # Temporary files
│       └── embeddings/          # FAISS search indices
│           ├── semart_index.faiss
│           ├── semart_metadata.pkl
│           ├── wikiart_index.faiss
│           └── wikiart_metadata.pkl
└── scripts/                     # Processing pipeline
    ├── README.md                # Detailed script documentation
    ├── config/                  # Centralized configuration
    │   ├── data_config.py       # Paths and dataset settings
    │   ├── model_config.py      # AI model configurations
    │   └── processing_config.py # Processing parameters
    ├── step1_data_acquisition/  # Download and organize data
    │   ├── README.md
    │   ├── download_semart.py
    │   ├── download_wikiart.py
    │   └── validate_data.py
    ├── step2_description_generation/  # Generate AI descriptions
    │   ├── README.md
    │   ├── generate_descriptions.py
    │   └── description_utils.py
    ├── step3_embedding_generation/    # Create search indices
    │   ├── README.md
    │   ├── generate_faiss_databases.py
    │   └── embedding_utils.py
    └── utils/                   # Shared utilities
        ├── logging_setup.py
        ├── file_operations.py
        └── validation.py
```

---

## 🚀 **Quick Start**

### **Full Pipeline Execution**
```bash
# From pipeline directory, with .venv activated

# Step 1: Download datasets (2-4 hours)
cd scripts/step1_data_acquisition
python download_semart.py
python download_wikiart.py

# Step 2: Generate descriptions (8-24 hours per dataset)
cd ../step2_description_generation
python generate_descriptions.py semart
python generate_descriptions.py wikiart

# Step 3: Create search indices (2-6 hours)
cd ../step3_embedding_generation
python generate_faiss_databases.py
```

### **Development/Testing Mode**
```bash
# Enable test mode in config/processing_config.py
# This processes only ~50 images per dataset for rapid iteration

# Edit configuration
nano scripts/config/processing_config.py
# Set: PROCESSING_LIMITS["test_mode"] = True

# Run pipeline (much faster)
# ... same commands as above
```

---

## ⚙️ **Configuration**

All settings are centralized in `scripts/config/` for easy management:

### **`data_config.py`**
- Dataset paths and URLs
- Directory structure
- File naming conventions

### **`model_config.py`**
- AI model selections (Qwen2.5-VL, GTE-Large)
- GPU allocation settings
- Model parameters (temperature, max_tokens)

### **`processing_config.py`**
- Processing limits (useful for testing)
- Parallel processing settings
- Logging and validation options

**Example**: To use different models, edit `model_config.py`:
```python
VLM_CONFIG = {
    "model_name": "Qwen/Qwen2.5-VL-7B-Instruct",  # Change this
    "num_gpus": 2,                                 # Adjust for your setup
    "batch_size": 1                                # Based on GPU memory
}
```

---

## 📊 **Expected Outputs**

After running the complete pipeline, you'll have:

### **Data Structure**
```
data/processed/
├── descriptions/
│   ├── output_merged_semart.csv    # 21K+ images with AI descriptions
│   └── output_merged_wikiart.csv   # 15K+ images with AI descriptions
└── embeddings/
    ├── semart_index.faiss          # Vector search index
    ├── semart_metadata.pkl         # Searchable metadata
    ├── wikiart_index.faiss
    └── wikiart_metadata.pkl
```

### **File Formats**

**Description CSVs**: Original metadata + AI-generated descriptions
```csv
IMAGE_FILE,TITLE,AUTHOR,description
image1.jpg,"The Starry Night","Van Gogh","A swirling night sky..."
```

**FAISS Indices**: Binary vector search files for fast semantic retrieval
**Metadata PKL**: Pandas DataFrames with cleaned, searchable metadata

---

## 🔧 **Troubleshooting**

### **Common Issues**

**1. CUDA Out of Memory**
```bash
# Reduce batch sizes in config/model_config.py
VLM_CONFIG["batch_size"] = 1
EMBEDDING_CONFIG["batch_size"] = 16
```

**2. Download Interruptions**
```bash
# Scripts are resumable - just re-run
python download_semart.py  # Will skip completed parts
```

**3. Processing Interruptions**
```bash
# Description generation resumes automatically
python generate_descriptions.py semart  # Continues from checkpoint
```

### **Logs and Monitoring**
- **Log Location**: `scripts/logs/`
- **Progress Tracking**: All scripts show progress bars
- **Error Handling**: Detailed error messages with suggested fixes

---

## 📈 **Performance Optimization**

### **Hardware Recommendations**
- **GPU**: Multiple CUDA GPUs for parallel processing
- **Storage**: SSD for faster I/O operations
- **RAM**: 32GB+ for large dataset processing

### **Software Optimizations**
- **Batch Size**: Increase if you have sufficient VRAM
- **Parallel Processing**: Utilize multiple GPUs/cores
- **Test Mode**: Use for development and debugging

### **Expected Processing Times**
| Step | Dataset | Time (GPU) | Time (CPU) |
|------|---------|------------|------------|
| **Step 1** | SemArt | 1 hour | 2 hours |
| **Step 1** | WikiArt | 3 hours | 6 hours |
| **Step 2** | SemArt (21K) | 12 hours | 72+ hours |
| **Step 2** | WikiArt (15K) | 8 hours | 48+ hours |
| **Step 3** | Both | 4 hours | 8 hours |

---

## 🎯 **Output Integration**

The generated FAISS indices and metadata are **directly compatible** with:

- **ArtEvoke Web Platform**: Copy `embeddings/` to production server
- **Custom Applications**: Use FAISS indices for art similarity search
- **Research Projects**: Analyze AI-generated descriptions and embeddings
- **API Services**: Build search endpoints using the indices

---

## 🔍 **Next Steps**

1. **Run the Pipeline**: Follow the Quick Start guide above
2. **Explore Configuration**: Customize models and parameters in `scripts/config/`
3. **Integrate Results**: Use outputs in the main ArtEvoke platform
4. **Scale Up**: Process additional datasets or fine-tune models
5. **Contribute**: Help improve the pipeline with optimizations and new features

**Ready to process art datasets with AI? Start with Step 1!** 🚀🎨
