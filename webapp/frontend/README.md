# 🎨 ArtEvoke Frontend

The frontend of **ArtEvoke** is a React-based web application designed to support cognitive therapy for Alzheimer's patients through art-based memory interventions. The platform provides two main therapeutic modalities: **Memory Reconstruction** and **Art Exploration**, along with comprehensive session management and accessibility features.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Key Features](#key-features)
- [Project Structure](#project-structure)
- [Core Modules](#core-modules)
- [API Integration](#api-integration)
- [User Workflows](#user-workflows)
- [Accessibility Features](#accessibility-features)
- [Internationalization](#internationalization)
- [Getting Started](#getting-started)
- [Available Scripts](#available-scripts)
- [Technology Stack](#technology-stack)

---

## 🌟 Overview

ArtEvoke's frontend provides an intuitive interface for doctors and patients to interact with AI-powered art therapy tools. The application connects personal memories to visual artworks, helping trigger and reconstruct memories through carefully selected images from curated art databases.

### Purpose

- **For Doctors**: Create and manage patient profiles, configure therapeutic sessions, monitor patient progress
- **For Patients**: Participate in guided or free-mode therapy sessions using art exploration and memory reconstruction
- **For Caregivers**: Facilitate accessible, bilingual therapeutic experiences with voice input and text-to-speech support

---

## 🏗️ Architecture

The frontend follows a **component-based architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                     User Interface                       │
│  (React Components + Bootstrap 5 + Custom CSS)          │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                   Application Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Contexts   │  │  Custom Hooks│  │    Utils     │ │
│  │ - Auth       │  │ - useStory   │  │ - Token      │ │
│  │ - Theme      │  │ - useImage   │  │ - Speech     │ │
│  │ - ReadAloud  │  │ - useSave    │  │ - Time       │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                      API Layer                          │
│  (RESTful communication with FastAPI Backend)           │
│  - Authentication Endpoints                             │
│  - Memory Reconstruction API                            │
│  - Art Exploration API                                  │
│  - Session Management API                               │
│  - Evaluation API                                       │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────┐
│                    Other Services           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  FastAPI │  │  MySQL   │  │  Qdrant  │   │
│  │   API    │  │   DB     │  │  Vector  │   │
│  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────┘
```

### Data Flow

1. **User Interaction** → React components capture user input
2. **State Management** → Context providers maintain global state
3. **API Calls** → Fetch requests to FastAPI backend
4. **Backend Processing** → AI models process data (LLM, embedding search)
5. **Response Handling** → Components update UI with results
6. **Persistence** → Data saved to MySQL database

---

## ✨ Key Features

### 🧠 Memory Reconstruction

Transform personal stories into visual narratives:

- **Text/Speech Input**: Users narrate personal memories via typing or voice input
- **Text Correction**: AI-powered grammar and coherence improvement
- **Story Segmentation**: Intelligent segmentation into meaningful phrases
- **Image Retrieval**: Qdrant semantic search across art databases (WikiArt, SemArt, Ipiranga)
- **Image Selection**: Interactive grid for choosing relevant artwork
- **Progress Tracking**: Save and resume reconstruction sessions

### 🎨 Art Exploration

Discover artwork through keyword-driven exploration:

- **Keyword Search**: Natural language search across art collections
- **Multi-Image Selection**: Choose multiple artworks that resonate
- **Story Generation**: AI generates contextual narratives connecting selected artworks
- **Interactive Regeneration**: Refine generated stories
- **Dataset Selection**: Choose between WikiArt, SemArt, or Ipiranga collections

### 👨‍⚕️ Session Management

Comprehensive tools for healthcare professionals:

- **Patient Profiles**: Create and manage patient information
- **Session Configuration**: Set up guided therapy sessions with:
  - Activity selection (Memory Reconstruction / Art Exploration)
  - Dataset selection
  - Time limits and interruption handling
  - Pre/post-session evaluations
- **Progress Monitoring**: Track patient engagement and results
- **Evaluation Tools**: Cognitive assessment questionnaires

### ♿ Accessibility

Built for users with diverse needs:

- **Theme Switching**: High contrast, soft, and default themes
- **Font Size Adjustment**: Dynamic text scaling
- **Text-to-Speech**: Read-aloud functionality for all content
- **Voice Input**: Speech recognition for text entry
- **Bilingual Support**: Full Portuguese and English localization

---

## 📁 Project Structure

```
frontend/
├── public/                          # Static assets
│   ├── index.html                   # HTML template
│   ├── manifest.json                # PWA manifest
│   ├── ae_example/                  # Art Exploration examples
│   └── mr_example/                  # Memory Reconstruction examples
│
├── src/
│   ├── App.js                       # Main application component with routing
│   ├── index.js                     # React DOM entry point
│   │
│   ├── assets/                      # Images and static resources
│   │   └── images/
│   │
│   ├── components/                  # Reusable UI components
│   │   ├── common/                  # Shared components
│   │   │   ├── ConsentForm/         # LGPD consent form
│   │   │   ├── ErrorModal/          # Error display modal
│   │   │   ├── Footer/              # Application footer
│   │   │   ├── Navbar/              # Navigation bar with auth state
│   │   │   ├── ProtectedRoute/      # Route authentication wrapper
│   │   │   └── Toast/               # Toast notifications
│   │   ├── interruptionModal/       # Session timeout handler
│   │   ├── languageSelector/        # Language switcher (PT/EN)
│   │   ├── Timer/                   # Session countdown timer
│   │   └── ui/                      # Accessibility UI components
│   │       ├── AccessibilityPanel/  # Accessibility controls panel
│   │       ├── FontSizeAdjuster/    # Font size controls
│   │       ├── ReadAloudButton/     # TTS button
│   │       └── QuestionReadAloudButton/ # TTS for questions
│   │
│   ├── config/                      # Configuration files
│   │   └── interruption.config.js   # Session interruption settings
│   │
│   ├── constants/                   # Application constants
│   │   └── questionTypes.js         # Evaluation question types
│   │
│   ├── contexts/                    # React Context providers
│   │   ├── AuthContext.js           # Authentication state management
│   │   ├── ThemeContext.js          # Theme state management
│   │   └── ReadAloudContext.js      # TTS state management
│   │
│   ├── features/                    # Feature-specific modules
│   │   └── speech/
│   │       └── SpeechInput.jsx      # Voice input component
│   │
│   ├── hooks/                       # Custom React hooks
│   │   └── useTextToSpeech.js       # TTS functionality hook
│   │
│   ├── i18n/                        # Internationalization
│   │   ├── index.js                 # i18next configuration
│   │   ├── detector.js              # Language detection
│   │   └── translations/            # Translation files
│   │       ├── en/                  # English translations
│   │       └── pt/                  # Portuguese translations
│   │
│   ├── pages/                       # Application pages/views
│   │   ├── About/                   # About page
│   │   ├── Home/                    # Landing page
│   │   ├── Profile/                 # User profile page
│   │   │
│   │   ├── Auth/                    # Authentication pages
│   │   │   ├── RoleSelection/       # Doctor/Patient selection
│   │   │   ├── Login/               # General login
│   │   │   ├── SignUp/              # General signup
│   │   │   ├── DoctorLogin/         # Doctor login
│   │   │   ├── DoctorSignUp/        # Doctor registration
│   │   │   ├── PatientLogin/        # Patient login
│   │   │   └── PatientComplete/     # Patient profile completion
│   │   │
│   │   ├── ArtExploration/          # Art Exploration module
│   │   │   ├── ArtExplorationFree.js      # Free mode
│   │   │   ├── ArtExplorationSession.js   # Session mode
│   │   │   ├── components/                 # AE-specific components
│   │   │   │   ├── InstructionsSection.js
│   │   │   │   ├── KeywordInputForm.js
│   │   │   │   ├── ImageSelection.js
│   │   │   │   └── GeneratedStory.js
│   │   │   ├── hooks/                      # AE-specific hooks
│   │   │   └── Evaluation/                 # Post-activity evaluation
│   │   │
│   │   ├── MemoryReconstruction/   # Memory Reconstruction module
│   │   │   ├── MemoryReconstructionFree.js      # Free mode
│   │   │   ├── MemoryReconstructionSession.js   # Session mode
│   │   │   ├── components/                       # MR-specific components
│   │   │   │   ├── InstructionsSection.js
│   │   │   │   ├── StoryInputForm.js
│   │   │   │   └── ImageSelectionGrid.js
│   │   │   ├── hooks/                            # MR-specific hooks
│   │   │   │   ├── useStorySubmit.js
│   │   │   │   ├── useImageSelection.js
│   │   │   │   └── useSave.js
│   │   │   └── Evaluation/                       # Post-activity evaluation
│   │   │
│   │   ├── Patients/                # Patient management
│   │   │   ├── Patients.js          # Patient list
│   │   │   └── CreatePatient.js     # Patient creation form
│   │   │
│   │   └── Sessions/                # Session management
│   │       ├── Sessions.js          # Session list
│   │       ├── CreateSession.js     # Session creation
│   │       ├── SessionDetails.js    # Session details view
│   │       ├── SessionResults.js    # Session results and evaluations
│   │       └── components/
│   │           ├── PreEvaluationModal.js
│   │           └── PosEvaluationModal.js
│   │
│   ├── styles/                      # Global styles
│   │   ├── App.css                  # Main app styles
│   │   └── index.css                # Base styles
│   │
│   └── utils/                       # Utility functions
│       ├── speech.js                # Speech recognition utilities
│       ├── timeFormatter.js         # Time formatting helpers
│       └── token.js                 # JWT token utilities
│
├── Dockerfile                       # Docker configuration
├── package.json                     # Dependencies and scripts
└── README.md                        # This file
```

---

## 🔧 Core Modules

### 1. Memory Reconstruction Module

**Purpose**: Help patients reconstruct personal memories through art selection.

**Workflow**:
```
User Input (Text/Voice)
    ↓
Text Correction (LLM)
    ↓
Story Segmentation
    ↓
Semantic Search (Qdrant)
    ↓
Image Results Display
    ↓
User Selection
    ↓
Save to Database
```

**Key Components**:
- `StoryInputForm`: Text/voice input with language selection
- `ImageSelectionGrid`: Multi-section image selection interface
- `useStorySubmit`: Hook for story processing
- `useImageSelection`: Hook for managing image selections
- `useSave`: Hook for persisting reconstruction data

**API Endpoints**:
- `POST /api/memory/improve-text` - Text correction
- `POST /api/memory/submit` - Story segmentation and image retrieval
- `POST /api/memory/save` - Save reconstruction

### 2. Art Exploration Module

**Purpose**: Enable keyword-based art discovery and narrative generation.

**Workflow**:
```
Keyword Input
    ↓
Semantic Search (Qdrant)
    ↓
Image Results Display
    ↓
Multi-Image Selection
    ↓
Story Generation (LLM)
    ↓
Display Generated Narrative
    ↓
Save to Database
```

**Key Components**:
- `KeywordInputForm`: Keyword and dataset selection
- `ImageSelection`: Image selection with generation trigger
- `GeneratedStory`: Display and regenerate AI narratives
- `useImageSearch`: Hook for keyword search
- `useStoryGeneration`: Hook for narrative generation

**API Endpoints**:
- `POST /api/art/search` - Keyword-based image search
- `POST /api/art/generate-story` - Generate narrative
- `POST /api/art/save` - Save exploration

### 3. Session Management Module

**Purpose**: Structure and monitor therapeutic sessions.

**Features**:
- **Session Configuration**: Activity type, dataset, time limits
- **Patient Assignment**: Link sessions to patient profiles
- **Evaluation Integration**: Pre/post cognitive assessments
- **Progress Tracking**: Monitor session completion and outcomes

**Key Components**:
- `CreateSession`: Session configuration form
- `Sessions`: Session list with filtering
- `SessionDetails`: Detailed session view
- `SessionResults`: Session outcomes and evaluations
- `PreEvaluationModal` / `PosEvaluationModal`: Assessment forms

**API Endpoints**:
- `POST /api/sessions/` - Create session
- `GET /api/sessions/{id}` - Get session details
- `GET /api/sessions/my-sessions` - List user sessions
- `POST /api/sessions/{id}/pre-evaluation` - Submit pre-evaluation
- `POST /api/sessions/{id}/pos-evaluation` - Submit post-evaluation
- `GET /api/sessions/{id}/results` - Get session results

### 4. Authentication System

**Purpose**: Secure access with role-based permissions.

**User Roles**:
- **Doctor**: Full access to patient management and session creation
- **Patient**: Access to assigned sessions and free-mode activities

**Authentication Flow**:
```
Role Selection (Doctor/Patient)
    ↓
Login/Signup Form
    ↓
JWT Token Generation
    ↓
Token Storage (localStorage)
    ↓
Automatic Token Validation
    ↓
Protected Route Access
```

**Key Components**:
- `AuthContext`: Global authentication state
- `ProtectedRoute`: Route guard component
- Token validation with expiration checking

**API Endpoints**:
- `POST /api/doctors/signup` - Doctor registration
- `POST /api/doctors/login` - Doctor login
- `POST /api/patients/login` - Patient login
- `POST /api/signup` - General signup

---

## 🔌 API Integration

### Backend Connection

The frontend communicates with a **FastAPI** backend through RESTful endpoints. All requests include JWT authentication tokens in headers.

**Base Configuration**:
```javascript
const token = localStorage.getItem('token');
const headers = {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json',
};
```

### Key API Routes

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/memory/submit` | POST | Process story and retrieve images |
| `/api/memory/improve-text` | POST | Correct text with LLM |
| `/api/memory/save` | POST | Save memory reconstruction |
| `/api/art/search` | POST | Search images by keywords |
| `/api/art/generate-story` | POST | Generate narrative from images |
| `/api/art/save` | POST | Save art exploration |
| `/api/sessions/` | GET/POST | List/create sessions |
| `/api/sessions/{id}` | GET | Get session details |
| `/api/doctors/patients` | GET/POST | List/create patients |
| `/api/evaluation/create` | POST | Submit evaluation |

### Integration with Backend Services

```
Frontend (React)
    ↓
FastAPI Backend
    ↓
┌────────────────┬──────────────┬
│   MySQL DB     │   Qdrant     │
│  (Structured)  │  (Vectors)   │ 
└────────────────┴──────────────┴
         ↓                ↓              
    User Data      Vector Search   
    Sessions       Collection       
    Evaluations    Management       
```

---

## 👥 User Workflows

### Patient Workflow (Free Mode)

1. **Login** → Patient authentication
2. **Choose Activity** → Memory Reconstruction or Art Exploration
3. **Input Story/Keywords** → Text or voice input
4. **Select Images** → Choose from AI-retrieved artwork
5. **Generate/View Results** → AI-generated narratives
6. **Save Progress** → Store for future reference

### Patient Workflow (Session Mode)

1. **Login** → Patient authentication
2. **Access Assigned Session** → Guided activity
3. **Pre-Evaluation** (optional) → Cognitive assessment
4. **Perform Activity** → Time-limited interaction
5. **Post-Evaluation** (optional) → Cognitive assessment
6. **Session Completion** → Results saved automatically

### Doctor Workflow

1. **Login** → Doctor authentication
2. **Create Patient Profile** → Register patient information
3. **Configure Session** → Set activity, dataset, time, evaluations
4. **Assign to Patient** → Link session to patient
5. **Monitor Progress** → View session results
6. **Review Evaluations** → Analyze cognitive assessments

---

## ♿ Accessibility Features

### Visual Accessibility

- **Theme Options**:
  - Default theme
  - High-contrast theme (enhanced visibility)
  - Soft theme (reduced eye strain)
- **Font Size Adjustment**: 5 size levels (XS to XL)
- **Responsive Design**: Mobile, tablet, desktop optimization

### Auditory Accessibility

- **Text-to-Speech**:
  - Read entire page content
  - Read individual questions
  - Configurable reading speed
- **Voice Input**:
  - Speech-to-text for story input
  - Automatic text correction
  - Multi-language support (PT/EN)

### Cognitive Accessibility

- **Clear Instructions**: Step-by-step guidance
- **Progress Indicators**: Visual feedback on activity status
- **Session Timers**: Clear time remaining displays
- **Interruption Warnings**: Alerts before session timeout

---

## 🌍 Internationalization

### Supported Languages

- **Portuguese (PT-BR)** - Primary language
- **English (EN)** - Secondary language

### Implementation

**Technology**: `react-i18next` + `i18next`

**Structure**:
```
i18n/
├── translations/
│   ├── en/
│   │   ├── common.json      # Common translations
│   │   ├── auth.json        # Authentication
│   │   ├── pages.json       # Page-specific
│   │   └── accessibility.json
│   └── pt/
│       ├── common.json
│       ├── auth.json
│       ├── pages.json
│       └── accessibility.json
```

**Persistence**: Language preference stored in `localStorage`

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** ≥ 16.x
- **npm** ≥ 8.x
- **Backend services** running (FastAPI, MySQL, Qdrant)

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/augustovillar/ArtEvoke.git
cd ArtEvoke/webapp/frontend
```

2. **Install dependencies**:
```bash
npm install
```

3. **Environment Configuration**:

The frontend connects to the backend through the configured proxy or direct URLs. Ensure the backend is running at the expected location.

### Docker Deployment

The frontend can be deployed as part of the full stack using Docker Compose:

```bash
cd ArtEvoke/webapp
docker-compose up -d frontend
```

**Docker Configuration**:
- **Image**: `node:16-alpine`
- **Port**: 3000
- **Build**: Multi-stage build for optimized production
- **Nginx**: Serves static files in production

---

## 🛠️ Technology Stack

### Core Framework

- **React** 19.0.0 - UI library
- **React Router DOM** 7.2.0 - Client-side routing
- **React Scripts** 5.0.1 - Build tooling (Create React App)

### UI & Styling

- **Bootstrap** 5.3.3 - CSS framework
- **Custom CSS Modules** - Component-specific styles
- **Responsive Design** - Mobile-first approach

### State Management

- **React Context API** - Global state management
  - `AuthContext` - Authentication state
  - `ThemeContext` - Theme preferences
  - `ReadAloudContext` - TTS state

### Internationalization

- **react-i18next** 13.0.0 - React bindings
- **i18next** 23.0.0 - Core i18n framework
- **i18next-browser-languagedetector** 7.0.0 - Language detection

### HTTP & API

- **Axios** 1.8.1 - HTTP client
- **Fetch API** - Native browser API for requests

### Testing

- **@testing-library/react** 16.2.0 - Component testing
- **@testing-library/jest-dom** 6.6.3 - Custom matchers
- **@testing-library/user-event** 13.5.0 - User interaction simulation

### Browser APIs

- **Web Speech API** - Voice input and TTS
- **localStorage** - Client-side data persistence
- **Service Workers** - PWA capabilities (optional)

### Development Tools

- **ESLint** - Code linting
- **Prettier** - Code formatting (if configured)
- **React DevTools** - Component inspection

---

## 📊 Component Architecture Diagram

```
App.js (Root)
├── AuthProvider
│   ├── ThemeProvider
│   │   └── ReadAloudProvider
│   │       ├── Navbar
│   │       │   ├── LanguageSelector
│   │       │   └── AccessibilityPanel
│   │       │       ├── FontSizeAdjuster
│   │       │       └── ReadAloudButton
│   │       │
│   │       ├── Routes
│   │       │   ├── Public Routes
│   │       │   │   ├── Home
│   │       │   │   ├── About
│   │       │   │   └── Auth/* (Login, Signup, etc.)
│   │       │   │
│   │       │   └── Protected Routes
│   │       │       ├── Profile
│   │       │       ├── Patients/*
│   │       │       ├── Sessions/*
│   │       │       ├── MemoryReconstruction (Free/Session)
│   │       │       │   ├── InstructionsSection
│   │       │       │   ├── StoryInputForm
│   │       │       │   │   └── SpeechInput
│   │       │       │   ├── ImageSelectionGrid
│   │       │       │   └── Evaluation
│   │       │       │
│   │       │       └── ArtExploration (Free/Session)
│   │       │           ├── InstructionsSection
│   │       │           ├── KeywordInputForm
│   │       │           ├── ImageSelection
│   │       │           ├── GeneratedStory
│   │       │           └── Evaluation
│   │       │
│   │       ├── Footer
│   │       ├── Toast
│   │       ├── ErrorModal
│   │       ├── InterruptionModal
│   │       └── Timer
```

---

## 🔒 Security Considerations

### Authentication

- **JWT tokens** with expiration validation
- **Token refresh** on expiration detection
- **Role-based access control** (Doctor/Patient)
- **Protected routes** with automatic redirect

### Data Protection

- **LGPD compliance** with consent forms
- **Secure localStorage** usage (tokens only)
- **HTTPS enforcement** in production
- **No sensitive data** in client-side code

### Best Practices

- Input sanitization on voice/text input
- XSS prevention through React's built-in escaping
- CORS configuration in backend
- Regular dependency updates

---

## 🤝 Integration with Other Modules

### Backend (FastAPI)

- **Location**: `/webapp/FastAPI`
- **Communication**: RESTful API over HTTP/HTTPS
- **Authentication**: JWT Bearer tokens
- **Data Format**: JSON

### Database (MySQL)

- **Access**: Through FastAPI ORM
- **Tables**: Users, Patients, Sessions, Evaluations, Art Items
- **Relationships**: Foreign keys managed by backend

### Vector Database (Qdrant)

- **Access**: Through FastAPI client
- **Purpose**: Semantic search for art exploration
- **Collections**: WikiArt, SemArt, Ipiranga


### Diagram: Full Stack Integration

```
┌─────────────────────────────────────────────┐
│           Frontend (React)                   │
│  Port: 3000 (dev) / Nginx (prod)            │
└──────────────────┬──────────────────────────┘
                   │ HTTP/HTTPS
┌──────────────────▼──────────────────────────┐
│         Nginx Reverse Proxy                 │
│  Routes: /api → Backend, / → Frontend       │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│        FastAPI Backend (Python)             │
│  Port: 8000                                 │
│  Services: Authentication, Image Search,    │
│            Story Generation, Session Mgmt   │
└─────┬─────────┬─────────────────────────────┘
      │         │         
      ▼         ▼         
┌─────────┐ ┌─────────┐
│  MySQL  │ │ Qdrant  │ 
│  Port:  │ │ Port:   │ 
│  3306   │ │  6333   │ 
└─────────┘ └─────────┘ 
```

---

## 📞 Support & Documentation

For more information about the full ArtEvoke platform:

- **Project Root README**: `/ArtEvoke/README.md`
- **Backend Documentation**: `/webapp/FastAPI/README.md` (if available)
- **API Documentation**: Access FastAPI's auto-generated docs at `/docs` when backend is running

---

## 📄 License

This project is part of a master's thesis research:

> Augusto Silva & Vinicius Alvarenga. "ArtEvoke: AI-powered platform to trigger memories in Alzheimer's patients using art imagery." Escola Politécnica da Universidade de São Paulo.
For usage permissions and citations, please contact the research team.

---
