# eviStream Production Deployment Plan

**Version:** 1.0  
**Date:** January 2026  
**Project:** Medical Document Extraction Platform  
**Current State:** Streamlit Prototype  
**Target State:** Production Web Application

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Architecture Decisions](#architecture-decisions)
3. [Technology Stack](#technology-stack)
4. [Development Timeline](#development-timeline)
5. [Detailed Implementation Plan](#detailed-implementation-plan)
6. [Cost Estimates](#cost-estimates)
7. [Risk Management](#risk-management)
8. [Success Metrics](#success-metrics)
9. [Team & Resources](#team--resources)
10. [Next Steps](#next-steps)

---

## Executive Summary

### Project Goal
Transform the current Streamlit prototype into a production-ready web application with:
- Modern React frontend
- RESTful FastAPI backend
- Scalable AWS infrastructure
- Redis caching layer
- Background job processing
- Professional monitoring and security

### Key Metrics
- **Timeline:** 6-8 weeks with Cursor AI assistance (vs 12 weeks manual)
- **Budget:** $80-150/month operational costs
- **Team Size:** 1-2 developers
- **Target Users:** Researchers, medical professionals
- **Expected Load:** 100-500 extractions/day

### Success Criteria
1. Full-featured web application deployed to AWS
2. Extraction accuracy maintained from prototype
3. Response time < 2 seconds for API calls
4. Background jobs complete within 5 minutes
5. 99% uptime
6. Comprehensive error tracking and monitoring

---

## Architecture Decisions

### 1. Frontend Architecture

#### UI Component Library
**Decision:** Material-UI (MUI)

**Rationale:**
- Professional, polished look out of the box
- Comprehensive component library
- Excellent documentation
- Active community
- Built-in accessibility features
- Good TypeScript support

**Alternatives Considered:**
- Ant Design: Great for data-heavy apps, but documentation less comprehensive
- Chakra UI: Lightweight but smaller ecosystem
- Tailwind CSS: Maximum flexibility but requires more design work

#### State Management
**Decision:** React Query + Zustand

**Rationale:**
- **React Query:** Perfect for API-driven apps, handles caching, loading states, and refetching automatically
- **Zustand:** Lightweight global state for authentication, theme, and user preferences
- Minimal boilerplate compared to Redux
- Easy to learn and maintain

**State Distribution:**
```
React Query → API data (projects, forms, extraction results)
Zustand → App state (user session, theme, UI preferences)
Local State → Component-specific UI state
```

#### Routing Strategy
**Decision:** React Router v6 (SPA)

**Rationale:**
- Standard for single-page applications
- No SEO requirements (internal tool)
- Excellent TypeScript support
- Nested routing for complex layouts

**Routes Structure:**
```
/                       → Landing/Login
/dashboard              → Main dashboard
/projects               → Project list
/projects/:id           → Project detail
/projects/:id/forms     → Forms for project
/forms/:id/extract      → Extraction interface
/extractions/:id        → Results viewer
/settings               → User settings
```

---

### 2. Backend Architecture

#### API Architecture Style
**Decision:** REST API with FastAPI

**Rationale:**
- FastAPI's automatic OpenAPI documentation
- Native async/await support
- Pydantic for validation
- Excellent performance
- Easy integration with existing Python code
- Standard REST is sufficient for CRUD operations

**API Versioning:**
```
/api/v1/projects
/api/v1/forms
/api/v1/extractions
/api/v1/schemas
```

#### Background Job Processing
**Decision:** Celery + Redis

**Rationale:**
- DSPy extractions take 30 seconds to 5 minutes per PDF
- Need reliable job queue with retry logic
- Support for distributed workers
- Monitoring and task tracking built-in
- Industry standard for Python background tasks

**Job Flow:**
```
User submits extraction →
  API creates job →
    Returns job_id immediately →
      Celery worker processes →
        Updates job status in Redis →
          User polls for completion →
            Results cached in Redis
```

**Alternative Considered:**
- FastAPI BackgroundTasks: Too simple, no distributed support
- AWS Lambda: Cold starts problematic for long-running tasks
- Temporal: Overkill for current needs

#### File Storage
**Decision:** AWS S3

**Rationale:**
- Industry standard for object storage
- Highly durable (99.999999999%)
- Cost-effective (~$0.023/GB/month)
- Seamless integration with AWS services
- Pre-signed URLs for secure file access
- Lifecycle policies for automatic cleanup

**Storage Strategy:**
```
s3://evistream-pdfs/
├── uploads/{user_id}/{upload_id}/
│   └── original.pdf
├── processed/{extraction_id}/
│   ├── converted.md
│   └── metadata.json
└── results/{extraction_id}/
    └── results.json
```

---

### 3. Database Architecture

#### Primary Database
**Decision:** PostgreSQL 14+

**Rationale:**
- ACID compliance for data integrity
- Excellent JSON support (for dynamic form schemas)
- Strong with SQLAlchemy ORM
- Battle-tested for production
- Supports complex queries
- Good performance for read-heavy workloads

**Schema Design Philosophy:** Hybrid Approach

**Core Entities (Normalized):**
```sql
-- Users and projects: strict relational
users (id, email, name, role, created_at)
projects (id, user_id, name, description, created_at)
forms (id, project_id, name, status, created_at)

-- Flexible data: JSON fields
forms.schema_definition JSONB  -- Dynamic form structure
forms.field_mapping JSONB      -- Form-to-signature mapping
forms.decomposition JSONB      -- LangGraph decomposition result
```

**Extraction Results (Semi-Structured):**
```sql
extractions (
  id UUID,
  form_id UUID,
  status TEXT,  -- queued, processing, completed, failed
  created_at TIMESTAMP,
  completed_at TIMESTAMP
)

extraction_results (
  id UUID,
  extraction_id UUID,
  pdf_filename TEXT,
  extracted_data JSONB,  -- Dynamic schema
  confidence_scores JSONB,
  created_at TIMESTAMP
)
```

**Rationale for JSON:**
- Form schemas are dynamic (generated at runtime)
- Extraction results structure varies per form
- Allows flexibility without schema migrations
- PostgreSQL has excellent JSON query performance

**Indexes:**
```sql
-- Frequently queried fields
CREATE INDEX idx_extractions_status ON extractions(status);
CREATE INDEX idx_extractions_form_id ON extractions(form_id);
CREATE INDEX idx_results_extraction_id ON extraction_results(extraction_id);
CREATE INDEX idx_forms_project_id ON forms(project_id);

-- JSON field indexes (PostgreSQL GIN)
CREATE INDEX idx_forms_schema ON forms USING GIN (schema_definition);
CREATE INDEX idx_results_data ON extraction_results USING GIN (extracted_data);
```

#### Caching Strategy
**Decision:** Multi-layer caching with Redis

**Cache Layers:**

**1. Application Cache (Redis):**
```
Layer 1: Hot data (5-15 min TTL)
├── Project lists by user
├── Form schemas
└── Active extraction statuses

Layer 2: Computation results (1-6 hour TTL)
├── Extraction results
├── Generated DSPy modules
└── Decomposition results

Layer 3: Session data (30 min TTL)
└── User sessions
```

**2. CDN Cache (CloudFront):**
```
Static Assets (24 hour TTL)
├── React build files
├── Images and icons
└── Public documentation
```

**3. HTTP Cache (Browser):**
```
Cache-Control Headers:
├── GET /api/v1/projects → max-age=300 (5 min)
├── GET /api/v1/extractions/{id} → max-age=3600 (1 hour)
└── GET /api/v1/forms → max-age=600 (10 min)
```

**Cache Invalidation Strategy:**
```python
# On update/delete operations
def update_project(project_id):
    # 1. Update database
    db.update(project_id)
    
    # 2. Invalidate cache
    cache.delete(f"project:{project_id}")
    cache.delete(f"projects:user:{user_id}")
    
    # 3. Broadcast to other workers (if distributed)
    redis.publish("cache_invalidation", f"project:{project_id}")
```

---

### 4. Authentication & Authorization

#### Authentication Strategy
**Decision:** JWT Tokens

**Implementation:**
```
Login Flow:
1. User submits credentials
2. Backend validates against database
3. Generate JWT token (expires in 30 min)
4. Return access_token + refresh_token
5. Frontend stores in httpOnly cookie
6. Include in Authorization header for API calls

Token Structure:
{
  "sub": "user_id",
  "email": "user@example.com",
  "role": "user",
  "exp": 1234567890
}
```

**Security Measures:**
- Tokens stored in httpOnly cookies (XSS protection)
- CORS configured for specific origins
- Rate limiting on login endpoint (5 attempts/minute)
- Refresh token rotation
- Token blacklist for logout

**Future Enhancements (Post-MVP):**
- OAuth2 integration (Google, GitHub)
- Two-factor authentication (2FA)
- API keys for programmatic access
- SSO for enterprise customers

#### Authorization Model
**Decision:** Role-Based Access Control (RBAC) + Project Ownership

**Roles:**
```python
class UserRole(enum.Enum):
    ADMIN = "admin"      # Full system access
    USER = "user"        # Can create projects, run extractions
    VIEWER = "viewer"    # Read-only access
```

**Permissions Matrix:**

| Action | Admin | User (Owner) | User (Collaborator) | Viewer |
|--------|-------|--------------|---------------------|--------|
| View projects | All | Own | Shared | Shared |
| Create project | ✓ | ✓ | ✗ | ✗ |
| Delete project | ✓ | Own only | ✗ | ✗ |
| Create form | ✓ | Own projects | ✗ | ✗ |
| Run extraction | ✓ | Own/shared | Shared only | ✗ |
| View results | ✓ | Own/shared | Shared only | Shared |
| Share project | ✓ | Own only | ✗ | ✗ |

**Implementation:**
```python
# Decorator-based authorization
@router.post("/api/v1/projects")
@require_role(UserRole.USER)
async def create_project():
    pass

@router.delete("/api/v1/projects/{id}")
@require_ownership_or_admin
async def delete_project(id: str):
    pass
```

---

### 5. Deployment Architecture

#### Hosting Strategy
**Decision:** AWS ECS with Fargate

**Architecture Diagram:**
```
Internet
    ↓
CloudFront (CDN)
    ↓
ALB (Application Load Balancer)
    ↓
┌─────────────┬─────────────┬─────────────┐
│   ECS       │   ECS       │   ECS       │
│ (Backend 1) │ (Backend 2) │ (Backend 3) │
│  FastAPI    │  FastAPI    │  FastAPI    │
└─────────────┴─────────────┴─────────────┘
         ↓              ↓              ↓
    ┌────────┐     ┌────────┐    ┌────────┐
    │  RDS   │     │ElastiC │    │   S3   │
    │Postgres│     │  Redis │    │  PDFs  │
    └────────┘     └────────┘    └────────┘
```

**Components:**

**1. Frontend (CloudFront + S3):**
- React app built to static files
- Hosted on S3 bucket
- CloudFront CDN for global distribution
- SSL certificate via AWS Certificate Manager
- Custom domain via Route 53

**2. Backend (ECS Fargate):**
- Docker containers running FastAPI
- Auto-scaling: 2-10 tasks based on CPU/memory
- Health checks every 30 seconds
- Rolling deployments (zero downtime)
- Task definition stores environment variables

**3. Background Workers (ECS Fargate):**
- Separate ECS service for Celery workers
- Auto-scaling based on queue length
- Same Docker image as API (different command)
- Scales 1-5 workers based on pending jobs

**4. Database (RDS PostgreSQL):**
- db.t3.medium (2 vCPU, 4GB RAM)
- Multi-AZ for high availability
- Automated backups (7 day retention)
- Read replica for reporting queries (optional)

**5. Cache & Queue (ElastiCache Redis):**
- cache.t3.micro (0.5 vCPU, 0.5GB RAM)
- Cluster mode disabled (single node)
- Automatic failover enabled
- Snapshot backups enabled

**6. File Storage (S3):**
- Standard storage class
- Lifecycle policy: Delete uploads after 90 days
- Versioning enabled
- Server-side encryption (AES-256)

**Rationale:**
- **ECS over EC2:** No server management, auto-scaling, pay-per-use
- **Fargate over Kubernetes:** Simpler operations, no cluster management
- **Multi-AZ:** High availability, automatic failover
- **CloudFront:** Fast global access, DDoS protection

#### Environment Strategy
**Decision:** 3 Environments

**Environments:**

**1. Local (Development):**
```
Purpose: Day-to-day development
Infrastructure: Docker Compose
Database: Local PostgreSQL
Redis: Local Redis
S3: LocalStack (S3 emulator)
Cost: Free
```

**2. Staging:**
```
Purpose: Testing before production
Infrastructure: AWS (minimal instances)
Database: db.t3.micro RDS
Redis: cache.t3.micro ElastiCache
S3: Separate staging bucket
Cost: ~$30-40/month
Domain: staging.evistream.com
```

**3. Production:**
```
Purpose: Live user traffic
Infrastructure: AWS (full setup)
Database: db.t3.medium RDS (Multi-AZ)
Redis: cache.t3.micro ElastiCache
S3: Production bucket with versioning
Cost: ~$80-150/month
Domain: app.evistream.com
```

**Promotion Strategy:**
```
Developer → Local testing →
  Commit to main →
    Auto-deploy to Staging →
      Smoke tests pass →
        Manual approval →
          Deploy to Production →
            Monitor for 1 hour
```

#### CI/CD Strategy
**Decision:** GitHub Actions

**Pipeline Configuration:**

**.github/workflows/deploy.yml:**
```yaml
name: Deploy to AWS

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run backend tests
        run: |
          cd backend
          pip install -r requirements.txt
          pytest
      - name: Run frontend tests
        run: |
          cd frontend
          npm install
          npm test

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Build Docker image
        run: docker build -t evistream-backend .
      - name: Push to ECR
        run: |
          aws ecr get-login-password | docker login
          docker push $ECR_REPO

  deploy-staging:
    needs: build-and-push
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to ECS Staging
        run: aws ecs update-service --cluster staging
      - name: Run smoke tests
        run: ./scripts/smoke-test.sh staging

  deploy-production:
    needs: deploy-staging
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production  # Requires manual approval
    steps:
      - name: Deploy to ECS Production
        run: aws ecs update-service --cluster production
      - name: Monitor deployment
        run: ./scripts/monitor.sh production
```

**Deployment Steps:**
1. **Tests:** Run all unit/integration tests
2. **Build:** Create Docker images for backend
3. **Push:** Upload to AWS ECR
4. **Deploy Staging:** Update ECS service
5. **Smoke Tests:** Verify staging works
6. **Manual Approval:** Team lead approves
7. **Deploy Production:** Update ECS service
8. **Monitor:** Watch metrics for 1 hour

**Rollback Strategy:**
```bash
# If deployment fails, automatic rollback
aws ecs update-service \
  --cluster production \
  --service backend \
  --task-definition backend:previous

# Or manual rollback to specific version
aws ecs update-service \
  --cluster production \
  --service backend \
  --task-definition backend:42
```

---

### 6. Monitoring & Observability

#### Error Tracking
**Decision:** Sentry

**Configuration:**
```python
# Backend
import sentry_sdk
sentry_sdk.init(
    dsn="https://...",
    environment="production",
    traces_sample_rate=0.1,  # 10% of transactions
    profiles_sample_rate=0.1,
)

# Frontend
Sentry.init({
  dsn: "https://...",
  environment: "production",
  tracesSampleRate: 0.1,
});
```

**What to Track:**
- Unhandled exceptions
- API endpoint failures
- Extraction job failures
- Database connection errors
- Authentication failures

**Alerts:**
- Slack notification for critical errors
- Email for high-priority issues
- PagerDuty for production outages

#### Logging Strategy
**Decision:** Structured JSON logging to CloudWatch

**Log Levels:**
```python
# backend/app/utils/logger.py
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }
        
        # Add extra context
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
            
        return json.dumps(log_data)
```

**What to Log:**

**INFO Level:**
- API requests (method, path, user_id, response_time)
- Extraction jobs started/completed
- Cache hits/misses
- Authentication events (login, logout)

**WARNING Level:**
- Slow queries (> 1 second)
- Cache failures (fallback to DB)
- Rate limit warnings
- Deprecated API usage

**ERROR Level:**
- API endpoint failures
- Database errors
- External service failures (S3, Redis)
- Validation errors

**Log Retention:**
- CloudWatch Logs: 30 days
- S3 Archive: 1 year (compressed)

#### Metrics & Dashboards
**Decision:** CloudWatch Metrics + Custom Dashboard

**Key Metrics:**

**1. Application Metrics:**
```
- API request count (by endpoint)
- API response time (p50, p95, p99)
- Error rate (%)
- Extraction job queue length
- Extraction job completion time
- Cache hit rate (%)
```

**2. Infrastructure Metrics:**
```
- ECS CPU utilization (%)
- ECS memory utilization (%)
- RDS CPU utilization (%)
- RDS connections count
- Redis memory usage (%)
- ALB target response time
```

**3. Business Metrics:**
```
- Active users (daily/weekly/monthly)
- Extractions per day
- Average extractions per user
- Form schemas created per day
- PDF processing success rate (%)
```

**CloudWatch Dashboard:**
```
┌─────────────────────────────────────────┐
│         Application Health              │
├─────────────┬───────────────────────────┤
│ API Latency │ Error Rate               │
│  (graph)    │  (number + graph)        │
├─────────────┼───────────────────────────┤
│ Queue Length│ Job Success Rate         │
│  (number)   │  (pie chart)             │
└─────────────┴───────────────────────────┘

┌─────────────────────────────────────────┐
│       Infrastructure Health             │
├─────────────┬───────────────────────────┤
│ ECS CPU     │ RDS Connections          │
│  (graph)    │  (graph)                 │
├─────────────┼───────────────────────────┤
│ Redis Mem   │ S3 Storage               │
│  (graph)    │  (number)                │
└─────────────┴───────────────────────────┘
```

**Alerts Configuration:**

| Metric | Threshold | Action |
|--------|-----------|--------|
| Error rate | > 5% for 5 min | Slack + Email |
| API latency | p95 > 2s for 5 min | Slack |
| Queue length | > 100 jobs | Auto-scale workers |
| RDS CPU | > 80% for 10 min | Email + Review |
| ECS task failures | > 3 in 5 min | PagerDuty |
| Monthly AWS cost | > $150 | Email alert |

---

## Technology Stack

### Complete Stack Overview

```
┌─────────────────────────────────────────────┐
│              FRONTEND                       │
├─────────────────────────────────────────────┤
│ Framework:     React 18 + TypeScript        │
│ UI Library:    Material-UI (MUI)            │
│ State:         React Query + Zustand        │
│ Routing:       React Router v6              │
│ Forms:         React Hook Form              │
│ HTTP Client:   Axios                        │
│ Build:         Vite                         │
│ Testing:       Jest + React Testing Library │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│              BACKEND                        │
├─────────────────────────────────────────────┤
│ Framework:     FastAPI                      │
│ Language:      Python 3.10+                 │
│ ORM:           SQLAlchemy 2.0               │
│ Migrations:    Alembic                      │
│ Validation:    Pydantic v2                  │
│ Auth:          python-jose (JWT)            │
│ Jobs:          Celery                       │
│ Testing:       pytest + httpx               │
│ Code Quality:  ruff (linter), black (format)│
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│          EXISTING COMPONENTS                │
├─────────────────────────────────────────────┤
│ Extraction:    DSPy Framework               │
│ Workflow:      LangGraph                    │
│ LLM:           Anthropic Claude / Google    │
│ Validation:    Custom validators            │
│ PDF Processing: Marker (MD conversion)      │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│          DATA & STORAGE                     │
├─────────────────────────────────────────────┤
│ Database:      PostgreSQL 14+               │
│ Cache:         Redis 7+                     │
│ File Storage:  AWS S3                       │
│ Blob Storage:  S3 (PDFs, results)          │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│            AWS SERVICES                     │
├─────────────────────────────────────────────┤
│ Compute:       ECS Fargate                  │
│ Load Balancer: Application Load Balancer    │
│ Database:      RDS PostgreSQL               │
│ Cache:         ElastiCache Redis            │
│ Storage:       S3                           │
│ CDN:           CloudFront                   │
│ DNS:           Route 53                     │
│ Certificates:  Certificate Manager          │
│ Registry:      ECR (Docker images)          │
│ Monitoring:    CloudWatch                   │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│          DEVOPS & TOOLING                   │
├─────────────────────────────────────────────┤
│ Version Control: GitHub                     │
│ CI/CD:          GitHub Actions              │
│ Containers:     Docker + Docker Compose     │
│ IaC:            Terraform (optional)        │
│ Error Tracking: Sentry                      │
│ IDE:            Cursor AI                   │
└─────────────────────────────────────────────┘
```

### Version Requirements

**Frontend:**
```json
{
  "node": ">=18.0.0",
  "react": "^18.2.0",
  "@mui/material": "^5.14.0",
  "@tanstack/react-query": "^5.0.0",
  "zustand": "^4.4.0",
  "axios": "^1.6.0",
  "react-router-dom": "^6.20.0",
  "typescript": "^5.3.0"
}
```

**Backend:**
```txt
python>=3.10,<3.13
fastapi==0.104.0
sqlalchemy==2.0.23
alembic==1.12.0
pydantic==2.5.0
celery[redis]==5.3.4
redis==5.0.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pytest==7.4.3
httpx==0.25.0
```

---

## Development Timeline

### Timeline Comparison

| Phase | Without Cursor | With Cursor | Savings |
|-------|---------------|-------------|---------|
| Backend Foundation | 3 weeks | 2 weeks | 1 week |
| Caching Layer | 1 week | 3 days | 4 days |
| Frontend Development | 3 weeks | 2 weeks | 1 week |
| AWS Deployment | 2 weeks | 1 week | 1 week |
| Monitoring & Security | 1 week | 4 days | 3 days |
| Testing & Polish | 2 weeks | 1 week | 1 week |
| **TOTAL** | **12 weeks** | **6-7 weeks** | **~5 weeks** |

---

## Detailed Implementation Plan

### Phase 1: Backend Foundation (Weeks 1-2 with Cursor)

#### Week 1: Core API Setup

**Day 1-2: Project Setup**

**Tasks:**
1. Initialize FastAPI project structure
2. Set up PostgreSQL connection
3. Configure Alembic for migrations
4. Create base models (User, Project, Form)
5. Implement JWT authentication
6. Set up environment configuration

**Cursor Assistance:**
```
Prompt: "Create a production-ready FastAPI project with:
- User authentication using JWT tokens
- PostgreSQL connection with SQLAlchemy 2.0
- Alembic for migrations
- Environment configuration with pydantic-settings
- Project and Form models with proper relationships
- Health check and documentation endpoints"

Cursor generates: Complete project structure in 10 minutes
You do: Review code, test locally, adjust naming
```

**Deliverables:**
- [ ] FastAPI app running on `http://localhost:8000`
- [ ] `/docs` (Swagger UI) accessible
- [ ] `/health` endpoint responding
- [ ] User registration/login endpoints working
- [ ] PostgreSQL database connected
- [ ] Initial migration applied

**Time: 2 days**

---

**Day 3-4: CRUD Endpoints**

**Tasks:**
1. Projects API endpoints (create, list, get, update, delete)
2. Forms API endpoints (create, list, get, update, delete)
3. Pydantic schemas for validation
4. Authorization middleware (user can only access own projects)
5. Pagination for list endpoints
6. Error handling and validation

**Cursor Assistance:**
```
Prompt: "Create complete CRUD endpoints for Projects with:
- POST /api/v1/projects (create)
- GET /api/v1/projects (list with pagination)
- GET /api/v1/projects/{id} (get one)
- PUT /api/v1/projects/{id} (update)
- DELETE /api/v1/projects/{id} (delete)
- Proper authorization (users can only access own projects)
- Pydantic schemas for request/response
- Error handling with proper status codes"

Cursor generates: All endpoints with validation and auth
You do: Test with Postman, add business logic
```

**Deliverables:**
- [ ] All project endpoints working
- [ ] All form endpoints working
- [ ] Authorization enforced
- [ ] Validation errors return 422
- [ ] Postman collection with all endpoints

**Time: 2 days**

---

**Day 5: Redis Integration**

**Tasks:**
1. Set up Redis connection
2. Create cache service wrapper
3. Add caching to GET endpoints
4. Cache invalidation on updates

**Cursor Assistance:**
```
Prompt: "Add Redis caching to FastAPI with:
- Async Redis client
- Cache decorator for endpoints
- TTL: 5 min for lists, 1 hour for individual items
- Automatic cache invalidation on updates/deletes
- Cache keys: 'projects:{user_id}', 'project:{id}'"

Cursor generates: Complete caching layer
You do: Test cache hits/misses, verify TTL
```

**Deliverables:**
- [ ] Redis running locally
- [ ] Cache service implemented
- [ ] GET endpoints use cache
- [ ] Cache invalidates on updates
- [ ] Cache hit rate logged

**Time: 1 day**

---

#### Week 2: Extraction Pipeline

**Day 1-2: DSPy Integration**

**Tasks:**
1. Move existing `core/generators` into backend
2. Update imports for FastAPI structure
3. Create extraction service wrapper
4. Add endpoints for schema generation
5. Store generated schemas in database

**Cursor Assistance:**
```
Prompt: "Create FastAPI endpoints for DSPy schema generation:
- POST /api/v1/schemas/generate (takes form_data, returns task_id)
- GET /api/v1/schemas/{task_id}/status (returns generation status)
- GET /api/v1/schemas/{task_id} (returns generated schema)
- Integrate with existing LangGraph workflow
- Store schemas in forms.schema_definition JSONB field"

Cursor generates: Service layer and endpoints
You do: Integrate your existing workflow code, test
```

**Deliverables:**
- [ ] Schema generation endpoint working
- [ ] LangGraph workflow integrated
- [ ] Schemas stored in database
- [ ] Status polling working

**Time: 2 days**

---

**Day 3-4: Background Jobs**

**Tasks:**
1. Set up Celery with Redis broker
2. Create extraction task
3. File upload to S3
4. Job status tracking
5. Result storage

**Cursor Assistance:**
```
Prompt: "Set up Celery background jobs for PDF extraction:
- Celery app configuration with Redis broker
- Task: extract_pdf(extraction_id, pdf_url, form_schema)
- Upload PDF to S3, download markdown
- Run DSPy extraction
- Store results in extraction_results table
- Update job status in Redis (queued, processing, completed, failed)
- API endpoints: POST /extractions/run, GET /extractions/{id}/status"

Cursor generates: Complete Celery setup
You do: Test with real PDFs, tune worker settings
```

**Deliverables:**
- [ ] Celery worker running
- [ ] S3 uploads working
- [ ] Extraction jobs complete successfully
- [ ] Results stored correctly
- [ ] Status updates in real-time

**Time: 2 days**

---

**Day 5: Testing & Polish**

**Tasks:**
1. Write unit tests for endpoints
2. Integration tests for extraction flow
3. Fix bugs found during testing
4. Add API documentation
5. Code cleanup and optimization

**Cursor Assistance:**
```
Prompt: "Generate pytest tests for these API endpoints:
- Test all CRUD operations
- Test authentication and authorization
- Test error cases (404, 401, 422)
- Mock external dependencies (S3, Redis)
- Test extraction job lifecycle"

Cursor generates: Comprehensive test suite
You do: Run tests, fix failures, add edge cases
```

**Deliverables:**
- [ ] 70%+ test coverage
- [ ] All critical paths tested
- [ ] API documentation complete
- [ ] Backend ready for frontend integration

**Time: 1 day**

---

### Phase 2: Frontend Development (Weeks 3-4 with Cursor)

#### Week 3: Core UI

**Day 1: React Setup**

**Tasks:**
1. Initialize React with TypeScript
2. Set up Material-UI theme
3. Configure React Router
4. Create layout components
5. Set up Axios client

**Cursor Assistance:**
```
Prompt: "Create React TypeScript app with:
- Material-UI theme (light/dark mode)
- React Router with protected routes
- Axios client with auth interceptor
- Layout: AppBar, Sidebar, Content area
- Auth context and hooks
- Login page with MUI components"

Cursor generates: Complete React setup
You do: Customize theme colors, test routing
```

**Deliverables:**
- [ ] React app running on `http://localhost:3000`
- [ ] MUI theme applied
- [ ] Routing configured
- [ ] Login page functional

**Time: 1 day**

---

**Day 2-3: Core Pages**

**Tasks:**
1. Dashboard page (overview)
2. Projects list page
3. Project detail page
4. Form builder/editor page

**Cursor Assistance:**
```
Prompt: "Create ProjectsPage component with:
- MUI DataGrid showing projects
- Create button opens dialog
- Edit/Delete actions
- useProjects hook with React Query
- Loading skeletons
- Error handling with Snackbar"

Cursor generates: Complete page with all features
You do: Style, test interactions, add business logic
```

**Deliverables:**
- [ ] All core pages functional
- [ ] CRUD operations working
- [ ] Loading states handled
- [ ] Errors displayed to user

**Time: 2 days**

---

**Day 4-5: Extraction UI**

**Tasks:**
1. PDF upload component
2. Extraction form (select schema, upload files)
3. Job status polling
4. Progress indicators

**Cursor Assistance:**
```
Prompt: "Create ExtractionPage with:
- Dropzone for PDF upload (react-dropzone)
- Form schema selector (autocomplete)
- Submit button starts extraction
- Progress indicator with job status
- Poll /extractions/{id}/status every 2 seconds
- Redirect to results when complete"

Cursor generates: Complete extraction UI
You do: Test with real files, handle edge cases
```

**Deliverables:**
- [ ] File upload working
- [ ] Extraction jobs start correctly
- [ ] Status polling functional
- [ ] User sees progress updates

**Time: 2 days**

---

#### Week 4: Results & Polish

**Day 1-2: Results Viewer**

**Tasks:**
1. Results table view (MUI DataGrid)
2. JSON view toggle
3. PDF viewer (react-pdf)
4. Export to CSV
5. Download results

**Cursor Assistance:**
```
Prompt: "Create ResultsViewer component with:
- Toggle between Table view and JSON view
- MUI DataGrid for table (columns from schema)
- JSON view with syntax highlighting
- PDF viewer on right side (react-pdf)
- Export to CSV button (use papaparse)
- Download original PDF button"

Cursor generates: Complete results viewer
You do: Style layout, test with various data
```

**Deliverables:**
- [ ] Results display correctly
- [ ] Table view formatted well
- [ ] JSON view readable
- [ ] PDF viewer works
- [ ] Export to CSV functional

**Time: 2 days**

---

**Day 3-4: UX Polish**

**Tasks:**
1. Loading skeletons everywhere
2. Toast notifications for actions
3. Responsive design (mobile-friendly)
4. Dark mode toggle
5. Error boundaries

**Cursor Assistance:**
```
Prompt: "Add UX improvements:
- Replace loading spinners with MUI Skeletons
- Add react-toastify for success/error messages
- Make all pages responsive (use MUI breakpoints)
- Add dark mode toggle in AppBar
- Add error boundaries for crash recovery"

Cursor generates: All UX improvements
You do: Test on mobile, refine animations
```

**Deliverables:**
- [ ] Smooth loading experience
- [ ] User feedback on actions
- [ ] Mobile-responsive
- [ ] Dark mode working
- [ ] Graceful error handling

**Time: 2 days**

---

**Day 5: Integration Testing**

**Tasks:**
1. End-to-end testing with real data
2. Fix bugs found during testing
3. Performance optimization
4. Accessibility audit

**Deliverables:**
- [ ] Full user flow tested
- [ ] No console errors
- [ ] Fast page loads
- [ ] Accessible to screen readers

**Time: 1 day**

---

### Phase 3: AWS Deployment (Week 5 with Cursor)

#### Week 5: Infrastructure & Deployment

**Day 1-2: AWS Setup**

**Tasks:**
1. Create AWS account (if needed)
2. Set up IAM users and roles
3. Create VPC and subnets
4. Set up RDS PostgreSQL
5. Set up ElastiCache Redis
6. Create S3 bucket
7. Configure security groups

**Manual Steps (Can't be automated):**
- AWS account creation
- Billing alerts configuration
- IAM user creation

**Cursor Assistance:**
```
Prompt: "Create Terraform configuration for AWS:
- VPC with public/private subnets
- RDS PostgreSQL (db.t3.medium, Multi-AZ)
- ElastiCache Redis (cache.t3.micro)
- S3 bucket with versioning
- Security groups (ALB, ECS, RDS, Redis)
- IAM roles for ECS tasks"

Cursor generates: Complete Terraform config
You do: Review, apply with terraform apply
```

**Deliverables:**
- [ ] AWS infrastructure running
- [ ] Database accessible from VPC
- [ ] Redis accessible from VPC
- [ ] S3 bucket created
- [ ] Security groups configured

**Time: 2 days**

---

**Day 3-4: Containerization & Deploy**

**Tasks:**
1. Create Dockerfile for backend
2. Create docker-compose for local testing
3. Build and push to ECR
4. Create ECS task definitions
5. Set up ECS services (API + workers)
6. Configure ALB
7. Deploy frontend to CloudFront

**Cursor Assistance:**
```
Prompt: "Create production Dockerfile for FastAPI:
- Multi-stage build
- Poetry for dependencies
- Non-root user
- Health check
- Optimized layers
Then create ECS task definition and service config"

Cursor generates: Docker + ECS configs
You do: Build, test, push to ECR, deploy
```

**Deliverables:**
- [ ] Docker images building
- [ ] Backend running on ECS
- [ ] Workers processing jobs
- [ ] Frontend on CloudFront
- [ ] ALB routing traffic

**Time: 2 days**

---

**Day 5: SSL & Domain**

**Tasks:**
1. Configure Route 53 domain
2. Request SSL certificate
3. Configure CloudFront with SSL
4. Configure ALB with SSL
5. Test HTTPS access

**Deliverables:**
- [ ] Custom domain working
- [ ] HTTPS enabled
- [ ] Certificate validated
- [ ] All traffic encrypted

**Time: 1 day**

---

### Phase 4: Monitoring & Testing (Week 6 with Cursor)

#### Week 6: Production Readiness

**Day 1-2: Monitoring Setup**

**Tasks:**
1. Configure Sentry for errors
2. Set up CloudWatch dashboards
3. Create alarms (high error rate, slow API, etc.)
4. Set up log aggregation
5. Configure cost alerts

**Cursor Assistance:**
```
Prompt: "Generate CloudWatch dashboard config:
- API latency (p50, p95, p99)
- Error rate (%)
- ECS CPU/memory
- RDS connections
- Queue length
- Alarms: error rate > 5%, latency > 2s"

Cursor generates: Dashboard and alarm configs
You do: Create in AWS console, test alerts
```

**Deliverables:**
- [ ] Sentry catching errors
- [ ] CloudWatch dashboard live
- [ ] Alarms triggering correctly
- [ ] Logs searchable

**Time: 2 days**

---

**Day 3-4: Testing**

**Tasks:**
1. End-to-end testing on staging
2. Load testing with Locust
3. Security audit (OWASP checklist)
4. Performance optimization
5. Bug fixes

**Cursor Assistance:**
```
Prompt: "Create Locust load test script:
- Simulate 50 concurrent users
- Create projects, upload PDFs, run extractions
- Target: 100 requests/second
- Report p95 latency and error rate"

Cursor generates: Complete load test
You do: Run tests, identify bottlenecks, optimize
```

**Deliverables:**
- [ ] Load tests passing
- [ ] Security audit complete
- [ ] Performance benchmarks met
- [ ] Critical bugs fixed

**Time: 2 days**

---

**Day 5: Launch Preparation**

**Tasks:**
1. Write user documentation
2. Create demo video
3. Prepare launch checklist
4. Soft launch with beta users
5. Collect feedback

**Deliverables:**
- [ ] Documentation published
- [ ] Demo video recorded
- [ ] Beta users invited
- [ ] Feedback collected
- [ ] Ready for full launch

**Time: 1 day**

---

## Cost Estimates

### Monthly Operational Costs

**AWS Services (Production):**

| Service | Specification | Monthly Cost |
|---------|--------------|--------------|
| **ECS Fargate (API)** | 2-4 tasks (0.5 vCPU, 1GB) | $30-60 |
| **ECS Fargate (Workers)** | 1-3 tasks (1 vCPU, 2GB) | $25-50 |
| **RDS PostgreSQL** | db.t3.medium (2 vCPU, 4GB), Multi-AZ | $45-60 |
| **ElastiCache Redis** | cache.t3.micro (0.5 vCPU, 0.5GB) | $12-15 |
| **S3 Storage** | 100GB storage, 1000 requests | $3-5 |
| **CloudFront** | 100GB transfer | $8-12 |
| **Route 53** | 1 hosted zone | $0.50 |
| **Application Load Balancer** | 1 ALB | $16-20 |
| **Data Transfer** | Outbound 50GB | $4-6 |
| **CloudWatch** | Logs, metrics, alarms | $5-10 |
| **ECR** | Docker image storage | $1-2 |
| **Backups** | RDS snapshots, S3 versioning | $2-5 |
| **Total (Estimated)** | | **$151-245/month** |

**Optimizations to Reduce Cost:**

**Development Environment (~$30-40/month):**
- db.t3.micro RDS (instead of t3.medium)
- Single-AZ RDS
- 1 ECS task (instead of auto-scaling)
- cache.t3.micro Redis
- No CloudFront (use ALB directly)
- **Savings: ~$110/month**

**Minimal Production (~$80-100/month):**
- db.t3.small RDS
- cache.t3.micro Redis
- 2 ECS tasks (API)
- 1 ECS task (worker)
- CloudFront on-demand pricing
- **Still production-ready, lower cost**

---

### Third-Party Services

| Service | Plan | Monthly Cost |
|---------|------|--------------|
| **Sentry** | Team (100K events/mo) | Free - $26 |
| **Domain Name** | .com TLD | $1/month ($12/year) |
| **Cursor Pro** | AI coding assistant | $20 |
| **GitHub** | Free or Team | $0-4/user |
| **Total Third-Party** | | **$21-51/month** |

---

### Development Costs

**Assuming 1 Developer @ $50/hour:**

**Manual Development (12 weeks):**
- 12 weeks × 40 hours = 480 hours
- 480 hours × $50/hour = **$24,000**

**With Cursor (6 weeks):**
- 6 weeks × 40 hours = 240 hours
- 240 hours × $50/hour = **$12,000**
- Cursor Pro: $20/month × 2 months = $40
- **Total: $12,040**
- **Savings: $11,960 (50%)**

---

### Total Cost of Ownership (First Year)

**Development:**
- With Cursor: $12,000

**Operations (12 months):**
- Production AWS: $1,800 (avg $150/month)
- Third-party services: $600 (avg $50/month)

**Total First Year: ~$14,400**

**Ongoing (per year after):**
- AWS: $1,800/year
- Services: $600/year
- Maintenance (10% dev time): $1,200/year
- **Total: ~$3,600/year**

---

## Risk Management

### Critical Risks & Mitigation Strategies

#### 1. Cost Overruns (Risk Level: HIGH)

**Risk:**
AWS costs exceed budget, especially during development/testing phase.

**Impact:**
- $500+ surprise bills
- Project budget exhausted
- Need to shut down services

**Mitigation:**
1. **Set Billing Alerts:**
   - $50 alert (warning)
   - $100 alert (review usage)
   - $150 alert (critical, stop non-essential services)

2. **Use AWS Cost Explorer:**
   - Review costs weekly
   - Identify unexpected charges
   - Optimize underutilized resources

3. **Development Best Practices:**
   - Shut down staging when not in use
   - Use auto-scaling with maximum limits
   - Delete old snapshots and logs
   - Use spot instances for workers (70% cost reduction)

4. **Cost Optimization:**
   - Use S3 lifecycle policies (delete old uploads after 90 days)
   - Enable CloudWatch log retention (30 days max)
   - Use RDS reserved instances if running 24/7 (40% savings)

**Monitoring:**
- Weekly cost review meetings
- Track cost per extraction
- Budget dashboard in CloudWatch

---

#### 2. DSPy Integration Breakage (Risk Level: HIGH)

**Risk:**
Existing DSPy extraction code doesn't work in new architecture.

**Impact:**
- Core functionality broken
- Need to rewrite extraction logic
- Project timeline extended by 2-4 weeks

**Mitigation:**
1. **Test Early (Week 2 Day 1):**
   - First task: Integrate existing code
   - Test with sample PDFs immediately
   - Identify issues before building UI

2. **Keep Streamlit as Backup:**
   - Don't delete original prototype
   - Can fall back if integration fails
   - Use as reference implementation

3. **Incremental Integration:**
   - Step 1: Move code without changes
   - Step 2: Test in isolation
   - Step 3: Integrate with FastAPI
   - Step 4: Add background jobs
   - Validate at each step

4. **Maintain Test Suite:**
   - Keep extraction tests from prototype
   - Run tests after each change
   - Track extraction accuracy metrics

**Monitoring:**
- Extraction success rate metric
- Compare results with prototype
- Alert if accuracy drops > 5%

---

#### 3. Database Migration Issues (Risk Level: MEDIUM)

**Risk:**
Data loss or corruption during migrations, especially with JSON fields.

**Impact:**
- Lost user data
- Need to restore from backup
- User trust damaged

**Mitigation:**
1. **Always Backup Before Migration:**
   ```bash
   # Automated in deployment script
   pg_dump production_db > backup_$(date +%Y%m%d).sql
   ```

2. **Test Migrations in Staging:**
   - Never run migrations in production first
   - Copy production data to staging for realistic testing
   - Verify data integrity after migration

3. **Use Alembic Properly:**
   - Always create migration: `alembic revision --autogenerate`
   - Review generated SQL before applying
   - Test rollback: `alembic downgrade -1`

4. **Implement Health Checks:**
   - Database connectivity check
   - Critical table existence check
   - Data integrity checks (row counts, constraints)

**Recovery Plan:**
- Keep 7 days of automated backups
- Practice restore procedure quarterly
- Document recovery steps

---

#### 4. Performance Issues (Risk Level: MEDIUM)

**Risk:**
System is too slow, especially for extraction jobs or large result sets.

**Impact:**
- Poor user experience
- Users abandon platform
- Need expensive infrastructure upgrades

**Mitigation:**
1. **Load Testing (Week 6):**
   - Test with 50 concurrent users
   - Test with large PDFs (50+ pages)
   - Test with 1000+ extraction results
   - Identify bottlenecks early

2. **Caching Strategy:**
   - Cache extraction results (1 hour)
   - Cache form schemas (6 hours)
   - Use CloudFront for static assets
   - Result: 60-80% faster reads

3. **Database Optimization:**
   - Add indexes on frequent queries
   - Use connection pooling (SQLAlchemy)
   - Implement read replicas for reporting
   - Monitor slow queries (> 1 second)

4. **Async Processing:**
   - Move heavy work to background jobs
   - Return job_id immediately
   - User polls for status
   - No blocking API calls

**Performance Targets:**
- API response time: < 500ms (p95)
- Extraction job completion: < 5 minutes
- Results page load: < 2 seconds
- Cache hit rate: > 70%

**Monitoring:**
- CloudWatch API latency metrics
- Slow query logs
- Cache hit rate tracking
- User-reported performance issues

---

#### 5. Security Vulnerabilities (Risk Level: HIGH)

**Risk:**
Security breach, data leak, or unauthorized access.

**Impact:**
- User data compromised
- Regulatory violations (HIPAA if medical data)
- Reputation damage
- Legal liability

**Mitigation:**
1. **Follow OWASP Top 10:**
   - SQL injection: Use ORMs (SQLAlchemy) ✓
   - XSS: React escapes by default ✓
   - CSRF: Use httpOnly cookies ✓
   - Authentication: JWT with expiration ✓

2. **AWS Security Best Practices:**
   - Use security groups (restrict ports)
   - Enable VPC (no public database access)
   - Use IAM roles (no hardcoded credentials)
   - Enable encryption at rest (RDS, S3)
   - Enable encryption in transit (SSL/TLS)

3. **Code Security:**
   - Store secrets in AWS Secrets Manager
   - Never commit `.env` files
   - Use dependency scanning (Dependabot)
   - Regular security audits

4. **Access Control:**
   - Role-based permissions
   - Audit logs for sensitive operations
   - Two-factor authentication (post-MVP)
   - Regular access review

**Security Checklist:**
- [ ] All endpoints require authentication
- [ ] Users can only access own data
- [ ] Passwords hashed with bcrypt
- [ ] HTTPS enforced everywhere
- [ ] CORS configured properly
- [ ] Rate limiting on public endpoints
- [ ] Input validation on all endpoints
- [ ] Security headers set (HSTS, CSP)
- [ ] Dependencies up-to-date
- [ ] Secrets in AWS Secrets Manager

**Monitoring:**
- Failed login attempts
- Unauthorized access attempts
- Unusual API usage patterns
- AWS GuardDuty alerts

---

#### 6. Third-Party Service Failures (Risk Level: LOW-MEDIUM)

**Risk:**
External services fail (Anthropic API, Sentry, etc.)

**Impact:**
- Extractions fail
- No error tracking
- User-facing errors

**Mitigation:**
1. **Graceful Degradation:**
   - If Sentry fails, log locally
   - If cache fails, fallback to DB
   - If S3 fails, retry with exponential backoff

2. **Circuit Breaker Pattern:**
   ```python
   @circuit_breaker(fail_threshold=5, timeout=60)
   def call_llm_api():
       # If fails 5 times, open circuit for 60s
       pass
   ```

3. **Retry Logic:**
   - Automatic retries for transient failures
   - Exponential backoff (1s, 2s, 4s, 8s)
   - Max 3 retries

4. **Service Monitoring:**
   - Track API success rates
   - Alert on > 5% failure rate
   - Have backup LLM providers

**Recovery Plan:**
- Document manual fallback procedures
- Have backup API keys
- Queue jobs for later retry

---

#### 7. Deployment Failures (Risk Level: MEDIUM)

**Risk:**
Deployment breaks production, causing downtime.

**Impact:**
- Service unavailable
- Users can't work
- Data processing stopped

**Mitigation:**
1. **Blue-Green Deployments:**
   - ECS deploys new version alongside old
   - Test new version with health checks
   - Switch traffic only if healthy
   - Automatic rollback if unhealthy

2. **Staged Rollout:**
   ```
   Local → Staging → Production
   Test each environment before proceeding
   ```

3. **Health Checks:**
   ```python
   @app.get("/health")
   async def health():
       # Check database connection
       # Check Redis connection
       # Check critical services
       return {"status": "healthy"}
   ```

4. **Rollback Plan:**
   - Keep previous ECS task definition
   - One-command rollback: `./scripts/rollback.sh`
   - Test rollback procedure quarterly

**Deployment Checklist:**
- [ ] All tests passing
- [ ] Staging deployment successful
- [ ] Health checks passing
- [ ] Database migrations successful
- [ ] Smoke tests passing
- [ ] Team notified of deployment
- [ ] Rollback plan ready
- [ ] Monitor metrics for 1 hour post-deploy

**Monitoring:**
- ECS task health
- ALB target health
- API error rates
- User-reported issues

---

## Success Metrics

### Launch Criteria (Week 6)

**Technical Metrics:**
- [ ] All API endpoints functional
- [ ] Extraction accuracy ≥ 95% of prototype
- [ ] API response time p95 < 2 seconds
- [ ] Extraction job completion < 5 minutes
- [ ] Uptime ≥ 99.5% in staging
- [ ] Test coverage ≥ 70%
- [ ] Zero critical security vulnerabilities
- [ ] All monitoring and alerts configured

**User Experience:**
- [ ] Complete user flow tested end-to-end
- [ ] Mobile responsive on 3 device sizes
- [ ] Accessible (WCAG 2.1 AA)
- [ ] Error messages helpful and clear
- [ ] Loading states smooth (no jarring)
- [ ] Dark mode functional
- [ ] Documentation complete

**Operations:**
- [ ] CI/CD pipeline working
- [ ] Backup/restore tested
- [ ] Rollback procedure tested
- [ ] On-call runbook complete
- [ ] Cost monitoring configured
- [ ] Log aggregation working

---

### Key Performance Indicators (KPIs)

**Week 4 (MVP Milestone):**
- Backend API: 30+ endpoints functional
- Frontend: 5 main pages working
- Integration: Full user flow possible
- Tests: 50%+ coverage

**Week 6 (Launch Milestone):**
- Deployed to AWS and accessible
- 5 beta users actively using
- 100+ extractions completed successfully
- < 5 critical bugs found

**Month 1 (Post-Launch):**
- 20+ active users
- 500+ extractions completed
- 99%+ uptime
- < 2% error rate
- < $150/month AWS costs

**Month 3 (Stable Operations):**
- 50+ active users
- 2000+ extractions completed
- 99.5%+ uptime
- < 1% error rate
- Optimized costs (< $100/month)

---

### Business Metrics

**User Adoption:**
- Active users (daily/weekly/monthly)
- New user signups per week
- User retention rate
- Feature adoption rate

**Usage Metrics:**
- Extractions per day
- Average extractions per user
- Form schemas created
- PDF processing time

**Quality Metrics:**
- Extraction accuracy (vs ground truth)
- User-reported errors
- Time to extract vs prototype
- Result quality ratings (user feedback)

**Technical Health:**
- API uptime (%)
- Error rate (%)
- Mean time to recovery (MTTR)
- Deployment frequency
- Change failure rate

---

## Team & Resources

### Required Skills

**Must Have:**
- Python programming (intermediate) ✓ You have this
- Basic SQL and database concepts
- REST API fundamentals
- Git and version control
- Command line / terminal usage

**Nice to Have:**
- React/JavaScript basics
- Docker fundamentals
- AWS basic knowledge
- CI/CD concepts

**Will Learn During Project:**
- FastAPI framework
- React Query and state management
- AWS ECS/Fargate deployment
- Redis caching strategies
- Celery background jobs
- CloudWatch monitoring

---

### Development Tools

**Required:**
- Cursor AI (IDE) - $20/month ✓ You have this
- AWS Account - Free tier available
- GitHub Account - Free
- Postman or Thunder Client - Free
- Docker Desktop - Free
- PostgreSQL (local) - Free
- Redis (local or Cloud) - Free tier available

**Recommended:**
- TablePlus (database GUI) - Free tier
- AWS Console mobile app - Free
- Slack (team communication) - Free
- Notion (documentation) - Free

---

### External Dependencies

**AI Services:**
- Anthropic API or Google AI - Pay per use
- Current usage from prototype

**AWS Services:**
- See cost estimates section
- Credit card required
- Start with free tier where possible

**Domain & SSL:**
- Domain name (optional): ~$12/year
- SSL certificate: Free via AWS ACM

---

## Next Steps

### Immediate Actions (This Week)

**Day 1: Environment Setup**
1. [ ] Install Docker Desktop
2. [ ] Install PostgreSQL locally
3. [ ] Install Redis locally
4. [ ] Set up AWS account (if not already)
5. [ ] Configure AWS CLI

**Day 2-3: Backend Foundation**
1. [ ] Use Cursor to generate FastAPI structure
2. [ ] Set up local database
3. [ ] Create initial models (User, Project, Form)
4. [ ] Implement authentication
5. [ ] Test with Postman

**Day 4-5: Integration Planning**
1. [ ] Review existing DSPy code
2. [ ] Plan integration approach
3. [ ] Create test dataset (sample PDFs and expected results)
4. [ ] Set up project tracking (GitHub Issues or Notion)

---

### Weekly Checkpoints

**End of Week 1:**
- Backend API with authentication running
- Database schema created
- Redis caching working
- Postman collection with all endpoints

**End of Week 2:**
- DSPy extraction integrated
- Background jobs working
- S3 file upload functional
- Extraction end-to-end tested

**End of Week 3:**
- React app with all pages
- Authentication flow working
- Project and form management UI complete
- API integration functional

**End of Week 4:**
- Extraction UI complete
- Results viewer functional
- Full user flow working
- Ready for deployment

**End of Week 5:**
- Deployed to AWS
- HTTPS enabled
- Monitoring configured
- Staging environment tested

**End of Week 6:**
- Production tested with real users
- Documentation complete
- Bugs fixed
- Launch-ready

---

### Decision Points

**Week 2 Decision: Continue or Pivot?**
- If DSPy integration is smooth → Continue as planned
- If integration has major issues → Consider keeping Streamlit backend, build React frontend around it
- If extraction quality drops → Pause, fix accuracy before continuing

**Week 4 Decision: MVP or Full Build?**
- If ahead of schedule → Add nice-to-have features
- If on schedule → Proceed to deployment
- If behind schedule → Cut non-essential features, focus on core functionality

**Week 6 Decision: Launch or Delay?**
- If all metrics green → Launch to production
- If minor issues → Soft launch with limited users
- If major issues → Delay, fix critical bugs first

---

### Support & Help

**When You Get Stuck:**

1. **Cursor AI:**
   - Ask Cursor for help with specific errors
   - Use Cursor chat to debug issues
   - Composer for generating fixes

2. **Documentation:**
   - FastAPI docs: https://fastapi.tiangolo.com/
   - React Query: https://tanstack.com/query/latest
   - Material-UI: https://mui.com/
   - AWS docs: https://docs.aws.amazon.com/

3. **Community:**
   - FastAPI Discord
   - React subreddit
   - AWS re:Post forums
   - Stack Overflow

4. **Me (AI Assistant):**
   - Come back anytime for clarifications
   - I can help debug specific issues
   - I can review architecture decisions

---

## Appendix

### Useful Commands

**Docker:**
```bash
# Build backend
docker build -t evistream-backend .

# Run locally
docker-compose up

# Stop services
docker-compose down

# View logs
docker-compose logs -f backend
```

**Database:**
```bash
# Create migration
alembic revision --autogenerate -m "Add new table"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1

# Backup database
pg_dump dbname > backup.sql

# Restore database
psql dbname < backup.sql
```

**AWS CLI:**
```bash
# Push Docker image to ECR
aws ecr get-login-password | docker login --username AWS
docker push $ECR_REPO

# Update ECS service
aws ecs update-service --cluster prod --service backend

# View logs
aws logs tail /ecs/backend --follow

# Check costs
aws ce get-cost-and-usage --time-period Start=2024-01,End=2024-02
```

**Development:**
```bash
# Backend
cd backend
uvicorn app.main:app --reload

# Frontend
cd frontend
npm run dev

# Run tests
pytest
npm test

# Format code
black .
npm run format

# Lint code
ruff check .
npm run lint
```

---

### Reference Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                        USERS                            │
│              (Browsers, Mobile Devices)                 │
└────────────────────┬────────────────────────────────────┘
                     │ HTTPS
                     ↓
┌─────────────────────────────────────────────────────────┐
│                   Route 53 (DNS)                        │
│              app.evistream.com → CloudFront             │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴───────────┐
        │                        │
        ↓                        ↓
┌───────────────┐      ┌─────────────────┐
│  CloudFront   │      │  Application    │
│   (Static)    │      │ Load Balancer   │
│               │      │    (API)        │
│  React App    │      │                 │
│  /js, /css    │      │  HTTPS only     │
└───────────────┘      └────────┬────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
                    ↓                       ↓
        ┌──────────────────┐    ┌─────────────────┐
        │   ECS Service    │    │  ECS Service    │
        │   (FastAPI)      │    │  (Celery)       │
        │                  │    │                 │
        │  Task 1: API     │    │  Task 1: Worker │
        │  Task 2: API     │    │  Task 2: Worker │
        │  Task 3: API     │    │  Task 3: Worker │
        │                  │    │                 │
        │  Auto-scales     │    │  Auto-scales    │
        │  CPU > 70%       │    │  Queue > 50     │
        └────────┬─────────┘    └────────┬────────┘
                 │                       │
                 └───────────┬───────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
            ↓                ↓                ↓
    ┌──────────────┐ ┌──────────────┐ ┌──────────┐
    │     RDS      │ │ ElastiCache  │ │    S3    │
    │  PostgreSQL  │ │    Redis     │ │          │
    │              │ │              │ │  - PDFs  │
    │  Multi-AZ    │ │  - Cache     │ │  - Logs  │
    │  Encrypted   │ │  - Queue     │ │  - Static│
    │  Backups     │ │  - Sessions  │ │          │
    └──────────────┘ └──────────────┘ └──────────┘

    ┌─────────────────────────────────────────────┐
    │          Monitoring & Logging               │
    ├─────────────────────────────────────────────┤
    │  CloudWatch    │  Sentry    │  Cost Alerts │
    │  - Logs        │  - Errors  │  - Budget    │
    │  - Metrics     │  - APM     │  - Threshold │
    │  - Alarms      │  - Traces  │              │
    └─────────────────────────────────────────────┘
```

---

### Glossary

**API (Application Programming Interface):**
Interface for programs to communicate. In this project, REST API endpoints that React frontend calls.

**Auto-scaling:**
Automatically increasing/decreasing compute resources based on demand (e.g., more CPU → add more tasks).

**Cache:**
Temporary storage of frequently accessed data for faster retrieval. Redis stores results so we don't re-compute.

**CDN (Content Delivery Network):**
Distributed servers that deliver content from location closest to user. CloudFront caches React app globally.

**CI/CD (Continuous Integration/Continuous Deployment):**
Automated pipeline that tests and deploys code when changes are pushed to Git.

**CRUD (Create, Read, Update, Delete):**
Basic operations for data management. Most APIs provide CRUD for each resource.

**ECS (Elastic Container Service):**
AWS service to run Docker containers without managing servers.

**Fargate:**
Serverless compute for containers. AWS manages servers, you just run containers.

**JWT (JSON Web Token):**
Standard for authentication tokens. Contains user info, signed to prevent tampering.

**ORM (Object-Relational Mapping):**
SQLAlchemy translates Python objects to SQL queries. Write `user.save()` instead of SQL.

**RDS (Relational Database Service):**
Managed PostgreSQL/MySQL service. AWS handles backups, updates, scaling.

**TTL (Time To Live):**
How long cached data stays before expiring. 1 hour TTL = cache refreshes every hour.

**VPC (Virtual Private Cloud):**
Isolated network in AWS. Database lives in VPC, not accessible from internet.

---

### Troubleshooting Guide

**Problem: Docker build fails**
```bash
# Clear Docker cache
docker system prune -a

# Rebuild without cache
docker build --no-cache -t evistream .
```

**Problem: Database connection fails**
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check connection string
echo $DATABASE_URL

# Test connection manually
psql $DATABASE_URL
```

**Problem: Celery workers not processing**
```bash
# Check Redis is running
redis-cli ping

# Check worker status
celery -A app.celery_app inspect active

# Restart workers
docker-compose restart worker
```

**Problem: AWS deployment fails**
```bash
# Check ECS task logs
aws logs tail /ecs/backend --follow

# Check task stopped reason
aws ecs describe-tasks --cluster prod --tasks $TASK_ID

# Common issues:
# - Environment variables not set
# - Security group blocking ports
# - Task role missing permissions
```

**Problem: High AWS costs**
```bash
# Check cost breakdown
aws ce get-cost-and-usage --time-period Start=2024-01,End=2024-02 --granularity DAILY

# Common causes:
# - Forgot to stop staging environment
# - Auto-scaling set too high
# - RDS instance too large
# - S3 storage not cleaned up
```

---

## Revision History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | Jan 2026 | Initial plan created | AI Assistant |

---

## Contact & Feedback

**Questions?**
- Come back to this chat anytime
- I can clarify any section
- I can help with specific implementation details
- I can review your architecture decisions

**Ready to Start?**
Let me know when you want to begin Week 1 Day 1, and I'll guide you through using Cursor to generate your FastAPI backend structure!

---

**END OF DOCUMENT**

Total Pages: 52
Total Words: ~15,000
Reading Time: 60 minutes
Implementation Time: 6-8 weeks with Cursor





