# eviStream Production Migration Guide

**From Streamlit Prototype to Production-Ready Platform**

Version: 1.0
Last Updated: 2026-01-15
Timeline: 4-8 weeks (Solo Developer)
Estimated Effort: 150-200 hours

---

## Table of Contents

1. [Executive Overview](#executive-overview)
2. [Architecture Deep Dive](#architecture-deep-dive)
3. [Technology Stack](#technology-stack)
4. [Phase 1: Backend Development](#phase-1-backend-development)
5. [Phase 2: Frontend Development](#phase-2-frontend-development)
6. [Phase 3: Infrastructure Setup](#phase-3-infrastructure-setup)
7. [Phase 4: Testing & Quality Assurance](#phase-4-testing--quality-assurance)
8. [Phase 5: Deployment & Migration](#phase-5-deployment--migration)
9. [Monitoring & Observability](#monitoring--observability)
10. [Cost Analysis](#cost-analysis)
11. [Security Considerations](#security-considerations)
12. [Troubleshooting Guide](#troubleshooting-guide)
13. [Appendix](#appendix)

---

## Executive Overview

### Current State

eviStream currently runs as a **Streamlit application** with:
- Single-user local deployment
- File-based storage (`storage/` directory)
- Synchronous operations blocking the UI
- Manual execution via command line
- Limited scalability

### Target State

Transform eviStream into a **production-ready SaaS platform** with:
- Multi-tenant architecture with user authentication
- Cloud-native infrastructure (AWS ECS)
- Asynchronous job processing with real-time updates
- RESTful APIs for integration
- Horizontal scalability
- Professional web interface

### Key Benefits

**For Users:**
- ✅ Multi-user support with secure authentication
- ✅ Real-time job progress tracking
- ✅ Concurrent extraction jobs
- ✅ Persistent cloud storage
- ✅ Modern, responsive UI
- ✅ Mobile-friendly interface

**For Developers:**
- ✅ Clean API-first architecture
- ✅ Separation of concerns (frontend/backend/workers)
- ✅ Easy testing and debugging
- ✅ Horizontal scalability
- ✅ Infrastructure as code
- ✅ CI/CD ready

**For Operations:**
- ✅ Auto-scaling based on load
- ✅ Health monitoring and alerting
- ✅ Centralized logging
- ✅ Zero-downtime deployments
- ✅ Disaster recovery capabilities

### Migration Principles

1. **Preserve Core Logic** - Don't rewrite extraction/evaluation/code generation
2. **Wrap, Don't Replace** - Create service layers around existing code
3. **Incremental Migration** - Backend → Frontend → Infrastructure
4. **Test Continuously** - Validate each component before integration
5. **Monitor Everything** - Observability from day one

---

## Architecture Deep Dive

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Internet / Users                         │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Application Load      │
                    │      Balancer (ALB)     │
                    │   - HTTPS Termination   │
                    │   - Path-based Routing  │
                    └──────────┬──────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                       │
   ┌────▼─────┐         ┌─────▼──────┐        ┌─────▼──────┐
   │ Frontend │         │  Backend   │        │ WebSocket  │
   │ (Next.js)│         │  (FastAPI) │        │  Server    │
   │          │         │            │        │            │
   │ Port 3000│         │ Port 8000  │        │ Port 8000  │
   └──────────┘         └─────┬──────┘        └────────────┘
                              │
                 ┌────────────┼────────────┐
                 │            │            │
          ┌──────▼────┐  ┌───▼────┐  ┌───▼────────┐
          │  Celery   │  │ Redis  │  │  Supabase  │
          │  Workers  │  │ Queue  │  │ PostgreSQL │
          │           │  │ Cache  │  │            │
          └─────┬─────┘  └────────┘  └────────────┘
                │
          ┌─────▼─────┐
          │    S3     │
          │  Storage  │
          └───────────┘
```

### Component Responsibilities

#### **Frontend (Next.js + React)**
- **Purpose**: User interface and client-side logic
- **Technology**: Next.js 14+ (App Router), React, TypeScript, Tailwind CSS
- **Key Features**:
  - Server-side rendering for SEO
  - Client-side state management
  - WebSocket integration for real-time updates
  - File upload with progress tracking
  - Responsive design (mobile-friendly)

#### **Backend API (FastAPI)**
- **Purpose**: Business logic, authentication, API endpoints
- **Technology**: FastAPI, Python 3.11+, Pydantic, SQLAlchemy
- **Key Features**:
  - RESTful API with OpenAPI docs
  - JWT-based authentication
  - Request validation with Pydantic
  - Async/await support
  - WebSocket endpoints for real-time updates
  - Service layer pattern (wraps core logic)

#### **Background Workers (Celery)**
- **Purpose**: Long-running tasks (PDF processing, code generation, extraction)
- **Technology**: Celery, Python 3.11+
- **Key Features**:
  - Task queue with Redis broker
  - Automatic retry on failure
  - Progress tracking
  - Concurrent task execution
  - Task result storage

#### **Message Broker & Cache (Redis)**
- **Purpose**: Job queue, caching, session storage
- **Technology**: Redis 7+, AWS ElastiCache
- **Key Features**:
  - Celery message broker
  - Task result backend
  - Application cache (DSPy, evaluation)
  - Session management
  - Rate limiting

#### **Database (Supabase/PostgreSQL)**
- **Purpose**: Persistent data storage
- **Technology**: PostgreSQL 15+ (via Supabase)
- **Key Features**:
  - User accounts and authentication
  - Project metadata
  - Form definitions
  - Document metadata
  - Extraction results
  - Row-level security (RLS)

#### **Object Storage (AWS S3)**
- **Purpose**: File storage (PDFs, markdown, generated code)
- **Technology**: AWS S3, CloudFront CDN
- **Key Features**:
  - Versioned storage
  - Pre-signed URLs for secure access
  - CDN integration for fast access
  - Lifecycle policies for cost optimization

### Data Flow Diagrams

#### **1. User Registration & Authentication**

```
User Browser                    FastAPI Backend              Supabase
    │                                │                           │
    │ POST /api/v1/auth/register     │                           │
    ├────────────────────────────────>                           │
    │   {email, password, name}      │                           │
    │                                │ Hash password             │
    │                                │ INSERT INTO users         │
    │                                ├──────────────────────────>│
    │                                │                           │
    │                                │ <─────────────────────────┤
    │                                │   User created            │
    │                                │ Generate JWT token        │
    │ <──────────────────────────────┤                           │
    │   {token, user_id}             │                           │
    │                                │                           │
    │ Store token in localStorage    │                           │
    │                                │                           │
```

#### **2. PDF Upload & Processing**

```
User Browser          FastAPI           Celery Worker         S3         Supabase
    │                    │                    │                │              │
    │ POST /documents/   │                    │                │              │
    │    upload          │                    │                │              │
    ├───────────────────>│                    │                │              │
    │ {file, project_id} │                    │                │              │
    │                    │ Create doc record  │                │              │
    │                    ├────────────────────┼────────────────┼─────────────>│
    │                    │                    │                │              │
    │                    │ Upload PDF to S3   │                │              │
    │                    ├────────────────────┼───────────────>│              │
    │                    │                    │                │              │
    │                    │ Enqueue job        │                │              │
    │                    ├───────────────────>│                │              │
    │ <──────────────────┤                    │                │              │
    │ {job_id, doc_id}   │                    │                │              │
    │                    │                    │                │              │
    │ ─────WebSocket─────┼────────────────────┤                │              │
    │ Connected          │                    │                │              │
    │                    │                    │ Process PDF    │              │
    │                    │                    │ (Marker)       │              │
    │                    │                    │                │              │
    │ <──────Progress────┼────────────────────┤                │              │
    │ {progress: 50%}    │                    │                │              │
    │                    │                    │                │              │
    │                    │                    │ Upload markdown│              │
    │                    │                    ├───────────────>│              │
    │                    │                    │                │              │
    │                    │                    │ Update record  │              │
    │                    │                    ├────────────────┼──────────────>
    │                    │                    │                │              │
    │ <──────Completed───┼────────────────────┤                │              │
    │ {status: done}     │                    │                │              │
```

#### **3. Form Creation & Code Generation**

```
User Browser          FastAPI           Celery Worker        Supabase    File System
    │                    │                    │                 │              │
    │ POST /forms/       │                    │                 │              │
    ├───────────────────>│                    │                 │              │
    │ {name, fields}     │                    │                 │              │
    │                    │ Create form record │                 │              │
    │                    ├────────────────────┼─────────────────>              │
    │                    │                    │                 │              │
    │                    │ Enqueue generation │                 │              │
    │                    ├───────────────────>│                 │              │
    │ <──────────────────┤                    │                 │              │
    │ {job_id, form_id}  │                    │                 │              │
    │                    │                    │                 │              │
    │ ─────WebSocket─────┤                    │                 │              │
    │                    │                    │                 │              │
    │                    │                    │ LangGraph       │              │
    │                    │                    │ Workflow        │              │
    │ <──────Progress────┼────────────────────┤                 │              │
    │ {stage: decompose} │                    │                 │              │
    │                    │                    │                 │              │
    │                    │                    │ Generate        │              │
    │                    │                    │ signatures.py   │              │
    │                    │                    │ modules.py      │              │
    │                    │                    ├─────────────────┼──────────────>
    │                    │                    │                 │              │
    │                    │                    │ Register schema │              │
    │                    │                    │                 │              │
    │                    │                    │ Update form     │              │
    │                    │                    ├─────────────────>              │
    │                    │                    │                 │              │
    │ <──────Completed───┼────────────────────┤                 │              │
    │ {status: active}   │                    │                 │              │
```

#### **4. Extraction Job Execution**

```
User Browser     FastAPI      Celery Worker    S3      DSPy Pipeline    Supabase
    │               │               │            │            │              │
    │ POST /extract │               │            │            │              │
    ├──────────────>│               │            │            │              │
    │ {form, docs}  │               │            │            │              │
    │               │ Enqueue job   │            │            │              │
    │               ├──────────────>│            │            │              │
    │ <─────────────┤               │            │            │              │
    │ {job_id}      │               │            │            │              │
    │               │               │            │            │              │
    │ ──WebSocket───┤               │            │            │              │
    │               │               │            │            │              │
    │               │               │ For each doc:          │              │
    │               │               │                        │              │
    │               │               │ Download   │            │              │
    │               │               │ markdown   │            │              │
    │               │               ├───────────>│            │              │
    │               │               │            │            │              │
    │               │               │ Run        │            │              │
    │               │               │ extraction │            │              │
    │               │               ├────────────┼───────────>│              │
    │               │               │            │            │              │
    │ <──Progress───┼───────────────┤            │ Extract    │              │
    │ {doc 1/2}     │               │            │ fields     │              │
    │               │               │            │            │              │
    │               │               │ <──────────┼────────────┤              │
    │               │               │            │ Results    │              │
    │               │               │                        │              │
    │               │               │ Save results           │              │
    │               │               ├────────────┼────────────┼──────────────>
    │               │               │            │            │              │
    │ <──Completed──┼───────────────┤            │            │              │
    │ {results_id}  │               │            │            │              │
```

### Database Schema

#### **Core Tables**

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    full_name TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Projects table (updated with user_id)
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Project forms table (updated with status)
CREATE TABLE project_forms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    form_name TEXT NOT NULL,
    form_description TEXT,
    fields JSONB NOT NULL,
    status TEXT NOT NULL DEFAULT 'DRAFT',
    schema_name TEXT,
    task_dir TEXT,
    statistics JSONB,
    error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Project documents table (updated with S3 paths)
CREATE TABLE project_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    unique_filename TEXT,
    s3_pdf_path TEXT,
    s3_markdown_path TEXT,
    markdown_content_preview TEXT,
    processing_status TEXT DEFAULT 'PENDING',
    processing_error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Jobs table (new - tracks background jobs)
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
    job_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'PENDING',
    progress INTEGER DEFAULT 0,
    celery_task_id TEXT,
    input_data JSONB,
    result_data JSONB,
    error_message TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Extraction results table
CREATE TABLE extraction_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id) ON DELETE SET NULL,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    form_id UUID REFERENCES project_forms(id) ON DELETE SET NULL,
    document_id UUID REFERENCES project_documents(id) ON DELETE SET NULL,
    extracted_data JSONB NOT NULL,
    evaluation_metrics JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_project_forms_project_id ON project_forms(project_id);
CREATE INDEX idx_project_forms_status ON project_forms(status);
CREATE INDEX idx_project_documents_project_id ON project_documents(project_id);
CREATE INDEX idx_jobs_user_id ON jobs(user_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_created_at ON jobs(created_at DESC);
CREATE INDEX idx_extraction_results_job_id ON extraction_results(job_id);
CREATE INDEX idx_extraction_results_project_id ON extraction_results(project_id);
```

#### **Row-Level Security (RLS) Policies**

```sql
-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_forms ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE extraction_results ENABLE ROW LEVEL SECURITY;

-- Users can only see their own data
CREATE POLICY "Users can view own user record" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own user record" ON users
    FOR UPDATE USING (auth.uid() = id);

-- Projects: users can only see their own projects
CREATE POLICY "Users can view own projects" ON projects
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own projects" ON projects
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own projects" ON projects
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own projects" ON projects
    FOR DELETE USING (auth.uid() = user_id);

-- Forms: users can only access forms in their projects
CREATE POLICY "Users can view forms in own projects" ON project_forms
    FOR SELECT USING (
        project_id IN (SELECT id FROM projects WHERE user_id = auth.uid())
    );

-- Similar policies for documents, jobs, results...
```

---

## Technology Stack

### Backend Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **API Framework** | FastAPI | 0.109+ | RESTful API server |
| **Language** | Python | 3.11+ | Backend language |
| **ASGI Server** | Uvicorn | 0.27+ | Production ASGI server |
| **Task Queue** | Celery | 5.3+ | Background job processing |
| **Message Broker** | Redis | 7.0+ | Celery broker & cache |
| **ORM** | SQLAlchemy | 2.0+ | Database ORM |
| **Validation** | Pydantic | 2.5+ | Data validation |
| **Auth** | python-jose | 3.3+ | JWT token handling |
| **Password Hashing** | passlib | 1.7+ | Secure password hashing |
| **Database Client** | supabase-py | 2.3+ | Supabase client |
| **HTTP Client** | httpx | 0.26+ | Async HTTP requests |
| **Cloud SDK** | boto3 | 1.34+ | AWS S3 integration |

### Frontend Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | Next.js | 14.1+ | React framework |
| **UI Library** | React | 18.2+ | UI components |
| **Language** | TypeScript | 5.3+ | Type-safe JavaScript |
| **Styling** | Tailwind CSS | 3.4+ | Utility-first CSS |
| **Component Library** | shadcn/ui | latest | Pre-built components |
| **HTTP Client** | axios | 1.6+ | API requests |
| **State Management** | Zustand | 4.5+ | Global state |
| **Forms** | React Hook Form | 7.50+ | Form handling |
| **Validation** | Zod | 3.22+ | Schema validation |
| **WebSocket** | native WebSocket | - | Real-time updates |

### Infrastructure Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Container Platform** | AWS ECS Fargate | Serverless container orchestration |
| **Load Balancer** | AWS ALB | HTTPS termination, routing |
| **Container Registry** | AWS ECR | Docker image storage |
| **Cache** | AWS ElastiCache (Redis) | Distributed cache |
| **Object Storage** | AWS S3 | File storage |
| **CDN** | AWS CloudFront | Content delivery |
| **Database** | Supabase (PostgreSQL) | Managed database |
| **Secrets** | AWS Secrets Manager | Credential management |
| **Monitoring** | AWS CloudWatch | Logging & metrics |
| **IaC** | Terraform | Infrastructure as code |
| **CI/CD** | GitHub Actions | Automated deployment |

### Development Tools

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Containerization** | Docker | Local development |
| **Orchestration** | Docker Compose | Multi-container setup |
| **API Testing** | Postman | Manual API testing |
| **Load Testing** | Locust | Performance testing |
| **Code Quality** | Ruff | Python linting |
| **Type Checking** | mypy | Python type checking |
| **Testing** | pytest | Python unit tests |

---

## Phase 1: Backend Development

### 1.1 Project Setup

#### Directory Structure

Create the following structure:

```bash
cd /path/to/eviStream
mkdir -p backend/{app/{api/v1,models,services,workers,core},tests}
```

Complete structure:

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI app entry point
│   ├── config.py                    # Configuration management
│   ├── dependencies.py              # Dependency injection
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py            # Main API router
│   │       ├── auth.py              # Authentication endpoints
│   │       ├── projects.py          # Project CRUD
│   │       ├── documents.py         # Document management
│   │       ├── forms.py             # Form CRUD & generation
│   │       ├── extractions.py       # Extraction jobs
│   │       ├── results.py           # Results retrieval
│   │       └── websocket.py         # WebSocket endpoints
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py               # Pydantic models
│   │   ├── database.py              # SQLAlchemy models
│   │   └── enums.py                 # Enums (JobStatus, etc.)
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py          # Authentication logic
│   │   ├── extraction_service.py    # Extraction wrapper
│   │   ├── form_generation_service.py # Code gen wrapper
│   │   ├── pdf_processing_service.py  # PDF processing
│   │   ├── storage_service.py       # S3 abstraction
│   │   └── cache_service.py         # Redis caching
│   │
│   ├── workers/
│   │   ├── __init__.py
│   │   ├── celery_app.py            # Celery configuration
│   │   ├── extraction_tasks.py      # Extraction jobs
│   │   ├── pdf_tasks.py             # PDF processing jobs
│   │   └── generation_tasks.py      # Code generation jobs
│   │
│   └── core/                        # Symlink to ../core
│       → ../../core
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api/
│   ├── test_services/
│   └── test_workers/
│
├── requirements.txt
├── requirements-dev.txt
├── Dockerfile
├── .env.example
└── README.md
```

#### Create Symlink to Core Logic

```bash
cd backend/app
ln -s ../../core core
ln -s ../../dspy_components dspy_components
ln -s ../../schemas schemas
ln -s ../../utils utils
```

#### requirements.txt

```txt
# FastAPI and Server
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# Database and ORM
sqlalchemy==2.0.25
alembic==1.13.1
supabase==2.3.0

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0

# Task Queue
celery==5.3.6
redis==5.0.1

# AWS
boto3==1.34.34

# HTTP Client
httpx==0.26.0

# Validation
pydantic==2.5.3
pydantic-settings==2.1.0

# Existing dependencies (core logic)
dspy==2.0.0
streamlit==1.31.0
pandas==2.2.0
numpy==1.26.0
matplotlib==3.8.0
seaborn==0.13.0
scikit-learn==1.4.0
tiktoken==0.5.2
sentence-transformers==2.3.0
scipy==1.12.0
aiofiles==23.2.1
diskcache==5.6.3
```

#### requirements-dev.txt

```txt
-r requirements.txt

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
httpx==0.26.0

# Code Quality
ruff==0.1.14
mypy==1.8.0
black==24.1.1

# Load Testing
locust==2.20.0
```

### 1.2 Configuration Management

#### app/config.py

```python
"""
Application configuration management.
Loads settings from environment variables with sensible defaults.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "eviStream"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production

    # API
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # Security
    SECRET_KEY: str  # REQUIRED: Generate with: openssl rand -hex 32
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Database (Supabase)
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: str  # For admin operations

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_DB: int = 1
    REDIS_SESSION_DB: int = 2

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    CELERY_TASK_TIME_LIMIT: int = 3600  # 1 hour
    CELERY_TASK_SOFT_TIME_LIMIT: int = 3300  # 55 minutes

    # AWS
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "us-east-1"
    S3_BUCKET: str = "evistream-production"

    # File Upload
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100 MB
    ALLOWED_EXTENSIONS: set[str] = {"pdf"}

    # Core Logic (from existing config)
    DEFAULT_MODEL: str = "gemini/gemini-3-pro-preview"
    EVALUATION_MODEL: str = "gemini/gemini-2.5-flash"
    MAX_TOKENS: int = 20000
    TEMPERATURE: float = 1.0
    EVALUATION_TEMPERATURE: float = 0.0
    BATCH_CONCURRENCY: int = 5
    EVALUATION_CONCURRENCY: int = 20

    # Paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
    UPLOAD_DIR: Path = PROJECT_ROOT / "storage" / "uploads"
    CACHE_DIR: Path = PROJECT_ROOT / "cache"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
```

#### .env.example

```bash
# Application
DEBUG=true
ENVIRONMENT=development

# Security
SECRET_KEY=your-secret-key-here-generate-with-openssl-rand-hex-32

# Database (Supabase)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# Redis
REDIS_URL=redis://localhost:6379/0

# AWS
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
S3_BUCKET=evistream-production

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost"]

# LLM
GEMINI_API_KEY=your-gemini-key
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
```

### 1.3 Database Models

#### app/models/enums.py

```python
"""Enums for database models."""

from enum import Enum


class JobType(str, Enum):
    """Types of background jobs."""
    PDF_PROCESSING = "pdf_processing"
    FORM_GENERATION = "form_generation"
    EXTRACTION = "extraction"


class JobStatus(str, Enum):
    """Job execution status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class FormStatus(str, Enum):
    """Form generation status."""
    DRAFT = "draft"
    GENERATING = "generating"
    AWAITING_REVIEW = "awaiting_review"
    REGENERATING = "regenerating"
    ACTIVE = "active"
    FAILED = "failed"


class DocumentStatus(str, Enum):
    """Document processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
```

#### app/models/schemas.py

```python
"""Pydantic schemas for API request/response validation."""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from .enums import JobStatus, JobType, FormStatus, DocumentStatus


# ============================================================================
# Authentication Schemas
# ============================================================================

class UserRegister(BaseModel):
    """User registration request."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    """User login request."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    user_id: UUID


class UserResponse(BaseModel):
    """User information response."""
    id: UUID
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Project Schemas
# ============================================================================

class ProjectCreate(BaseModel):
    """Project creation request."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class ProjectUpdate(BaseModel):
    """Project update request."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    """Project response."""
    id: UUID
    user_id: UUID
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    # Counts
    forms_count: int = 0
    documents_count: int = 0

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Document Schemas
# ============================================================================

class DocumentUploadResponse(BaseModel):
    """Document upload response."""
    id: UUID
    filename: str
    unique_filename: str
    project_id: UUID
    job_id: UUID
    status: DocumentStatus


class DocumentResponse(BaseModel):
    """Document information response."""
    id: UUID
    project_id: UUID
    filename: str
    unique_filename: Optional[str]
    s3_pdf_path: Optional[str]
    s3_markdown_path: Optional[str]
    processing_status: DocumentStatus
    processing_error: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Form Schemas
# ============================================================================

class FieldDefinition(BaseModel):
    """Form field definition."""
    field_name: str
    field_description: str
    field_type: str  # text, number, enum, object, array
    field_control_type: Optional[str] = None  # dropdown, checkbox_group_with_text, etc.
    options: Optional[List[str]] = None
    example: Optional[str] = None
    extraction_hints: Optional[str] = None
    subform_fields: Optional[List['FieldDefinition']] = None


class FormCreate(BaseModel):
    """Form creation request."""
    project_id: UUID
    form_name: str = Field(..., min_length=1, max_length=255)
    form_description: str
    fields: List[FieldDefinition]
    enable_review: bool = False


class FormUpdate(BaseModel):
    """Form update request."""
    form_name: Optional[str] = None
    form_description: Optional[str] = None
    fields: Optional[List[FieldDefinition]] = None


class FormResponse(BaseModel):
    """Form response."""
    id: UUID
    project_id: UUID
    form_name: str
    form_description: Optional[str]
    fields: List[Dict[str, Any]]
    status: FormStatus
    schema_name: Optional[str]
    task_dir: Optional[str]
    statistics: Optional[Dict[str, Any]]
    error: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Extraction Schemas
# ============================================================================

class ExtractionCreate(BaseModel):
    """Extraction job creation request."""
    project_id: UUID
    form_id: UUID
    document_ids: List[UUID]


class ExtractionResponse(BaseModel):
    """Extraction job response."""
    job_id: UUID
    project_id: UUID
    form_id: UUID
    document_ids: List[UUID]
    status: JobStatus


class ExtractionResultResponse(BaseModel):
    """Extraction result response."""
    id: UUID
    job_id: UUID
    project_id: UUID
    form_id: UUID
    document_id: UUID
    extracted_data: Dict[str, Any]
    evaluation_metrics: Optional[Dict[str, Any]]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Job Schemas
# ============================================================================

class JobResponse(BaseModel):
    """Background job response."""
    id: UUID
    user_id: UUID
    project_id: Optional[UUID]
    job_type: JobType
    status: JobStatus
    progress: int
    celery_task_id: Optional[str]
    input_data: Optional[Dict[str, Any]]
    result_data: Optional[Dict[str, Any]]
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# WebSocket Messages
# ============================================================================

class WSMessage(BaseModel):
    """WebSocket message format."""
    event: str  # job.started, job.progress, job.completed, job.failed
    job_id: UUID
    data: Dict[str, Any]


# Resolve forward references
FieldDefinition.model_rebuild()
```

### 1.4 FastAPI Application

#### app/main.py

```python
"""
FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.config import settings
from app.api.v1.router import api_router


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-ready medical data extraction platform",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancer."""
    return JSONResponse(
        content={
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT
        }
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "eviStream API",
        "version": settings.APP_VERSION,
        "docs": "/api/docs"
    }


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={"detail": "Not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors."""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
```

#### app/api/v1/router.py

```python
"""
Main API router that combines all endpoint routers.
"""

from fastapi import APIRouter

from .auth import router as auth_router
from .projects import router as projects_router
from .documents import router as documents_router
from .forms import router as forms_router
from .extractions import router as extractions_router
from .results import router as results_router
from .websocket import router as websocket_router


api_router = APIRouter()

# Include all routers
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(projects_router, prefix="/projects", tags=["Projects"])
api_router.include_router(documents_router, prefix="/documents", tags=["Documents"])
api_router.include_router(forms_router, prefix="/forms", tags=["Forms"])
api_router.include_router(extractions_router, prefix="/extractions", tags=["Extractions"])
api_router.include_router(results_router, prefix="/results", tags=["Results"])
api_router.include_router(websocket_router, prefix="/ws", tags=["WebSocket"])
```

### 1.5 Authentication System

#### app/services/auth_service.py

```python
"""
Authentication service handling user registration, login, and JWT tokens.
"""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

from app.config import settings
from app.models.schemas import UserRegister, UserLogin, Token


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for authentication operations."""

    def __init__(self):
        self.pwd_context = pwd_context

    def hash_password(self, password: str) -> str:
        """Hash a password."""
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash."""
        return self.pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, user_id: UUID, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        if expires_delta is None:
            expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        expire = datetime.utcnow() + expires_delta

        to_encode = {
            "sub": str(user_id),
            "exp": expire,
            "iat": datetime.utcnow()
        }

        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

        return encoded_jwt

    def verify_token(self, token: str) -> UUID:
        """Verify JWT token and return user_id."""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            user_id: str = payload.get("sub")

            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials"
                )

            return UUID(user_id)

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )


# Global auth service instance
auth_service = AuthService()
```

#### app/dependencies.py

```python
"""
Dependency injection functions for FastAPI endpoints.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from uuid import UUID

from app.services.auth_service import auth_service
from app.config import settings


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UUID:
    """
    Dependency to get current authenticated user from JWT token.

    Usage:
        @router.get("/me")
        async def get_me(user_id: UUID = Depends(get_current_user)):
            return {"user_id": user_id}
    """
    token = credentials.credentials
    user_id = auth_service.verify_token(token)
    return user_id


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[UUID]:
    """
    Dependency to get current user if authenticated, None otherwise.
    """
    if credentials is None:
        return None

    try:
        token = credentials.credentials
        user_id = auth_service.verify_token(token)
        return user_id
    except HTTPException:
        return None
```

#### app/api/v1/auth.py

```python
"""
Authentication endpoints for user registration and login.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from supabase import create_client

from app.models.schemas import UserRegister, UserLogin, Token, UserResponse
from app.services.auth_service import auth_service
from app.config import settings
from app.dependencies import get_current_user
from uuid import UUID


router = APIRouter()

# Initialize Supabase client
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """
    Register a new user.

    - **email**: User email address
    - **password**: User password (min 8 characters)
    - **full_name**: Optional full name
    """
    try:
        # Check if user already exists
        existing = supabase.table("users").select("id").eq("email", user_data.email).execute()
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Hash password
        hashed_password = auth_service.hash_password(user_data.password)

        # Create user in database
        result = supabase.table("users").insert({
            "email": user_data.email,
            "hashed_password": hashed_password,
            "full_name": user_data.full_name,
            "is_active": True
        }).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )

        user = result.data[0]
        user_id = UUID(user["id"])

        # Generate access token
        access_token = auth_service.create_access_token(user_id)

        return Token(
            access_token=access_token,
            token_type="bearer",
            user_id=user_id
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """
    Login with email and password.

    Returns JWT access token on success.
    """
    try:
        # Get user from database
        result = supabase.table("users").select("*").eq("email", credentials.email).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        user = result.data[0]

        # Verify password
        if not auth_service.verify_password(credentials.password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        # Check if user is active
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )

        user_id = UUID(user["id"])

        # Generate access token
        access_token = auth_service.create_access_token(user_id)

        return Token(
            access_token=access_token,
            token_type="bearer",
            user_id=user_id
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(user_id: UUID = Depends(get_current_user)):
    """
    Get current user information.

    Requires authentication.
    """
    try:
        result = supabase.table("users").select("*").eq("id", str(user_id)).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return UserResponse(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
```

[Due to length limits, I'll continue with the remaining phases in the next section. This covers:
- Phase 1.1-1.5: Backend setup, config, database models, FastAPI app, and authentication
- The documentation follows the same detailed, production-ready style as COMPREHENSIVE_DOCUMENTATION.md
- Each section includes complete, copy-paste-ready code examples

Would you like me to continue with the remaining phases (1.6-1.9, Phase 2-5, monitoring, etc.)?]

### 1.6 Service Layer - Wrapping Core Logic

The service layer wraps existing core extraction logic without modification.

#### app/services/extraction_service.py

```python
"""
Extraction service - wraps core extraction pipeline.
"""

import asyncio
from typing import Dict, List, Optional
from uuid import UUID

# Import existing core logic
from core.extractor import run_async_extraction_and_evaluation
from schemas import get_schema, build_runtime


class ExtractionService:
    """Service to handle extraction operations."""

    async def run_extraction(
        self,
        markdown_content: str,
        source_file: str,
        schema_name: str,
        ground_truth: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Run extraction pipeline on markdown content.

        Args:
            markdown_content: Markdown text from PDF
            source_file: Original filename
            schema_name: Schema to use (e.g., 'patient_population')
            ground_truth: Optional ground truth for evaluation

        Returns:
            Dict with extracted data and metrics
        """
        try:
            # Get schema configuration
            schema_config = get_schema(schema_name)
            schema_runtime = build_runtime(schema_config)

            # Run existing extraction pipeline
            result = await run_async_extraction_and_evaluation(
                markdown_content=markdown_content,
                source_file=source_file,
                one_study_records=ground_truth or [],
                schema_runtime=schema_runtime,
                override=False,
                run_diagnostic=False,
                print_results=False,
                field_level_analysis=True,
                print_field_table=False
            )

            return result

        except Exception as e:
            raise Exception(f"Extraction failed: {str(e)}")

    async def run_batch_extraction(
        self,
        documents: List[Dict],
        schema_name: str
    ) -> List[Dict]:
        """
        Run extraction on multiple documents in parallel.

        Args:
            documents: List of dicts with markdown_content and filename
            schema_name: Schema to use

        Returns:
            List of extraction results
        """
        from core.config import BATCH_CONCURRENCY

        semaphore = asyncio.Semaphore(BATCH_CONCURRENCY)
        
        async def extract_one(doc):
            async with semaphore:
                return await self.run_extraction(
                    markdown_content=doc['markdown_content'],
                    source_file=doc['filename'],
                    schema_name=schema_name
                )

        results = await asyncio.gather(
            *[extract_one(doc) for doc in documents],
            return_exceptions=True
        )

        return results


# Global service instance
extraction_service = ExtractionService()
```

#### app/services/form_generation_service.py

```python
"""
Form generation service - wraps LangGraph code generation workflow.
"""

import asyncio
from typing import Dict
from pathlib import Path

from core.generators.workflow import WorkflowOrchestrator
from core.generators.task_utils import register_dynamic_schema


class FormGenerationService:
    """Service to handle form code generation."""

    def __init__(self):
        self.orchestrator = WorkflowOrchestrator(
            human_review_enabled=False  # Review handled via API
        )

    async def generate_code(
        self,
        form_data: Dict,
        project_id: str,
        form_id: str,
        enable_review: bool = False
    ) -> Dict:
        """
        Generate DSPy code from form definition.

        Args:
            form_data: Form definition with fields
            project_id: Project UUID
            form_id: Form UUID
            enable_review: Whether to pause for human review

        Returns:
            Dict with schema_name, task_dir, and generation stats
        """
        try:
            # Build form definition for decomposition
            form_definition = {
                "form_name": form_data.get("form_name"),
                "form_description": form_data.get("form_description"),
                "fields": form_data.get("fields", [])
            }

            # Run LangGraph workflow
            if enable_review:
                # Return decomposition for review
                from core.generators.decomposition import decompose_form
                
                decomposition_result = await asyncio.to_thread(
                    decompose_form,
                    form_definition
                )

                return {
                    "status": "awaiting_review",
                    "decomposition": decomposition_result
                }
            else:
                # Run complete generation workflow
                config = {
                    "form_data": form_definition,
                    "project_id": project_id,
                    "form_id": form_id
                }

                # Execute workflow
                result = await asyncio.to_thread(
                    self.orchestrator.run_complete_workflow,
                    config
                )

                # Register schema in runtime
                schema_name = register_dynamic_schema(
                    project_id,
                    form_id,
                    form_definition
                )

                return {
                    "status": "completed",
                    "schema_name": schema_name,
                    "task_dir": result.get("task_dir"),
                    "signatures_generated": len(result.get("signatures", [])),
                    "modules_generated": len(result.get("modules", [])),
                    "pipeline_stages": len(result.get("pipeline_stages", []))
                }

        except Exception as e:
            raise Exception(f"Code generation failed: {str(e)}")

    async def regenerate_with_feedback(
        self,
        decomposition: Dict,
        feedback: Dict,
        project_id: str,
        form_id: str
    ) -> Dict:
        """
        Regenerate code after human review with feedback.

        Args:
            decomposition: Original decomposition
            feedback: User feedback/corrections
            project_id: Project UUID
            form_id: Form UUID

        Returns:
            Generation result
        """
        # Apply feedback to decomposition
        updated_decomposition = self._apply_feedback(decomposition, feedback)

        # Generate code with updated decomposition
        # Implementation depends on LangGraph workflow
        pass

    def _apply_feedback(self, decomposition: Dict, feedback: Dict) -> Dict:
        """Apply user feedback to decomposition."""
        # Merge feedback into decomposition
        updated = decomposition.copy()
        
        # Update signatures based on feedback
        if "signature_feedback" in feedback:
            updated["signatures"] = feedback["signature_feedback"]

        # Update pipeline structure based on feedback
        if "pipeline_feedback" in feedback:
            updated["pipeline"] = feedback["pipeline_feedback"]

        return updated


# Global service instance
form_generation_service = FormGenerationService()
```

#### app/services/storage_service.py

```python
"""
Storage service for S3 operations.
"""

import boto3
from typing import BinaryIO, Optional
from pathlib import Path
import json
from botocore.exceptions import ClientError

from app.config import settings


class StorageService:
    """Service for cloud storage operations (S3)."""

    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket = settings.S3_BUCKET

    def upload_pdf(
        self,
        file: BinaryIO,
        user_id: str,
        project_id: str,
        document_id: str,
        filename: str
    ) -> str:
        """
        Upload PDF to S3.

        Args:
            file: File object to upload
            user_id: User UUID
            project_id: Project UUID
            document_id: Document UUID
            filename: Original filename

        Returns:
            S3 URL (s3://bucket/key)
        """
        key = f"uploads/{user_id}/{project_id}/{document_id}/{filename}"

        try:
            self.s3_client.upload_fileobj(
                file,
                self.bucket,
                key,
                ExtraArgs={'ContentType': 'application/pdf'}
            )

            return f"s3://{self.bucket}/{key}"

        except ClientError as e:
            raise Exception(f"S3 upload failed: {str(e)}")

    def upload_markdown_json(
        self,
        content: dict,
        user_id: str,
        project_id: str,
        document_id: str,
        unique_filename: str
    ) -> str:
        """
        Upload markdown JSON to S3.

        Args:
            content: Markdown JSON content (from Marker)
            user_id: User UUID
            project_id: Project UUID
            document_id: Document UUID
            unique_filename: Unique filename

        Returns:
            S3 URL
        """
        key = f"uploads/{user_id}/{project_id}/{document_id}/{unique_filename}.json"

        try:
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=json.dumps(content),
                ContentType='application/json'
            )

            return f"s3://{self.bucket}/{key}"

        except ClientError as e:
            raise Exception(f"S3 upload failed: {str(e)}")

    def download_markdown_json(self, s3_url: str) -> dict:
        """
        Download markdown JSON from S3.

        Args:
            s3_url: Full S3 URL (s3://bucket/key)

        Returns:
            Parsed JSON content
        """
        key = s3_url.replace(f"s3://{self.bucket}/", "")

        try:
            response = self.s3_client.get_object(Bucket=self.bucket, Key=key)
            content = response['Body'].read()
            return json.loads(content)

        except ClientError as e:
            raise Exception(f"S3 download failed: {str(e)}")

    def generate_presigned_url(
        self,
        s3_url: str,
        expiration: int = 3600
    ) -> str:
        """
        Generate pre-signed URL for temporary browser access.

        Args:
            s3_url: S3 URL
            expiration: URL expiration time in seconds

        Returns:
            Pre-signed HTTPS URL
        """
        key = s3_url.replace(f"s3://{self.bucket}/", "")

        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': key},
                ExpiresIn=expiration
            )

            return url

        except ClientError as e:
            raise Exception(f"Pre-signed URL generation failed: {str(e)}")

    def delete_file(self, s3_url: str):
        """Delete file from S3."""
        key = s3_url.replace(f"s3://{self.bucket}/", "")

        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=key)
        except ClientError as e:
            raise Exception(f"S3 delete failed: {str(e)}")


# Global service instance
storage_service = StorageService()
```

### 1.7 Celery Workers

#### app/workers/celery_app.py

```python
"""
Celery application configuration.
"""

from celery import Celery
from app.config import settings


# Create Celery app
celery_app = Celery(
    "evistream",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=settings.CELERY_TASK_TIME_LIMIT,
    task_soft_time_limit=settings.CELERY_TASK_SOFT_TIME_LIMIT,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
    result_expires=3600 * 24,  # 24 hours
)

# Auto-discover tasks
celery_app.autodiscover_tasks(['app.workers'])
```

#### app/workers/pdf_tasks.py

```python
"""
Background tasks for PDF processing.
"""

from celery import Task
from typing import Dict
from pathlib import Path
import tempfile

from app.workers.celery_app import celery_app
from app.services.storage_service import storage_service
from pdf_processor.pdf_processor import PDFProcessor
from supabase import create_client
from app.config import settings


class CallbackTask(Task):
    """Task with progress callback support."""

    def on_success(self, retval, task_id, args, kwargs):
        """Called when task succeeds."""
        # Notify via WebSocket
        pass

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called when task fails."""
        # Notify via WebSocket and update database
        pass


@celery_app.task(bind=True, base=CallbackTask, name='process_pdf')
def process_pdf_task(
    self,
    document_id: str,
    user_id: str,
    project_id: str,
    s3_pdf_url: str,
    filename: str
) -> Dict:
    """
    Background task to process PDF with Marker.

    Args:
        document_id: Document UUID
        user_id: User UUID
        project_id: Project UUID
        s3_pdf_url: S3 URL of PDF
        filename: Original filename

    Returns:
        Dict with processing results
    """
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

    try:
        # Update task state: starting
        self.update_state(
            state='PROCESSING',
            meta={'progress': 0, 'status': 'Downloading PDF from S3'}
        )

        # Download PDF from S3 to temp file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            # Download from S3
            s3_key = s3_pdf_url.replace(f"s3://{settings.S3_BUCKET}/", "")
            storage_service.s3_client.download_fileobj(
                settings.S3_BUCKET,
                s3_key,
                tmp_file
            )
            temp_pdf_path = tmp_file.name

        # Update progress
        self.update_state(
            state='PROCESSING',
            meta={'progress': 20, 'status': 'Processing PDF with Marker'}
        )

        # Process PDF with Marker
        processor = PDFProcessor({
            "extract_images": False,
            "output_dir": "/tmp/marker_output"
        })

        result = processor.process_pdf_file(temp_pdf_path)

        # Update progress
        self.update_state(
            state='PROCESSING',
            meta={'progress': 70, 'status': 'Uploading markdown to S3'}
        )

        # Upload markdown JSON to S3
        unique_filename = result.get("unique_filename")
        markdown_content = result.get("markdown_content")

        s3_markdown_url = storage_service.upload_markdown_json(
            content={"marker": result},
            user_id=user_id,
            project_id=project_id,
            document_id=document_id,
            unique_filename=unique_filename
        )

        # Update document record in database
        self.update_state(
            state='PROCESSING',
            meta={'progress': 90, 'status': 'Updating database'}
        )

        supabase.table("project_documents").update({
            "s3_markdown_path": s3_markdown_url,
            "unique_filename": unique_filename,
            "markdown_content_preview": markdown_content[:500],
            "processing_status": "COMPLETED"
        }).eq("id", document_id).execute()

        # Clean up temp file
        Path(temp_pdf_path).unlink(missing_ok=True)

        # Complete
        return {
            "document_id": document_id,
            "status": "completed",
            "s3_markdown_url": s3_markdown_url,
            "unique_filename": unique_filename
        }

    except Exception as e:
        # Update document with error
        supabase.table("project_documents").update({
            "processing_status": "FAILED",
            "processing_error": str(e)
        }).eq("id", document_id).execute()

        # Re-raise for Celery
        raise
```

#### app/workers/generation_tasks.py

```python
"""
Background tasks for form code generation.
"""

from celery import Task
from typing import Dict

from app.workers.celery_app import celery_app
from app.services.form_generation_service import form_generation_service
from supabase import create_client
from app.config import settings


@celery_app.task(bind=True, name='generate_form_code')
def generate_form_code_task(
    self,
    project_id: str,
    form_id: str,
    form_data: Dict,
    enable_review: bool = False
) -> Dict:
    """
    Background task to generate DSPy code from form definition.

    Args:
        project_id: Project UUID
        form_id: Form UUID
        form_data: Form definition
        enable_review: Whether to pause for review

    Returns:
        Generation results
    """
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

    try:
        # Update form status: generating
        supabase.table("project_forms").update({
            "status": "GENERATING" if not enable_review else "DECOMPOSING"
        }).eq("id", form_id).execute()

        # Update task state
        self.update_state(
            state='PROCESSING',
            meta={'progress': 10, 'stage': 'Decomposing form'}
        )

        # Run code generation
        import asyncio
        result = asyncio.run(
            form_generation_service.generate_code(
                form_data=form_data,
                project_id=project_id,
                form_id=form_id,
                enable_review=enable_review
            )
        )

        # Update task state
        self.update_state(
            state='PROCESSING',
            meta={'progress': 90, 'stage': 'Finalizing'}
        )

        # Update form record
        if result["status"] == "completed":
            supabase.table("project_forms").update({
                "status": "ACTIVE",
                "schema_name": result["schema_name"],
                "task_dir": result["task_dir"],
                "statistics": {
                    "signatures_generated": result["signatures_generated"],
                    "modules_generated": result["modules_generated"],
                    "pipeline_stages": result["pipeline_stages"]
                }
            }).eq("id", form_id).execute()
        elif result["status"] == "awaiting_review":
            supabase.table("project_forms").update({
                "status": "AWAITING_REVIEW",
                "decomposition_data": result["decomposition"]
            }).eq("id", form_id).execute()

        return result

    except Exception as e:
        # Update form with error
        supabase.table("project_forms").update({
            "status": "FAILED",
            "error": str(e)
        }).eq("id", form_id).execute()

        raise
```

#### app/workers/extraction_tasks.py

```python
"""
Background tasks for data extraction.
"""

from celery import Task
from typing import Dict, List
import asyncio

from app.workers.celery_app import celery_app
from app.services.extraction_service import extraction_service
from app.services.storage_service import storage_service
from supabase import create_client
from app.config import settings


@celery_app.task(bind=True, name='run_extraction')
def run_extraction_task(
    self,
    job_id: str,
    project_id: str,
    form_id: str,
    document_ids: List[str],
    schema_name: str
) -> Dict:
    """
    Background task to run extraction on documents.

    Args:
        job_id: Job UUID
        project_id: Project UUID
        form_id: Form UUID
        document_ids: List of document UUIDs
        schema_name: Schema to use for extraction

    Returns:
        Extraction results
    """
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

    try:
        # Update job status: processing
        supabase.table("jobs").update({
            "status": "PROCESSING",
            "started_at": "now()"
        }).eq("id", job_id).execute()

        results = []

        # Process each document
        for i, doc_id in enumerate(document_ids):
            # Update progress
            progress = int((i / len(document_ids)) * 100)
            self.update_state(
                state='PROCESSING',
                meta={
                    'progress': progress,
                    'current_document': i + 1,
                    'total_documents': len(document_ids)
                }
            )

            # Get document
            doc_result = supabase.table("project_documents").select("*").eq("id", doc_id).execute()

            if not doc_result.data:
                continue

            doc = doc_result.data[0]

            # Download markdown from S3
            markdown_json = storage_service.download_markdown_json(doc["s3_markdown_path"])
            markdown_content = markdown_json.get("marker", {}).get("markdown", "")

            # Run extraction
            extraction_result = asyncio.run(
                extraction_service.run_extraction(
                    markdown_content=markdown_content,
                    source_file=doc["filename"],
                    schema_name=schema_name
                )
            )

            # Save result to database
            result_record = supabase.table("extraction_results").insert({
                "job_id": job_id,
                "project_id": project_id,
                "form_id": form_id,
                "document_id": doc_id,
                "extracted_data": extraction_result.get("baseline_results", []),
                "evaluation_metrics": extraction_result.get("baseline_evaluation")
            }).execute()

            results.append({
                "document_id": doc_id,
                "result_id": result_record.data[0]["id"] if result_record.data else None
            })

        # Update job: completed
        supabase.table("jobs").update({
            "status": "COMPLETED",
            "progress": 100,
            "completed_at": "now()",
            "result_data": {
                "total_documents": len(document_ids),
                "successful": len(results),
                "results": results
            }
        }).eq("id", job_id).execute()

        return {
            "job_id": job_id,
            "status": "completed",
            "results_count": len(results)
        }

    except Exception as e:
        # Update job with error
        supabase.table("jobs").update({
            "status": "FAILED",
            "error_message": str(e),
            "completed_at": "now()"
        }).eq("id", job_id).execute()

        raise
```

### 1.8 WebSocket Implementation

#### app/api/v1/websocket.py

```python
"""
WebSocket endpoint for real-time job updates.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict
from uuid import UUID
import json

from app.dependencies import get_current_user


router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections."""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        """Accept and store WebSocket connection."""
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        """Remove WebSocket connection."""
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, user_id: str):
        """Send message to specific user."""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(message)
            except Exception:
                # Connection closed, remove it
                self.disconnect(user_id)

    async def send_job_update(
        self,
        user_id: str,
        job_id: str,
        event: str,
        data: dict
    ):
        """Send job update to user."""
        message = {
            "event": event,
            "job_id": job_id,
            "data": data
        }
        await self.send_personal_message(message, user_id)


# Global connection manager
manager = ConnectionManager()


@router.websocket("/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: UUID):
    """
    WebSocket endpoint for real-time updates.

    Connect with: ws://localhost:8000/api/v1/ws/{user_id}?token={jwt_token}
    """
    # Note: In production, validate JWT token from query params
    # token = websocket.query_params.get("token")
    # validated_user_id = auth_service.verify_token(token)

    await manager.connect(str(user_id), websocket)

    try:
        while True:
            # Keep connection alive (receive ping messages)
            data = await websocket.receive_text()

            # Echo back (for debugging)
            if data:
                await websocket.send_json({
                    "event": "pong",
                    "message": "Connection alive"
                })

    except WebSocketDisconnect:
        manager.disconnect(str(user_id))


# Helper function to notify from background tasks
async def notify_job_progress(user_id: str, job_id: str, progress: int, status: str):
    """
    Notify user about job progress.
    Call this from Celery tasks.
    """
    await manager.send_job_update(
        user_id=user_id,
        job_id=job_id,
        event="job.progress",
        data={"progress": progress, "status": status}
    )


async def notify_job_completed(user_id: str, job_id: str, result: dict):
    """Notify user about job completion."""
    await manager.send_job_update(
        user_id=user_id,
        job_id=job_id,
        event="job.completed",
        data=result
    )


async def notify_job_failed(user_id: str, job_id: str, error: str):
    """Notify user about job failure."""
    await manager.send_job_update(
        user_id=user_id,
        job_id=job_id,
        event="job.failed",
        data={"error": error}
    )
```

[Continued in next response due to length...]

### 1.9 Complete API Endpoints

Due to length constraints, here are the key endpoint patterns. Full implementations follow similar patterns to auth.py.

#### Projects API (app/api/v1/projects.py)

**Endpoints:**
- `GET /api/v1/projects/` - List user's projects
- `POST /api/v1/projects/` - Create project
- `GET /api/v1/projects/{id}` - Get project details  
- `PATCH /api/v1/projects/{id}` - Update project
- `DELETE /api/v1/projects/{id}` - Delete project

#### Documents API (app/api/v1/documents.py)

**Endpoints:**
- `POST /api/v1/documents/upload` - Upload PDF, enqueue processing
- `GET /api/v1/documents/?project_id={id}` - List documents
- `GET /api/v1/documents/{id}` - Get document details
- `GET /api/v1/documents/{id}/download` - Get pre-signed download URL
- `DELETE /api/v1/documents/{id}` - Delete document

#### Forms API (app/api/v1/forms.py)

**Endpoints:**
- `GET /api/v1/forms/?project_id={id}` - List forms
- `POST /api/v1/forms/` - Create form, enqueue generation
- `GET /api/v1/forms/{id}` - Get form details
- `PATCH /api/v1/forms/{id}` - Update form
- `POST /api/v1/forms/{id}/regenerate` - Regenerate with feedback
- `DELETE /api/v1/forms/{id}` - Delete form

#### Extractions API (app/api/v1/extractions.py)

**Endpoints:**
- `POST /api/v1/extractions/` - Start extraction job
- `GET /api/v1/extractions/{job_id}` - Get job status
- `GET /api/v1/extractions/{job_id}/results` - Get results
- `DELETE /api/v1/extractions/{job_id}` - Cancel job

#### Results API (app/api/v1/results.py)

**Endpoints:**
- `GET /api/v1/results/?project_id={id}` - List results
- `GET /api/v1/results/{id}` - Get detailed result
- `GET /api/v1/results/{id}/export` - Export as CSV/JSON

---

## Phase 2: Frontend Development

### 2.1 Next.js Project Setup

#### Create Next.js Application

```bash
cd /path/to/eviStream
npx create-next-app@latest frontend --typescript --tailwind --app --src-dir
cd frontend
```

#### Install Dependencies

```bash
npm install axios zustand react-hook-form zod
npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu
npm install @radix-ui/react-select @radix-ui/react-toast
npm install lucide-react class-variance-authority clsx tailwind-merge
```

#### Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── (auth)/
│   │   │   ├── login/page.tsx
│   │   │   └── register/page.tsx
│   │   └── (dashboard)/
│   │       └── projects/
│   │           ├── page.tsx
│   │           └── [id]/
│   │               ├── page.tsx
│   │               ├── documents/page.tsx
│   │               ├── forms/page.tsx
│   │               ├── extractions/page.tsx
│   │               └── results/page.tsx
│   │
│   ├── components/
│   │   ├── ui/              # shadcn/ui components
│   │   ├── layout/
│   │   ├── documents/
│   │   ├── forms/
│   │   └── extractions/
│   │
│   ├── lib/
│   │   ├── api.ts
│   │   ├── auth.ts
│   │   ├── websocket.ts
│   │   └── utils.ts
│   │
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useWebSocket.ts
│   │   └── useApi.ts
│   │
│   └── types/
│       └── api.ts
│
├── public/
├── package.json
└── next.config.js
```

### 2.2 Core Frontend Components

#### API Client (src/lib/api.ts)

```typescript
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Clear token and redirect to login
          localStorage.removeItem('token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Authentication
  async register(email: string, password: string, fullName?: string) {
    const response = await this.client.post('/api/v1/auth/register', {
      email,
      password,
      full_name: fullName,
    });
    return response.data;
  }

  async login(email: string, password: string) {
    const response = await this.client.post('/api/v1/auth/login', {
      email,
      password,
    });
    return response.data;
  }

  async getCurrentUser() {
    const response = await this.client.get('/api/v1/auth/me');
    return response.data;
  }

  // Projects
  async getProjects() {
    const response = await this.client.get('/api/v1/projects/');
    return response.data;
  }

  async createProject(name: string, description?: string) {
    const response = await this.client.post('/api/v1/projects/', {
      name,
      description,
    });
    return response.data;
  }

  async getProject(id: string) {
    const response = await this.client.get(`/api/v1/projects/${id}`);
    return response.data;
  }

  // Documents
  async uploadDocument(projectId: string, file: File) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('project_id', projectId);

    const response = await this.client.post(
      '/api/v1/documents/upload',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  }

  async getDocuments(projectId: string) {
    const response = await this.client.get('/api/v1/documents/', {
      params: { project_id: projectId },
    });
    return response.data;
  }

  // Forms
  async createForm(data: {
    project_id: string;
    form_name: string;
    form_description: string;
    fields: any[];
    enable_review: boolean;
  }) {
    const response = await this.client.post('/api/v1/forms/', data);
    return response.data;
  }

  async getForms(projectId: string) {
    const response = await this.client.get('/api/v1/forms/', {
      params: { project_id: projectId },
    });
    return response.data;
  }

  // Extractions
  async startExtraction(data: {
    project_id: string;
    form_id: string;
    document_ids: string[];
  }) {
    const response = await this.client.post('/api/v1/extractions/', data);
    return response.data;
  }

  async getJobStatus(jobId: string) {
    const response = await this.client.get(`/api/v1/extractions/${jobId}`);
    return response.data;
  }

  async getExtractionResults(jobId: string) {
    const response = await this.client.get(
      `/api/v1/extractions/${jobId}/results`
    );
    return response.data;
  }
}

export const api = new ApiClient();
```

#### WebSocket Hook (src/hooks/useWebSocket.ts)

```typescript
import { useEffect, useRef, useState } from 'react';

interface WSMessage {
  event: string;
  job_id: string;
  data: any;
}

export function useWebSocket(userId: string | null) {
  const [connected, setConnected] = useState(false);
  const ws = useRef<WebSocket | null>(null);
  const listeners = useRef<Map<string, Set<(data: any) => void>>>(new Map());

  useEffect(() => {
    if (!userId) return;

    const token = localStorage.getItem('token');
    const wsUrl = `ws://localhost:8000/api/v1/ws/${userId}?token=${token}`;

    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => {
      console.log('WebSocket connected');
      setConnected(true);
    };

    ws.current.onclose = () => {
      console.log('WebSocket disconnected');
      setConnected(false);
    };

    ws.current.onmessage = (event) => {
      const message: WSMessage = JSON.parse(event.data);

      // Notify all listeners for this event
      const eventListeners = listeners.current.get(message.event);
      if (eventListeners) {
        eventListeners.forEach((callback) => callback(message.data));
      }
    };

    return () => {
      ws.current?.close();
    };
  }, [userId]);

  const subscribe = (event: string, callback: (data: any) => void) => {
    if (!listeners.current.has(event)) {
      listeners.current.set(event, new Set());
    }
    listeners.current.get(event)!.add(callback);

    // Return unsubscribe function
    return () => {
      listeners.current.get(event)?.delete(callback);
    };
  };

  return { connected, subscribe };
}
```

#### Job Progress Component (src/components/extractions/JobProgress.tsx)

```typescript
'use client';

import { useEffect, useState } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { Progress } from '@/components/ui/progress';

interface JobProgressProps {
  jobId: string;
  userId: string;
  onComplete?: (result: any) => void;
}

export function JobProgress({ jobId, userId, onComplete }: JobProgressProps) {
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('pending');
  const [error, setError] = useState<string | null>(null);
  const { subscribe } = useWebSocket(userId);

  useEffect(() => {
    // Subscribe to progress updates
    const unsubProgress = subscribe('job.progress', (data) => {
      if (data.job_id === jobId) {
        setProgress(data.progress);
        setStatus(data.status || 'processing');
      }
    });

    // Subscribe to completion
    const unsubComplete = subscribe('job.completed', (data) => {
      if (data.job_id === jobId) {
        setProgress(100);
        setStatus('completed');
        onComplete?.(data);
      }
    });

    // Subscribe to failures
    const unsubFailed = subscribe('job.failed', (data) => {
      if (data.job_id === jobId) {
        setStatus('failed');
        setError(data.error);
      }
    });

    return () => {
      unsubProgress();
      unsubComplete();
      unsubFailed();
    };
  }, [jobId, subscribe, onComplete]);

  return (
    <div className="w-full space-y-2">
      <div className="flex justify-between text-sm">
        <span className="font-medium">{status}</span>
        <span className="text-muted-foreground">{progress}%</span>
      </div>

      <Progress value={progress} />

      {error && (
        <div className="text-sm text-red-600 mt-2">
          Error: {error}
        </div>
      )}
    </div>
  );
}
```

### 2.3 Key UI Pages

#### Login Page (src/app/(auth)/login/page.tsx)

```typescript
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import Link from 'next/link';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const response = await api.login(email, password);
      
      // Store token
      localStorage.setItem('token', response.access_token);
      localStorage.setItem('user_id', response.user_id);

      // Redirect to projects
      router.push('/projects');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <div className="w-full max-w-md space-y-8 rounded-lg bg-white p-8 shadow-lg">
        <div>
          <h2 className="text-center text-3xl font-bold">eviStream</h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Sign in to your account
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div>
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          {error && (
            <div className="rounded-md bg-red-50 p-3 text-sm text-red-800">
              {error}
            </div>
          )}

          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? 'Signing in...' : 'Sign in'}
          </Button>

          <p className="text-center text-sm">
            Don't have an account?{' '}
            <Link href="/register" className="text-blue-600 hover:underline">
              Register
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}
```

---

## Phase 3: Infrastructure Setup

### 3.1 Docker Configuration

#### Backend Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create symlinks to core modules
RUN ln -sf /app/core /app/app/core && \
    ln -sf /app/dspy_components /app/app/dspy_components && \
    ln -sf /app/schemas /app/app/schemas

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Frontend Dockerfile

```dockerfile
# frontend/Dockerfile
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source
COPY . .

# Build
RUN npm run build

# Production image
FROM node:20-alpine AS runner

WORKDIR /app

# Copy built assets
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000

CMD ["node", "server.js"]
```

#### Worker Dockerfile

```dockerfile
# worker/Dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create symlinks
RUN ln -sf /app/core /app/app/core && \
    ln -sf /app/dspy_components /app/app/dspy_components && \
    ln -sf /app/schemas /app/app/schemas

# Run Celery worker
CMD ["celery", "-A", "app.workers.celery_app", "worker", \
     "--loglevel=info", "--concurrency=4"]
```

### 3.2 Docker Compose (Development)

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=development
      - DEBUG=true
      - REDIS_URL=redis://redis:6379/0
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - S3_BUCKET=${S3_BUCKET}
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./backend:/app
      - ./core:/app/core
      - ./dspy_components:/app/dspy_components
      - ./schemas:/app/schemas
    depends_on:
      - redis
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev

  worker:
    build: ./worker
    environment:
      - REDIS_URL=redis://redis:6379/0
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
    volumes:
      - ./backend:/app
      - ./core:/app/core
      - ./dspy_components:/app/dspy_components
      - ./schemas:/app/schemas
    depends_on:
      - redis
      - backend

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/dev.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - backend
      - frontend

volumes:
  redis_data:
```

### 3.3 AWS ECS Deployment with Terraform

#### infrastructure/main.tf

```hcl
terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket = "evistream-terraform-state"
    key    = "production/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "evistream-vpc"
  }
}

# Public Subnets
resource "aws_subnet" "public" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 1}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  map_public_ip_on_launch = true

  tags = {
    Name = "evistream-public-${count.index + 1}"
  }
}

# Private Subnets
resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "evistream-private-${count.index + 1}"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "evistream-igw"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "evistream-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "evistream-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id

  enable_deletion_protection = true

  tags = {
    Name = "evistream-alb"
  }
}

# ALB Target Groups
resource "aws_lb_target_group" "backend" {
  name        = "evistream-backend-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    path                = "/health"
    healthy_threshold   = 2
    unhealthy_threshold = 10
    timeout             = 60
    interval            = 120
    matcher             = "200"
  }

  deregistration_delay = 30
}

resource "aws_lb_target_group" "frontend" {
  name        = "evistream-frontend-tg"
  port        = 3000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    path     = "/"
    interval = 30
    timeout  = 5
    matcher  = "200"
  }
}

# ALB Listener (HTTPS)
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.main.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = aws_acm_certificate.main.arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.frontend.arn
  }
}

# API routing rule
resource "aws_lb_listener_rule" "api" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend.arn
  }

  condition {
    path_pattern {
      values = ["/api/*", "/ws/*"]
    }
  }
}

# ECS Task Definitions and Services
# (See detailed Terraform code in Appendix)

# ElastiCache Redis
resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "evistream-redis"
  engine               = "redis"
  node_type            = "cache.t3.medium"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.redis.name
  security_group_ids   = [aws_security_group.redis.id]

  tags = {
    Name = "evistream-redis"
  }
}

# S3 Bucket
resource "aws_s3_bucket" "storage" {
  bucket = "evistream-production"

  tags = {
    Name = "evistream-storage"
  }
}

resource "aws_s3_bucket_versioning" "storage" {
  bucket = aws_s3_bucket.storage.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Output values
output "alb_dns_name" {
  value = aws_lb.main.dns_name
}

output "redis_endpoint" {
  value = aws_elasticache_cluster.redis.cache_nodes[0].address
}
```

---

## Phase 4: Testing & Quality Assurance

### 4.1 Backend Testing

#### Unit Tests (tests/test_services/test_extraction_service.py)

```python
import pytest
from app.services.extraction_service import extraction_service


@pytest.mark.asyncio
async def test_extraction_service():
    """Test extraction service with sample data."""
    markdown = """
    # Clinical Trial
    
    Sample size: 120 patients
    Study design: Randomized Controlled Trial
    """
    
    result = await extraction_service.run_extraction(
        markdown_content=markdown,
        source_file="test.pdf",
        schema_name="patient_population"
    )
    
    assert result is not None
    assert "baseline_results" in result
```

#### Integration Tests

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_register_and_login():
    """Test user registration and login flow."""
    # Register
    response = client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "testpass123"
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    
    token = data["access_token"]
    
    # Access protected endpoint
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
```

### 4.2 Load Testing

#### Locust Test (tests/load_test.py)

```python
from locust import HttpUser, task, between


class EviStreamUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login before starting tests."""
        response = self.client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "testpass123"
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(3)
    def list_projects(self):
        """List projects (common operation)."""
        self.client.get(
            "/api/v1/projects/",
            headers=self.headers
        )
    
    @task(1)
    def start_extraction(self):
        """Start extraction job (heavy operation)."""
        self.client.post(
            "/api/v1/extractions/",
            json={
                "project_id": "test-project-id",
                "form_id": "test-form-id",
                "document_ids": ["doc-1"]
            },
            headers=self.headers
        )
```

Run load test:
```bash
locust -f tests/load_test.py --host=http://localhost:8000
```

---

## Phase 5: Deployment & Migration

### 5.1 CI/CD Pipeline

#### GitHub Actions (.github/workflows/deploy.yml)

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install -r backend/requirements-dev.txt
      
      - name: Run tests
        run: |
          cd backend
          pytest tests/ -v

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1
      
      - name: Build and push Backend
        run: |
          docker build -t evistream-backend ./backend
          docker tag evistream-backend:latest ${{ steps.login-ecr.outputs.registry }}/evistream-backend:latest
          docker push ${{ steps.login-ecr.outputs.registry }}/evistream-backend:latest
      
      - name: Build and push Frontend
        run: |
          docker build -t evistream-frontend ./frontend
          docker tag evistream-frontend:latest ${{ steps.login-ecr.outputs.registry }}/evistream-frontend:latest
          docker push ${{ steps.login-ecr.outputs.registry }}/evistream-frontend:latest
      
      - name: Build and push Worker
        run: |
          docker build -t evistream-worker ./worker
          docker tag evistream-worker:latest ${{ steps.login-ecr.outputs.registry }}/evistream-worker:latest
          docker push ${{ steps.login-ecr.outputs.registry }}/evistream-worker:latest

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to ECS
        run: |
          aws ecs update-service --cluster evistream-cluster --service evistream-backend --force-new-deployment
          aws ecs update-service --cluster evistream-cluster --service evistream-frontend --force-new-deployment
          aws ecs update-service --cluster evistream-cluster --service evistream-worker --force-new-deployment
```

### 5.2 Data Migration Script

```python
# scripts/migrate_to_production.py
import asyncio
from pathlib import Path
import json
from app.services.storage_service import storage_service
from supabase import create_client
from app.config import settings


async def migrate_pdfs():
    """Migrate PDFs from local storage to S3."""
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    
    storage_dir = Path("storage/uploads/pdfs")
    
    for pdf_file in storage_dir.glob("*.pdf"):
        # Get or create document record
        doc = supabase.table("project_documents").select("*").eq(
            "filename", pdf_file.name
        ).execute()
        
        if not doc.data:
            print(f"Skipping {pdf_file.name} - no database record")
            continue
        
        doc_data = doc.data[0]
        
        # Upload to S3
        with open(pdf_file, 'rb') as f:
            s3_url = storage_service.upload_pdf(
                file=f,
                user_id=doc_data["user_id"],
                project_id=doc_data["project_id"],
                document_id=doc_data["id"],
                filename=pdf_file.name
            )
        
        # Update database
        supabase.table("project_documents").update({
            "s3_pdf_path": s3_url
        }).eq("id", doc_data["id"]).execute()
        
        print(f"Migrated {pdf_file.name}")


if __name__ == "__main__":
    asyncio.run(migrate_pdfs())
```

---

## Monitoring & Observability

### CloudWatch Dashboard

```python
# scripts/create_cloudwatch_dashboard.py
import boto3

cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')

dashboard_body = {
    "widgets": [
        {
            "type": "metric",
            "properties": {
                "metrics": [
                    ["AWS/ECS", "CPUUtilization", {"stat": "Average"}],
                    [".", "MemoryUtilization", {"stat": "Average"}]
                ],
                "period": 300,
                "stat": "Average",
                "region": "us-east-1",
                "title": "ECS Resource Usage"
            }
        },
        {
            "type": "metric",
            "properties": {
                "metrics": [
                    ["AWS/ApplicationELB", "RequestCount", {"stat": "Sum"}],
                    [".", "TargetResponseTime", {"stat": "Average"}]
                ],
                "period": 300,
                "stat": "Average",
                "region": "us-east-1",
                "title": "API Performance"
            }
        }
    ]
}

cloudwatch.put_dashboard(
    DashboardName='eviStream-Production',
    DashboardBody=json.dumps(dashboard_body)
)
```

---

## Cost Analysis

### Monthly Cost Breakdown (AWS)

| Service | Configuration | Monthly Cost |
|---------|--------------|--------------|
| **ECS Fargate** | | |
| Backend (3 tasks) | 1 vCPU, 2GB RAM | $88 |
| Frontend (2 tasks) | 0.5 vCPU, 1GB RAM | $29 |
| Worker (2 tasks) | 2 vCPU, 4GB RAM | $117 |
| **Database** | | |
| Supabase Pro | Managed PostgreSQL | $25 |
| **Cache** | | |
| ElastiCache | cache.t3.medium | $50 |
| **Storage** | | |
| S3 (100GB) | + requests | $3 |
| **Networking** | | |
| ALB | Base + LCU | $20 |
| NAT Gateway | 2 AZs | $65 |
| **Monitoring** | | |
| CloudWatch | Logs + metrics | $10 |
| Sentry | Team plan | $26 |
| **TOTAL** | | **~$433/month** |

### Cost Optimization Strategies

1. **Use Spot Instances for Workers** - Save 70% on worker costs
2. **S3 Lifecycle Policies** - Move old files to cheaper storage tiers
3. **CloudFront Caching** - Reduce S3 data transfer costs
4. **Reserved Capacity** - Commit to 1-year for 30% discount
5. **Right-size Resources** - Monitor and adjust based on actual usage

---

## Security Considerations

### 1. Authentication & Authorization

- ✅ JWT tokens with short expiration (7 days)
- ✅ Secure password hashing (bcrypt)
- ✅ Row-level security in Supabase
- ✅ User isolation at project level

### 2. Data Protection

- ✅ HTTPS only (TLS 1.2+)
- ✅ Encrypted S3 storage (AES-256)
- ✅ Encrypted Redis connections
- ✅ Secrets in AWS Secrets Manager

### 3. API Security

- ✅ Rate limiting (TODO: implement)
- ✅ Input validation (Pydantic)
- ✅ CORS restrictions
- ✅ SQL injection prevention (ORMyour-content-here style updates and documentation improvements"]

  **Security Checklist:**
  - [ ] Enable AWS GuardDuty
  - [ ] Set up CloudTrail logging
  - [ ] Configure AWS WAF on ALB
  - [ ] Implement rate limiting
  - [ ] Enable VPC Flow Logs
  - [ ] Set up AWS Config rules
  - [ ] Configure backup policies
  - [ ] Enable MFA for AWS account

---

## Troubleshooting Guide

### Common Issues

#### 1. Celery Worker Not Processing Jobs

**Symptoms:** Jobs stuck in "PENDING" status

**Diagnosis:**
```bash
# Check worker logs
docker logs evistream-worker

# Check Redis connection
redis-cli -h localhost ping

# Check Celery status
celery -A app.workers.celery_app inspect active
```

**Solutions:**
- Restart worker: `docker restart evistream-worker`
- Check Redis connectivity
- Verify task routing configuration

#### 2. WebSocket Connection Drops

**Symptoms:** No real-time updates in frontend

**Diagnosis:**
```bash
# Check ALB timeout settings
aws elbv2 describe-load-balancers --load-balancer-arns <arn>

# Check frontend WebSocket code
# Look for reconnection logic
```

**Solutions:**
- Increase ALB idle timeout to 60+ seconds
- Implement reconnection logic in frontend
- Add WebSocket keepalive pings

#### 3. S3 Upload Failures

**Symptoms:** PDF upload fails with 403/500 errors

**Diagnosis:**
```bash
# Check IAM permissions
aws iam get-role-policy --role-name evistream-ecs-task

# Test S3 access
aws s3 ls s3://evistream-production/
```

**Solutions:**
- Verify IAM role has S3 write permissions
- Check S3 bucket policy
- Verify AWS credentials in environment

#### 4. High Memory Usage

**Symptoms:** ECS tasks being killed (OOM)

**Diagnosis:**
```bash
# Check CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name MemoryUtilization \
  --dimensions Name=ServiceName,Value=evistream-backend

# Check application logs for memory leaks
```

**Solutions:**
- Increase task memory allocation
- Profile code for memory leaks
- Implement memory limits in Python
- Use task recycling (worker_max_tasks_per_child)

---

## Appendix

### A. Complete Terraform Configuration

See `/infrastructure/` directory for:
- `main.tf` - Core infrastructure
- `ecs.tf` - ECS services and tasks
- `security_groups.tf` - Network security
- `variables.tf` - Input variables
- `outputs.tf` - Output values

### B. Environment Variables Reference

**Backend (.env):**
```bash
SECRET_KEY=<generate-with-openssl-rand-hex-32>
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key
REDIS_URL=redis://localhost:6379/0
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
S3_BUCKET=evistream-production
ENVIRONMENT=production
DEBUG=false
```

**Frontend (.env.production):**
```bash
NEXT_PUBLIC_API_URL=https://api.evistream.com
```

### C. Useful Commands

**Docker:**
```bash
# Build all services
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Execute command in container
docker-compose exec backend bash
```

**Celery:**
```bash
# Start worker
celery -A app.workers.celery_app worker --loglevel=info

# Monitor tasks
celery -A app.workers.celery_app flower

# Purge queue
celery -A app.workers.celery_app purge
```

**AWS:**
```bash
# Deploy new version
aws ecs update-service --cluster evistream --service backend --force-new-deployment

# View task logs
aws logs tail /ecs/evistream-backend --follow

# Check task health
aws ecs describe-tasks --cluster evistream --tasks <task-id>
```

### D. Performance Benchmarks

**Target Metrics:**
- API Response Time (p95): < 2 seconds
- PDF Processing: < 60 seconds per document
- Code Generation: < 120 seconds per form
- Extraction (single): < 30 seconds per document
- Concurrent Users: 100+
- Uptime: 99.9%

### E. Support & Resources

**Documentation:**
- API Docs: https://api.evistream.com/docs
- User Guide: (link to user docs)
- Architecture Diagrams: (link to diagrams)

**Monitoring:**
- CloudWatch Dashboard: (AWS Console link)
- Sentry: https://sentry.io/evistream
- Status Page: (status page link)

**Development:**
- GitHub Repo: (repo link)
- CI/CD Pipeline: (GitHub Actions link)
- Staging Environment: (staging URL)

---

## Conclusion

This guide provides a complete roadmap for migrating eviStream from a Streamlit prototype to a production-ready platform. Follow the phases sequentially, test thoroughly at each stage, and monitor continuously once deployed.

**Key Success Factors:**
1. Preserve core extraction logic - don't rewrite what works
2. Test early and often - catch issues before production
3. Monitor everything - observability from day one
4. Start simple, scale gradually - don't over-engineer initially
5. Document as you go - future you will thank present you

**Next Steps:**
1. Review this plan with stakeholders
2. Set up development environment
3. Begin Phase 1: Backend Development
4. Iterate and improve based on feedback

Good luck with your production migration! 🚀

---

**Document Version:** 1.0  
**Last Updated:** 2026-01-15  
**Author:** Claude Code Assistant  
**Status:** Ready for Implementation
