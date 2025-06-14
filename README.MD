# AVO API - AI-Powered Guideline Processing

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)

> Minimal backend API for automated guideline processing with AI-powered summarization and checklist generation.

## System Architecture

```mermaid
graph TD;
    A[Client] -->|POST /jobs| B[Django API];
    B -->|200ms response| A;
    B -->|Queue Task| C[Redis Queue];
    C -->|FIFO| D[Celery Worker];
    D -->|Step 1| E[GPT Summarize];
    E -->|Step 2| F[GPT Checklist];
    F -->|Save Results| G[PostgreSQL];
    A -->|GET /jobs/id| B;
    B -->|Query Status| G;
    G -->|Return Result| B;
    B -->|Status and Result| A;
    
    classDef client fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef api fill:#f3e5f5,stroke:#4a148c,stroke-width:2px;
    classDef queue fill:#fff3e0,stroke:#e65100,stroke-width:2px;
    classDef worker fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px;
    classDef gpt fill:#fce4ec,stroke:#880e4f,stroke-width:2px;
    classDef db fill:#e3f2fd,stroke:#0d47a1,stroke-width:2px;
    
    class A client;
    class B api;
    class C queue;
    class D worker;
    class E,F gpt;
    class G db;
```

![AVO API Architecture](./assets/avo_api_architecture.png)

## Quick Start
```bash
# Clone and start services
git clone https://github.com/yhskgo/avo-api.git
cd avo-api
cp .env.example .env
# Edit .env with your OPENAI_API_KEY
docker compose up --build

# Run tests (6 tests, comprehensive coverage)
docker compose --profile test run test

# API Documentation
http://localhost:8000/api/docs/
```

## API Endpoints
- `POST /api/jobs` → Returns `event_id` in <200ms
- `GET /api/jobs/{event_id}` → Job status and results
- `GET /api/schema/` → OpenAPI specification
- `GET /api/docs/` → Interactive API documentation

## Design Choices

**Tech Stack**: Django + Celery + Redis + PostgreSQL for:
- **Sub-200ms response**: Immediate job queuing with async processing
- **FIFO guarantee**: Redis queues ensure order preservation  
- **Scalability**: Horizontal worker scaling with Celery
- **Reliability**: PostgreSQL for persistent job state

**Two-Stage GPT Chain**:
1. **Summarize** guidelines using GPT-4o-mini/GPT-3.5-turbo
2. **Generate** actionable checklist from summary

**AI Tools Used**:
- **Claude**: Complete system architecture, code structure, testing framework, and Docker deployment setup
- **Mermaid**: Interactive system architecture diagram
- **OpenAPI**: Automatic API documentation with drf-spectacular  
- **GPT Integration**: Content processing pipeline with robust fallback handling

Built with extensive AI assistance for rapid, production-ready development.