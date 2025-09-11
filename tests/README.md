# 🧪 **ArtEvoke Model Testing & Evaluation**

This directory contains comprehensive testing suites for different AI models used in ArtEvoke. Each model type has its own isolated virtual environment to prevent dependency conflicts.

## 🎯 **Testing Philosophy**

**Isolated Environments**: Each model family gets its own virtual environment due to conflicting dependencies, different CUDA versions, and specialized requirements.

```
Different Models → Different Dependencies → Separate Virtual Environments
```

---

## 📁 **Directory Structure**

```
tests/
├── README.md                     # This guide
├── embeddings/                   # Sentence transformer testing
│   ├── README.md
│   ├── requirements.txt          # Embedding-specific deps
│   ├── .venv_embeddings/         # Isolated environment
│   ├── surveyCode.py
│   └── testEmbeddings.py
├── faiss/                        # Vector search testing
│   ├── README.md  
│   ├── requirements.txt
│   ├── .venv_faiss/              # Isolated environment
│   └── testFaiss.py
├── LLMs/                         # Language model testing
│   ├── README.md
│   ├── requirements.txt          # LLM-specific deps
│   ├── .venv_llms/               # Isolated environment
│   └── testLlm.py
├── LMMs/                         # Large multimodal models
│   ├── README.md
│   ├── requirements.txt          # LMM-specific deps
│   ├── .venv_lmms/               # Isolated environment
│   ├── evaluating.py
│   ├── llama/                    # LLaMA vision models
│   │   ├── README.md
│   │   ├── requirements.txt
│   │   └── testLlama.py
│   ├── llava/                    # LLaVA models
│   │   ├── README.md
│   │   ├── requirements.txt
│   │   ├── llavaMod.py
│   │   └── testLlava.py
│   └── qwen/                     # Qwen vision-language models
│       ├── README.md
│       ├── requirements.txt
│       ├── testQwen.py
│       └── generate2000Sampling.py
└── TextSeg/                      # Text segmentation testing
    ├── README.md
    ├── requirements.txt
    ├── .venv_textseg/            # Isolated environment
    └── testTextSeg.py
```

---

## ⚙️ **Environment Setup**

### **General Pattern**
Each test category follows the same setup pattern:

```bash
# Navigate to test category
cd tests/[category]

# Create isolated environment
python -m venv .venv_[category]
source .venv_[category]/bin/activate  # Windows: .venv_[category]\Scripts\activate

# Install specific dependencies
pip install -r requirements.txt

# Run tests
python test[Category].py
```

### **Quick Setup All Environments**
```bash
# From tests/ directory
./setup_all_envs.sh  # Creates all test environments (if script exists)

# Or manually:
for dir in embeddings faiss LLMs LMMs TextSeg; do
    cd $dir
    python -m venv .venv_${dir,,}
    source .venv_${dir,,}/bin/activate
    pip install -r requirements.txt
    deactivate
    cd ..
done
```

---

## 🧩 **Testing Categories**

### **🔤 Embeddings Testing** (`embeddings/`)
**Purpose**: Evaluate sentence transformer models for text encoding

- **Models Tested**: Various sentence-transformers models
- **Metrics**: Embedding quality, similarity accuracy, performance
- **Use Case**: Optimizing text-to-vector conversion for search

```bash
cd tests/embeddings
source .venv_embeddings/bin/activate
python testEmbeddings.py
```

### **🔍 FAISS Testing** (`faiss/`)  
**Purpose**: Validate vector search index performance

- **Index Types**: Flat, IVF, PQ compression
- **Metrics**: Search accuracy, speed, memory usage
- **Use Case**: Optimizing similarity search performance

```bash
cd tests/faiss
source .venv_faiss/bin/activate
python testFaiss.py
```

### **🔤 LLM Testing** (`LLMs/`)
**Purpose**: Evaluate language models for text generation

- **Models**: Various transformer-based language models
- **Tasks**: Text completion, story generation, coherence
- **Metrics**: BLEU, perplexity, semantic similarity

```bash
cd tests/LLMs  
source .venv_llms/bin/activate
python testLlm.py
```

### **👁️ LMM Testing** (`LMMs/`)
**Purpose**: Comprehensive multimodal model evaluation

- **Models**: LLaMA, LLaVA, Qwen vision-language models
- **Tasks**: Image description, visual question answering
- **Metrics**: Description quality, accuracy, consistency

#### **Qwen Models** (`LMMs/qwen/`)
```bash
cd tests/LMMs/qwen
source ../.venv_lmms/bin/activate
python testQwen.py
python generate2000Sampling.py  # Large-scale evaluation
```

#### **LLaVA Models** (`LMMs/llava/`)
```bash
cd tests/LMMs/llava
source ../.venv_lmms/bin/activate
python testLlava.py
```

#### **LLaMA Vision** (`LMMs/llama/`)
```bash
cd tests/LMMs/llama
source ../.venv_lmms/bin/activate
python testLlama.py
```

### **✂️ Text Segmentation** (`TextSeg/`)
**Purpose**: Test text splitting and preprocessing

- **Methods**: Sentence-based, semantic, length-based
- **Use Case**: Optimizing text preprocessing for better descriptions
- **Metrics**: Segment quality, boundary detection accuracy

```bash
cd tests/TextSeg
source .venv_textseg/bin/activate  
python testTextSeg.py
```

---

## 📊 **Testing Workflows**

### **Model Comparison Pipeline**
```bash
# Compare embedding models
cd tests/embeddings
source .venv_embeddings/bin/activate
python surveyCode.py  # Comprehensive embedding comparison

# Evaluate description quality across LMMs
cd ../LMMs
source .venv_lmms/bin/activate
python evaluating.py  # Multi-model evaluation
```

### **Performance Benchmarking**
```bash
# FAISS index optimization
cd tests/faiss
source .venv_faiss/bin/activate
python testFaiss.py --benchmark --index-types flat,ivf,pq

# LMM speed vs quality tradeoff
cd ../LMMs/qwen
source ../.venv_lmms/bin/activate
python testQwen.py --batch-sizes 1,4,8 --precision fp16,fp32
```

---

## ⚡ **Environment Dependencies**

### **Why Separate Environments?**

| Issue | Example | Solution |
|-------|---------|----------|
| **CUDA Versions** | LMM needs CUDA 11.8, Embeddings needs 12.0 | Separate envs |
| **Library Conflicts** | Different transformers versions | Isolated deps |
| **Model Size** | Some models need 32GB RAM | Resource isolation |
| **Development** | Test new models without breaking existing | Safe experimentation |

### **Typical Requirements**

**Embeddings Environment**:
```
sentence-transformers>=2.2.0
faiss-cpu>=1.7.4
torch>=2.0.0
numpy<2.0.0
```

**LMM Environment**:
```  
transformers>=4.30.0
torch>=2.0.0
torchvision>=0.15.0
accelerate>=0.20.0
qwen_vl_utils
```

---

## 🔧 **Development Guidelines**

### **Adding New Tests**
1. **Create Category Directory**: `mkdir tests/new_category`
2. **Setup Environment**: `python -m venv .venv_new_category`
3. **Create Requirements**: List specific dependencies
4. **Write Tests**: Follow existing patterns
5. **Document**: Add README.md

### **Environment Naming Convention**
- **Pattern**: `.venv_[category]` (lowercase)
- **Examples**: `.venv_embeddings`, `.venv_lmms`, `.venv_faiss`
- **Activation**: `source .venv_[category]/bin/activate`

### **Test Structure Pattern**
```python
#!/usr/bin/env python3
"""
Test Description: What this test evaluates
Model Category: Which models are tested
Metrics: What measurements are taken
"""

import os
import sys
import logging
from pathlib import Path

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent.parent))

def setup_logging():
    """Configure test logging"""
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger(__name__)

def test_model_performance():
    """Main test function"""
    pass

if __name__ == "__main__":
    logger = setup_logging()
    logger.info("Starting [Category] tests...")
    test_model_performance()
```

---

## 📈 **Performance Monitoring**

### **Resource Usage Tracking**
- **GPU Memory**: Monitor VRAM usage during tests
- **System RAM**: Track memory consumption 
- **Processing Time**: Measure inference speed
- **Accuracy Metrics**: Evaluate model performance

### **Automated Testing** (Future)
```bash
# Run all test suites
./run_all_tests.sh

# Generate performance report
python generate_test_report.py --output reports/
```

---

## 🎯 **Integration with Pipeline**

### **Model Selection Process**
1. **Test in Isolation**: Use test environments
2. **Compare Results**: Analyze metrics across models
3. **Select Best Model**: Based on accuracy/speed tradeoffs
4. **Update Pipeline Config**: Modify `pipeline/scripts/config/model_config.py`
5. **Validate in Production**: Run pipeline with new model

### **Continuous Evaluation**
- **Model Drift**: Monitor performance over time
- **New Model Integration**: Test latest model releases
- **Performance Regression**: Catch performance decreases

---

## 🚀 **Quick Start Testing**

### **Evaluate Current Pipeline Models**
```bash
# Test current embedding model (gte-large)
cd tests/embeddings
source .venv_embeddings/bin/activate
python testEmbeddings.py --model thenlper/gte-large

# Test current VLM model (Qwen2.5-VL)
cd ../LMMs/qwen
source ../.venv_lmms/bin/activate
python testQwen.py --model Qwen/Qwen2.5-VL-7B-Instruct
```

### **Compare Alternative Models**
```bash
# Compare multiple embedding models
cd tests/embeddings
python surveyCode.py --models all-MiniLM-L6-v2,gte-large,e5-large

# Evaluate different LMMs
cd ../LMMs
python evaluating.py --models qwen,llava,llama
```

---

## 📝 **Notes for Researchers**

- **Reproducibility**: All tests include random seed setting
- **Datasets**: Tests use small subsets for speed (full evaluation available)
- **Metrics**: Standard evaluation metrics implemented
- **Reports**: Generate detailed performance comparisons

**Ready to test and optimize AI models? Choose your testing category and dive in!** 🧪🚀
