"""Repository ingestion and transformation functions."""

from datetime import datetime, timezone
from collections.abc import Iterable
from typing import Any

from ingestion.github_client import GitHubClient
from utils.logger import get_logger


logger = get_logger(__name__)


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
        "size",
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


def _validate_non_negative_int(value: Any, field_name: str) -> int:
    """
    Validate that a GitHub numeric field is a non-negative integer.

    Args:
        value: Raw value from GitHub.
        field_name: Field name used in the validation error.

    Returns:
        int: Validated integer.
    """
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name} must be a non-negative integer.")

    return value


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

    repo_name = str(repository_data["name"]).strip()
    default_branch = str(repository_data["default_branch"]).strip()
    html_url = str(repository_data["html_url"]).strip()

    if not repo_name:
        raise ValueError("GitHub response contains an empty repository name.")
    if not default_branch:
        raise ValueError("GitHub response contains an empty default branch.")
    if not html_url:
        raise ValueError("GitHub response contains an empty HTML URL.")

    return {
        "repo_name": repo_name,
        "owner": str(owner_login).strip(),
        "description": repository_data.get("description"),
        "stars": _validate_non_negative_int(
            repository_data["stargazers_count"],
            "stargazers_count",
        ),
        "forks": _validate_non_negative_int(
            repository_data["forks_count"],
            "forks_count",
        ),
        "watchers": _validate_non_negative_int(
            repository_data["watchers_count"],
            "watchers_count",
        ),
        "open_issues": _validate_non_negative_int(
            repository_data["open_issues_count"],
            "open_issues_count",
        ),
        "size_kb": _validate_non_negative_int(repository_data["size"], "size"),
        "language": repository_data.get("language"),
        "default_branch": default_branch,
        "created_at": parse_github_datetime(repository_data["created_at"]),
        "updated_at": parse_github_datetime(repository_data["updated_at"]),
        "html_url": html_url,
        "last_synced": datetime.now(timezone.utc),
    }


def transform_repositories(
    repositories_data: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Transform and de-duplicate raw repository responses.

    Args:
        repositories_data: Raw GitHub repository responses.

    Returns:
        list[dict[str, Any]]: Clean repository records ready for persistence.
    """
    transformed_repositories: list[dict[str, Any]] = []
    seen_repositories: set[tuple[str, str]] = set()

    for repository_data in repositories_data:
        transformed = transform_repository(repository_data)
        repository_key = (
            transformed["owner"].lower(),
            transformed["repo_name"].lower(),
        )

        if repository_key in seen_repositories:
            logger.warning(
                "Duplicate skipped: %s/%s",
                transformed["owner"],
                transformed["repo_name"],
            )
            continue

        seen_repositories.add(repository_key)
        transformed_repositories.append(transformed)

    return transformed_repositories


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


def fetch_repositories_for_account(
    github_client: GitHubClient,
    account: str,
) -> list[dict[str, Any]]:
    """
    Fetch and transform all repositories for a GitHub organization or user.

    Args:
        github_client: Authenticated GitHub API client.
        account: GitHub organization or user login.

    Returns:
        list[dict[str, Any]]: Repository data ready to be saved.
    """
    repositories_data = github_client.get_repositories_for_account(account=account)
    return transform_repositories(repositories_data)
