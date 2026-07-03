"""Tests for the GitHub API client."""

from typing import Any

from ingestion.github_client import GitHubClient


class FakeResponse:
    """Minimal response object used by GitHubClient tests."""

    def __init__(
        self,
        payload: Any,
        status_code: int = 200,
        links: dict[str, Any] | None = None,
    ) -> None:
        self._payload = payload
        self.status_code = status_code
        self.links = links or {}
        self.headers: dict[str, str] = {}
        self.text = ""

    def json(self) -> Any:
        """Return the fake JSON payload."""
        return self._payload


class FakeSession:
    """Simple fake requests session with queued responses."""

    def __init__(self, responses: list[FakeResponse]) -> None:
        self.responses = responses
        self.calls: list[dict[str, Any]] = []
        self.headers: dict[str, str] = {}

    def get(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        timeout: int | None = None,
    ) -> FakeResponse:
        """Record the request and return the next queued response."""
        self.calls.append({"url": url, "params": params, "timeout": timeout})
        return self.responses.pop(0)


def test_get_repositories_for_account_handles_pagination() -> None:
    """The client should follow GitHub pagination links."""
    first_page = FakeResponse(
        payload=[{"name": "repo-one"}],
        links={"next": {"url": "https://api.github.com/page/2"}},
    )
    second_page = FakeResponse(payload=[{"name": "repo-two"}])
    fake_session = FakeSession([first_page, second_page])
    client = GitHubClient(token="token", timeout_seconds=10)
    client.session = fake_session

    repositories = client.get_repositories_for_account("apache")

    assert repositories == [{"name": "repo-one"}, {"name": "repo-two"}]
    assert len(fake_session.calls) == 2
    assert fake_session.calls[0]["params"]["page"] == 1
    assert fake_session.calls[1]["params"]["page"] == 2
    assert fake_session.calls[0]["params"]["per_page"] == 100


def test_get_repositories_for_account_falls_back_to_user_endpoint() -> None:
    """The client should try the user endpoint when org lookup returns 404."""
    org_not_found = FakeResponse(payload={}, status_code=404)
    user_response = FakeResponse(payload=[{"name": "personal-repo"}])
    fake_session = FakeSession([org_not_found, user_response])
    client = GitHubClient(token="token", timeout_seconds=10)
    client.session = fake_session

    repositories = client.get_repositories_for_account("octocat")

    assert repositories == [{"name": "personal-repo"}]
    assert "/orgs/octocat/repos" in fake_session.calls[0]["url"]
    assert "/users/octocat/repos" in fake_session.calls[1]["url"]
