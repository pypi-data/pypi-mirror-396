<p align="center">
  <img src="docs/logo.png" alt="FastAPI Template Logo" width="400">
</p>

<h1 align="center">FastAPI Template</h1>

<p align="center">
  <strong>A powerful CLI tool for generating production-ready FastAPI projects with best practices, integrated authentication, and flexible ORM options.</strong>
</p>

## Features

- 🚀 **Production Ready**: Pre-configured with security, logging, and deployment best practices
- 🔐 **Integrated Authentication**: FastAPI-Users integration with JWT authentication
- 🗄️ **Flexible ORM**: Choose between SQLAlchemy (PostgreSQL) or Beanie (MongoDB)
- 🐳 **Docker Support**: Complete Docker setup with docker-compose
- 📦 **Celery Integration**: Background task processing
- 🧪 **Testing Ready**: Pre-configured testing setup
- 📊 **API Documentation**: Auto-generated OpenAPI/Swagger documentation
- 🎯 **CLI Driven**: Simple command-line interface for project generation

## Quick Start

### Installation

```bash
pip install fastapi-template-cli
```

### Create a New Project

```bash
# Create an API-only project with SQLAlchemy
fastapi-template-cli new my-api --orm sqlalchemy --type api

# Create a modular project with MongoDB
fastapi-template-cli new my-app --orm beanie --type modular

# Create with project description
fastapi-template-cli new my-project --orm sqlalchemy --type modular \
  --description "My awesome FastAPI project" --author "Your Name"
```

## Project Types

### API-Only Projects
- Lightweight FastAPI backend
- Database integration (SQLAlchemy or Beanie)
- FastAPI-Users authentication
- No frontend or background tasks

### Modular Projects
- Complete backend with FastAPI
- Database integration
- FastAPI-Users authentication
- Celery for background tasks
- Redis for caching and task queue
- Docker setup with docker-compose

## ORM Options

### SQLAlchemy (PostgreSQL)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy 2.0 with async support
- **Migrations**: Alembic
- **Connection**: asyncpg driver

### Beanie (MongoDB)
- **Database**: MongoDB
- **ODM**: Beanie (async MongoDB ODM)
- **Driver**: Motor
- **Schema**: Pydantic-based documents

## Usage

### Basic Commands

```bash
# List available templates
fastapi-template-cli list-templates

# Create a new project
fastapi-template-cli new myproject

# Show version
fastapi-template-cli version
```

### Project Structure

Generated projects follow a clean architecture:

```
myproject/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── api.py
│   │       └── endpoints/
│   │           └── users.py
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── db/
│   │   ├── session.py (SQLAlchemy) or mongo.py (Beanie)
│   │   └── base_class.py (SQLAlchemy)
│   ├── models/
│   │   └── user.py
│   ├── schemas/
│   │   └── user.py
│   ├── users.py (FastAPI-Users config)
│   └── main.py
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml (modular only)
├── alembic/ (SQLAlchemy only)
├── workers/ (modular only)
├── pyproject.toml
├── .env
└── .gitignore
```

## Template Comparison

### Modular Template
- **Includes Redis** as Celery broker and result backend
- **Separate Celery worker** for long-running tasks
- **Celery Beat** for scheduled tasks
- **Complete frontend integration**
- **Production-ready Docker setup**

### API Template
- **Lightweight FastAPI core**
- **Database-only backend**
- **Minimal dependencies**
- **Optimized for microservices**
- **Simplified Docker setup**

## Project Structure Details

### API Template
```
e-commerce/
├── app/
│   ├── api/v1/
│   │   ├── api.py              # Main API router
│   │   └── endpoints/
│   │       └── users.py        # User endpoints
│   ├── core/
│   │   ├── config.py           # Application configuration
│   │   ├── security.py         # Security utilities
│   │   └── users.py           # User management
│   ├── database/
│   │   ├── base.py            # Database base setup
│   │   ├── base_class.py      # Base model class
│   │   └── session.py         # Database session
│   ├── models/
│   │   └── users.py           # User models
│   ├── schemas/
│   │   └── user.py            # Pydantic schemas
│   ├── users/
│   │   ├── dependencies.py    # User dependencies
│   │   └── manager.py         # User manager
│   └── main.py                # FastAPI application
├── alembic/                   # Database migrations
├── docker/                    # Docker configuration
├── tests/                     # Test files
├── .env.dev                   # Development environment
├── .env.prod                  # Production environment
└── pyproject.toml            # Project dependencies
```

### Modular Template
```
full-erp/
├── app/
│   ├── core/
│   │   ├── config.py           # Application configuration
│   │   ├── security.py         # Security utilities
│   │   └── users.py           # User management
│   ├── database/
│   │   ├── base.py            # Database base setup
│   │   ├── base_class.py      # Base model class
│   │   └── session.py         # Database session
│   ├── models/
│   │   └── users.py           # User models
│   ├── routers/
│   │   └── test.py            # Test endpoints
│   ├── schemas/
│   │   └── user.py            # Pydantic schemas
│   ├── services/              # Business logic services
│   ├── users/
│   │   ├── dependencies.py    # User dependencies
│   │   └── manager.py         # User manager
│   ├── utils/                 # Utility functions
│   ├── workers/
│   │   ├── celery_app.py      # Celery configuration
│   │   └── tasks.py           # Background tasks
│   └── main.py                # FastAPI application
├── alembic/                   # Database migrations
├── docker/                    # Docker configuration
├── tests/                     # Test files
├── .env.dev                   # Development environment
├── .env.prod                  # Production environment
├── docker-compose.dev.yml     # Development Docker setup
├── docker-compose.prod.yml    # Production Docker setup
└── pyproject.toml            # Project dependencies
```

## Development

### SQLAlchemy Projects

1. **Setup Database**
   ```bash
   cd myproject
   pip install -e .
   alembic upgrade head
   ```

2. **Run Development Server**
   ```bash
   uvicorn app.main:app --reload
   ```

3. **Create Database Migration**
   ```bash
   alembic revision --autogenerate -m "Add new table"
   ```

### Beanie Projects

1. **Setup MongoDB**
   ```bash
   cd myproject
   pip install -e .
   # MongoDB will auto-initialize on first connection
   ```

2. **Run Development Server**
   ```bash
   uvicorn app.main:app --reload
   ```

### Modular Projects (Docker)

1. **Start All Services**
   ```bash
   cd myproject
   docker-compose up -d
   ```

2. **Access Services**
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - MongoDB: localhost:27017 (Beanie)
   - PostgreSQL: localhost:5432 (SQLAlchemy)
   - Redis: localhost:6379

## Configuration

### Environment Variables

Create a `.env` file in your project root:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/dbname  # SQLAlchemy
MONGODB_URL=mongodb://localhost:27017/myproject  # Beanie

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis (modular)
REDIS_URL=redis://localhost:6379/0

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-password
```

### Database Configuration

#### SQLAlchemy (PostgreSQL)
```bash
# Install PostgreSQL
# Create database
createdb myproject

# Set DATABASE_URL
export DATABASE_URL=postgresql+asyncpg://user:password@localhost/myproject
```

#### Beanie (MongoDB)
```bash
# Install MongoDB
# MongoDB will create database on first connection
export MONGODB_URL=mongodb://localhost:27017/myproject
```

## Deployment

### Docker Deployment

For modular projects:

```bash
# Build and run
docker-compose -f docker-compose.dev.yaml up -d --build

# Stop services
docker-compose -f docker-compose.dev.yaml down
```

### Production Deployment

1. **Environment Variables**
   ```bash
   export SECRET_KEY=your-production-secret
   export DATABASE_URL=your-production-db-url
   ```

2. **Gunicorn/Uvicorn**
   ```bash
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

3. **Traefik Reverse Proxy**
   Includes Traefik configuration in `docker-compose.prod.yml`:
   ```yaml
   services:
     traefik:
       image: traefik:v3.0
       command:
         - --api.dashboard=true
         - --providers.docker=true
         - --entrypoints.web.address=:80
         - --entrypoints.websecure.address=:443
         - --certificatesresolvers.letsencrypt.acme.tlschallenge=true
         - --certificatesresolvers.letsencrypt.acme.email=your-email@domain.com
         - --certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json
   ```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests for new functionality
5. Run tests: `pytest`
6. Commit your changes: `git commit -am 'Add feature'`
7. Push to the branch: `git push origin feature-name`
8. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📖 [Documentation](https://github.com/your-org/fastapi-template/wiki)
- 🐛 [Issue Tracker](https://github.com/your-org/fastapi-template/issues)
- 💬 [Discussions](https://github.com/your-org/fastapi-template/discussions)
