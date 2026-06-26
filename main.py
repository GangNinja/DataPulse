"""Entry point for the DataPulse Week 1 pipeline."""

from config.settings import get_settings
from database.crud import RepositoryPersistenceError, upsert_repository
from database.database import DatabaseConnectionError, get_db_session, initialize_database
from ingestion.fetch_repositories import fetch_repository
from ingestion.github_client import GitHubAPIError, GitHubClient
from utils.logger import get_logger


logger = get_logger(__name__)


def run_pipeline() -> None:
    """
    Run the Week 1 GitHub-to-PostgreSQL ingestion flow.

    Flow:
        1. Read configuration.
        2. Fetch repository data from GitHub.
        3. Transform and validate the response.
        4. Store the result in PostgreSQL.
        5. Print a success message.
    """
    settings = get_settings()

    github_client = GitHubClient(
        token=settings.github_token,
        timeout_seconds=settings.request_timeout_seconds,
    )

    repository_data = fetch_repository(
        github_client=github_client,
        owner=settings.github_owner,
        repo=settings.github_repo,
    )

    session_factory = initialize_database(settings.database_url)

    with get_db_session(session_factory) as session:
        saved_repository = upsert_repository(session, repository_data)

    print(
        "Success: "
        f"{saved_repository.owner}/{saved_repository.repo_name} "
        "was stored in PostgreSQL."
    )


if __name__ == "__main__":
    try:
        run_pipeline()
    except ValueError as exc:
        logger.error("Configuration or validation error: %s", exc)
        raise SystemExit(1) from exc
    except GitHubAPIError as exc:
        logger.error("GitHub API failure: %s", exc)
        raise SystemExit(1) from exc
    except DatabaseConnectionError as exc:
        logger.error("Database connection failure: %s", exc)
        raise SystemExit(1) from exc
    except RepositoryPersistenceError as exc:
        logger.error("Repository persistence failure: %s", exc)
        raise SystemExit(1) from exc
