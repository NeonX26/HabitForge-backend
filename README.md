# DailyMomentum Backend

FastAPI + PostgreSQL API for DailyMomentum.

## Setup

```bash
cd backend
docker compose up -d
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic revision --autogenerate -m "initial"
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

Health: [http://localhost:8000/health](http://localhost:8000/health)

All routes under `/api/v1`.

postgresql://neondb_owner:[npg_Ukblyxm4gJ1n@ep-icy-thunder-apzxpywj.c-7.us-east-1.aws.neon.tech](mailto:npg_Ukblyxm4gJ1n@ep-icy-thunder-apzxpywj.c-7.us-east-1.aws.neon.tech)/neondb?sslmode=require



postgresql+psycopg://neondb_owner:[npg_Ukblyxm4gJ1n@ep-icy-thunder-apzxpywj.c-7.us-east-1.aws.neon.tech](mailto:npg_Ukblyxm4gJ1n@ep-icy-thunder-apzxpywj.c-7.us-east-1.aws.neon.tech)/neondb?sslmode=require