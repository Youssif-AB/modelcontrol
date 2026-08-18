# ModelControl

ModelControl is a full-stack ML model governance platform for registering, versioning, reviewing, approving, monitoring, and auditing machine-learning models.

It combines a React/TypeScript interface with a FastAPI backend, PostgreSQL persistence, role-based governance workflows, automated testing, observability, Dockerized Linux deployment, GitHub Actions CI, and MLflow Tracking / Model Registry integration.

## Architecture

```text
                       ┌───────────────────┐
                       │   React + Nginx   │
                       │     Frontend      │
                       └─────────┬─────────┘
                                 │
                                 ▼
                       ┌───────────────────┐
                       │      FastAPI      │
                       │     Backend       │
                       └─────┬────────┬────┘
                             │        │
                  governance │        │ external integration
                             ▼        ▼
                    ┌────────────┐  ┌──────────────┐
                    │ PostgreSQL │  │    MLflow    │
                    │            │  │ Tracking +   │
                    │ models     │  │ Registry     │
                    │ versions   │  │ runs         │
                    │ findings   │  │ metrics      │
                    │ monitoring │  │ parameters   │
                    │ audit      │  │ artifacts    │
                    └────────────┘  └──────────────┘
```

## Core capabilities

- Model inventory with owners, risk tiers, business areas, and lifecycle status
- Model version management
- Draft → review → approval → retirement lifecycle state machine
- Review findings with severity and resolution workflows
- Model-performance monitoring with configurable warning and critical thresholds
- Append-only application audit history for governance actions
- JWT authentication
- Role-based access control for Admin, Model Owner, and Reviewer roles
- Login rate limiting
- MLflow Tracking / Model Registry integration
- Import of registered MLflow model versions, run metrics, parameters, and artifact references
- PostgreSQL constraints, indexes, relationships, and Alembic migrations
- Structured JSON logging and request IDs
- Prometheus request and latency metrics
- Liveness and database-readiness endpoints
- Docker Compose Linux environment
- GitHub Actions CI for backend tests, PostgreSQL migrations, frontend lint/build, and Docker smoke testing

## Technology

### Backend

Python, FastAPI, SQLAlchemy, PostgreSQL, Alembic, PyJWT, Argon2, SlowAPI, Prometheus Client, MLflow.

### Frontend

React, TypeScript, Vite, React Router, Nginx.

### Engineering

Docker, Docker Compose, Linux containers, pytest, GitHub Actions, structured logging, health checks, RBAC, database migrations.

## Run locally with Docker

Create a root `.env` file from `.env.example` and supply secure local values:

```text
POSTGRES_PASSWORD=<local-password>
JWT_SECRET_KEY=<long-random-secret>
```

Build and start the environment:

```bash
docker compose up -d --build
```

Check service status:

```bash
docker compose ps
```

The application exposes:

```text
Frontend:       http://localhost:5173
FastAPI docs:   http://localhost:8000/docs
Prometheus:     http://localhost:8000/metrics/
MLflow UI:      http://localhost:5000
```

## Create the first administrator

```bash
docker compose exec backend python create_admin.py
```

Log into ModelControl through the frontend using the account you create.

## Seed MLflow demo data

Create a real MLflow experiment run with parameters, metrics, an artifact, and a registered model version:

```bash
docker compose exec backend python -m scripts.seed_mlflow
```

Open the MLflow UI:

```text
http://localhost:5000
```

The seed creates a registered model named:

```text
DemoChurnModel
```

## Test the MLflow integration

Authenticate through Swagger at:

```text
http://localhost:8000/docs
```

List registered MLflow models:

```text
GET /integrations/mlflow/models
```

Create a ModelControl model, note its ID, then import the MLflow model version:

```text
POST /models/{model_id}/versions/import/mlflow
```

Example request:

```json
{
  "model_name": "DemoChurnModel",
  "version": "1"
}
```

ModelControl retrieves the registered version from MLflow, reads the associated run metrics and parameters, creates a governed ModelControl version, and records the import in the audit history.

## Governance roles

### Admin

Can perform all governance actions.

### Model Owner

Can register owned models, create versions, submit models for review, record monitoring results, resolve findings, and retire owned models.

### Reviewer

Can review models, approve or reject models under review, and create governance findings.

## Automated tests

Run the backend suite:

```bash
cd backend
pytest -v
```

Run frontend quality checks:

```bash
cd frontend
npm run lint
npm run build
```

GitHub Actions executes backend tests, validates the PostgreSQL migration chain, checks the frontend production build, builds the Docker environment, and smoke-tests the running services.

## Observability

Liveness:

```text
GET /health
```

Database readiness:

```text
GET /ready
```

Prometheus metrics:

```text
GET /metrics/
```

API responses include an `X-Request-ID`, and backend logs emit structured JSON containing the request ID, route, status code, and request latency.

## Security and reliability

ModelControl uses JWT authentication, Argon2 password hashing, RBAC enforcement, login rate limiting, explicit CORS configuration, trusted-host validation, security response headers, PostgreSQL constraints, environment-based secrets, database connection pre-ping, health checks, and container restart policies.

## Project status

The current implementation demonstrates the complete core governance workflow and local production-style infrastructure.

Cloud deployment is intentionally outside the current project scope.