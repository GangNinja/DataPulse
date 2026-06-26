"""Repository ingestion and transformation functions."""

from datetime import datetime, timezone
from typing import Any

from ingestion.github_client import GitHubClient


def parse_github_datetime(value: str) -> datetime:
    """
    Parse GitHub's ISO 8601 timestamp into a timezone-aware datetime.

    Args:
        value: Timestamp from the GitHub API.

    Returns:
        datetime: Parsed UTC datetime.
    """
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def validate_repository_response(repository_data: dict[str, Any]) -> None:
    """
    Validate the GitHub repository response contains required fields.

    Args:
        repository_data: Raw repository JSON from GitHub.

    Raises:
        ValueError: If a required field is missing.
    """
    required_fields = {
        "name",
        "owner",
        "stargazers_count",
        "forks_count",
        "watchers_count",
        "open_issues_count",
        "default_branch",
        "created_at",
        "updated_at",
        "html_url",
    }

    missing_fields = [
        field for field in required_fields if field not in repository_data
    ]

    if missing_fields:
        missing = ", ".join(sorted(missing_fields))
        raise ValueError(f"GitHub response is missing required fields: {missing}")


def transform_repository(repository_data: dict[str, Any]) -> dict[str, Any]:
    """
    Transform raw GitHub JSON into database-ready repository data.

    Args:
        repository_data: Raw repository JSON from GitHub.

    Returns:
        dict[str, Any]: Clean repository data for persistence.
    """
    validate_repository_response(repository_data)

    owner_data = repository_data.get("owner") or {}
    owner_login = owner_data.get("login")

    if not owner_login:
        raise ValueError("GitHub response is missing owner login.")

    return {
        "repo_name": repository_data["name"],
        "owner": owner_login,
        "description": repository_data.get("description"),
        "stars": repository_data["stargazers_count"],
        "forks": repository_data["forks_count"],
        "watchers": repository_data["watchers_count"],
        "open_issues": repository_data["open_issues_count"],
        "language": repository_data.get("language"),
        "default_branch": repository_data["default_branch"],
        "created_at": parse_github_datetime(repository_data["created_at"]),
        "updated_at": parse_github_datetime(repository_data["updated_at"]),
        "html_url": repository_data["html_url"],
        "last_synced": datetime.now(timezone.utc),
    }


def fetch_repository(
    github_client: GitHubClient,
    owner: str,
    repo: str,
) -> dict[str, Any]:
    """
    Fetch and transform repository data from GitHub.

    Args:
        github_client: Authenticated GitHub API client.
        owner: Repository owner or organization.
        repo: Repository name.

    Returns:
        dict[str, Any]: Repository data ready to be saved.
    """
    repository_data = github_client.get_repository(owner=owner, repo=repo)
    return transform_repository(repository_data)
