"""Repository health score extension for DataPulse."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from config.settings import get_settings
from database.database import get_db_session, initialize_database
from database.models import Repository, RepositoryHealth
from utils.logger import get_logger


logger = get_logger(__name__)

ACTIVITY_WINDOW_DAYS = 365
MIN_HEALTH_SCORE = 0.0
MAX_HEALTH_SCORE = 100.0


class RepositoryHealthError(Exception):
    """Raised when repository health cannot be calculated or stored."""


@dataclass(frozen=True)
class HealthScoreContext:
    """Maximum values used to normalize repository health metrics."""

    max_stars: int
    max_forks: int
    max_watchers: int


def _as_utc(value: datetime) -> datetime:
    """Normalize naive or aware datetimes to UTC."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc)


def _validate_non_negative_number(value: int | float | None, field_name: str) -> float:
    """Validate a required health score input."""
    if value is None:
        raise ValueError(f"{field_name} is required.")
    if not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be numeric.")
    if value < 0:
        raise ValueError(f"{field_name} must be non-negative.")

    return float(value)


def _clamp_score(value: float) -> float:
    """Clamp a score into the 0-100 range."""
    return max(MIN_HEALTH_SCORE, min(value, MAX_HEALTH_SCORE))


def normalize_metric(
    value: int | float | None,
    max_value: int | float,
    field_name: str = "value",
) -> float:
    """
    Normalize a metric to a 0-100 score.

    Args:
        value: Repository metric value.
        max_value: Maximum value for the same metric across the dataset.
        field_name: Metric name used in validation errors.

    Returns:
        float: Normalized value between 0 and 100.
    """
    metric_value = _validate_non_negative_number(value, field_name)
    maximum = _validate_non_negative_number(max_value, f"max_{field_name}")

    if maximum == 0:
        return MIN_HEALTH_SCORE

    return round(_clamp_score((metric_value / maximum) * MAX_HEALTH_SCORE), 2)


def calculate_repository_activity(
    updated_at: datetime | None,
    as_of: datetime | None = None,
) -> float:
    """
    Calculate repository activity from update recency.

    A repository updated today receives 100. A repository not updated for one
    year or more receives 0.
    """
    if updated_at is None:
        raise ValueError("updated_at is required.")

    comparison_time = _as_utc(as_of or datetime.now(timezone.utc))
    updated_time = _as_utc(updated_at)
    days_since_update = max((comparison_time - updated_time).days, 0)
    stale_ratio = min(days_since_update, ACTIVITY_WINDOW_DAYS) / ACTIVITY_WINDOW_DAYS

    return round(_clamp_score(MAX_HEALTH_SCORE - (stale_ratio * 100)), 2)


def calculate_repository_health_score(
    stars: int | None,
    forks: int | None,
    watchers: int | None,
    activity: int | float | None,
    context: HealthScoreContext,
) -> float:
    """
    Calculate the weighted repository health score.

    Formula:
        40% stars + 30% forks + 20% watchers + 10% repository activity
    """
    normalized_stars = normalize_metric(stars, context.max_stars, "stars")
    normalized_forks = normalize_metric(forks, context.max_forks, "forks")
    normalized_watchers = normalize_metric(
        watchers,
        context.max_watchers,
        "watchers",
    )
    activity_score = _validate_non_negative_number(activity, "activity")
    activity_score = _clamp_score(activity_score)

    health_score = (
        normalized_stars * 0.40
        + normalized_forks * 0.30
        + normalized_watchers * 0.20
        + activity_score * 0.10
    )

    return round(_clamp_score(health_score), 2)


def assign_health_category(health_score: int | float | None) -> str:
    """Assign a business-friendly health category."""
    score = _validate_non_negative_number(health_score, "health_score")
    score = _clamp_score(score)

    if score >= 90:
        return "Excellent"
    if score >= 75:
        return "Very Good"
    if score >= 60:
        return "Good"
    if score >= 40:
        return "Average"
    return "Needs Attention"


def build_health_score_context(repositories: list[Repository]) -> HealthScoreContext:
    """Build normalization context from all stored repositories."""
    return HealthScoreContext(
        max_stars=max((repository.stars for repository in repositories), default=0),
        max_forks=max((repository.forks for repository in repositories), default=0),
        max_watchers=max(
            (repository.watchers for repository in repositories),
            default=0,
        ),
    )


def build_repository_health_values(
    repository: Repository,
    context: HealthScoreContext,
    as_of: datetime | None = None,
) -> dict[str, Any]:
    """
    Build repository health values for persistence.

    Args:
        repository: Stored repository ORM object.
        context: Normalization context for repository metrics.
        as_of: Optional timestamp for deterministic tests.

    Returns:
        dict[str, Any]: Values ready for the repository_health table.
    """
    calculated_at = _as_utc(as_of or datetime.now(timezone.utc))
    activity = calculate_repository_activity(repository.updated_at, calculated_at)
    health_score = calculate_repository_health_score(
        stars=repository.stars,
        forks=repository.forks,
        watchers=repository.watchers,
        activity=activity,
        context=context,
    )

    return {
        "repository_id": repository.id,
        "health_score": health_score,
        "health_category": assign_health_category(health_score),
        "created_at": calculated_at,
    }


def refresh_repository_health(
    session: Session,
    as_of: datetime | None = None,
) -> int:
    """
    Refresh repository health scores for every stored repository.

    Args:
        session: Active SQLAlchemy database session.
        as_of: Optional timestamp for deterministic tests.

    Returns:
        int: Number of health rows inserted or updated.

    Raises:
        RepositoryHealthError: If health data cannot be persisted.
    """
    logger.info("Calculating Repository Health...")
    repositories = session.query(Repository).all()
    context = build_health_score_context(repositories)

    try:
        for repository in repositories:
            health_values = build_repository_health_values(
                repository=repository,
                context=context,
                as_of=as_of,
            )
            health = (
                session.query(RepositoryHealth)
                .filter(RepositoryHealth.repository_id == repository.id)
                .one_or_none()
            )

            if health is None:
                session.add(RepositoryHealth(**health_values))
            else:
                for field_name, value in health_values.items():
                    setattr(health, field_name, value)

        logger.info("Repository Health Score Generated")
        session.commit()
        logger.info("Health Data Stored")
        return len(repositories)

    except (SQLAlchemyError, ValueError) as exc:
        session.rollback()
        logger.error("Repository health refresh failed: %s", exc)
        raise RepositoryHealthError("Unable to refresh repository health.") from exc


def _parse_repository_lookup(repository_name: str) -> tuple[str | None, str]:
    """Parse repository lookups as either repo_name or owner/repo_name."""
    cleaned_name = repository_name.strip()
    if not cleaned_name:
        raise ValueError("repository_name is required.")

    if "/" not in cleaned_name:
        return None, cleaned_name

    owner, repo_name = cleaned_name.split("/", maxsplit=1)
    if not owner.strip() or not repo_name.strip():
        raise ValueError("repository_name must be repo_name or owner/repo_name.")

    return owner.strip(), repo_name.strip()


def _get_repository_health_from_session(
    session: Session,
    repository_name: str,
) -> dict[str, Any]:
    """Read repository health details from an active database session."""
    owner, repo_name = _parse_repository_lookup(repository_name)
    query = (
        session.query(Repository, RepositoryHealth)
        .join(RepositoryHealth, RepositoryHealth.repository_id == Repository.id)
        .filter(func.lower(Repository.repo_name) == repo_name.lower())
    )

    if owner is not None:
        query = query.filter(func.lower(Repository.owner) == owner.lower())

    repository, health = query.order_by(Repository.stars.desc()).first() or (None, None)

    if repository is None or health is None:
        raise RepositoryHealthError(
            f"Repository health was not found for {repository_name}."
        )

    return {
        "repository_name": repository.repo_name,
        "stars": repository.stars,
        "forks": repository.forks,
        "watchers": repository.watchers,
        "activity": calculate_repository_activity(repository.updated_at),
        "health_score": health.health_score,
        "category": health.health_category,
    }


def get_repository_health(
    repository_name: str,
    session: Session | None = None,
) -> dict[str, Any]:
    """
    Return repository health details by repository name.

    Args:
        repository_name: Repository name or owner/repository name.
        session: Optional active SQLAlchemy session.

    Returns:
        dict[str, Any]: Repository name, stars, forks, watchers, activity,
        health score, and category.
    """
    if session is not None:
        return _get_repository_health_from_session(session, repository_name)

    settings = get_settings()
    session_factory = initialize_database(settings.database_url)

    with get_db_session(session_factory) as db_session:
        return _get_repository_health_from_session(db_session, repository_name)
