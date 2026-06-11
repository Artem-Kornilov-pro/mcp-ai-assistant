"""MCP server for GitHub API integration."""

import os
from typing import Any

import httpx
from fastmcp import FastMCP

mcp = FastMCP("GitHub")

BASE_URL = "https://api.github.com"


def _headers() -> dict[str, str]:
    """Get authorization headers."""
    token = os.getenv("GITHUB_TOKEN", "")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable is not set")
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _request(method: str, path: str, json: dict[str, Any] | None = None) -> dict[str, Any]:
    """Make an authenticated GitHub API request."""
    url = f"{BASE_URL}{path}"
    response = httpx.request(
        method=method,
        url=url,
        headers=_headers(),
        json=json,
        timeout=30.0,
    )
    if response.status_code == 401:
        raise PermissionError("GitHub authentication failed. Check GITHUB_TOKEN.")
    if response.status_code == 403:
        raise PermissionError("GitHub access forbidden. Check token permissions.")
    if response.status_code == 404:
        raise FileNotFoundError(f"GitHub resource not found: {path}")
    if response.status_code >= 400:
        raise RuntimeError(f"GitHub API error: {response.status_code} - {response.text}")
    return response.json()


@mcp.tool()
def list_repos() -> list[str]:
    """List all repositories for the authenticated user.

    Returns:
        List of repository full names (e.g., "user/repo-name").
    """
    data = _request("GET", "/user/repos?per_page=100&sort=updated")
    return [repo["full_name"] for repo in data]


@mcp.tool()
def create_issue(repo: str, title: str, body: str = "") -> str:
    """Create a new issue in a repository.

    Args:
        repo: Repository full name (e.g., "user/repo-name").
        title: Issue title.
        body: Issue description (markdown supported).

    Returns:
        URL of the created issue.
    """
    payload: dict[str, str] = {"title": title}
    if body:
        payload["body"] = body

    data = _request("POST", f"/repos/{repo}/issues", json=payload)
    return data["html_url"]


@mcp.tool()
def search_code(query: str, repo: str | None = None) -> list[str]:
    """Search for code in GitHub repositories.

    Args:
        query: Search query (supports GitHub code search syntax).
        repo: Optional repository filter (e.g., "user/repo-name").

    Returns:
        List of matching file paths with repository info.
    """
    q = query
    if repo:
        q = f"{query} repo:{repo}"

    data = _request("GET", f"/search/code?q={q}&per_page=30")
    items = data.get("items", [])
    return [f"{item['repository']['full_name']}: {item['path']}" for item in items]


@mcp.tool()
def get_file(repo: str, path: str) -> str:
    """Get contents of a file from a repository.

    Args:
        repo: Repository full name (e.g., "user/repo-name").
        path: File path within the repository.

    Returns:
        File content as text (decoded from base64).
    """
    import base64

    data = _request("GET", f"/repos/{repo}/contents/{path}")
    content = data.get("content", "")
    return base64.b64decode(content).decode("utf-8")


if __name__ == "__main__":
    mcp.run()
