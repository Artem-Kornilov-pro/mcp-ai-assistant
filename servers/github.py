"""MCP server for GitHub API integration."""

import base64
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


def _request(
    method: str,
    path: str,
    json: dict[str, Any] | None = None,
    raw: bool = False,
) -> dict[str, Any] | httpx.Response:
    """Make an authenticated GitHub API request."""
    url = f"{BASE_URL}{path}"
    response = httpx.request(
        method=method,
        url=url,
        headers=_headers(),
        json=json,
        timeout=30.0,
    )
    if raw:
        if response.status_code >= 400:
            raise RuntimeError(f"GitHub API error: {response.status_code} - {response.text}")
        return response

    if response.status_code == 401:
        raise PermissionError("GitHub authentication failed. Check GITHUB_TOKEN.")
    if response.status_code == 403:
        raise PermissionError("GitHub access forbidden. Check token permissions.")
    if response.status_code == 404:
        raise FileNotFoundError(f"GitHub resource not found: {path}")
    if response.status_code >= 400:
        raise RuntimeError(f"GitHub API error: {response.status_code} - {response.text}")
    return response.json()


# ===================== Repositories =====================


@mcp.tool()
def list_repos(sort: str = "updated", per_page: int = 30) -> list[str]:
    """List repositories for the authenticated user.

    Args:
        sort: Sort by (updated, created, pushed, full_name). Default: updated.
        per_page: Results per page (max 100). Default: 30.

    Returns:
        List of repository full names.
    """
    data = _request("GET", f"/user/repos?per_page={per_page}&sort={sort}&type=all")
    if isinstance(data, dict):
        return [data["full_name"]]
    return [repo["full_name"] for repo in data]


@mcp.tool()
def get_repo_info(repo: str) -> dict[str, Any]:
    """Get detailed information about a repository.

    Args:
        repo: Repository full name (e.g., "user/repo-name").

    Returns:
        Dict with description, stars, language, topics, license, etc.
    """
    data = _request("GET", f"/repos/{repo}")
    if isinstance(data, dict):
        return {
            "name": data.get("full_name"),
            "description": data.get("description"),
            "stars": data.get("stargazers_count"),
            "language": data.get("language"),
            "topics": data.get("topics", []),
            "license": data.get("license", {}).get("spdx_id") if data.get("license") else None,
            "url": data.get("html_url"),
            "default_branch": data.get("default_branch"),
        }
    return {}


@mcp.tool()
def create_repo(name: str, description: str = "", private: bool = False) -> str:
    """Create a new repository.

    Args:
        name: Repository name.
        description: Optional description.
        private: Whether the repo is private. Default: False.

    Returns:
        URL of the created repository.
    """
    payload: dict[str, Any] = {"name": name, "private": private}
    if description:
        payload["description"] = description
    data = _request("POST", "/user/repos", json=payload)
    if isinstance(data, dict):
        return data.get("html_url", "Repository created")
    return "Repository created"


# ===================== Files & Contents =====================


@mcp.tool()
def get_file(repo: str, path: str, branch: str = "") -> str:
    """Get contents of a file from a repository.

    Args:
        repo: Repository full name (e.g., "user/repo-name").
        path: File path within the repository.
        branch: Branch name. Default: default branch.

    Returns:
        File content as text.
    """
    url = f"/repos/{repo}/contents/{path}"
    if branch:
        url += f"?ref={branch}"
    data = _request("GET", url)
    if isinstance(data, dict):
        content = data.get("content", "")
        return base64.b64decode(content).decode("utf-8")
    return str(data)


@mcp.tool()
def list_directory(repo: str, path: str = "", branch: str = "") -> list[str]:
    """List contents of a directory in a repository.

    Args:
        repo: Repository full name (e.g., "user/repo-name").
        path: Directory path inside repo. Empty for root.
        branch: Branch name. Default: default branch.

    Returns:
        List of file/directory names with type indicators.
    """
    url = f"/repos/{repo}/contents/{path}"
    if branch:
        url += f"?ref={branch}"
    data = _request("GET", url)
    if isinstance(data, list):
        return [f"{'📁' if item['type'] == 'dir' else '📄'} {item['name']}" for item in data]
    return []


@mcp.tool()
def create_or_update_file(
    repo: str,
    path: str,
    content: str,
    message: str = "Update file",
    branch: str = "",
) -> str:
    """Create or update a file in a repository.

    Args:
        repo: Repository full name (e.g., "user/repo-name").
        path: File path inside repo.
        content: New file content.
        message: Commit message.
        branch: Branch to commit to. Creates new branch if doesn't exist.

    Returns:
        URL of the committed file.
    """
    # Get SHA if file exists (needed for update)
    sha: str | None = None
    try:
        existing = _request("GET", f"/repos/{repo}/contents/{path}")
        if isinstance(existing, dict):
            sha = existing.get("sha")
    except FileNotFoundError:
        pass

    payload: dict[str, Any] = {
        "message": message,
        "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
    }
    if sha:
        payload["sha"] = sha
    if branch:
        payload["branch"] = branch

    data = _request("PUT", f"/repos/{repo}/contents/{path}", json=payload)
    if isinstance(data, dict):
        return data.get("content", {}).get("html_url", "File created/updated")
    return "File created/updated"


# ===================== Issues =====================


@mcp.tool()
def create_issue(repo: str, title: str, body: str = "", labels: list[str] | None = None) -> str:
    """Create a new issue in a repository.

    Args:
        repo: Repository full name (e.g., "user/repo-name").
        title: Issue title.
        body: Issue description (markdown supported).
        labels: List of label names to apply.

    Returns:
        URL of the created issue.
    """
    payload: dict[str, Any] = {"title": title}
    if body:
        payload["body"] = body
    if labels:
        payload["labels"] = labels

    data = _request("POST", f"/repos/{repo}/issues", json=payload)
    if isinstance(data, dict):
        return data["html_url"]
    return "Issue created"


@mcp.tool()
def list_issues(repo: str, state: str = "open", per_page: int = 20) -> list[dict[str, Any]]:
    """List issues in a repository.

    Args:
        repo: Repository full name.
        state: open, closed, or all. Default: open.
        per_page: Results per page.

    Returns:
        List of issues with title, number, state, url.
    """
    data = _request("GET", f"/repos/{repo}/issues?state={state}&per_page={per_page}")
    if isinstance(data, list):
        return [
            {
                "number": issue["number"],
                "title": issue["title"],
                "state": issue["state"],
                "url": issue["html_url"],
            }
            for issue in data
        ]
    return []


@mcp.tool()
def update_issue(
    repo: str, issue_number: int, title: str = "", body: str = "", state: str = ""
) -> str:
    """Update an existing issue.

    Args:
        repo: Repository full name.
        issue_number: Issue number to update.
        title: New title (optional).
        body: New body (optional).
        state: open or closed (optional).

    Returns:
        URL of the updated issue.
    """
    payload: dict[str, Any] = {}
    if title:
        payload["title"] = title
    if body:
        payload["body"] = body
    if state:
        payload["state"] = state

    data = _request("PATCH", f"/repos/{repo}/issues/{issue_number}", json=payload)
    if isinstance(data, dict):
        return data.get("html_url", "Issue updated")
    return "Issue updated"


# ===================== Pull Requests =====================


@mcp.tool()
def create_pull_request(
    repo: str,
    title: str,
    head: str,
    base: str = "main",
    body: str = "",
) -> str:
    """Create a pull request.

    Args:
        repo: Repository full name.
        title: PR title.
        head: Source branch name.
        base: Target branch. Default: main.
        body: PR description.

    Returns:
        URL of the created pull request.
    """
    payload: dict[str, Any] = {"title": title, "head": head, "base": base}
    if body:
        payload["body"] = body

    data = _request("POST", f"/repos/{repo}/pulls", json=payload)
    if isinstance(data, dict):
        return data["html_url"]
    return "PR created"


@mcp.tool()
def list_pull_requests(repo: str, state: str = "open") -> list[dict[str, Any]]:
    """List pull requests in a repository.

    Args:
        repo: Repository full name.
        state: open, closed, or all. Default: open.

    Returns:
        List of PRs with title, number, state, url.
    """
    data = _request("GET", f"/repos/{repo}/pulls?state={state}")
    if isinstance(data, list):
        return [
            {
                "number": pr["number"],
                "title": pr["title"],
                "state": pr["state"],
                "head": pr["head"]["ref"],
                "base": pr["base"]["ref"],
                "url": pr["html_url"],
            }
            for pr in data
        ]
    return []


@mcp.tool()
def merge_pull_request(repo: str, pull_number: int, method: str = "merge") -> str:
    """Merge a pull request.

    Args:
        repo: Repository full name.
        pull_number: PR number.
        method: merge, squash, or rebase. Default: merge.

    Returns:
        Status message.
    """
    payload = {"merge_method": method}
    _request("PUT", f"/repos/{repo}/pulls/{pull_number}/merge", json=payload)
    return f"PR #{pull_number} merged successfully"


# ===================== Search =====================


@mcp.tool()
def search_code(query: str, repo: str | None = None, per_page: int = 30) -> list[str]:
    """Search for code in GitHub repositories.

    Args:
        query: Search query.
        repo: Optional repository filter.
        per_page: Results per page.

    Returns:
        List of matching file paths.
    """
    q = query
    if repo:
        q = f"{query} repo:{repo}"
    data = _request("GET", f"/search/code?q={q}&per_page={per_page}")
    if isinstance(data, dict):
        items = data.get("items", [])
        return [f"{item['repository']['full_name']}: {item['path']}" for item in items]
    return []


@mcp.tool()
def search_repos(query: str, per_page: int = 20) -> list[str]:
    """Search for repositories on GitHub.

    Args:
        query: Search query.
        per_page: Results per page.

    Returns:
        List of repository full names.
    """
    data = _request("GET", f"/search/repositories?q={query}&per_page={per_page}")
    if isinstance(data, dict):
        items = data.get("items", [])
        return [item["full_name"] for item in items]
    return []


# ===================== Branches & Commits =====================


@mcp.tool()
def list_branches(repo: str) -> list[str]:
    """List branches in a repository.

    Args:
        repo: Repository full name.

    Returns:
        List of branch names.
    """
    data = _request("GET", f"/repos/{repo}/branches")
    if isinstance(data, list):
        return [branch["name"] for branch in data]
    return []


@mcp.tool()
def create_branch(repo: str, branch_name: str, from_branch: str = "main") -> str:
    """Create a new branch from an existing branch.

    Args:
        repo: Repository full name.
        branch_name: New branch name.
        from_branch: Source branch. Default: main.

    Returns:
        Status message.
    """
    # Get SHA of source branch
    ref_data = _request("GET", f"/repos/{repo}/git/ref/heads/{from_branch}")
    if isinstance(ref_data, dict):
        sha = ref_data["object"]["sha"]
        payload = {"ref": f"refs/heads/{branch_name}", "sha": sha}
        _request("POST", f"/repos/{repo}/git/refs", json=payload)
        return f"Branch '{branch_name}' created from '{from_branch}'"
    return "Branch created"


@mcp.tool()
def list_commits(repo: str, per_page: int = 20, branch: str = "") -> list[dict[str, Any]]:
    """List recent commits in a repository.

    Args:
        repo: Repository full name.
        per_page: Results per page.
        branch: Branch name. Default: default branch.

    Returns:
        List of commits with sha, message, author, date.
    """
    url = f"/repos/{repo}/commits?per_page={per_page}"
    if branch:
        url += f"&sha={branch}"
    data = _request("GET", url)
    if isinstance(data, list):
        return [
            {
                "sha": c["sha"][:7],
                "message": c["commit"]["message"].split("\n")[0],
                "author": c["commit"]["author"]["name"],
                "date": c["commit"]["author"]["date"],
            }
            for c in data
        ]
    return []


if __name__ == "__main__":
    mcp.run()
