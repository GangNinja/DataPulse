"""Tests for repository metric transformations."""

from datetime import datetime, timezone

from database.models import Repository
from transformations.repository_metrics import (
    build_repository_metric_values,
    calculate_popularity_score,
    categorize_language,
    categorize_repository_size,
)


def test_calculate_popularity_score_uses_weighted_formula() -> None:
    """Popularity score should use the Week 2 formula."""
    score = calculate_popularity_score(stars=100, forks=20, watchers=10)

    assert score == 67.0


def test_repository_metric_values_are_derived_from_repository() -> None:
    """Metric values should be built from a stored repository record."""
    as_of = datetime(2024, 1, 11, tzinfo=timezone.utc)
    repository = Repository(
        id=1,
        owner="OpenAI",
        repo_name="DataPulse",
        description=None,
        stars=100,
        forks=20,
        watchers=10,
        open_issues=5,
        size_kb=150_000,
        language="Python",
        default_branch="main",
        created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2024, 1, 8, tzinfo=timezone.utc),
        html_url="https://github.com/openai/datapulse",
        last_synced=as_of,
    )

    values = build_repository_metric_values(repository, as_of=as_of)

    assert values["repository_age_days"] == 10
    assert values["popularity_score"] == 67.0
    assert values["days_since_last_update"] == 3
    assert values["size_category"] == "Large"
    assert values["language_category"] == "Programming"


def test_size_and_language_categories() -> None:
    """Size and language categories should be analysis-friendly."""
    assert categorize_repository_size(1_000) == "Small"
    assert categorize_repository_size(50_000) == "Medium"
    assert categorize_repository_size(150_000) == "Large"
    assert categorize_language(None) == "No Language"
    assert categorize_language("HTML") == "Markup"
    assert categorize_language("Jupyter Notebook") == "Notebook"
