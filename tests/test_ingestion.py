"""Tests for GitHub repository response transformation."""

from datetime import datetime, timezone

import pytest

from ingestion.fetch_repositories import transform_repositories, transform_repository


def _github_repository_payload(name: str = "DataPulse") -> dict[str, object]:
    """Create a minimal valid GitHub repository response."""
    return {
        "name": name,
        "owner": {"login": "OpenAI"},
        "description": "Repository intelligence platform.",
        "stargazers_count": 100,
        "forks_count": 25,
        "watchers_count": 10,
        "open_issues_count": 3,
        "size": 2048,
        "language": "Python",
        "default_branch": "main",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-15T00:00:00Z",
        "html_url": "https://github.com/openai/datapulse",
    }


def test_transform_repository_maps_github_fields() -> None:
    """Raw GitHub fields should become database-ready repository fields."""
    transformed = transform_repository(_github_repository_payload())

    assert transformed["owner"] == "OpenAI"
    assert transformed["repo_name"] == "DataPulse"
    assert transformed["stars"] == 100
    assert transformed["forks"] == 25
    assert transformed["watchers"] == 10
    assert transformed["size_kb"] == 2048
    assert transformed["created_at"] == datetime(2024, 1, 1, tzinfo=timezone.utc)
    assert transformed["last_synced"].tzinfo is not None


def test_transform_repository_rejects_negative_metrics() -> None:
    """Negative GitHub count fields should fail validation."""
    payload = _github_repository_payload()
    payload["stargazers_count"] = -1

    with pytest.raises(ValueError, match="stargazers_count"):
        transform_repository(payload)


def test_transform_repositories_skips_duplicate_payloads() -> None:
    """Duplicate repository payloads should be removed before persistence."""
    payload_one = _github_repository_payload(name="DataPulse")
    payload_two = _github_repository_payload(name="datapulse")

    transformed = transform_repositories([payload_one, payload_two])

    assert len(transformed) == 1
    assert transformed[0]["repo_name"] == "DataPulse"
