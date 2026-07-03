"""Create and update operations for repository records."""

from dataclasses import dataclass
from collections.abc import Iterable
from typing import Any

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from database.models import Repository
from utils.logger import get_logger


logger = get_logger(__name__)


class RepositoryPersistenceError(Exception):
    """Raised when repository data cannot be saved."""


@dataclass
class RepositoryStoreSummary:
    """Summary of a repository batch persistence operation."""

    inserted_count: int = 0
    skipped_duplicates: int = 0


def _repository_identity(repository_data: dict[str, Any]) -> tuple[str, str]:
    """Return a case-insensitive repository identity key."""
    owner = str(repository_data["owner"]).strip()
    repo_name = str(repository_data["repo_name"]).strip()

    if not owner or not repo_name:
        raise ValueError("Repository owner and name are required.")

    return owner.lower(), repo_name.lower()


def _validate_repository_payload(repository_data: dict[str, Any]) -> None:
    """Validate required repository fields before persistence."""
    required_fields = {
        "repo_name",
        "owner",
        "stars",
        "forks",
        "watchers",
        "open_issues",
        "size_kb",
        "default_branch",
        "created_at",
        "updated_at",
        "html_url",
        "last_synced",
    }
    missing_fields = [
        field for field in required_fields if field not in repository_data
    ]

    if missing_fields:
        missing = ", ".join(sorted(missing_fields))
        raise ValueError(f"Repository payload is missing fields: {missing}")

    for field_name in ("stars", "forks", "watchers", "open_issues", "size_kb"):
        value = repository_data[field_name]
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"{field_name} must be a non-negative integer.")


def get_repository_by_identity(
    session: Session,
    owner: str,
    repo_name: str,
) -> Repository | None:
    """
    Find a repository using case-insensitive owner and repository name.

    Args:
        session: Active SQLAlchemy database session.
        owner: GitHub owner or organization login.
        repo_name: GitHub repository name.

    Returns:
        Repository | None: Matching repository if it already exists.
    """
    return (
        session.query(Repository)
        .filter(
            func.lower(Repository.owner) == owner.lower(),
            func.lower(Repository.repo_name) == repo_name.lower(),
        )
        .one_or_none()
    )


def upsert_repository(
    session: Session,
    repository_data: dict[str, Any],
) -> Repository:
    """
    Insert a repository or update it if it already exists.

    Args:
        session: Active SQLAlchemy database session.
        repository_data: Repository fields prepared for persistence.

    Returns:
        Repository: Saved repository ORM object.

    Raises:
        RepositoryPersistenceError: If saving the repository fails.
    """
    _validate_repository_payload(repository_data)

    try:
        repository = get_repository_by_identity(
            session=session,
            owner=repository_data["owner"],
            repo_name=repository_data["repo_name"],
        )

        if repository is None:
            repository = Repository(**repository_data)
            session.add(repository)
            logger.info("Inserted new repository record.")
        else:
            for field_name, value in repository_data.items():
                setattr(repository, field_name, value)
            logger.info("Duplicate repository found. Existing record updated.")

        session.commit()
        session.refresh(repository)
        logger.info("Repository stored successfully.")
        return repository

    except IntegrityError as exc:
        session.rollback()
        logger.error("Duplicate repository constraint failed: %s", exc)
        raise RepositoryPersistenceError(
            "Repository already exists and could not be updated."
        ) from exc
    except SQLAlchemyError as exc:
        session.rollback()
        logger.error("Database operation failed: %s", exc)
        raise RepositoryPersistenceError("Unable to save repository data.") from exc


def store_repositories(
    session: Session,
    repositories_data: Iterable[dict[str, Any]],
) -> RepositoryStoreSummary:
    """
    Insert repositories and skip duplicates already seen or already stored.

    Args:
        session: Active SQLAlchemy database session.
        repositories_data: Repository payloads prepared for persistence.

    Returns:
        RepositoryStoreSummary: Inserted and skipped repository counts.

    Raises:
        RepositoryPersistenceError: If saving repositories fails.
    """
    summary = RepositoryStoreSummary()
    seen_repositories: set[tuple[str, str]] = set()

    try:
        for repository_data in repositories_data:
            _validate_repository_payload(repository_data)
            repository_key = _repository_identity(repository_data)
            owner = repository_data["owner"]
            repo_name = repository_data["repo_name"]

            if repository_key in seen_repositories:
                summary.skipped_duplicates += 1
                logger.warning("Duplicate skipped: %s/%s", owner, repo_name)
                continue

            seen_repositories.add(repository_key)
            existing_repository = get_repository_by_identity(
                session=session,
                owner=owner,
                repo_name=repo_name,
            )

            if existing_repository is not None:
                summary.skipped_duplicates += 1
                logger.warning("Duplicate skipped: %s/%s", owner, repo_name)
                continue

            session.add(Repository(**repository_data))
            summary.inserted_count += 1

        session.commit()
        logger.info("Stored %s repositories.", summary.inserted_count)
        return summary

    except IntegrityError as exc:
        session.rollback()
        logger.error("Duplicate repository constraint failed: %s", exc)
        raise RepositoryPersistenceError(
            "Repository already exists and could not be inserted."
        ) from exc
    except SQLAlchemyError as exc:
        session.rollback()
        logger.error("Database operation failed: %s", exc)
        raise RepositoryPersistenceError("Unable to save repository data.") from exc
