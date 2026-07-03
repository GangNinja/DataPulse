"""Tests for database persistence and duplicate detection."""

from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from database.crud import store_repositories, upsert_repository
from database.database import get_db_session, initialize_database
from database.models import Base, Repository
from transformations.repository_metrics import refresh_repository_metrics


def _session() -> Session:
    """Create an isolated in-memory database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine)
    return session_factory()


def _repository_data(repo_name: str = "DataPulse") -> dict[str, object]:
    """Create valid repository data for persistence tests."""
    timestamp = datetime(2024, 1, 1, tzinfo=timezone.utc)
    return {
        "repo_name": repo_name,
        "owner": "OpenAI",
        "description": "Repository intelligence platform.",
        "stars": 100,
        "forks": 20,
        "watchers": 10,
        "open_issues": 2,
        "size_kb": 4096,
        "language": "Python",
        "default_branch": "main",
        "created_at": timestamp,
        "updated_at": timestamp,
        "html_url": "https://github.com/openai/datapulse",
        "last_synced": timestamp,
    }


def test_upsert_repository_inserts_record() -> None:
    """A new repository payload should create a database row."""
    session = _session()

    saved_repository = upsert_repository(session, _repository_data())

    assert saved_repository.id is not None
    assert session.query(Repository).count() == 1
    session.close()


def test_store_repositories_skips_case_insensitive_duplicates() -> None:
    """Batch storage should skip duplicates instead of inserting twice."""
    session = _session()
    repository_one = _repository_data(repo_name="DataPulse")
    repository_two = _repository_data(repo_name="datapulse")

    summary = store_repositories(session, [repository_one, repository_two])

    assert summary.inserted_count == 1
    assert summary.skipped_duplicates == 1
    assert session.query(Repository).count() == 1
    session.close()


def test_saved_repository_attributes_remain_available_after_session_closes() -> None:
    """Pipeline output should be able to read saved repository values."""
    session_factory = initialize_database("sqlite:///:memory:")

    with get_db_session(session_factory) as session:
        saved_repository = upsert_repository(session, _repository_data())
        refresh_repository_metrics(session)

    assert saved_repository.owner == "OpenAI"
    assert saved_repository.repo_name == "DataPulse"
