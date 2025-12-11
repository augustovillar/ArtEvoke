# 🎨 ArtEvoke Platform

ArtEvoke is an AI-powered platform that connects personal stories to visual artworks, helping trigger memories in people living with Alzheimer's disease. 🖥️ [Access the platform here](https://artevoke.com.br). 

The platform leverages:
- **Large Multimodal Models (LMMs)** for visual artwork captioning
- **Large Language Models (LLMs)** for text correction and narrative generation
- **Vector databases (Qdrant)** for semantic similarity search across 30,000+ artworks
- **Embedding models** for high-quality semantic representations

📄 **Full Thesis Report**: [Master Thesis - ArtEvoke](link_here)

---

## 📁 Project Structure

```
ArtEvoke/
├── project_assets/          # Research & preprocessing assets
│   ├── data/                # Raw dataset inputs and metadata
│   │   ├── Ipiranga/        # Museu do Ipiranga collection
│   │   ├── SemArt/          # SemArt dataset
│   │   └── WikiArt/         # WikiArt dataset
│   ├── scripts/             # Core processing scripts
│   │   ├── generateDescriptions.py      # LMM-based captioning
│   │   ├── generateQdrantCollection.py  # Vector DB setup
│   │   └── docker-compose.yml           # Services orchestration
│   └── tests/               # Model evaluation and selection
│       ├── embeddings/      # Embedding model benchmarks
│       ├── LLMs/            # Language model evaluation
│       ├── LMMs/            # Vision model comparison
│       ├── qdrant/          # Vector search testing
│       └── TextSeg/         # Segmentation strategies
│
├── webapp/                  # Production web application
│   ├── FastAPI/             # Backend API (Python)
│   │   ├── routes/          # API endpoints
│   │   ├── orm/             # Database models
│   │   ├── clients/         # External service clients
│   │   ├── utils/           # Helper functions
│   │   └── prompts/         # LLM system prompts
│   │
│   ├── frontend/            # Frontend application (React)
│   │   ├── src/
│   │   │   ├── pages/       # Application pages
│   │   │   ├── components/  # Reusable UI components
│   │   │   ├── contexts/    # Global state management
│   │   │   └── i18n/        # Internationalization (PT/EN)
│   │   └── public/
│   │
│   ├── data/                # Application data
│   │   ├── db/              # MySQL schemas and migrations
│   │   ├── static/          # Artwork image files
│   │   ├── vector_db/       # Qdrant snapshots
│   │   └── embeddings/      # Embedding indices (legacy)
│   │
│   ├── nginx/               # Reverse proxy configuration
│   ├── env/                 # Environment variables
│   └── docker-compose.yml   # Full stack deployment
│
├── .gitignore
└── README.md
```

---

## 🌟 Key Features

### 🧠 Memory Reconstruction
Help patients reconstruct personal memories through art:
- Input personal stories via text or voice
- AI-powered text correction and segmentation
- Semantic search retrieves relevant artworks
- Interactive image selection per story segment
- Session tracking and progress monitoring

### 🎨 Art Exploration
Discover artwork through guided exploration:
- Keyword-based semantic search
- Multi-image selection from curated collections
- AI-generated narratives connecting selected artworks
- Support for WikiArt, SemArt, and Ipiranga collections

### 👨‍⚕️ Session Management
Comprehensive tools for healthcare professionals:
- Create and manage patient profiles
- Configure guided therapy sessions
- Monitor patient engagement and progress
- Pre/post-session cognitive evaluations
- Detailed result analytics

### ♿ Accessibility Features
Built for diverse user needs:
- High contrast and soft theme options
- Dynamic font size adjustment
- Text-to-speech functionality
- Voice input with automatic correction
- Full bilingual support (Portuguese/English)

---

## 🧪 Research & Testing Suite

The `project_assets/tests/` folder includes comprehensive evaluation scripts:

- **🔠 embeddings/**: Benchmark sentence embedding models (recall@k, latency)
- **🧮 qdrant/**: Vector database performance evaluation
- **🧾 LLMs/**: Language model testing for text correction and generation
- **🖼️ LMMs/**: Visual captioning comparison (Qwen2.5-VL, LLaVA, etc.)
- **✂️ TextSeg/**: Story segmentation strategy analysis

Each subfolder contains detailed instructions for running experiments.

---

## 🚀 Getting Started

### Prerequisites

- **Docker & Docker Compose** (recommended for full stack)
- **Python** ≥ 3.10 (for local development)
- **Node.js** ≥ 16 (for frontend development)
- **CUDA-enabled GPU** (optional, for local model inference)

### Quick Start with Docker

1. **Clone the repository**:
```bash
git clone https://github.com/augustovillar/ArtEvoke.git
cd ArtEvoke/webapp
```

2. **Configure environment variables**:
```bash
cp env/.backend.env.example env/.backend.env
cp env/.mysql.env.example env/.mysql.env
# Edit .env files with your credentials and API keys
```

3. **Start all services**:
```bash
docker-compose up --build
```

Services will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5001
- **MySQL**: localhost:3306
- **Qdrant**: http://localhost:6333

### Local Development

See detailed setup instructions in:
- **Backend**: [webapp/FastAPI/README.md](webapp/FastAPI/README.md)
- **Frontend**: [webapp/frontend/README.md](webapp/frontend/README.md)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                   Frontend (React)                       │
│  - User Interface (Doctors & Patients)                  │
│  - Session Management                                   │
│  - Accessibility Features                               │
└────────────────────────┬────────────────────────────────┘
                         │ REST API
┌────────────────────────▼────────────────────────────────┐
│                  Backend (FastAPI)                       │
│  - Authentication & Authorization                       │
│  - Memory Reconstruction Service                        │
│  - Art Exploration Service                              │
│  - Session & Evaluation Management                      │
└─────┬──────────────┬──────────────┬─────────────────────┘
      │              │              │
      ▼              ▼              ▼
┌──────────┐  ┌───────────┐  ┌────────────┐
│  MySQL   │  │  Qdrant   │  │ External   │
│ Database │  │  Vector   │  │ AI APIs    │
│          │  │  Search   │  │ - Maritaca │
│          │  │           │  │ - DeepInfra│
└──────────┘  └───────────┘  └────────────┘
```

### Technology Stack

**Frontend**:
- React 19 with React Router
- Bootstrap 5 for UI components
- i18next for internationalization
- Web Speech API for voice features

**Backend**:
- FastAPI (Python 3.13)
- SQLAlchemy ORM with MySQL
- Qdrant vector database
- Maritaca AI (Sabia-3 LLM)
- DeepInfra (Qwen3-Embedding-4B)

**Infrastructure**:
- Docker & Docker Compose
- Nginx reverse proxy
- MySQL 8.0
- Qdrant vector database

---

## 📂 Data Sources

The platform utilizes three curated art collections:

1. **WikiArt** (~15,000 images)
   - Global art history spanning centuries
   - Multiple styles and movements
   - Artist and school metadata

2. **SemArt** (~15,000 images)
   - Semantically annotated artworks
   - Rich metadata with titles, authors, dates
   - European art focus

3. **Ipiranga Museum** (Brazilian collection)
   - Historical Brazilian artwork
   - Cultural heritage focus
   - Regional significance

All images are captioned using **Qwen2.5-VL** multimodal model and indexed in Qdrant for semantic search.

---

## 🔧 Data Processing Pipeline

### 1. 🔍 Visual Captioning (LMM)

Generate detailed descriptions from artwork images:

```bash
cd project_assets/scripts
python generateDescriptions.py semart
```

- Uses Qwen2.5-VL multimodal model
- Parallel processing on multiple GPUs
- Outputs detailed CSV descriptions

### 2. 🧠 Vector Database Setup

Build Qdrant collections with embeddings:

```bash
python generateQdrantCollection.py
```

- Embeds captions using Qwen3-Embedding-4B
- Creates persistent Qdrant collections
- Generates snapshots for deployment

### 3. 📊 Database Population

Populate MySQL with artwork metadata:

```bash
# Automatically executed via docker-compose
# Schema files in: webapp/data/db/schemas/
```

---

## 🔌 API Overview

The backend exposes comprehensive REST endpoints:

### Core Endpoints

- **Authentication**: `/api/doctors/login`, `/api/patients/login`
- **Memory Reconstruction**: `/api/memory/submit`, `/api/memory/save`
- **Art Exploration**: `/api/art/search`, `/api/art/generate-story`
- **Sessions**: `/api/sessions/`, `/api/sessions/{id}/results`
- **Evaluations**: `/api/evaluation/create`

Full API documentation available at: http://localhost:5001/docs

---

## 📊 Workflow Examples

### Memory Reconstruction Flow

```
1. Patient inputs personal story (text or voice)
2. Backend corrects text using Maritaca LLM
3. Story segmented into meaningful phrases
4. Each segment embedded (Qwen3-Embedding-4B)
5. Qdrant searches for similar artwork
6. Patient selects relevant images per segment
7. Reconstruction saved to database
```

### Art Exploration Flow

```
1. Patient inputs keywords or themes
2. Keywords embedded and searched in Qdrant
3. Top-k similar artworks retrieved
4. Patient selects multiple artworks
5. Maritaca LLM generates connecting narrative
6. Generated story displayed and saved
```

---

## 🔒 Security & Privacy

- **JWT Authentication**: Secure token-based auth
- **Role-Based Access**: Doctor/Patient permissions
- **Password Security**: Bcrypt + SHA-256 hashing
- **HTTPS Enforcement**: Encrypted communication in production

---

## 📚 Documentation

- **Backend API**: [webapp/FastAPI/README.md](webapp/FastAPI/README.md)
- **Frontend**: [webapp/frontend/README.md](webapp/frontend/README.md)
- **Environment Setup**: [webapp/env/README.md](webapp/env/README.md)
- **API Reference**: http://localhost:5001/docs (when running)


---

## 📄 License & Citation

This project is part of a master's thesis research. If you use this work, please cite:

> Augusto Silva & Vinicius Alvarenga. "ArtEvoke: AI-powered platform to trigger memories in Alzheimer's patients using art imagery." Escola Politécnica da Universidade de São Paulo.

For usage permissions and academic citations, please contact the research team.

---

## 🙏 Acknowledgments

- **Museu do Ipiranga** for the Brazilian art collection
- **Maritaca AI** for Portuguese-optimized language models
- Research advisors and clinical partners


