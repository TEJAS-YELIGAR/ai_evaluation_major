# VTU AI Answer Evaluator

AI-powered answer booklet evaluation system for VTU.

## Quick Start

### Requirements
- Docker Desktop (docker.com/products/docker-desktop)
- 8GB RAM minimum

### Setup

1. Clone the repo
2. Create `backend/.env` file (see .env.example)
3. Run: `docker compose up --build`
4. Run migrations: `docker compose exec backend alembic upgrade head`
5. Open: http://localhost:5173

### Default Login
- Username: admin
- Password: admin123

### URLs
- Dashboard: http://localhost:5173
- API Docs: http://localhost:8000/docs
- Database UI: http://localhost:5050

### Stop
docker compose down

### Full reset (delete all data)
docker compose down -v
