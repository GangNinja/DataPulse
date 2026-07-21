# Week 4: Data Quality, Dashboard, and Docker

Week 4 extends DataPulse from an analytics-ready pipeline into a local
containerized analytics application.

## Session 1: Data Quality Improvement

Added a `quality/` module for:

- Missing value handling
- NULL value handling
- Duplicate repository detection
- Duplicate repository ID detection
- URL validation
- Negative metric validation
- Timestamp validation
- Data cleaning
- Data quality report generation

Reports are saved in:

```text
reports/data_quality_report_latest.txt
```

## Session 2: Streamlit Dashboard

Added an interactive dashboard in:

```text
dashboard/streamlit_app.py
```

Dashboard pages:

- Home
- Repository Analytics
- Repository Health
- Data Quality Report

The dashboard uses Plotly charts and reads from PostgreSQL.

## Session 3: Docker Support

Added:

- `Dockerfile`
- `docker-compose.yml`
- `.dockerignore`

Docker services:

- `postgres`: PostgreSQL warehouse container
- `dashboard`: Streamlit dashboard container
- `pipeline`: Optional ingestion pipeline container

## Docker Ports

```text
PostgreSQL host port: 5433
PostgreSQL container port: 5432
Streamlit dashboard host port: 8502
Streamlit dashboard container port: 8501
```

The Docker PostgreSQL service uses host port `5433` to avoid conflicting with a
local PostgreSQL installation on `5432`.

## Docker Commands

Start Docker Desktop before running Docker commands.

Start PostgreSQL and the Streamlit dashboard:

```powershell
docker compose up --build
```

Open the dashboard:

```text
http://localhost:8502
```

Run the ingestion pipeline inside Docker:

```powershell
docker compose run --rm pipeline
```

Stop containers:

```powershell
docker compose down
```

Stop containers and remove Docker database volume:

```powershell
docker compose down -v
```

## Environment Variables

Docker Compose reads GitHub settings from the local `.env` file:

```env
GITHUB_TOKEN=your_github_token_here
GITHUB_OWNER=microsoft
GITHUB_REPO=
REQUEST_TIMEOUT_SECONDS=30
POSTGRES_DB=datapulse
POSTGRES_USER=datapulse_user
POSTGRES_PASSWORD=change_me_for_local_docker
```

The Docker services override `DATABASE_URL` internally so containers connect to
the PostgreSQL service using the Docker service name:

```text
postgresql+psycopg2://<POSTGRES_USER>:<POSTGRES_PASSWORD>@postgres:5432/<POSTGRES_DB>
```

## Deployment Notes

This Docker setup is intended for local development and portfolio
demonstration. Production deployment would need:

- Secret management
- Managed database configuration
- Secure network settings
- Persistent storage planning
- Observability and monitoring
- CI/CD automation
