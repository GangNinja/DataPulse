"""SQLAlchemy ORM models for DataPulse."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""


class Repository(Base):
    """Repository metadata stored from the GitHub API."""

    __tablename__ = "repositories"
    __table_args__ = (
        UniqueConstraint("owner", "repo_name", name="uq_repository_owner_name"),
        CheckConstraint("stars >= 0", name="ck_repositories_stars_non_negative"),
        CheckConstraint("forks >= 0", name="ck_repositories_forks_non_negative"),
        CheckConstraint(
            "watchers >= 0",
            name="ck_repositories_watchers_non_negative",
        ),
        CheckConstraint(
            "open_issues >= 0",
            name="ck_repositories_open_issues_non_negative",
        ),
        CheckConstraint(
            "size_kb >= 0",
            name="ck_repositories_size_kb_non_negative",
        ),
        Index("ix_repositories_owner", "owner"),
        Index("ix_repositories_repo_name", "repo_name"),
        Index("ix_repositories_language", "language"),
        Index("ix_repositories_stars", "stars"),
        Index("ix_repositories_updated_at", "updated_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    repo_name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    stars: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    forks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    watchers: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    open_issues: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    size_kb: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    language: Mapped[str | None] = mapped_column(String(100), nullable=True)
    default_branch: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    html_url: Mapped[str] = mapped_column(String(500), nullable=False)
    last_synced: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    metrics: Mapped[RepositoryMetric | None] = relationship(
        back_populates="repository",
        cascade="all, delete-orphan",
        uselist=False,
    )
    health: Mapped[RepositoryHealth | None] = relationship(
        back_populates="repository",
        cascade="all, delete-orphan",
        uselist=False,
    )


class RepositoryMetric(Base):
    """Analytics-ready derived repository metrics."""

    __tablename__ = "repository_metrics"
    __table_args__ = (
        UniqueConstraint("repository_id", name="uq_repository_metrics_repository_id"),
        CheckConstraint(
            "repository_age_days >= 0",
            name="ck_repository_metrics_age_non_negative",
        ),
        CheckConstraint(
            "days_since_last_update >= 0",
            name="ck_repository_metrics_days_since_update_non_negative",
        ),
        CheckConstraint(
            "popularity_score >= 0",
            name="ck_repository_metrics_popularity_non_negative",
        ),
        CheckConstraint(
            "size_category IN ('Small', 'Medium', 'Large')",
            name="ck_repository_metrics_size_category",
        ),
        Index("ix_repository_metrics_owner", "owner"),
        Index("ix_repository_metrics_repo_name", "repo_name"),
        Index("ix_repository_metrics_language_category", "language_category"),
        Index("ix_repository_metrics_popularity_score", "popularity_score"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    repository_id: Mapped[int] = mapped_column(
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
    )
    owner: Mapped[str] = mapped_column(String(255), nullable=False)
    repo_name: Mapped[str] = mapped_column(String(255), nullable=False)
    repository_age_days: Mapped[int] = mapped_column(Integer, nullable=False)
    popularity_score: Mapped[float] = mapped_column(Float, nullable=False)
    days_since_last_update: Mapped[int] = mapped_column(Integer, nullable=False)
    size_category: Mapped[str] = mapped_column(String(20), nullable=False)
    language_category: Mapped[str] = mapped_column(String(100), nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    repository: Mapped[Repository] = relationship(back_populates="metrics")


class RepositoryHealth(Base):
    """Repository health score generated by the Week 3 extension."""

    __tablename__ = "repository_health"
    __table_args__ = (
        UniqueConstraint("repository_id", name="uq_repository_health_repository_id"),
        CheckConstraint(
            "health_score >= 0 AND health_score <= 100",
            name="ck_repository_health_score_range",
        ),
        CheckConstraint(
            """
            health_category IN (
                'Excellent',
                'Very Good',
                'Good',
                'Average',
                'Needs Attention'
            )
            """,
            name="ck_repository_health_category",
        ),
        Index("ix_repository_health_score", "health_score"),
        Index("ix_repository_health_category", "health_category"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    repository_id: Mapped[int] = mapped_column(
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
    )
    health_score: Mapped[float] = mapped_column(Float, nullable=False)
    health_category: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    repository: Mapped[Repository] = relationship(back_populates="health")
