"""Unit tests for Validate MCP server."""


class TestValidateEmail:
    """Tests for validate_email tool."""

    def test_valid(self) -> None:
        from servers.validate_server import validate_email

        assert validate_email("user@example.com") == "True"

    def test_invalid(self) -> None:
        from servers.validate_server import validate_email

        assert validate_email("not-an-email") == "False"

    def test_extra_text(self) -> None:
        from servers.validate_server import validate_email

        assert validate_email("hello user@example.com world") == "False"


class TestValidateUrl:
    """Tests for validate_url tool."""

    def test_valid_https(self) -> None:
        from servers.validate_server import validate_url

        assert validate_url("https://example.com/path?query=1") == "True"

    def test_valid_http(self) -> None:
        from servers.validate_server import validate_url

        assert validate_url("http://example.com") == "True"

    def test_invalid(self) -> None:
        from servers.validate_server import validate_url

        assert validate_url("not a url") == "False"


class TestExtractEmails:
    """Tests for extract_emails tool."""

    def test_finds_multiple(self) -> None:
        from servers.validate_server import extract_emails

        result = extract_emails("Contact a@example.com or b@test.org for info")
        assert result == "a@example.com, b@test.org"

    def test_none_found(self) -> None:
        from servers.validate_server import extract_emails

        assert extract_emails("no emails here") == "No emails found."


class TestExtractUrls:
    """Tests for extract_urls tool."""

    def test_finds_multiple(self) -> None:
        from servers.validate_server import extract_urls

        result = extract_urls("Visit https://a.com and https://b.com/x today")
        assert result == "https://a.com, https://b.com/x"

    def test_none_found(self) -> None:
        from servers.validate_server import extract_urls

        assert extract_urls("no links here") == "No URLs found."


class TestSlugify:
    """Tests for slugify tool."""

    def test_basic(self) -> None:
        from servers.validate_server import slugify

        assert slugify("Hello World!") == "hello-world"

    def test_extra_whitespace_and_punctuation(self) -> None:
        from servers.validate_server import slugify

        assert slugify("  Привет -- Мир!! ") == "привет-мир"

    def test_already_slug(self) -> None:
        from servers.validate_server import slugify

        assert slugify("already-a-slug") == "already-a-slug"
