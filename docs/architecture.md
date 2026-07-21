# DataPulse Architecture

DataPulse is organized as a modular data engineering project. Each layer owns a
clear responsibility so the project can grow without rewriting earlier work.

## High-Level Architecture

```mermaid
flowchart LR
    A["GitHub REST API"] --> B["Ingestion Layer"]
    B --> C["Data Quality Framework"]
    C --> D["PostgreSQL Warehouse"]
    D --> E["Transformation Layer"]
    E --> F["Repository Health Extension"]
    D --> G["Analytics SQL"]
    D --> H["Streamlit Dashboard"]
    F --> H
```

## ETL Flow

```mermaid
flowchart TD
    A["Load .env Settings"] --> B["Connect to GitHub API"]
    B --> C["Fetch Repository Pages"]
    C --> D["Transform API Response"]
    D --> E["Clean and Validate Records"]
    E --> F{"Valid Record?"}
    F -->|Yes| G["Insert New Repository"]
    F -->|Duplicate| H["Skip Duplicate"]
    F -->|Invalid| I["Reject Record"]
    G --> J["Refresh Repository Metrics"]
    H --> J
    I --> K["Write Quality Report"]
    J --> L["Calculate Health Score"]
    L --> K
```

## Docker Architecture

```mermaid
flowchart LR
    A["Host Machine"] --> B["Docker Compose"]
    B --> C["postgres container"]
    B --> D["dashboard container"]
    B --> E["pipeline container"]
    E --> C
    D --> C
    C --> F["postgres_data volume"]
    D --> G["localhost:8502"]
    E --> H["logs/ and reports/ mounts"]
```

## Data Model Summary

- `repositories`: raw GitHub repository metadata.
- `repository_metrics`: derived analytics metrics from Week 2.
- `repository_health`: health score and category from Week 3.

## Design Principles

- Keep ingestion, persistence, transformation, quality, and dashboard logic
  separate.
- Keep source data and derived analytics data in different tables.
- Use SQLAlchemy ORM for schema ownership and safer persistence.
- Use SQL files for analyst-friendly queries.
- Keep Docker services small and understandable for local portfolio demos.
