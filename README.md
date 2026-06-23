# Inventory & Order Management System

Production-ready inventory and order management app with a FastAPI backend, React frontend, PostgreSQL database, SQLAlchemy ORM, Alembic migrations, Docker images, Docker Compose, and Vercel deployment configuration.

## Live URLs

- Frontend: `https://inventory-management-system-ten-orcin-48.vercel.app`
- Backend API: `https://inventory-management-api-ten.vercel.app`
- Backend health check: `https://inventory-management-api-ten.vercel.app/api/v1/health`
- API base URL: `https://inventory-management-api-ten.vercel.app/api/v1`

## Tech Stack

- Backend: FastAPI, SQLAlchemy, Pydantic, Alembic
- Frontend: React, Vite, TypeScript
- Database: PostgreSQL
- Containers: Docker, Docker Compose
- Deployment: Vercel for frontend and backend, Neon PostgreSQL for hosted database

## Project Structure

```text
backend/
  alembic/
  api/
  app/
    api/
    core/
    database/
    models/
    schemas/
    services/
  tests/
frontend/
  src/
    components/
    pages/
    services/
    styles/
docker-compose.yml
render.yaml
```

## Backend Features

- Product CRUD
- Customer CRUD
- Order CRUD
- Atomic inventory reduction during order creation
- Stock restoration on order cancellation/deletion
- Server-side order total calculation
- Dashboard summary API
- Meaningful HTTP errors for validation, not found, duplicate, and stock conflicts

## Frontend Features

- Dashboard page
- Products page
- Customers page
- Orders page
- Loading states
- Error states
- Form validation
- Reusable table, field, state, and status components
- Responsive operational layout

## Backend Environment

Create `backend/.env` from `backend/.env.example`.

```bash
APP_NAME=Inventory & Order Management API
APP_ENV=development
API_V1_PREFIX=/api/v1
DATABASE_URL=postgresql+psycopg://inventory_user:inventory_password@localhost:5432/inventory_db
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DASHBOARD_LOW_STOCK_THRESHOLD=5
BACKEND_CORS_ORIGINS=http://127.0.0.1:5173,http://127.0.0.1:4173,http://localhost:5173,http://localhost:4173
```

## Frontend Environment

Create `frontend/.env` from `frontend/.env.example`.

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

For deployed frontend, use:

```bash
VITE_API_BASE_URL=https://inventory-management-api-ten.vercel.app/api/v1
```

## Local Backend Setup

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/alembic upgrade head
.venv/bin/uvicorn app.main:app --reload
```

Backend runs at:

```text
http://127.0.0.1:8000
```

## Local Frontend Setup

```bash
cd frontend
npm install --cache .npm-cache
npm run dev
```

Frontend runs at:

```text
http://127.0.0.1:5173
```

## Tests

Run backend tests:

```bash
cd backend
.venv/bin/pytest -q
```

Run frontend production build:

```bash
cd frontend
npm run build
```

## Docker

Build backend image:

```bash
docker build -t inventory-backend:local ./backend
```

Build frontend image:

```bash
docker build -t inventory-frontend:local --build-arg VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1 ./frontend
```

## Docker Compose

Start the full local stack:

```bash
docker compose up --build
```

Default URLs:

- Frontend: `http://127.0.0.1:4173`
- Backend: `http://127.0.0.1:8000`
- PostgreSQL: `127.0.0.1:5432`

Stop services:

```bash
docker compose down
```

Remove the database volume:

```bash
docker compose down -v
```

## API Endpoints

Health:

```text
GET /api/v1/health
```

Dashboard:

```text
GET /api/v1/dashboard
```

Products:

```text
GET    /api/v1/products
POST   /api/v1/products
GET    /api/v1/products/{product_id}
PUT    /api/v1/products/{product_id}
DELETE /api/v1/products/{product_id}
```

Customers:

```text
GET    /api/v1/customers
POST   /api/v1/customers
GET    /api/v1/customers/{customer_id}
PUT    /api/v1/customers/{customer_id}
DELETE /api/v1/customers/{customer_id}
```

Orders:

```text
GET    /api/v1/orders
POST   /api/v1/orders
GET    /api/v1/orders/{order_id}
PUT    /api/v1/orders/{order_id}
DELETE /api/v1/orders/{order_id}
```

## Deployment

### Backend On Vercel

Deploy from `backend/`:

```bash
cd backend
vercel --prod
```

Required production environment variables:

```bash
APP_NAME=Inventory & Order Management API
APP_ENV=production
API_V1_PREFIX=/api/v1
DATABASE_URL=postgresql://neondb_owner:<password>@ep-shy-night-aophux4i-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DASHBOARD_LOW_STOCK_THRESHOLD=5
BACKEND_CORS_ORIGINS=https://inventory-management-system-ten-orcin-48.vercel.app
```

Run migrations against Neon:

```bash
cd backend
.venv/bin/alembic upgrade head
```

### Frontend On Vercel

Deploy from the repository root if the root Vercel project points at the frontend project, or from `frontend/` if linked separately:

```bash
vercel --prod
```

Required production environment variable:

```bash
VITE_API_BASE_URL=https://inventory-management-api-ten.vercel.app/api/v1
```

## Required Deliverables

- GitHub repository: use the GitHub repo URL for this project.
- Docker Hub backend image: push `inventory-backend:local` to Docker Hub and use the repository URL.
- Live frontend deployment: `https://inventory-management-system-ten-orcin-48.vercel.app`
- Live backend API: `https://inventory-management-api-ten.vercel.app`

## Validation Checklist

```bash
cd backend
.venv/bin/pytest -q
```

```bash
cd frontend
npm run build
```

```bash
docker compose config
docker compose up --build
```
