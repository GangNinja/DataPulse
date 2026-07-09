"""Tests for the Week 3 repository health extension."""

from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from database.models import Base, Repository, RepositoryHealth
from extensions.repository_health import (
    HealthScoreContext,
    assign_health_category,
    build_repository_health_values,
    calculate_repository_activity,
    calculate_repository_health_score,
    get_repository_health,
    refresh_repository_health,
)


def _session() -> Session:
    """Create an isolated in-memory database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    return session_factory()


def _repository(
    repo_name: str = "DataPulse",
    stars: int | None = 100,
    forks: int = 50,
    watchers: int = 25,
) -> Repository:
    """Create a repository ORM object for health tests."""
    timestamp = datetime(2024, 1, 1, tzinfo=timezone.utc)
    return Repository(
        owner="OpenAI",
        repo_name=repo_name,
        description="Repository intelligence platform.",
        stars=stars,
        forks=forks,
        watchers=watchers,
        open_issues=2,
        size_kb=4096,
        language="Python",
        default_branch="main",
        created_at=timestamp,
        updated_at=timestamp,
        html_url="https://github.com/openai/datapulse",
        last_synced=timestamp,
    )


def test_health_score_calculation_uses_weighted_formula() -> None:
    """Maximum normalized values should produce a perfect health score."""
    context = HealthScoreContext(max_stars=100, max_forks=50, max_watchers=25)

    score = calculate_repository_health_score(
        stars=100,
        forks=50,
        watchers=25,
        activity=100,
        context=context,
    )

    assert score == 100.0


def test_health_category_assignment_boundaries() -> None:
    """Health score category boundaries should match Week 3 rules."""
    assert assign_health_category(95) == "Excellent"
    assert assign_health_category(89) == "Very Good"
    assert assign_health_category(74) == "Good"
    assert assign_health_category(59) == "Average"
    assert assign_health_category(39) == "Needs Attention"


def test_refresh_repository_health_inserts_database_record() -> None:
    """Refreshing health scores should populate repository_health."""
    session = _session()
    as_of = datetime(2024, 1, 1, tzinfo=timezone.utc)
    session.add(_repository())
    session.commit()

    refreshed_count = refresh_repository_health(session, as_of=as_of)
    stored_health = session.query(RepositoryHealth).one()

    assert refreshed_count == 1
    assert stored_health.health_score == 100.0
    assert stored_health.health_category == "Excellent"
    session.close()


def test_get_repository_health_returns_expected_payload() -> None:
    """The lookup API should return repository details and health output."""
    session = _session()
    as_of = datetime(2024, 1, 1, tzinfo=timezone.utc)
    session.add(_repository())
    session.commit()
    refresh_repository_health(session, as_of=as_of)

    health = get_repository_health("OpenAI/DataPulse", session=session)

    assert health["repository_name"] == "DataPulse"
    assert health["stars"] == 100
    assert health["forks"] == 50
    assert health["watchers"] == 25
    assert health["health_score"] == 100.0
    assert health["category"] == "Excellent"
    session.close()


def test_invalid_repository_values_raise_value_error() -> None:
    """Negative values should be rejected before health scoring."""
    context = HealthScoreContext(max_stars=100, max_forks=50, max_watchers=25)

    with pytest.raises(ValueError, match="stars|value"):
        calculate_repository_health_score(
            stars=-1,
            forks=10,
            watchers=5,
            activity=100,
            context=context,
        )


def test_missing_repository_values_raise_value_error() -> None:
    """Missing values should not produce health scores."""
    repository = _repository(stars=None)
    context = HealthScoreContext(max_stars=100, max_forks=50, max_watchers=25)

    with pytest.raises(ValueError, match="value|required"):
        build_repository_health_values(repository, context)

    with pytest.raises(ValueError, match="updated_at"):
        calculate_repository_activity(None)
