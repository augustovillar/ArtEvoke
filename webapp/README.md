# VisualCuesApp

A full-stack web application built with **React** (frontend), **FastAPI** (backend), and **MongoDB** (database). This app is developed as part of a Masters Thesis undertaken by Marc Bejjani and Augusto Silva at the Université Catholique de Louvain, under the supervision of Professor Benoît Macq, presented in June of 2025.

# ArtEvoke

A full-stack web application built with **React** (frontend), **FastAPI** (backend), and **MongoDB** (database). This app is developed as part of a Masters Thesis undertaken by Marc Bejjani and Augusto Silva at the Université Catholique de Louvain, under the supervision of Professor Benoît Macq, presented in June of 2025.

This thesis explores how artificial intelligence can support non-drug interventions for people living with Alzheimer's disease (AD) through the use of visual stimuli and art. We present a prototype platform that combines large multimodal models (LMMs), large language models (LLMs), and embedding-based vector search to connect personal stories with curated artworks. Designed to assist memory recall and cognitive engagement, ArtEvoke generates personalized visual narratives or retrieves relevant paintings based on the user's story. Art is used not only as a memory trigger but also as a tool to promote emotional connection and engagement. The prototype is intended for testing in future therapeutic and research settings, particularly as a scalable support tool for caregivers and clinical practitioners. We evaluate model performance, retrieval effectiveness using FAISS, and user interaction design with a focus on accessibility. These findings highlight the potential of AI tools to support scalable cognitive stimulation in dementia care.

---

## 🚀 Features

### Core Platform
- 🌐 **Frontend**: React.js with dynamic user interface and internationalization (PT/EN)
- ⚙️ **Backend**: FastAPI with async support and AI model integration
- 💾 **Database**: MongoDB for user data and session management
- 🐳 **Containerized**: Each component (frontend, backend, nginx) runs in its own Docker container
- 🌍 **Production-Ready**: Includes an NGINX reverse proxy for deployment

### AI-Powered Functionality
- 🎨 **Art Search**: Semantic search across curated art datasets using FAISS vector embeddings
- 📖 **Story Generation**: AI-powered narrative creation based on selected artworks
- 🧠 **Memory Reconstruction**: Interactive evaluation system for cognitive assessment
- 🖼️ **Art Exploration**: Guided art discovery with evaluation capabilities

### Therapeutic Features
- 👤 **User Management**: Secure authentication and profile management
- 📊 **Session Tracking**: Dual-mode architecture (in-session vs out-of-session)
- 🔄 **Interruption System**: Seamless session interruption and resumption
- 📈 **Progress Evaluation**: Comprehensive assessment tools for memory and recall
- 🎯 **Accessibility**: Designed for elderly users and caregivers

---

## 📁 Project Structure

```
webapp/
├── docker-compose.yml           # Docker configuration
├── data/                        # ✅ Persistent data (Docker volumes)
│   ├── static/                  # Static images
│   │   ├── semart/              # SemArt dataset images
│   │   ├── wikiart/             # WikiArt dataset images
│   │   └── museum/              # Museum dataset images
│   ├── embeddings/              # FAISS indices and metadata
│   │   ├── *.faiss              # FAISS index files
│   │   └── *.pkl                # Metadata files
│   ├── db/                      # Database files
│   └── uploads/                 # User uploads
├── FastAPI/                     # Backend code (rebuild without losing data)
├── frontend/                    # Frontend code (hot reload)
└── nginx/                       # NGINX configuration
```

### New Structure Benefits

1. **Rebuild without data loss**: Code can be rebuilt without affecting data
2. **Persistent volumes**: Data maintained between container restarts
3. **Clear organization**: Separation between code and data
4. **Hot reload**: Frontend can be updated quickly

### Docker Volumes

All persistent data is mapped as volumes in docker-compose.yml:
- `./data:/app/data` - Maps entire data structure to container

### Configuration

- **STATIC_DIR**: Set to `../data/static` in container environment
- **Database**: SQLite in `../data/db/`
- **FAISS**: Indices in `../data/embeddings/`

```
ArtEvoke/webapp/
├── FastAPI/                     # Backend service (FastAPI)
│   ├── main.py                  # Entry point for the FastAPI app
│   ├── routes/                  # API endpoint definitions
│   │   ├── art_routes.py        # Art search and story generation
│   │   └── user_routes.py       # User management and sessions
│   ├── utils/                   # Utility functions
│   │   ├── embeddings.py        # FAISS and embedding operations
│   │   ├── text_processing.py   # NLP and text utilities
│   │   └── auth.py              # Authentication helpers
│   └── requirements.txt         # Python dependencies
├── frontend/                    # Frontend service (React)
│   ├── src/
│   │   ├── pages/               # Main application pages
│   │   │   ├── ArtExploration/  # Art discovery and evaluation
│   │   │   ├── MemoryReconstruction/ # Memory assessment tools
│   │   │   ├── Profile/         # User profile management
│   │   │   └── Auth/            # Login and registration
│   │   ├── components/          # Reusable UI components
│   │   ├── hooks/               # Custom React hooks
│   │   ├── contexts/            # React context providers
│   │   └── i18n/                # Internationalization (PT/EN)
│   └── package.json             # Frontend dependencies and scripts
├── nginx/                       # NGINX configuration
│   ├── nginx-prod.conf          # Production configuration
│   └── nginx-local.conf         # Local development configuration
├── data/                        # Persistent data (Docker volumes)
│   ├── static/                  # Art dataset images
│   ├── embeddings/              # FAISS indices and metadata
│   └── db/                      # Database files
├── docker-compose.yml           # Container orchestration
├── LICENSE                      # Project license
└── README.md                    # Project documentation
```

---

## ⚙️ Getting Started

### Requirements
- Docker
- Docker Compose

### 1. Clone the Repository

```bash
git clone https://github.com/augustovillar/ArtEvoke.git
cd ArtEvoke/webapp
```

### 2. Run the Application with Docker

```bash
docker-compose up --build
```

Com Logs:

```bash
docker compose up -d --build && docker compose logs -f
```

### 3. Access the Application

Once running, you can access:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

---

## 🔧 Development

### Environment Setup

The application uses environment variables for configuration. Key variables include:
- `STATIC_DIR`: Path to static art images
- `DATABASE_URL`: MongoDB connection string
- `API_KEYS`: External service integrations

### Art Datasets

The platform integrates three major art datasets:
- **WikiArt**: Comprehensive art history collection
- **SemArt**: Semantic art annotations
- **Museum Collections**: Curated museum pieces

### AI Models

- **Embeddings**: Sentence transformers for semantic search
- **LLM**: Maritaca AI for story generation
- **FAISS**: Vector similarity search for art retrieval

---

## 🧪 Testing & Evaluation

The platform includes comprehensive evaluation systems:

### Memory Reconstruction
- Object recall questions with distractors
- Session interruption and resumption
- Progress tracking and scoring

### Art Exploration
- Image recall assessment
- Objective questioning system
- Dual-mode evaluation (session/out-of-session)

### Metrics
- Retrieval effectiveness using FAISS
- User interaction analytics
- Cognitive engagement measurements

---

## 🚀 Deployment

### Production Environment

For production deployment, ensure:
1. Proper SSL certificates for NGINX
2. Environment variables configured
3. Database backups automated
4. Static assets properly served

### Scaling Considerations

- MongoDB replica sets for high availability
- Load balancing for multiple frontend instances
- Caching strategies for art search results
- CDN integration for static art images

---

## 🎯 Recent Updates

### Art Exploration Evaluation System
- Complete evaluation workflow with image recall and objective questions
- Dual-mode architecture supporting both in-session and out-of-session flows
- Dynamic UX that adapts based on user context (session vs standalone mode)
- Integration with interruption system for seamless session management

### Memory Reconstruction Enhancements
- Comprehensive evaluation system with progress tracking
- Object recall questions with visual distractors
- Session interruption and resumption capabilities
- Detailed scoring and assessment metrics

### Technical Improvements
- Component reusability between evaluation systems
- Internationalization support for Portuguese and English
- Modular CSS architecture with scoped styling
- Enhanced error handling and user feedback systems

---

## 📚 Research Context

This platform serves as a research tool for studying:
- **Cognitive Stimulation**: Effects of art-based interventions on memory
- **AI in Healthcare**: Application of LMMs and LLMs in therapeutic settings
- **User Experience**: Accessibility design for elderly users and caregivers
- **Scalability**: Potential for widespread adoption in clinical settings

The evaluation systems provide quantitative metrics for research analysis while maintaining an engaging user experience suitable for therapeutic applications.

---

## License

This project is licensed under the ISC License. See the [LICENSE](./LICENSE) file for details.


