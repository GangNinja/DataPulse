"""Entry point for the DataPulse pipeline."""

from config.settings import get_settings
from database.crud import (
    RepositoryPersistenceError,
    store_repositories,
    upsert_repository,
)
from database.database import (
    DatabaseConnectionError,
    get_db_session,
    initialize_database,
)
from extensions.repository_health import (
    RepositoryHealthError,
    refresh_repository_health,
)
from ingestion.fetch_repositories import (
    fetch_repositories_for_account,
    fetch_repository,
)
from ingestion.github_client import GitHubAPIError, GitHubClient
from quality.quality_checker import run_repository_quality_checks
from quality.report import save_quality_report
from transformations.repository_metrics import (
    RepositoryMetricError,
    refresh_repository_metrics,
)
from utils.logger import get_logger


logger = get_logger(__name__)


def run_pipeline() -> None:
    """
    Run the GitHub-to-PostgreSQL ingestion and analytics flow.

    Flow:
        1. Read configuration.
        2. Fetch repository data from GitHub.
        3. Transform and validate the response.
        4. Run data quality checks and generate a quality report.
        5. Store raw repository data in PostgreSQL.
        6. Refresh analytics-ready repository metrics.
        7. Refresh repository health scores.
        8. Print a success message.
    """
    settings = get_settings()

    logger.info("Connecting to GitHub...")
    github_client = GitHubClient(
        token=settings.github_token,
        timeout_seconds=settings.request_timeout_seconds,
    )

    session_factory = initialize_database(settings.database_url)

    if settings.github_repo:
        logger.info("Fetching repository...")
        repository_data = fetch_repository(
            github_client=github_client,
            owner=settings.github_owner,
            repo=settings.github_repo,
        )
        quality_result = run_repository_quality_checks([repository_data])
        quality_report_path = save_quality_report(quality_result.report)

        if not quality_result.valid_records:
            raise ValueError("No valid repository records passed data quality checks.")

        with get_db_session(session_factory) as session:
            saved_repository = upsert_repository(
                session,
                quality_result.valid_records[0],
            )
            metric_count = refresh_repository_metrics(session)
            health_count = refresh_repository_health(session)

        print(
            "Success: "
            f"{saved_repository.owner}/{saved_repository.repo_name} "
            "was stored in PostgreSQL. "
            f"{metric_count} analytics rows refreshed. "
            f"{health_count} health rows refreshed. "
            f"Quality report: {quality_report_path}"
        )
        return

    logger.info("Fetching repositories...")
    repositories_data = fetch_repositories_for_account(
        github_client=github_client,
        account=settings.github_owner,
    )
    quality_result = run_repository_quality_checks(repositories_data)
    quality_report_path = save_quality_report(quality_result.report)

    if not quality_result.valid_records:
        raise ValueError("No valid repository records passed data quality checks.")

    with get_db_session(session_factory) as session:
        summary = store_repositories(session, quality_result.valid_records)
        metric_count = refresh_repository_metrics(session)
        health_count = refresh_repository_health(session)

    print(
        "Success: "
        f"stored {summary.inserted_count} repositories, "
        f"skipped {summary.skipped_duplicates} duplicates, "
        f"refreshed {metric_count} analytics rows, "
        f"refreshed {health_count} health rows, "
        f"and generated quality report {quality_report_path}."
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
    except RepositoryMetricError as exc:
        logger.error("Repository metric failure: %s", exc)
        raise SystemExit(1) from exc
    except RepositoryHealthError as exc:
        logger.error("Repository health failure: %s", exc)
        raise SystemExit(1) from exc
