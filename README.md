# DataPulse - GitHub Repository Intelligence Platform

DataPulse is a Python data engineering project that ingests GitHub repository
metadata into PostgreSQL and prepares it for analytics. Week 1 established the
basic GitHub-to-database pipeline. Week 2 upgrades the project into an
analytics-ready warehouse with bulk repository ingestion, stronger database
models, transformation logic, reusable SQL, logging, documentation, and tests.

This version intentionally does not include Streamlit, Docker, GitHub Actions,
dbt, weather data, deployment, or authentication. Those belong to later weeks.

## Week 2 Progress

- Fetch all repositories for a GitHub organization or user.
- Handle GitHub API pagination.
- Skip duplicate repositories during batch ingestion.
- Add repository validation, indexes, constraints, and `last_synced` tracking.
- Store repository size in KB for downstream analytics.
- Create a `repository_metrics` analytics table.
- Generate repository age, popularity score, days since update, size category,
  and language category.
- Add reusable analytics SQL queries.
- Save structured logs to `logs/datapulse.log`.
- Add an architecture decision record in `docs/adr/ADR-001.md`.
- Add pytest coverage for ingestion, transformations, persistence, and duplicate
  detection.

## Architecture

```text
DataPulse/
    config/              Environment-driven runtime settings
    ingestion/           GitHub API client and response transformation
    database/            SQLAlchemy models, sessions, and persistence
    transformations/     Analytics-ready derived metrics
    sql/                 Analyst-friendly SQL examples
    docs/adr/            Architecture decision records
    tests/               Pytest test suite
    utils/               Shared logging utilities
    main.py              Pipeline entry point
```

The pipeline performs this flow:

1. Read configuration from `.env`.
2. Connect to the GitHub REST API.
3. Fetch either one repository or all repositories for an account.
4. Validate and transform GitHub responses.
5. Store repository data in PostgreSQL.
6. Skip duplicates during bulk ingestion.
7. Refresh analytics metrics in `repository_metrics`.
8. Write logs to console and `logs/datapulse.log`.

## Installation

Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Variables

Copy `.env.example` to `.env`:

```bash
copy .env.example .env
```

Fetch all repositories for an organization or user:

```env
GITHUB_TOKEN=your_real_github_token
GITHUB_OWNER=microsoft
GITHUB_REPO=
DATABASE_URL=postgresql+psycopg2://datapulse_user:datapulse_password@localhost:5432/datapulse
REQUEST_TIMEOUT_SECONDS=30
```

Fetch a single repository, keeping the Week 1 path available:

```env
GITHUB_OWNER=tensorflow
GITHUB_REPO=tensorflow
```

## Database Setup

Create a PostgreSQL database and user before running the project.

```sql
CREATE DATABASE datapulse;
CREATE USER datapulse_user WITH PASSWORD 'datapulse_password';
GRANT ALL PRIVILEGES ON DATABASE datapulse TO datapulse_user;
GRANT ALL ON SCHEMA public TO datapulse_user;
```

The application creates required tables automatically on startup. Additive
schema updates are applied safely for PostgreSQL so existing data is not dropped.

## Warehouse Tables

`repositories` stores raw GitHub repository metadata:

- Repository identity: `owner`, `repo_name`, `html_url`
- Repository activity: `stars`, `forks`, `watchers`, `open_issues`
- Repository metadata: `description`, `language`, `default_branch`, `size_kb`
- Timestamps: `created_at`, `updated_at`, `last_synced`

The pair `owner` and `repo_name` is unique. Batch ingestion also performs
case-insensitive duplicate detection before inserting records.

`repository_metrics` stores analytics-ready derived fields:

- `repository_age_days`
- `popularity_score`
- `days_since_last_update`
- `size_category`
- `language_category`
- `calculated_at`

## Transformation Layer

Transformation code lives in `transformations/repository_metrics.py`.

Popularity score uses this formula:

```text
(stars * 0.6) + (forks * 0.3) + (watchers * 0.1)
```

Repository size categories are based on GitHub repository size in KB:

- Small: under 10,000 KB
- Medium: 10,000 KB to under 100,000 KB
- Large: 100,000 KB and above

Language categories group repositories into practical analytics buckets such as
Programming, Markup, Scripting, Configuration, Notebook, No Language, and Other.

## Analytics Queries

Reusable SQL lives in `sql/analytics_queries.sql`. It includes queries for:

- Top repositories by stars, forks, and popularity score
- Most common language
- Average stars by language
- Repositories created this year
- Recently updated repositories
- Repository age distribution
- Largest organizations
- Most active repositories
- Repositories with no language
- Size category distribution
- Stale repositories
- Analytics rows that need refreshing

## How to Run

From the `DataPulse` directory:

```bash
python main.py
```

Example successful batch run:

```text
INFO Connecting to GitHub...
INFO Fetching repositories...
INFO Stored 50 repositories.
INFO Refreshed 50 repository metric rows.
Success: stored 50 repositories, skipped 0 duplicates, and refreshed 50 analytics rows.
```

## Testing

Run the test suite:

```bash
pytest
```

The tests cover the GitHub API client, transformation functions, database
insertion, and duplicate detection.

## Project Roadmap

Completed:

- Week 1: Basic GitHub repository ingestion into PostgreSQL.
- Week 2: Bulk ingestion, warehouse-ready schema, transformations, SQL, logging,
  ADR, documentation, and tests.

Planned future work:

- Add dashboarding after the warehouse layer is stable.
- Add scheduling or orchestration.
- Add dbt models.
- Add Docker for local development.
- Add CI/CD and deployment.
- Add authentication only when the application has a user-facing layer.
