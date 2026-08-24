<img width="2962" height="1361" alt="image" src="https://github.com/user-attachments/assets/81183cb2-d2f3-4f42-bf65-791362870e38" />

# ModelControl

ModelControl is a full-stack governance application for registering, reviewing, approving, monitoring, versioning, and auditing machine-learning models. It provides one controlled inventory for model owners, independent reviewers, and administrators without attempting to replace experiment tracking or model serving systems.

The currently validated environment is local Docker Compose. Azure deployment is planned as a final-stage deployment step; this repository does not claim a completed cloud deployment.

## Architecture

```text
Browser
  |
  +-- React + TypeScript (Nginx)
          |
          +-- FastAPI governance API
                 |-- PostgreSQL: users, models, versions, findings,
                 |               monitoring, and audit history
                 +-- MLflow Tracking and Model Registry
```

The backend applies authentication, role checks, lifecycle transition rules, validation, audit creation, request IDs, and metrics. The frontend is a role-aware governance console with compact tables and explicit loading, empty, error, and pending states.

## Governance workflow

Models move through a backend-enforced state machine:

```text
Draft -> Under review -> Approved -> Retired
             |
             +-- Reject with reason -> Draft
```

- Owners submit their models for review and may retire approved models.
- Reviewers approve models or return them to draft with a required rejection reason.
- Administrators may perform all lifecycle actions.
- Optional approval and retirement notes, rejection reasons, the authenticated actor, and the resulting status are retained in the append-only audit history.

Invalid transitions and unauthorized actions are rejected by the API even if a client attempts to bypass the UI.

## Roles

| Capability | Admin | Model owner | Reviewer |
|---|:---:|:---:|:---:|
| View inventory and model evidence | Yes | Yes | Yes |
| Register models | Yes | Own models | No |
| Add/import versions | Yes | Own models | Read only |
| Submit or retire | Yes | Own models | No |
| Approve or reject | Yes | No | Yes |
| Create findings | Yes | No | Yes |
| Resolve findings | Yes | Own models | No |
| Record monitoring | Yes | Own models | Read only |

## MLflow and version comparison

Authenticated users can browse registered MLflow models, versions, run IDs, statuses, and artifact sources. Owners and administrators can import a selected MLflow version into a governed ModelControl model; reviewers retain read-only registry access.

An import creates the next ModelControl version and stores structured provenance:

- registered model and MLflow version
- run ID and artifact source
- available run metrics and parameters
- import audit event and actor

The comparison view compares any two ModelControl versions in a compact table. Manually created versions truthfully show unavailable provenance rather than synthetic metrics. Current risk, lifecycle, ownership, and latest monitoring state appear as comparison context.

## Findings, monitoring, and audit

Review findings track severity, open/resolved state, descriptions, and resolution notes. Monitoring records compare current performance with a baseline using metric direction and configurable warning/critical thresholds.

Audit history is immutable in the UI and supports text search, event-type filtering, newest/oldest ordering, readable labels, timestamps, and actor display. Historical rows created before actor recording show that the actor was not recorded.

## Run locally with Docker

Copy `.env.example` to `.env` and replace both example secrets:

```text
POSTGRES_PASSWORD=<local-database-password>
JWT_SECRET_KEY=<long-random-secret>
```

Then start the stack:

```bash
docker compose up -d --build
docker compose ps
```

Services are exposed at:

| Service | URL |
|---|---|
| ModelControl | http://localhost:5173 |
| FastAPI documentation | http://localhost:8000/docs |
| Prometheus metrics | http://localhost:8000/metrics/ |
| MLflow | http://localhost:5000 |

The backend container applies Alembic migrations before starting. Create the first administrator with:

```bash
docker compose exec backend python create_admin.py
```

## Demo workflow

1. Create an administrator and sign in.
2. Create owner and reviewer users through `POST /auth/users` in the API documentation.
3. Register a model as an owner.
4. Seed a real MLflow run and registered version:

   ```bash
   docker compose exec backend python -m scripts.seed_mlflow
   ```

5. Browse `DemoChurnModel` in the model detail page and import a version.
6. Compare the imported version with another manual or MLflow version.
7. Submit the model, sign in as a reviewer, record findings, and approve or reject it.
8. Search the audit history to verify actions, notes, and actors.

## Development checks

Backend:

```bash
cd backend
pytest -v
alembic heads
```

Frontend:

```bash
cd frontend
npm ci
npm run lint
npm run test
npm run build
```

Stack validation:

```bash
docker compose config
docker compose build
docker compose up -d
docker compose ps
```

The frontend tests use Vitest, React Testing Library, user-event, and jsdom. They cover lifecycle permissions and rejection, MLflow loading/import/failure behavior, audit filtering, and expired-session handling. Pytest covers authentication, lifecycle/RBAC, findings, monitoring, MLflow permissions and structured imports, audit creation, health, readiness, request IDs, and Prometheus output.

GitHub Actions installs dependencies, applies migrations to PostgreSQL, runs backend tests, runs frontend lint/tests/build, validates Compose, builds the images, starts the stack, and checks backend, frontend, and MLflow health.

## Security and operations

- JWT secrets and database credentials come from environment variables and are not stored in source.
- Passwords use Argon2 hashing; login requests are rate limited.
- CORS and trusted hosts are explicitly configurable.
- Nginx and FastAPI set defensive response headers.
- API errors avoid exposing internal exceptions.
- Session tokens use browser session storage and are cleared on a 401 response.
- Structured request logs include request ID, route, status, and latency.
- `/health`, `/ready`, and `/metrics/` remain available for container and operational checks.

For a later Azure deployment, use managed secrets, a managed PostgreSQL service, persistent artifact storage, HTTPS, a stable same-origin API route or explicit production CORS/CSP configuration, and the existing container health endpoints. No Azure resources are created by this project setup.
