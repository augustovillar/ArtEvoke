# 🔧 **ArtEvoke Scripts Pipeline**

This directory contains all processing scripts organized in a clear, sequential pipeline. Each step has specific prerequisites and outputs.

## 📋 **Pipeline Overview**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Step 1: Data   │    │  Step 2: AI     │    │  Step 3: Vector │
│  Acquisition    │───▶│  Descriptions   │───▶│  Embeddings     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
   Raw Images             Enhanced CSV           FAISS Index
   + Metadata            + Descriptions         + Search Ready
```

## ⚙️ **Prerequisites**

### System Requirements
- **Python**: 3.8+ 
- **GPU**: CUDA-compatible (recommended, 8GB+ VRAM)
- **Storage**: 50GB+ free space
- **RAM**: 16GB+ recommended

### Environment Setup
```bash
# From project root
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## 🔽 **Step 1: Data Acquisition**

Downloads and cleans art datasets from official sources.

### 📁 Location
```bash
cd scripts/step1_data_acquisition/
```

### 🚀 Execution
```bash
# Download individual datasets
python download_semart.py     # ~2GB download
python download_wikiart.py    # ~30GB download  
python download_museum.py     # Optional

# Validate data integrity
python validate_data.py
```

### 📊 Output Structure
```
data/raw/
├── SemArt/
│   ├── Images/              # 21,000+ art images
│   └── metadata/            # CSV files with metadata
│       ├── SemArt500.csv
│       ├── SemArt2000.csv
│       └── SemArt15000.csv
└── WikiArt/
    ├── Images/              # 15,000+ images by genre
    └── WikiArt15000.csv
```

### ⏱️ **Time Estimate**: 2-4 hours (depending on internet speed)

---

## 🤖 **Step 2: Description Generation**

Generates detailed AI descriptions using Qwen2.5-VL vision-language model.

### 📋 Prerequisites
- ✅ **Step 1 completed** (datasets downloaded)
- ✅ **GPU available** (CPU processing will be very slow)

### 📁 Location
```bash
cd scripts/step2_description_generation/
```

### 🚀 Execution
```bash
# Generate descriptions for each dataset
python generate_descriptions.py semart
python generate_descriptions.py wikiart

# Optional: Process museum dataset
python generate_descriptions.py museum
```

### 🔧 Configuration
Edit `config/model_config.py` to adjust:
- Model parameters (temperature, max_tokens)
- GPU allocation
- Batch sizes

### 📊 Output
```
data/processed/descriptions/
├── output_merged_semart.csv    # SemArt + AI descriptions
├── output_merged_wikiart.csv   # WikiArt + AI descriptions  
└── intermediate/               # Temporary processing files
```

### ⏱️ **Time Estimate**: 8-24 hours per dataset (GPU dependent)

---

## 🔍 **Step 3: Embedding Generation**

Creates FAISS vector indices for fast semantic search.

### 📋 Prerequisites
- ✅ **Step 2 completed** (descriptions generated)

### 📁 Location
```bash
cd scripts/step3_embedding_generation/
```

### 🚀 Execution
```bash
# Generate embeddings and FAISS indices
python generate_faiss_databases.py
```

### 📊 Output
```
data/processed/embeddings/
├── semart_index.faiss         # Vector search index
├── semart_metadata.pkl        # Searchable metadata
├── wikiart_index.faiss
└── wikiart_metadata.pkl
```

### ⏱️ **Time Estimate**: 2-6 hours

---

## 🎛️ **Configuration**

All settings are centralized in `config/`:

### **`data_config.py`**
- File paths and directory structure
- Dataset-specific parameters

### **`model_config.py`**
- AI model configurations (VLM + embedding models)
- GPU allocation settings

### **`processing_config.py`**
- Processing limits (useful for testing)
- Parallel processing settings
- Logging configuration

## 🧪 **Testing Mode**

For development and testing, enable test mode:

```python
# In config/processing_config.py
PROCESSING_LIMITS["test_mode"] = True
```

This processes only small samples (~50 images per dataset) for rapid iteration.

---

## 🔧 **Troubleshooting**

### **Common Issues**

**1. CUDA Out of Memory**
```bash
# Reduce batch size in config/model_config.py
VLM_CONFIG["batch_size"] = 1
EMBEDDING_CONFIG["batch_size"] = 16
```

**2. Download Interruption**
```bash
# Scripts are resumable - simply re-run the same command
python download_semart.py  # Will skip completed parts
```

**3. Processing Interruption**
```bash
# Description generation resumes automatically
python generate_descriptions.py semart  # Continues from last checkpoint
```

### **Logs Location**
```
scripts/logs/
├── semart_download.log
├── description_generation.log
└── faiss_generation.log
```

---

## 📈 **Performance Optimization**

### **For Faster Processing**
1. **Use multiple GPUs**: Adjust `num_gpus` in model configs
2. **Increase batch sizes**: If you have sufficient VRAM
3. **Use SSD storage**: Significantly faster I/O operations
4. **Enable test mode**: For development and debugging

### **Resource Usage**
- **Step 1**: Network I/O intensive
- **Step 2**: GPU compute intensive  
- **Step 3**: CPU + moderate GPU usage

---

## 🎯 **Next Steps**

After completing all steps, your processed data will be ready for:
- Integration with the VisualCuesApp platform
- Custom art search applications
- Research and analysis projects

The generated FAISS indices and metadata can be directly used by the main ArtEvoke platform for real-time art retrieval!
