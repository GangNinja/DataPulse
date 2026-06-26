"""Reusable GitHub REST API client."""

from typing import Any

import requests

from utils.logger import get_logger


logger = get_logger(__name__)


class GitHubAPIError(Exception):
    """Raised when the GitHub API request fails."""


class GitHubClient:
    """Client for retrieving repository data from the GitHub REST API."""

    BASE_URL = "https://api.github.com"

    def __init__(self, token: str, timeout_seconds: int = 30) -> None:
        """
        Initialize the client with authentication and timeout settings.

        Args:
            token: GitHub personal access token.
            timeout_seconds: Request timeout in seconds.
        """
        self.timeout_seconds = timeout_seconds
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "DataPulse-Week1",
            }
        )

    def get_repository(self, owner: str, repo: str) -> dict[str, Any]:
        """
        Fetch a single repository from GitHub.

        Args:
            owner: Repository owner or organization.
            repo: Repository name.

        Returns:
            dict[str, Any]: Raw JSON response from GitHub.

        Raises:
            GitHubAPIError: If authentication, rate limiting, or API access fails.
        """
        url = f"{self.BASE_URL}/repos/{owner}/{repo}"
        logger.info("Fetching repository %s/%s from GitHub...", owner, repo)

        try:
            response = self.session.get(url, timeout=self.timeout_seconds)
        except requests.RequestException as exc:
            logger.error("GitHub API request failed: %s", exc)
            raise GitHubAPIError("Unable to connect to GitHub API.") from exc

        self._raise_for_status(response)
        return response.json()

    @staticmethod
    def _raise_for_status(response: requests.Response) -> None:
        """
        Convert GitHub response errors into clear application errors.

        Args:
            response: GitHub API response.

        Raises:
            GitHubAPIError: If GitHub returned an unsuccessful response.
        """
        if response.status_code == 200:
            return

        if response.status_code in {401, 403}:
            remaining = response.headers.get("X-RateLimit-Remaining")
            if remaining == "0":
                logger.error("GitHub API rate limit reached.")
                raise GitHubAPIError("GitHub API rate limit reached.")

            logger.error("Authentication failed or access was denied.")
            raise GitHubAPIError("Authentication failed or access was denied.")

        if response.status_code == 404:
            logger.error("Repository was not found.")
            raise GitHubAPIError("Repository was not found.")

        logger.error(
            "GitHub API returned status %s: %s",
            response.status_code,
            response.text,
        )
        raise GitHubAPIError(
            f"GitHub API request failed with status {response.status_code}."
        )
