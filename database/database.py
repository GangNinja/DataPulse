"""Database engine and session management."""

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
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
        logger.info("Connected to database and verified tables.")
        return sessionmaker(bind=engine, autocommit=False, autoflush=False)
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
