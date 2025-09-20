# VisualCuesApp

A full-stack web application built with **React** (frontend), **FastAPI** (backend), and **MongoDB** (database). This app is developed as part of a Masters Thesis undertaken by Marc Bejjani and Augusto Silva at the Université Catholique de Louvain, under the supervision of Professor Benoît Macq, presented in June of 2025.

This thesis explores how artificial intelligence can support non-drug interventions for people living with Alzheimer’s disease (AD) through the use of visual stimuli and art. We present a prototype platform that combines large multimodal models (LMMs), large language models (LLMs), and embedding-based vector search to connect personal stories with curated artworks. Designed to assist memory recall and cognitive engagement, ArtEvoke generates personalized visual narratives or retrieves relevant paintings based on the user’s story. Art is used not only as a memory trigger but also as a tool to promote emotional connection and engagement. The prototype is intended for testing in future therapeutic and research settings, particularly as a scalable support tool for caregivers and clinical practitioners. We evaluate model performance, retrieval effectiveness using FAISS, and user interaction design with a focus on accessibility. These findings highlight the potential of AI tools to support scalable cognitive stimulation in dementia care.

---

## 🚀 Features

- 🌐 **Frontend**: React.js with dynamic user interface
- ⚙️ **Backend**: FastAPI with async support
- 💾 **Database**: MongoDB
- 🐳 **Containerized**: Each component (frontend, backend, nginx) runs in its own Docker container
- 🌍 **Production-Ready**: Includes an NGINX reverse proxy for deployment

---

## 📁 Project Structure

<pre> project-root/ ├── FastAPI/ # Backend service (FastAPI) │ ├── main.py # Entry point for the FastAPI app │ └── new_venv/ # Python virtual environment ├── frontend/ # Frontend service (React) │ ├── src/ # React source files │ └── package.json # Frontend dependencies and scripts ├── nginx/ # NGINX config for production deployment │ └── default.conf # NGINX site configuration ├── docker-compose.yml # Orchestrates frontend, backend, and nginx containers ├── LICENSE # Project license (ISC) ├── README.md # Project documentation ├── package.json # Root-level scripts and config (e.g. for concurrently) </pre>

---

## ⚙️ Getting Started

### Requirements
- Docker
- Docker Compose

### 1. Clone the Repository

```bash
git clone https://github.com/MarcBejjani/VisualCuesApp.git
cd VisualCuesApp
```

### 2. Run the Application with Docker

```bash
docker-compose up --build
```


---

## License

This project is licensed under the ISC License. See the [LICENSE](./LICENSE) file for details.


