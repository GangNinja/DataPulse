"""Repository analytics transformations for DataPulse."""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database.models import Repository, RepositoryMetric
from utils.logger import get_logger


logger = get_logger(__name__)

SMALL_REPOSITORY_MAX_KB = 10_000
MEDIUM_REPOSITORY_MAX_KB = 100_000

PROGRAMMING_LANGUAGES = {
    "c",
    "c#",
    "c++",
    "dart",
    "go",
    "java",
    "javascript",
    "kotlin",
    "php",
    "python",
    "r",
    "ruby",
    "rust",
    "scala",
    "swift",
    "typescript",
}

MARKUP_LANGUAGES = {
    "css",
    "html",
    "markdown",
    "mdx",
    "scss",
}

SCRIPTING_LANGUAGES = {
    "dockerfile",
    "makefile",
    "powershell",
    "shell",
}

CONFIGURATION_LANGUAGES = {
    "hcl",
    "json",
    "nix",
    "terraform",
    "yaml",
}


class RepositoryMetricError(Exception):
    """Raised when repository metrics cannot be generated."""


def _as_utc(value: datetime) -> datetime:
    """Normalize naive or aware datetimes to UTC."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc)


def calculate_repository_age_days(
    created_at: datetime,
    as_of: datetime | None = None,
) -> int:
    """Calculate repository age in whole days."""
    comparison_time = _as_utc(as_of or datetime.now(timezone.utc))
    created_time = _as_utc(created_at)
    return max((comparison_time - created_time).days, 0)


def calculate_popularity_score(stars: int, forks: int, watchers: int) -> float:
    """
    Calculate weighted popularity score.

    Formula:
        (stars * 0.6) + (forks * 0.3) + (watchers * 0.1)
    """
    for metric_name, metric_value in {
        "stars": stars,
        "forks": forks,
        "watchers": watchers,
    }.items():
        if metric_value < 0:
            raise ValueError(f"{metric_name} must be non-negative.")

    return round((stars * 0.6) + (forks * 0.3) + (watchers * 0.1), 2)


def calculate_days_since_last_update(
    updated_at: datetime,
    as_of: datetime | None = None,
) -> int:
    """Calculate days since a repository was last updated."""
    comparison_time = _as_utc(as_of or datetime.now(timezone.utc))
    updated_time = _as_utc(updated_at)
    return max((comparison_time - updated_time).days, 0)


def categorize_repository_size(size_kb: int) -> str:
    """
    Classify a repository by GitHub repository size in KB.

    Returns:
        str: Small, Medium, or Large.
    """
    if size_kb < 0:
        raise ValueError("size_kb must be non-negative.")

    if size_kb < SMALL_REPOSITORY_MAX_KB:
        return "Small"
    if size_kb < MEDIUM_REPOSITORY_MAX_KB:
        return "Medium"
    return "Large"


def categorize_language(language: str | None) -> str:
    """Group GitHub primary languages into analysis-friendly categories."""
    if language is None or not language.strip():
        return "No Language"

    normalized_language = language.strip().lower()

    if normalized_language == "jupyter notebook":
        return "Notebook"
    if normalized_language in PROGRAMMING_LANGUAGES:
        return "Programming"
    if normalized_language in MARKUP_LANGUAGES:
        return "Markup"
    if normalized_language in SCRIPTING_LANGUAGES:
        return "Scripting"
    if normalized_language in CONFIGURATION_LANGUAGES:
        return "Configuration"

    return "Other"


def build_repository_metric_values(
    repository: Repository,
    as_of: datetime | None = None,
) -> dict[str, Any]:
    """
    Build analytics metric values for one repository ORM object.

    Args:
        repository: Stored repository record.
        as_of: Optional comparison timestamp for deterministic tests.

    Returns:
        dict[str, Any]: Values ready for the repository_metrics table.
    """
    calculated_at = _as_utc(as_of or datetime.now(timezone.utc))

    return {
        "repository_id": repository.id,
        "owner": repository.owner,
        "repo_name": repository.repo_name,
        "repository_age_days": calculate_repository_age_days(
            repository.created_at,
            calculated_at,
        ),
        "popularity_score": calculate_popularity_score(
            repository.stars,
            repository.forks,
            repository.watchers,
        ),
        "days_since_last_update": calculate_days_since_last_update(
            repository.updated_at,
            calculated_at,
        ),
        "size_category": categorize_repository_size(repository.size_kb),
        "language_category": categorize_language(repository.language),
        "calculated_at": calculated_at,
    }


def refresh_repository_metrics(
    session: Session,
    as_of: datetime | None = None,
) -> int:
    """
    Refresh analytics metrics for every stored repository.

    Args:
        session: Active SQLAlchemy database session.
        as_of: Optional comparison timestamp for deterministic tests.

    Returns:
        int: Number of repository metric rows inserted or updated.

    Raises:
        RepositoryMetricError: If analytics data cannot be persisted.
    """
    repositories = session.query(Repository).all()

    try:
        for repository in repositories:
            metric_values = build_repository_metric_values(repository, as_of=as_of)
            metric = (
                session.query(RepositoryMetric)
                .filter(RepositoryMetric.repository_id == repository.id)
                .one_or_none()
            )

            if metric is None:
                session.add(RepositoryMetric(**metric_values))
            else:
                for field_name, value in metric_values.items():
                    setattr(metric, field_name, value)

        session.commit()
        logger.info("Refreshed %s repository metric rows.", len(repositories))
        return len(repositories)

    except SQLAlchemyError as exc:
        session.rollback()
        logger.error("Repository metric refresh failed: %s", exc)
        raise RepositoryMetricError("Unable to refresh repository metrics.") from exc
