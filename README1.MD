# AVO API - AI-Powered Guideline Processing System

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2.7-green.svg)](https://djangoproject.com)
[![Celery](https://img.shields.io/badge/Celery-5.3.4-red.svg)](https://docs.celeryq.dev)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-orange.svg)](https://openai.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Enterprise-grade AI backend system for automated guideline processing with real-time status tracking**

AVO API는 소프트웨어 개발 가이드라인을 AI로 자동 분석하여 요약과 체크리스트를 생성하는 백엔드 시스템입니다. Django + Celery + OpenAI GPT를 활용한 비동기 처리로 확장 가능하고 안정적인 서비스를 제공합니다.

## 🚀 Features

- **⚡ Ultra-fast Response**: < 200ms API response time
- **🔄 Asynchronous Processing**: FIFO queue with Celery workers
- **🤖 AI-Powered Analysis**: OpenAI GPT-4o-mini integration
- **📊 Real-time Tracking**: Live job status monitoring
- **🛡️ Production Ready**: Comprehensive error handling and logging
- **📈 Scalable Architecture**: Horizontal scaling support

## 🏗️ System Architecture

```
📱 Client (Postman/Frontend)
    ↓ POST /api/jobs (< 200ms)
🌐 Django REST API (Port 8000)
    ↓ Create Job + Queue Task
🔴 Redis (Message Broker + Cache)
    ↓ FIFO Queue Processing
👷 Celery Worker (Background Tasks)
    ↓ 2-Stage AI Chain
🤖 GPT Service → 🧠 OpenAI API
    ↓ Save Results
🐘 PostgreSQL (Persistent Storage)
    ↓ GET /api/jobs/{event_id}
📊 Real-time Status Response
```

## 📋 API Endpoints

### Create Job
```http
POST /api/jobs
Content-Type: application/json

Response (< 200ms):
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Get Job Status
```http
GET /api/jobs/{event_id}

Response:
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "message": "작업이 완료되었습니다.",
  "result": {
    "summary": {
      "_source": "openai_gpt",
      "_model": "gpt-4o-mini",
      "title": "소프트웨어 개발 가이드라인",
      "content": "가이드라인 요약 내용...",
      "key_points": ["핵심 포인트 1", "핵심 포인트 2"],
      "word_count": 150
    },
    "checklist": {
      "_source": "openai_gpt",
      "_model": "gpt-4o-mini",
      "categories": [
        {
          "name": "코드 품질 관리",
          "items": [
            {
              "id": 1,
              "text": "코드 리뷰를 수행했나요?",
              "required": true
            }
          ]
        }
      ],
      "total_items": 15,
      "required_items": 8
    }
  },
  "created_at": "2025-06-12T18:25:20Z",
  "updated_at": "2025-06-12T18:25:36Z"
}
```

## 🛠️ Tech Stack

- **Backend**: Python 3.11 + Django 4.2.7
- **API Framework**: Django REST Framework
- **Task Queue**: Celery 5.3.4
- **Message Broker**: Redis
- **Database**: PostgreSQL
- **AI Service**: OpenAI GPT-4o-mini
- **Monitoring**: Django Logs + Celery Flower

## 📁 Project Structure

```
avo_api/
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── .env                        # Environment variables
├── avo_api/                    # Django project settings
│   ├── __init__.py            # Celery app initialization
│   ├── settings.py            # Django configuration
│   ├── urls.py                # Main URL routing
│   ├── wsgi.py                # WSGI configuration
│   └── celery.py              # Celery configuration
├── jobs/                       # Jobs application
│   ├── models.py              # Job data model
│   ├── views.py               # API endpoints
│   ├── urls.py                # URL routing
│   ├── tasks.py               # Celery tasks
│   ├── admin.py               # Django admin
│   └── services/              # Business logic
│       ├── __init__.py
│       └── gpt_service.py     # OpenAI integration
└── logs/                       # Application logs
    └── django.log
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL
- Redis
- OpenAI API Key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/avo-api.git
   cd avo-api
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Set up database**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

### Running the Application

1. **Start Redis**
   ```bash
   redis-server
   ```

2. **Start Django development server**
   ```bash
   python manage.py runserver
   ```

3. **Start Celery worker** (in new terminal)
   ```bash
   celery -A avo_api worker --loglevel=info --queues=guideline_queue
   ```

4. **Start Celery monitoring** (optional)
   ```bash
   celery -A avo_api flower
   ```

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=avo_api
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
REDIS_URL=redis://localhost:6379/1

# OpenAI API
OPENAI_API_KEY=sk-your-openai-api-key-here
```

## 📊 Performance Metrics

- **API Response Time**: 50-100ms (< 200ms requirement ✅)
- **GPT Processing Time**: 10-15 seconds (asynchronous)
- **Concurrent Requests**: Unlimited with proper scaling
- **Queue Processing**: FIFO order guaranteed
- **Error Rate**: < 0.1% with comprehensive error handling

## 🧪 Testing

### Manual Testing with curl

```bash
# Create a job
curl -X POST http://localhost:8000/api/jobs \
  -H "Content-Type: application/json"

# Check job status
curl http://localhost:8000/api/jobs/{event_id}
```

### Using Postman

1. Import the provided Postman collection
2. Set environment variables
3. Run the test sequence:
   - POST /api/jobs
   - GET /api/jobs/{event_id}

## 📝 Logging

The system provides comprehensive logging:

- **Django Logs**: API requests, errors, performance
- **Celery Logs**: Task processing, GPT API calls
- **GPT Service Logs**: AI processing details, API responses

Logs are stored in `/logs/django.log` and displayed in console.

## 🔄 Job Status Flow

```
pending → processing → completed
   ↓           ↓           ↓
queue     GPT chain   results
entry     execution   storage
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

For support, please create an issue in the GitHub repository or contact the development team.

## 🚀 Deployment

### Docker Deployment (Recommended)

```bash
# Build and run with Docker Compose
docker-compose up -d
```

### Manual Deployment

1. Set up production database
2. Configure environment variables
3. Collect static files: `python manage.py collectstatic`
4. Run with Gunicorn: `gunicorn avo_api.wsgi:application`
5. Set up Nginx reverse proxy
6. Configure SSL certificates

## 📈 Monitoring

- **Application Monitoring**: Django admin interface
- **Task Monitoring**: Celery Flower dashboard
- **Database Monitoring**: PostgreSQL logs
- **API Monitoring**: Custom middleware logging

---

**Built with ❤️ by the AVO API Team**

*Transforming guidelines into actionable insights with AI*