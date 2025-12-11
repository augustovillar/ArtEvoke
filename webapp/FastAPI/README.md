# 🚀 ArtEvoke Backend API

The backend of **ArtEvoke** is a FastAPI-based REST API service that powers AI-driven cognitive therapy for Alzheimer's patients. It orchestrates LLM-based text processing, semantic image search, session management, and patient data persistence.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Key Features](#key-features)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Core Services](#core-services)
- [Database Schema](#database-schema)
- [AI Integration](#ai-integration)
- [Authentication & Security](#authentication--security)
- [Configuration](#configuration)
- [Getting Started](#getting-started)
- [API Documentation](#api-documentation)
- [Technology Stack](#technology-stack)

---

## 🌟 Overview

The ArtEvoke backend provides a comprehensive API layer for:

- **Memory Reconstruction**: Processing personal narratives and retrieving relevant artwork through semantic search
- **Art Exploration**: Keyword-based image discovery and AI-generated storytelling
- **Session Management**: Creating, tracking, and evaluating therapeutic sessions
- **User Management**: Authentication and authorization for doctors and patients
- **Cognitive Evaluation**: Pre/post-session cognitive assessments

### Purpose

- Process patient stories with LLM-based text correction and segmentation
- Perform semantic similarity search across 30,000+ artwork images
- Generate contextual narratives connecting selected artworks
- Store and retrieve therapy session data and evaluations
- Manage multi-role authentication (Doctor/Patient)

---

## 🏗️ Architecture

The backend follows a **layered architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                   API Layer (FastAPI)                   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Routes (Endpoints)                              │   │
│  │  - art_exploration, memory_reconstruction        │   │
│  │  - doctor_routes, patient_routes, session_routes │   │
│  │  - evaluation_routes, art_routes, vr_routes      │   │
│  └──────────────────────────────────────────────────┘   │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼───────────────────────────────┐
│                  Business Logic Layer                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  API Types   │  │    Utils     │  │   Clients    │ │
│  │  (DTOs)      │  │ - Auth       │  │ - Maritaca   │ │
│  │              │  │ - Embeddings │  │ - Qdrant     │ │
│  │              │  │ - Text Proc. │  │ - Database   │ │
│  │              │  │ - Spell Check│  │ - Embedding  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└───────────────────────┬───────────────────────────────┘
                        │
┌───────────────────────▼────────────────────────────────┐
│                  Data Access Layer                     │
│  ┌──────────────────────────────────────────────────┐  │
│  │  ORM Models (SQLAlchemy)                         │  │
│  │  - User Models (Doctor, Patient)                 │  │
│  │  - Session Models                                │  │
│  │  - Memory Reconstruction Models                  │  │
│  │  - Art Exploration Models                        │  │
│  │  - Catalog Models (WikiArt, SemArt, Ipiranga)    │  │
│  │  - Evaluation Models                             │  │
│  └──────────────────────────────────────────────────┘  │
└───────────────────────┬────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────-┐
│                  External Services                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────-┐   │
│  │  MySQL   │  │  Qdrant  │  │ Maritaca │  │DeepInfra│   │
│  │ Database │  │  Vector  │  │   LLM    │  │Embedding│   │
│  │          │  │   DB     │  │   API    │  │   API   │   │
│  └──────────┘  └──────────┘  └──────────┘  └───────-─┘   │
└─────────────────────────────────────────────────────────-┘
```

### Request Flow

```
Client Request
    ↓
FastAPI Route Handler
    ↓
Authentication Middleware (JWT validation)
    ↓
DTO Validation (Pydantic models)
    ↓
Business Logic Processing
    ↓
┌──────────────────────────────────┐
│  Parallel Processing:            │
│  - LLM Text Correction           │
│  - Semantic Search (Qdrant)      │
│  - Database Operations           │
└──────────────────────────────────┘
    ↓
Response Assembly
    ↓
JSON Response to Client
```

---

## ✨ Key Features

### 🧠 Memory Reconstruction API

Transform personal stories into visual memory aids:

- **Text Correction**: LLM-powered grammar and coherence improvement
- **Story Segmentation**: Intelligent phrase segmentation (conservative/broader modes)
- **Semantic Search**: Qdrant-based similarity search across art collections
- **Multi-Section Processing**: Batch processing of story segments
- **Image Retrieval**: Returns top-k relevant artworks per segment

### 🎨 Art Exploration API

Enable keyword-driven art discovery:

- **Keyword Search**: Vector-based semantic search using Qdrant
- **Story Generation**: LLM generates narratives connecting selected artworks
- **Multi-Dataset Support**: WikiArt, SemArt, Ipiranga collections
- **Contextual Narratives**: AI-generated stories linking art to patient memories

### 👨‍⚕️ Session Management

Comprehensive therapy session orchestration:

- **Session Creation**: Configure activities, datasets, time limits, evaluations
- **Patient Assignment**: Link sessions to specific patients
- **Progress Tracking**: Monitor session start, completion, and duration
- **Evaluation Integration**: Pre/post cognitive assessments
- **Result Retrieval**: Detailed session outcome reports

### 🔒 Authentication & Authorization

Multi-role secure access:

- **JWT-based authentication**: Stateless token validation
- **Role-based access control**: Doctor and Patient roles
- **Password security**: Bcrypt + SHA-256 hybrid hashing
- **Token expiration**: Configurable session timeouts

### 📊 Cognitive Evaluation

Track patient cognitive performance:

- **Pre-session assessments**: Baseline cognitive state
- **Post-session assessments**: Measure therapeutic impact
- **Standardized questionnaires**: Multiple-choice evaluations
- **Progress tracking**: Compare pre/post results

---

## 📁 Project Structure

```
FastAPI/
├── main.py                          # Application entry point
├── database.py                      # Database connection management
├── database_config.py               # Database URL configuration
├── pyproject.toml                   # Dependencies (uv package manager)
├── Dockerfile                       # Docker containerization
├── .dockerignore                    # Docker ignore rules
│
├── api_types/                       # Data Transfer Objects (DTOs)
│   ├── __init__.py
│   ├── common.py                    # Shared DTOs (Dataset, Language, etc.)
│   ├── art_exploration.py           # Art Exploration DTOs
│   ├── memory_reconstruction.py     # Memory Reconstruction DTOs
│   ├── session.py                   # Session DTOs
│   ├── patient.py                   # Patient DTOs
│   ├── user.py                      # User DTOs
│   └── evaluation.py                # Evaluation DTOs
│
├── clients/                         # External service clients
│   ├── __init__.py
│   ├── database_client.py           # MySQL connection factory
│   ├── embedding_client.py          # DeepInfra embedding API client
│   ├── maritaca_client.py           # Maritaca AI LLM client
│   └── qdrant_client.py             # Qdrant vector DB client
│
├── orm/                             # SQLAlchemy ORM models
│   ├── __init__.py                  # Database initialization
│   ├── base.py                      # Base model class
│   ├── user_models.py               # Doctor & Patient models
│   ├── session_models.py            # Session model
│   ├── memory_reconstruction_models.py  # MR models
│   ├── art_exploration_models.py    # AE models
│   ├── catalog_models.py            # WikiArt, SemArt, Ipiranga models
│   └── evaluation_models.py         # Evaluation models
│
├── routes/                          # API endpoint definitions
│   ├── __init__.py
│   ├── memory_reconstruction.py     # /api/memory endpoints
│   ├── art_exploration.py           # /api/art endpoints
│   ├── session_routes.py            # /api/sessions endpoints
│   ├── doctor_routes.py             # /api/doctors endpoints
│   ├── patient_routes.py            # /api/patients endpoints
│   ├── art_routes.py                # /api/art-search endpoints
│   ├── evaluation_routes.py         # /api/evaluation endpoints
│   └── vr_routes.py                 # /api/vr endpoints (future)
│
├── utils/                           # Utility functions
│   ├── auth.py                      # JWT & password hashing
│   ├── embeddings.py                # Embedding generation & search
│   ├── text_processing.py           # Story segmentation logic
│   ├── text_correction.py           # LLM response parsing
│   └── spell_check.py               # LanguageTool integration
│
├── prompts/                         # LLM system prompts
│   ├── mr_prompt_pt.md              # Memory Reconstruction (Portuguese)
│   ├── mr_prompt_en.md              # Memory Reconstruction (English)
│   ├── ae_prompt_pt.md              # Art Exploration (Portuguese)
│   ├── ae_prompt_en.md              # Art Exploration (English)
│   ├── speech_correct_text_pt.md    # Speech correction (Portuguese)
│   ├── speech_correct_text_en.md    # Speech correction (English)
│   └── vr_correct_text.md           # VR text correction
│
└── data/                            # Local data directory (volumes)
```

---

## 🔌 API Endpoints

### Authentication & User Management

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/doctors/signup` | POST | Register new doctor | No |
| `/api/doctors/login` | POST | Doctor authentication | No |
| `/api/patients/login` | POST | Patient authentication | No |
| `/api/signup` | POST | General user signup | No |
| `/api/doctors/patients` | GET | List doctor's patients | Doctor |
| `/api/doctors/patients` | POST | Create patient profile | Doctor |
| `/api/doctors/patients/{id}` | GET | Get patient details | Doctor |

### Memory Reconstruction

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/memory/improve-text` | POST | Correct text with LLM | Yes |
| `/api/memory/submit` | POST | Analyze story & retrieve images | Yes |
| `/api/memory/save` | POST | Save memory reconstruction | Yes |
| `/api/memory/retrieve` | GET | List user's reconstructions | Yes |
| `/api/memory/{id}` | GET | Get specific reconstruction | Yes |
| `/api/memory/{id}` | DELETE | Delete reconstruction | Yes |

### Art Exploration

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/art/search` | POST | Search images by keywords | Yes |
| `/api/art/generate-story` | POST | Generate narrative from images | Yes |
| `/api/art/save` | POST | Save art exploration | Yes |
| `/api/art/retrieve` | GET | List user's explorations | Yes |
| `/api/art/{id}` | GET | Get specific exploration | Yes |
| `/api/art/{id}` | DELETE | Delete exploration | Yes |

### Session Management

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/sessions/` | POST | Create new session | Doctor |
| `/api/sessions/my-sessions` | GET | List current user's sessions | Yes |
| `/api/sessions/patient/{patient_id}` | GET | List patient's sessions | Doctor |
| `/api/sessions/{id}` | GET | Get session details | Yes |
| `/api/sessions/{id}` | PUT | Update session status | Yes |
| `/api/sessions/{id}` | DELETE | Delete session | Doctor |
| `/api/sessions/{id}/results` | GET | Get session results | Yes |
| `/api/sessions/{id}/pre-evaluation` | POST | Submit pre-evaluation | Patient |
| `/api/sessions/{id}/pos-evaluation` | POST | Submit post-evaluation | Patient |
| `/api/sessions/{id}/evaluation` | GET | Get session evaluations | Doctor |

### Evaluation

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/evaluation/create` | POST | Create evaluation record | Yes |
| `/api/evaluation/{session_id}` | GET | Get session evaluation | Yes |

### General

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/` | GET | API root (health check) | No |
| `/docs` | GET | OpenAPI documentation (Swagger UI) | No |
| `/redoc` | GET | ReDoc API documentation | No |

---

## 🛠️ Core Services

### 1. Memory Reconstruction Service

**Workflow**:
```
Raw Story Text
    ↓
Text Correction (Maritaca LLM)
    ↓
Story Segmentation (TextProcessing)
    ↓
Embedding Generation (DeepInfra/Local)
    ↓
Qdrant Similarity Search
    ↓
Image Retrieval (MySQL Catalog)
    ↓
Response Assembly
```

**Key Functions**:
- `improve_text()`: LLM-based text correction
- `analyze_story()`: Story segmentation and image retrieval
- `save_memory_reconstruction()`: Persist reconstruction data

**Technologies**:
- **LLM**: Maritaca AI (Sabia-3 model)
- **Embeddings**: DeepInfra API (Qwen3-Embedding-4B)
- **Search**: Qdrant index with cosine similarity
- **Segmentation**: Sentence-based sliding window

### 2. Art Exploration Service

**Workflow**:
```
Keywords
    ↓
Embedding Generation
    ↓
Qdrant Vector Search
    ↓
Image Retrieval (MySQL)
    ↓
User Selection
    ↓
Story Generation (Maritaca LLM)
    ↓
Response with Narrative
```

**Key Functions**:
- `search_images()`: Qdrant-based semantic search
- `generate_story()`: LLM narrative generation
- `save_art_exploration()`: Persist exploration data

**Technologies**:
- **Vector DB**: Qdrant with pre-built collections
- **LLM**: Maritaca AI for story generation
- **Embeddings**: DeepInfra API

### 3. Session Management Service

**Capabilities**:
- Session configuration (activity type, dataset, time limits)
- Patient assignment and tracking
- Status management (pending, started, completed)
- Evaluation integration
- Result aggregation

**Database Tables**:
- `Session`: Main session metadata
- `MemoryReconstruction`: Linked MR activities
- `ArtExploration`: Linked AE activities
- `Evaluation`: Pre/post assessments

### 4. Authentication Service

**Features**:
- JWT token generation and validation
- Password hashing (Bcrypt + SHA-256)
- Role-based access control
- Token expiration handling

**Implementation**:
```python
# Token creation
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Authentication middleware
async def get_current_user(request: Request) -> dict:
    token = request.headers.get("Authorization").split(" ")[1]
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    # Extract user info from payload
    return user_info
```

### 5. Embedding Service

**Providers**:
- **DeepInfra API**: Cloud-based embedding generation (Qwen3-Embedding-4B)
- **Local Model**: (Optional) Self-hosted embedding model

**Functions**:
```python
def get_embedding(text: str):
    """Generate normalized embedding vector for single text"""
    embedding = encode_text([text])
    return embedding / np.linalg.norm(embedding)

def get_embeddings_for_texts(texts: list[str]):
    """Batch embedding generation for efficiency"""
    embeddings = encode_text(texts)
    return embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
```

**Search Methods**:
- **Qdrant**: Vector database for persistent collections


---

## 🤖 AI Integration

### LLM Integration (Maritaca AI)

**Model**: Sabia-3 (Brazilian Portuguese optimized)

**Use Cases**:
1. **Text Correction** (`/api/memory/improve-text`)
   - Grammar and spelling correction
   - Coherence improvement
   - Maintains original meaning

2. **Story Generation** (`/api/art/generate-story`)
   - Generates narratives connecting artworks
   - Context-aware storytelling
   - Bilingual support (PT/EN)

**Implementation**:
```python
from clients import get_maritaca_client

client = get_maritaca_client()

def correct_text(raw_text: str, language: str) -> str:
    prompt = load_speech_correct_prompt(language)
    
    response = client.chat.completions.create(
        model="sabia-3",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": raw_text}
        ],
        temperature=0.7,
        max_tokens=2000
    )
    
    return response.choices[0].message.content
```

### Embedding Generation (DeepInfra)

**Model**: Qwen3-Embedding-4B

**Features**:
- 4096-dimensional dense embeddings
- Multilingual support
- High semantic accuracy
- API-based (no local GPU required)

**Implementation**:
```python
from clients import encode_text

def get_embedding(text: str):
    embeddings = encode_text([text])
    # Normalize for cosine similarity
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    return embeddings.astype("float32")
```

### Vector Search

#### Qdrant 

- **Index Type**: HNSW (approximate search)
- **Metric**: Cosine similarity
- **Collections**: wikiart, semart, ipiranga
- **Features**: Persistent storage, efficient updates

**Search Implementation**:
```python
from clients import get_qdrant_client

def search_similar_vectors(text: str, dataset: Dataset, k: int = 6):
    query_embedding = get_embedding(text)
    
    results = get_qdrant_client().search(
        collection_name=dataset.value,
        query_vector=query_embedding[0].tolist(),
        limit=k,
        with_payload=True
    )
    
    return results
```

### Text Processing

**Segmentation Algorithm**:

```python
def doTextSegmentation(mode: str, text: str, max_sections: int):
    sentences = _get_sentences(text)  # Regex-based sentence splitting
    
    if mode == "conservative":
        size = 3  # 3 sentences per segment
        step = 2  # Overlap of 1 sentence
    elif mode == "broader":
        size = 2  # 2 sentences per segment
        step = 1  # Overlap of 1 sentence
    
    sections = _get_sections(sentences, size, step, max_sections)
    return sections
```

---

## 🔒 Authentication & Security

### JWT Token Structure

```json
{
  "patientId": "uuid",      // For patient tokens
  "doctorId": "uuid",       // For doctor tokens
  "exp": 1234567890,        // Expiration timestamp
  "iat": 1234567890         // Issued at timestamp
}
```

### Password Security

- **Algorithm**: Bcrypt + SHA-256 hybrid
- **Process**:
  1. SHA-256 hash the password (handles long passwords)
  2. Bcrypt hash the SHA-256 result (adds salt and cost factor)

```python
def get_password_hash(password: str):
    sha256_password = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return pwd_context.hash(sha256_password)

def verify_password(plain_password: str, hashed_password: str):
    sha256_password = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
    return pwd_context.verify(sha256_password, hashed_password)
```

### Access Control

**Protected Routes**:
- All `/api/memory/*` endpoints require authentication
- All `/api/art/*` endpoints require authentication
- `/api/doctors/*` endpoints require doctor role
- `/api/sessions/*` endpoints role-dependent

**Authorization Flow**:
```python
@router.post("/save")
async def save_memory_reconstruction(
    request: SaveMemoryReconstructionRequestDTO,
    current_user: dict = Depends(get_current_user),  # Auth required
    db: Session = Depends(get_db)
):
    # current_user contains: {"id": "uuid", "role": "patient|doctor"}
    # Process request...
```

### CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## ⚙️ Configuration

### Environment Variables

The backend is configured via environment variables in `/webapp/env/.backend.env`:

```bash
# Database Configuration
DB_HOST=mysql
DB_PORT=3306
DB_USER=appuser
DB_PASSWORD=changeme_app
DB_NAME=artevoke

# Qdrant Vector Database
QDRANT_HOST=qdrant
QDRANT_PORT=6333

# API Configuration
API_HOST=0.0.0.0
API_PORT=5001
API_WORKERS=4

# Security
JWT_SECRET=your-secret-key-here-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=300

# LLM Configuration
MARITACA_API_KEY=your_maritaca_api_key_here

# Embedding Configuration
DEEPINFRA_API_KEY=your_deepinfra_api_key_here

# Static Files
STATIC_DIR=../data/static
```

### Database Connection

**Connection String Format**:
```python
mysql+pymysql://user:password@host:port/database
```

**Connection Pooling**:
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600    # Recycle connections after 1 hour
)
```

### Static File Serving

The API serves artwork images directly:

```python
app.mount(
    "/art-images/wikiart",
    StaticFiles(directory="../data/static/wikiart"),
    name="wikiart_images"
)

app.mount(
    "/art-images/semart",
    StaticFiles(directory="../data/static/semart"),
    name="semart_images"
)
```

**Image URLs**:
- WikiArt: `http://api.artevoke.com.br/art-images/wikiart/{filename}`
- SemArt: `http://api.artevoke.com.br/art-images/semart/{filename}`

---

## 🚀 Getting Started

### Prerequisites

- **Python** ≥ 3.10
- **UV package manager** (or pip)
- **MySQL** 8.0
- **Qdrant** vector database
- **API Keys**: Maritaca AI, DeepInfra

### Docker Deployment

**Using Docker Compose** (recommended):

```bash
cd /webapp
docker-compose up -d backend
```

**Configuration** (`docker-compose.yml`):
```yaml
backend:
  build:
    context: ./FastAPI
    dockerfile: Dockerfile
  container_name: artevoke_backend
  ports:
    - "5001:5001"
  env_file:
    - ./env/.backend.env
  volumes:
    - ./data/static:/app/../data/static:ro
    - ./data/embeddings:/app/../data/embeddings:ro
  depends_on:
    - mysql
    - qdrant
  networks:
    - app_network
```

---

## 📚 API Documentation

FastAPI automatically generates interactive API documentation:

### Swagger UI (OpenAPI)

**URL**: `http://localhost:5001/docs`

Features:
- Interactive endpoint testing
- Request/response schemas
- Authentication testing
- Model definitions

### ReDoc

**URL**: `http://localhost:5001/redoc`

Features:
- Clean, readable documentation
- Detailed schema definitions
- Code samples

### OpenAPI Schema

**URL**: `http://localhost:5001/openapi.json`

Raw OpenAPI 3.0 specification for API clients and code generation.

---

## 🛠️ Technology Stack

### Core Framework

- **FastAPI** 0.115.11 - Modern async web framework
- **Uvicorn** 0.34.0 - ASGI server
- **Pydantic** 2.10.6 - Data validation
- **Python-dotenv** 1.0.1 - Environment management

### Database & ORM

- **SQLAlchemy** 2.0.36 - ORM and query builder
- **PyMySQL** 1.1.1 - MySQL driver
- **Alembic** 1.14.0 - Database migrations (optional)

### Authentication & Security

- **Passlib[bcrypt]** 1.7.4 - Password hashing
- **Python-jose** 3.4.0 - JWT encoding/decoding
- **Bcrypt** 4.0.1 - Bcrypt implementation
- **Cryptography** 44.0.2 - Cryptographic primitives

### AI & Machine Learning

- **OpenAI** 1.58.1 - OpenAI API client (DeepInfra compatible)
- **Qdrant-client** 1.15.1 - Vector database client
- **NumPy** (implicit) - Numerical operations

### NLP & Text Processing

- **Language-tool-python** 3.1.0 - Grammar checking (LanguageTool)

### External Services

- **Maritaca AI**: LLM for text correction and story generation
- **DeepInfra**: Embedding API (Qwen3-Embedding-4B)
- **Qdrant**: Vector database for semantic search
- **MySQL**: Relational database for structured data

---

## 🔄 Data Flow Examples

### Memory Reconstruction Flow

```
1. Frontend sends story text
   POST /api/memory/submit
   {
     "story": "I remember my grandmother's garden...",
     "language": "en",
     "dataset": "wikiart",
     "segmentation": "conservative",
     "max_images_per_section": 6
   }

2. Backend processes:
   a. Story segmentation (3 sentences per segment, overlap 1)
   b. Embedding generation (Qwen3-Embedding-4B via DeepInfra)
   c. Qdrant search (top-6 images per segment)
   d. Image metadata retrieval (MySQL)

3. Backend returns:
   {
     "sections": [
       {
         "section_text": "I remember my grandmother's garden...",
         "images": [
           {
             "id": "uuid",
             "image_url": "/art-images/wikiart/monet_garden.jpg",
             "caption": "Garden at Giverny by Claude Monet",
             "artist": "Claude Monet",
             "similarity_score": 0.89
           },
           ...
         ]
       },
       ...
     ]
   }
```

### Art Exploration Flow

```
1. Frontend sends keywords
   POST /api/art/search
   {
     "keywords": "sunset ocean peaceful",
     "dataset": "semart",
     "language": "en",
     "k": 12
   }

2. Backend processes:
   a. Embedding generation for keywords
   b. Qdrant vector search (top-12 results)
   c. Image metadata retrieval

3. User selects images from results

4. Frontend requests story generation
   POST /api/art/generate-story
   {
     "images": [
       {"id": "uuid1", "caption": "..."},
       {"id": "uuid2", "caption": "..."}
     ],
     "language": "en"
   }

5. Backend generates narrative:
   a. Constructs prompt with image captions
   b. Calls Maritaca AI LLM
   c. Parses and returns generated story

6. Backend returns:
   {
     "generated_story": "As the sun sets over the tranquil ocean..."
   }
```

---

## 🧪 Testing

### Manual Testing with cURL

**Authentication**:
```bash
# Doctor login
curl -X POST http://localhost:5001/api/doctors/login \
  -H "Content-Type: application/json" \
  -d '{"email": "doctor@example.com", "password": "password123"}'

# Response: {"access_token": "eyJhbGc...", "token_type": "bearer"}
```

**Memory Reconstruction**:
```bash
# Analyze story
curl -X POST http://localhost:5001/api/memory/submit \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "story": "I remember my childhood home...",
    "language": "en",
    "dataset": "wikiart",
    "segmentation": "conservative",
    "max_images_per_section": 6
  }'
```


---


## 🤝 Integration with Other Modules

### Frontend (React)

- **Communication**: REST API over HTTP/HTTPS
- **Authentication**: JWT Bearer tokens
- **Data Format**: JSON

### Database (MySQL)

- **Connection**: SQLAlchemy ORM
- **Pooling**: Connection pool for efficiency
- **Migrations**: Schema initialization via SQL scripts

### Vector Database (Qdrant)

- **Collections**: wikiart, semart, ipiranga
- **Snapshots**: Pre-built collections loaded on startup
- **Search**: HNSW index for fast approximate search

### Embedding Service (DeepInfra)

- **Model**: Qwen3-Embedding-4B
- **API**: OpenAI-compatible REST API
- **Rate Limiting**: Handled by DeepInfra

### LLM Service (Maritaca AI)

- **Model**: Sabia-3
- **API**: OpenAI-compatible REST API
- **Prompts**: Markdown templates in `/prompts` directory

---

## 📞 Support & Documentation

For more information about the full ArtEvoke platform:

- **Project Root README**: `/ArtEvoke/README.md`
- **Frontend Documentation**: `/webapp/frontend/README.md`
- **API Documentation**: `http://localhost:5001/docs` (when running)

---

## 📄 License

This project is part of a master's thesis research:

> Augusto Silva & Vinicius Alvarenga. "ArtEvoke: AI-powered platform to trigger memories in Alzheimer's patients using art imagery." Escola Politécnica da Universidade de São Paulo.

For usage permissions and citations, please contact the research team.

---

