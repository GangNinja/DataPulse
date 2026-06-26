"""Create and update operations for repository records."""

from typing import Any

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from database.models import Repository
from utils.logger import get_logger


logger = get_logger(__name__)


class RepositoryPersistenceError(Exception):
    """Raised when repository data cannot be saved."""


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
    try:
        repository = (
            session.query(Repository)
            .filter(
                Repository.owner == repository_data["owner"],
                Repository.repo_name == repository_data["repo_name"],
            )
            .one_or_none()
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
