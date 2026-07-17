"""Dashboard data access helpers for DataPulse."""

from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from quality.report import DEFAULT_REPORTS_DIRECTORY, LATEST_REPORT_NAME


def create_dashboard_engine(database_url: str) -> Engine:
    """
    Create a SQLAlchemy engine for dashboard queries.

    Args:
        database_url: Database connection string.

    Returns:
        Engine: SQLAlchemy engine configured for lightweight reads.
    """
    return create_engine(database_url, pool_pre_ping=True)


def _fetch_all(engine: Engine, query: str, **params: Any) -> list[dict[str, Any]]:
    """Run a query and return rows as dictionaries."""
    with engine.connect() as connection:
        result = connection.execute(text(query), params)
        return [dict(row._mapping) for row in result]


def _fetch_one(engine: Engine, query: str) -> dict[str, Any]:
    """Run a scalar-style query and return one row as a dictionary."""
    with engine.connect() as connection:
        row = connection.execute(text(query)).mappings().one()
        return dict(row)


def fetch_dashboard_kpis(engine: Engine) -> dict[str, Any]:
    """
    Fetch homepage KPI values.

    Args:
        engine: SQLAlchemy engine.

    Returns:
        dict[str, Any]: Dashboard-level metrics.
    """
    repository_kpis = _fetch_one(
        engine,
        """
        SELECT
            COUNT(*) AS total_repositories,
            COALESCE(ROUND(AVG(stars), 2), 0) AS average_stars,
            COALESCE(ROUND(AVG(forks), 2), 0) AS average_forks,
            COALESCE(ROUND(AVG(watchers), 2), 0) AS average_watchers
        FROM repositories
        """,
    )
    health_kpis = _fetch_one(
        engine,
        """
        SELECT
            COALESCE(
                ROUND(AVG(health_score)::numeric, 2),
                0
            ) AS average_health_score,
            COALESCE(MAX(health_score), 0) AS best_health_score,
            COALESCE(
                SUM(
                    CASE
                        WHEN health_category = 'Needs Attention' THEN 1
                        ELSE 0
                    END
                ),
                0
            ) AS needs_attention_count
        FROM repository_health
        """,
    )

    return {**repository_kpis, **health_kpis}


def fetch_language_distribution(
    engine: Engine,
    limit: int = 12,
) -> list[dict[str, Any]]:
    """Fetch repository counts by primary language."""
    return _fetch_all(
        engine,
        """
        SELECT
            COALESCE(language, 'Unknown') AS language,
            COUNT(*) AS repository_count
        FROM repositories
        GROUP BY COALESCE(language, 'Unknown')
        ORDER BY repository_count DESC, language
        LIMIT :limit
        """,
        limit=limit,
    )


def fetch_health_distribution(engine: Engine) -> list[dict[str, Any]]:
    """Fetch repository health category counts."""
    return _fetch_all(
        engine,
        """
        SELECT
            health_category,
            COUNT(*) AS repository_count
        FROM repository_health
        GROUP BY health_category
        """,
    )


def fetch_size_distribution(engine: Engine) -> list[dict[str, Any]]:
    """Fetch repository size category counts."""
    return _fetch_all(
        engine,
        """
        SELECT
            size_category,
            COUNT(*) AS repository_count
        FROM repository_metrics
        GROUP BY size_category
        ORDER BY repository_count DESC
        """,
    )


def fetch_top_repositories(engine: Engine, limit: int = 10) -> list[dict[str, Any]]:
    """Fetch top repositories by stars."""
    return _fetch_all(
        engine,
        """
        SELECT
            r.owner,
            r.repo_name,
            r.stars,
            r.forks,
            r.watchers,
            COALESCE(r.language, 'Unknown') AS language,
            rh.health_score,
            rh.health_category
        FROM repositories AS r
        LEFT JOIN repository_health AS rh ON rh.repository_id = r.id
        ORDER BY r.stars DESC, r.forks DESC
        LIMIT :limit
        """,
        limit=limit,
    )


def fetch_healthiest_repositories(
    engine: Engine,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Fetch top repositories by health score."""
    return _fetch_all(
        engine,
        """
        SELECT
            r.owner,
            r.repo_name,
            r.stars,
            r.forks,
            r.watchers,
            COALESCE(r.language, 'Unknown') AS language,
            rh.health_score,
            rh.health_category
        FROM repository_health AS rh
        JOIN repositories AS r ON r.id = rh.repository_id
        ORDER BY rh.health_score DESC, r.stars DESC
        LIMIT :limit
        """,
        limit=limit,
    )


def fetch_repositories_needing_attention(
    engine: Engine,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Fetch repositories in the Needs Attention health category."""
    return _fetch_all(
        engine,
        """
        SELECT
            r.owner,
            r.repo_name,
            r.stars,
            r.forks,
            r.watchers,
            r.updated_at,
            rh.health_score,
            rh.health_category
        FROM repository_health AS rh
        JOIN repositories AS r ON r.id = rh.repository_id
        WHERE rh.health_category = 'Needs Attention'
        ORDER BY rh.health_score ASC, r.updated_at ASC
        LIMIT :limit
        """,
        limit=limit,
    )


def read_latest_quality_report(
    reports_directory: Path = DEFAULT_REPORTS_DIRECTORY,
) -> str | None:
    """
    Read the latest data quality report if it exists.

    Args:
        reports_directory: Directory containing generated reports.

    Returns:
        str | None: Report text, or None when no report has been generated.
    """
    report_path = reports_directory / LATEST_REPORT_NAME
    if not report_path.exists():
        return None

    return report_path.read_text(encoding="utf-8")
