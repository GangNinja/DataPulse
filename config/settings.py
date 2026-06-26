"""Application settings loaded from environment variables."""

from dataclasses import dataclass
import os

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Runtime configuration for the DataPulse Week 1 pipeline."""

    github_token: str
    github_owner: str
    github_repo: str
    database_url: str
    request_timeout_seconds: int = 30


def get_settings() -> Settings:
    """
    Read and validate required settings from the environment.

    Returns:
        Settings: A frozen settings object used by the application.

    Raises:
        ValueError: If one or more required environment variables are missing.
    """
    settings = Settings(
        github_token=os.getenv("GITHUB_TOKEN", "").strip(),
        github_owner=os.getenv("GITHUB_OWNER", "").strip(),
        github_repo=os.getenv("GITHUB_REPO", "").strip(),
        database_url=os.getenv("DATABASE_URL", "").strip(),
        request_timeout_seconds=int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30")),
    )

    missing_values = [
        variable_name
        for variable_name, value in {
            "GITHUB_TOKEN": settings.github_token,
            "GITHUB_OWNER": settings.github_owner,
            "GITHUB_REPO": settings.github_repo,
            "DATABASE_URL": settings.database_url,
        }.items()
        if not value
    ]

    if missing_values:
        missing = ", ".join(missing_values)
        raise ValueError(f"Missing required environment variables: {missing}")

    return settings
