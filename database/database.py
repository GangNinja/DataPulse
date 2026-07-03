"""Database engine and session management."""

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text
from sqlalchemy.orm import Session, sessionmaker

from database.models import Base
from utils.logger import get_logger


logger = get_logger(__name__)


class DatabaseConnectionError(Exception):
    """Raised when the application cannot connect to PostgreSQL."""


def create_database_engine(database_url: str) -> Engine:
    """
    Create a SQLAlchemy database engine.

    Args:
        database_url: PostgreSQL connection URL.

    Returns:
        Engine: SQLAlchemy engine instance.
    """
    return create_engine(database_url, pool_pre_ping=True)


def _apply_postgres_schema_safety_updates(engine: Engine) -> None:
    """
    Apply additive PostgreSQL schema updates without dropping existing data.

    SQLAlchemy creates new tables, but it does not alter existing tables when
    the ORM model grows. These statements only add missing columns and indexes.
    """
    if engine.dialect.name != "postgresql":
        return

    statements = [
        """
        ALTER TABLE repositories
        ADD COLUMN IF NOT EXISTS size_kb INTEGER NOT NULL DEFAULT 0
        """,
        """
        ALTER TABLE repositories
        ADD COLUMN IF NOT EXISTS last_synced TIMESTAMP WITH TIME ZONE
        NOT NULL DEFAULT NOW()
        """,
        """
        CREATE INDEX IF NOT EXISTS ix_repositories_owner
        ON repositories (owner)
        """,
        """
        CREATE INDEX IF NOT EXISTS ix_repositories_repo_name
        ON repositories (repo_name)
        """,
        """
        CREATE INDEX IF NOT EXISTS ix_repositories_language
        ON repositories (language)
        """,
        """
        CREATE INDEX IF NOT EXISTS ix_repositories_stars
        ON repositories (stars)
        """,
        """
        CREATE INDEX IF NOT EXISTS ix_repositories_updated_at
        ON repositories (updated_at)
        """,
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'ck_repositories_stars_non_negative'
            ) THEN
                ALTER TABLE repositories
                ADD CONSTRAINT ck_repositories_stars_non_negative
                CHECK (stars >= 0) NOT VALID;
            END IF;
        END
        $$
        """,
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'ck_repositories_forks_non_negative'
            ) THEN
                ALTER TABLE repositories
                ADD CONSTRAINT ck_repositories_forks_non_negative
                CHECK (forks >= 0) NOT VALID;
            END IF;
        END
        $$
        """,
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'ck_repositories_watchers_non_negative'
            ) THEN
                ALTER TABLE repositories
                ADD CONSTRAINT ck_repositories_watchers_non_negative
                CHECK (watchers >= 0) NOT VALID;
            END IF;
        END
        $$
        """,
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'ck_repositories_open_issues_non_negative'
            ) THEN
                ALTER TABLE repositories
                ADD CONSTRAINT ck_repositories_open_issues_non_negative
                CHECK (open_issues >= 0) NOT VALID;
            END IF;
        END
        $$
        """,
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'ck_repositories_size_kb_non_negative'
            ) THEN
                ALTER TABLE repositories
                ADD CONSTRAINT ck_repositories_size_kb_non_negative
                CHECK (size_kb >= 0) NOT VALID;
            END IF;
        END
        $$
        """,
    ]

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def initialize_database(database_url: str) -> sessionmaker[Session]:
    """
    Connect to PostgreSQL and create required tables if they do not exist.

    Args:
        database_url: PostgreSQL connection URL.

    Returns:
        sessionmaker[Session]: Factory for creating database sessions.

    Raises:
        DatabaseConnectionError: If the database cannot be reached.
    """
    try:
        engine = create_database_engine(database_url)
        Base.metadata.create_all(bind=engine)
        _apply_postgres_schema_safety_updates(engine)
        logger.info("Connected to database and verified tables.")
        return sessionmaker(
            bind=engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )
    except SQLAlchemyError as exc:
        logger.error("Database connection failed: %s", exc)
        raise DatabaseConnectionError("Unable to connect to PostgreSQL.") from exc


@contextmanager
def get_db_session(
    session_factory: sessionmaker[Session],
) -> Generator[Session, None, None]:
    """
    Provide a database session and ensure it is closed after use.

    Args:
        session_factory: SQLAlchemy session factory.

    Yields:
        Session: Active SQLAlchemy session.
    """
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
