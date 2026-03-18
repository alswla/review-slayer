"""GitHub API client.

Handles GitHub App authentication (JWT → Installation Token)
and provides methods for interacting with the GitHub REST API.
"""

import logging
import time

import httpx
import jwt

from app.config import get_settings

logger = logging.getLogger(__name__)

GITHUB_API_BASE = "https://api.github.com"


class GitHubClient:
    """Async GitHub API client using GitHub App authentication."""

    def __init__(self, installation_id: int):
        self.installation_id = installation_id
        self._settings = get_settings()
        self._token: str | None = None

    # ──────────────────────────────────────
    #  Authentication
    # ──────────────────────────────────────

    def _create_jwt(self) -> str:
        """Create a short-lived JWT for GitHub App authentication."""
        now = int(time.time())
        payload = {
            "iat": now - 60,  # issued at (60s leeway)
            "exp": now + (10 * 60),  # expires in 10 min
            "iss": self._settings.github_app_id,
        }
        private_key = self._settings.github_private_key
        if not private_key:
            raise RuntimeError(
                "GitHub App private key not found. "
                f"Check GITHUB_PRIVATE_KEY_PATH={self._settings.github_private_key_path}"
            )
        return jwt.encode(payload, private_key, algorithm="RS256")

    async def _get_installation_token(self) -> str:
        """Exchange JWT for an installation access token."""
        if self._token:
            return self._token

        app_jwt = self._create_jwt()
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{GITHUB_API_BASE}/app/installations/{self.installation_id}/access_tokens",
                headers={
                    "Authorization": f"Bearer {app_jwt}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
            )
            resp.raise_for_status()
            self._token = resp.json()["token"]
            return self._token

    async def _headers(self) -> dict[str, str]:
        """Return authenticated request headers."""
        token = await self._get_installation_token()
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    # ──────────────────────────────────────
    #  API Methods
    # ──────────────────────────────────────

    async def get_pull_request_diff(self, repo: str, pr_number: int) -> str:
        """Fetch the unified diff for a pull request.

        Args:
            repo: Full repository name (e.g. "owner/repo").
            pr_number: Pull request number.

        Returns:
            The raw diff text.
        """
        headers = await self._headers()
        headers["Accept"] = "application/vnd.github.v3.diff"

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{GITHUB_API_BASE}/repos/{repo}/pulls/{pr_number}",
                headers=headers,
                follow_redirects=True,
            )
            resp.raise_for_status()
            return resp.text

    async def create_review_comment(self, repo: str, pr_number: int, body: str) -> dict:
        """Post a review comment on a pull request.

        Args:
            repo: Full repository name.
            pr_number: Pull request number.
            body: Markdown-formatted comment body.

        Returns:
            The created comment data from GitHub API.
        """
        headers = await self._headers()
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{GITHUB_API_BASE}/repos/{repo}/issues/{pr_number}/comments",
                headers=headers,
                json={"body": body},
            )
            resp.raise_for_status()
            logger.info("Comment posted to %s #%d", repo, pr_number)
            return resp.json()

    async def get_pull_request_files(self, repo: str, pr_number: int) -> list[dict]:
        """Fetch the list of files changed in a pull request.

        Args:
            repo: Full repository name.
            pr_number: Pull request number.

        Returns:
            List of file metadata dicts from GitHub API.
        """
        headers = await self._headers()
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{GITHUB_API_BASE}/repos/{repo}/pulls/{pr_number}/files",
                headers=headers,
            )
            resp.raise_for_status()
            return resp.json()

    async def get_file_content(self, repo: str, path: str, ref: str = "main") -> str | None:
        """Fetch a file's content from a repository.

        Args:
            repo: Full repository name.
            path: File path within the repository.
            ref: Git ref (branch/tag/commit). Defaults to "main".

        Returns:
            The file content as a string, or None if not found.
        """
        headers = await self._headers()
        headers["Accept"] = "application/vnd.github.raw+json"

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{GITHUB_API_BASE}/repos/{repo}/contents/{path}",
                headers=headers,
                params={"ref": ref},
            )
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return resp.text
