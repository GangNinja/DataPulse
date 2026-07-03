"""Reusable GitHub REST API client."""

from typing import Any

import requests
from requests import Response

from utils.logger import get_logger


logger = get_logger(__name__)


class GitHubAPIError(Exception):
    """Raised when the GitHub API request fails."""


class GitHubClient:
    """Client for retrieving repository data from the GitHub REST API."""

    BASE_URL = "https://api.github.com"
    DEFAULT_PER_PAGE = 100

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
                "User-Agent": "DataPulse-Week2",
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
        logger.info("Fetching repository %s/%s from GitHub...", owner, repo)
        response = self._get(f"/repos/{owner}/{repo}")
        return response.json()

    def get_repositories_for_account(
        self,
        account: str,
        per_page: int = DEFAULT_PER_PAGE,
    ) -> list[dict[str, Any]]:
        """
        Fetch every public repository for a GitHub organization or user.

        Args:
            account: GitHub organization or user login.
            per_page: Number of repositories requested per page.

        Returns:
            list[dict[str, Any]]: Raw repository responses from GitHub.

        Raises:
            GitHubAPIError: If GitHub cannot be reached or returns an error.
        """
        if per_page <= 0 or per_page > self.DEFAULT_PER_PAGE:
            raise ValueError("per_page must be between 1 and 100.")

        repositories: list[dict[str, Any]] = []
        page = 1
        endpoint = f"/orgs/{account}/repos"

        logger.info("Fetching repositories for GitHub account %s...", account)

        while True:
            params = {
                "per_page": per_page,
                "page": page,
                "sort": "updated",
                "direction": "desc",
            }
            response = self._get(
                endpoint,
                params=params,
                allow_not_found=endpoint.startswith("/orgs/"),
            )

            if response.status_code == 404 and endpoint.startswith("/orgs/"):
                logger.info(
                    "%s is not an organization endpoint. Trying user endpoint.",
                    account,
                )
                endpoint = f"/users/{account}/repos"
                page = 1
                continue

            page_data = response.json()
            if not isinstance(page_data, list):
                raise GitHubAPIError("GitHub repository list response was invalid.")

            if not page_data:
                break

            repositories.extend(page_data)
            logger.info(
                "Fetched page %s containing %s repositories.",
                page,
                len(page_data),
            )

            if "next" not in response.links:
                break

            page += 1

        logger.info("Fetched %s repositories from GitHub.", len(repositories))
        return repositories

    def _get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        allow_not_found: bool = False,
    ) -> Response:
        """
        Send a GET request to GitHub and normalize request failures.

        Args:
            endpoint: API path beginning with a slash.
            params: Optional query parameters.
            allow_not_found: Return 404 responses for caller-controlled fallback.

        Returns:
            Response: Successful GitHub response.
        """
        url = f"{self.BASE_URL}{endpoint}"

        try:
            response = self.session.get(
                url,
                params=params,
                timeout=self.timeout_seconds,
            )
        except requests.Timeout as exc:
            logger.error("API timeout while connecting to GitHub: %s", exc)
            raise GitHubAPIError("GitHub API timeout.") from exc
        except requests.RequestException as exc:
            logger.error("GitHub API request failed: %s", exc)
            raise GitHubAPIError("Unable to connect to GitHub API.") from exc

        if allow_not_found and response.status_code == 404:
            return response

        self._raise_for_status(response)
        return response

    @staticmethod
    def _raise_for_status(response: Response) -> None:
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
            logger.error("GitHub resource was not found.")
            raise GitHubAPIError("GitHub resource was not found.")

        logger.error(
            "GitHub API returned status %s: %s",
            response.status_code,
            response.text,
        )
        raise GitHubAPIError(
            f"GitHub API request failed with status {response.status_code}."
        )
