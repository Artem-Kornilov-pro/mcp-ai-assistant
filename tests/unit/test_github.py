"""Unit tests for GitHub MCP server."""

import os
from unittest.mock import MagicMock, patch

import pytest

os.environ["GITHUB_TOKEN"] = "test-token"


class TestListRepos:
    """Tests for list_repos tool."""

    def test_returns_repo_names(self) -> None:
        from servers.github import list_repos

        mock = MagicMock(
            return_value=[
                {"full_name": "user/repo1"},
                {"full_name": "user/repo2"},
            ]
        )
        with patch("servers.github._request", mock):
            result = list_repos()
            assert result == ["user/repo1", "user/repo2"]

    def test_calls_correct_endpoint(self) -> None:
        from servers.github import list_repos

        mock = MagicMock(return_value=[])
        with patch("servers.github._request", mock):
            list_repos()
            mock.assert_called_once_with("GET", "/user/repos?per_page=100&sort=updated")


class TestCreateIssue:
    """Tests for create_issue tool."""

    def test_creates_issue_with_title_only(self) -> None:
        from servers.github import create_issue

        mock = MagicMock(return_value={"html_url": "https://github.com/user/repo/issues/1"})
        with patch("servers.github._request", mock):
            result = create_issue("user/repo", "Bug report")
            assert result == "https://github.com/user/repo/issues/1"

    def test_creates_issue_with_body(self) -> None:
        from servers.github import create_issue

        mock = MagicMock(return_value={"html_url": "https://github.com/user/repo/issues/2"})
        with patch("servers.github._request", mock):
            result = create_issue("user/repo", "Feature request", body="Please add X")
            assert result == "https://github.com/user/repo/issues/2"

    def test_passes_correct_payload(self) -> None:
        from servers.github import create_issue

        mock = MagicMock(return_value={"html_url": "https://github.com/user/repo/issues/3"})
        with patch("servers.github._request", mock):
            create_issue("user/repo", "Title", body="Description")

        call_args = mock.call_args
        assert call_args.args[0] == "POST"
        assert call_args.args[1] == "/repos/user/repo/issues"
        assert call_args.kwargs["json"] == {"title": "Title", "body": "Description"}


class TestSearchCode:
    """Tests for search_code tool."""

    def test_search_without_repo(self) -> None:
        from servers.github import search_code

        items = [{"repository": {"full_name": "a/b"}, "path": "main.py"}]
        mock = MagicMock(return_value={"items": items})
        with patch("servers.github._request", mock):
            result = search_code("print")
            assert "a/b: main.py" in result

    def test_search_with_repo_filter(self) -> None:
        from servers.github import search_code

        mock = MagicMock(return_value={"items": []})
        with patch("servers.github._request", mock):
            search_code("print", repo="user/repo")
            assert "print repo:user/repo" in mock.call_args.args[1]

    def test_empty_results(self) -> None:
        from servers.github import search_code

        mock = MagicMock(return_value={"items": []})
        with patch("servers.github._request", mock):
            result = search_code("nonexistent_query_12345")
            assert result == []


class TestGetFile:
    """Tests for get_file tool."""

    def test_decodes_base64_content(self) -> None:
        import base64

        from servers.github import get_file

        content = base64.b64encode(b"hello world").decode("utf-8")
        mock = MagicMock(return_value={"content": content})
        with patch("servers.github._request", mock):
            result = get_file("user/repo", "README.md")
            assert result == "hello world"

    def test_calls_correct_endpoint(self) -> None:
        from servers.github import get_file

        mock = MagicMock(return_value={"content": "dGVzdA=="})
        with patch("servers.github._request", mock):
            get_file("user/repo", "src/main.py")
            mock.assert_called_once_with("GET", "/repos/user/repo/contents/src/main.py")


class TestAuthHeaders:
    """Tests for authentication headers."""

    def test_headers_include_token(self) -> None:
        from servers.github import _headers

        headers = _headers()
        assert headers["Authorization"] == "Bearer test-token"
        assert headers["Accept"] == "application/vnd.github+json"

    def test_missing_token_raises(self) -> None:
        from servers.github import _headers

        with patch.dict(os.environ, {"GITHUB_TOKEN": ""}, clear=True):
            with pytest.raises(ValueError, match="GITHUB_TOKEN"):
                _headers()
