"""Tests for update branch utilities."""

from micropython_branch_manager.config import BranchConfig, MicroPythonConfig
from micropython_branch_manager.update_branch import (
    format_mr_description,
    get_gitlab_mr_url,
    get_update_branch_name,
    git_url_to_https,
)


def test_get_update_branch_name():
    """get_update_branch_name appends _update suffix."""
    assert get_update_branch_name("main") == "main_update"
    assert get_update_branch_name("develop") == "develop_update"
    assert get_update_branch_name("feature-branch") == "feature-branch_update"


def test_git_url_to_https_ssh():
    """git_url_to_https converts SSH format."""
    url = "git@github.com:user/repo.git"
    result = git_url_to_https(url)
    assert result == "https://github.com/user/repo"


def test_git_url_to_https_https():
    """git_url_to_https handles HTTPS format."""
    url = "https://github.com/user/repo.git"
    result = git_url_to_https(url)
    assert result == "https://github.com/user/repo"

    # Without .git suffix
    url2 = "https://gitlab.com/user/repo"
    result2 = git_url_to_https(url2)
    assert result2 == "https://gitlab.com/user/repo"


def test_get_gitlab_mr_url_basic():
    """get_gitlab_mr_url generates correct URL."""
    url = get_gitlab_mr_url(
        "https://gitlab.com/user/repo",
        "feature-branch",
        "main",
    )

    assert url.startswith("https://gitlab.com/user/repo/-/merge_requests/new")
    assert "merge_request%5Bsource_branch%5D=feature-branch" in url
    assert "merge_request%5Btarget_branch%5D=main" in url


def test_get_gitlab_mr_url_encoding():
    """get_gitlab_mr_url URL-encodes special characters."""
    url = get_gitlab_mr_url(
        "https://gitlab.com/user/repo",
        "feature/with-slash",
        "main",
        title="Add feature: new thing",
        description="This is a **test** with\nlines",
    )

    # Check URL encoding of slash in branch name
    assert "feature%2Fwith-slash" in url
    # Check URL encoding of special chars in title
    assert "Add%20feature%3A%20new%20thing" in url
    # Check URL encoding of description
    assert "This%20is%20a%20%2A%2Atest%2A%2A" in url


def test_format_mr_description():
    """format_mr_description generates markdown."""
    config = MicroPythonConfig(
        integration_branch="main",
        remotes={
            "upstream": "https://github.com/micropython/micropython.git",
            "origin": "git@github.com:user/micropython.git",
            "unused": "https://example.com/unused.git",
        },
        branches=[
            BranchConfig(
                name="feature-1",
                remote="origin",
                pr_number=12345,
                title="Add feature 1",
                pr_url="https://github.com/micropython/micropython/pull/12345",
            ),
            BranchConfig(
                name="feature-2",
                remote="origin",
                pr_number=12346,
                title="Add feature 2",
                pr_url="https://github.com/micropython/micropython/pull/12346",
            ),
        ],
    )

    description = format_mr_description(config, config.remotes)

    # Check structure
    assert "## Branches" in description
    assert "## Remotes" in description
    assert "## Next Steps" in description

    # Check branches section
    assert "origin/feature-1" in description
    assert "Add feature 1" in description
    assert "https://github.com/micropython/micropython/pull/12345" in description

    # Check remotes section (includes upstream + remotes used by branches)
    assert "**upstream**" in description
    assert "**origin**" in description
    # unused remote not included since no branches use it

    # Check next steps section
    assert "git push" in description
    assert "main_update:main" in description or "+main_update:main" in description
