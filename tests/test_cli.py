# tests/test_cli.py

import os
import subprocess
import tempfile
from datetime import datetime
from unittest import mock

import pytest
import pytz
import toml
from click.testing import CliRunner
# Adjust the import path based on your project structure
from src.bumpcalver.cli import (
    create_git_tag,
    get_build_version,
    get_current_date,
    get_current_datetime_version,
    load_config,
    main,
    update_version_in_files,
)


# Test get_current_date()
def test_get_current_date():
    tz = "UTC"
    expected_date = datetime.now(pytz.timezone(tz)).strftime("%Y-%m-%d")
    assert get_current_date(timezone=tz) == expected_date


# Test get_current_date() with invalid timezone
def test_get_current_date_invalid_timezone(capfd):
    tz = "Invalid/Timezone"
    expected_date = datetime.now(pytz.timezone("America/New_York")).strftime("%Y-%m-%d")
    assert get_current_date(timezone=tz) == expected_date
    out, err = capfd.readouterr()
    assert (
        "Unknown timezone 'Invalid/Timezone'. Using default 'America/New_York'." in out
    )


# Test get_current_datetime_version()
def test_get_current_datetime_version():
    tz = "UTC"
    expected_datetime = datetime.now(pytz.timezone(tz)).strftime("%Y-%m-%d-%H%M")
    assert get_current_datetime_version(timezone=tz) == expected_datetime


# Test get_current_datetime_version() with invalid timezone
def test_get_current_datetime_version_invalid_timezone(capfd):
    tz = "Invalid/Timezone"
    expected_datetime = datetime.now(pytz.timezone("America/New_York")).strftime(
        "%Y-%m-%d-%H%M"
    )
    assert get_current_datetime_version(timezone=tz) == expected_datetime
    out, err = capfd.readouterr()
    assert (
        "Unknown timezone 'Invalid/Timezone'. Using default 'America/New_York'." in out
    )


# Test get_build_version()
def test_get_build_version():
    # Create a temporary file to simulate the file with the version
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
        temp_file.write('__version__ = "2023-09-30-001"\n')
        temp_file_path = temp_file.name

    file_config = {
        "path": temp_file_path,
        "variable": "__version__",
    }
    version_format = "{current_date}-{build_count:03}"
    tz = "UTC"

    # Mock current date to match the date in the temp file
    with mock.patch("src.bumpcalver.cli.get_current_date", return_value="2023-09-30"):
        new_version = get_build_version(file_config, version_format, timezone=tz)
        assert new_version == "2023-09-30-002"

    os.remove(temp_file_path)


# Test get_build_version() with invalid build count
def test_get_build_version_invalid_build_count(capfd):
    # Create a temporary file to simulate the file with the version
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
        temp_file.write('__version__ = "2023-09-30-abc"\n')
        temp_file_path = temp_file.name

    file_config = {
        "path": temp_file_path,
        "variable": "__version__",
    }
    version_format = "{current_date}-{build_count:03}"
    tz = "UTC"

    # Mock current date to match the date in the temp file
    with mock.patch("src.bumpcalver.cli.get_current_date", return_value="2023-09-30"):
        new_version = get_build_version(file_config, version_format, timezone=tz)
        assert new_version == "2023-09-30-001"
        # Ensure the warning message is printed
        out, err = capfd.readouterr()
        assert (
            f"Warning: Invalid build count 'abc' in {temp_file_path}. Resetting to 1."
            in out
        )

    os.remove(temp_file_path)


# Test get_build_version() with missing file
def test_get_build_version_missing_file(capfd):
    file_config = {
        "path": "non_existent_file.txt",
        "variable": "__version__",
    }
    version_format = "{current_date}-{build_count:03}"
    tz = "UTC"

    with mock.patch("src.bumpcalver.cli.get_current_date", return_value="2023-09-30"):
        new_version = get_build_version(file_config, version_format, timezone=tz)
        assert new_version == "2023-09-30-001"
        out, err = capfd.readouterr()
        assert "non_existent_file.txt not found" in out


# Test get_build_version() when version does not match expected format
def test_get_build_version_version_mismatch(capfd):
    # Create a temporary file with a version that doesn't match the pattern
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
        temp_file.write('__version__ = "v0.1.0"\n')
        temp_file_path = temp_file.name

    file_config = {
        "path": temp_file_path,
        "variable": "__version__",
    }
    version_format = "{current_date}-{build_count:03}"
    tz = "UTC"

    # Mock current date
    with mock.patch("src.bumpcalver.cli.get_current_date", return_value="2023-09-30"):
        new_version = get_build_version(file_config, version_format, timezone=tz)
        assert new_version == "2023-09-30-001"
        out, err = capfd.readouterr()
        assert f"Version in {temp_file_path} does not match expected format." in out

    os.remove(temp_file_path)


# Test get_build_version() when neither variable nor pattern is specified
def test_get_build_version_no_variable_or_pattern(capfd):
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
        temp_file.write("Some content without version variable\n")
        temp_file_path = temp_file.name

    file_config = {
        "path": temp_file_path,
        # Neither 'variable' nor 'pattern' is specified
    }
    version_format = "{current_date}-{build_count:03}"
    tz = "UTC"

    with mock.patch("src.bumpcalver.cli.get_current_date", return_value="2023-09-30"):
        new_version = get_build_version(file_config, version_format, timezone=tz)
        assert new_version == "2023-09-30-001"
        out, err = capfd.readouterr()
        assert f"No variable or pattern specified for file {temp_file_path}" in out

    os.remove(temp_file_path)


# Test update_version_in_files()
def test_update_version_in_files():
    # Create a temporary file to simulate the file to be updated
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
        temp_file.write('__version__ = "0.1.0"\n')
        temp_file_path = temp_file.name

    new_version = "2023-09-30-001"
    file_configs = [
        {
            "path": temp_file_path,
            "variable": "__version__",
        }
    ]

    updated_files = update_version_in_files(new_version, file_configs)

    # Verify the file content
    with open(temp_file_path, "r") as f:
        content = f.read()
        assert content.strip() == f'__version__ = "{new_version}"'

    assert os.path.relpath(temp_file_path) in updated_files

    os.remove(temp_file_path)


# Test update_version_in_files() with missing file
def test_update_version_in_files_missing_file(capfd):
    new_version = "2023-09-30-001"
    file_configs = [
        {
            "path": "non_existent_file.txt",
            "variable": "__version__",
        }
    ]

    updated_files = update_version_in_files(new_version, file_configs)
    assert updated_files == []
    out, err = capfd.readouterr()
    assert "non_existent_file.txt not found" in out


# Test update_version_in_files() with invalid pattern
def test_update_version_in_files_invalid_pattern():
    # Create a temporary file to simulate the file to be updated
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
        temp_file.write('__version__ = "0.1.0"\n')
        temp_file_path = temp_file.name

    new_version = "2023-09-30-001"
    file_configs = [
        {
            "path": temp_file_path,
            "pattern": r'__invalid__ = "(.*?)"',
        }
    ]

    updated_files = update_version_in_files(new_version, file_configs)

    # Verify the file content remains unchanged
    with open(temp_file_path, "r") as f:
        content = f.read()
        assert content.strip() == '__version__ = "0.1.0"'

    # Since no variable or pattern matched, file should not be in updated_files
    assert os.path.relpath(temp_file_path) not in updated_files

    os.remove(temp_file_path)


# Test update_version_in_files() when neither variable nor pattern is specified
def test_update_version_in_files_no_variable_or_pattern(capfd):
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
        temp_file.write("Some content without version variable\n")
        temp_file_path = temp_file.name

    new_version = "2023-09-30-001"
    file_configs = [
        {
            "path": temp_file_path,
            # Neither 'variable' nor 'pattern' is specified
        }
    ]

    updated_files = update_version_in_files(new_version, file_configs)
    assert updated_files == []
    out, err = capfd.readouterr()
    assert f"No variable or pattern specified for file {temp_file_path}" in out

    os.remove(temp_file_path)


# Test update_version_in_files() when an exception occurs
def test_update_version_in_files_exception(capfd):
    # Create a temporary file with read-only permissions
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
        temp_file.write('__version__ = "0.1.0"\n')
        temp_file_path = temp_file.name

    # Make the file read-only to cause a permission error
    os.chmod(temp_file_path, 0o444)

    new_version = "2023-09-30-001"
    file_configs = [
        {
            "path": temp_file_path,
            "variable": "__version__",
        }
    ]

    updated_files = update_version_in_files(new_version, file_configs)
    assert updated_files == []
    out, err = capfd.readouterr()
    assert "Error updating" in out

    # Reset permissions and remove the file
    os.chmod(temp_file_path, 0o666)
    os.remove(temp_file_path)


# Test load_config()
def test_load_config():
    # Create a temporary pyproject.toml
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
        temp_file.write(
            """
[tool.bumpcalver]
version_format = "{current_date}-{build_count:03}"
timezone = "UTC"
git_tag = true
auto_commit = true

[[tool.bumpcalver.file]]
path = "src/bumpcalver/__init__.py"
variable = "__version__"
"""
        )
        temp_file_path = temp_file.name

    # Mock os.path.exists to return True when checking for pyproject.toml
    with mock.patch("os.path.exists", return_value=True):
        # Mock open to read from our temp_file
        with mock.patch(
            "builtins.open", new=mock.mock_open(read_data=open(temp_file_path).read())
        ):
            config = load_config()
            assert config["version_format"] == "{current_date}-{build_count:03}"
            assert config["timezone"] == "UTC"
            assert config["git_tag"] is True
            assert config["auto_commit"] is True
            assert len(config["file_configs"]) == 1
            assert config["file_configs"][0]["path"] == "src/bumpcalver/__init__.py"
            assert config["file_configs"][0]["variable"] == "__version__"

    os.remove(temp_file_path)


# Test load_config() with missing pyproject.toml
def test_load_config_missing_pyproject():
    # Mock os.path.exists to return False when checking for pyproject.toml
    with mock.patch("os.path.exists", return_value=False):
        config = load_config()
        assert config == {}


def test_load_config_malformed_toml():
    # Create a temporary malformed pyproject.toml
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
        temp_file.write("""
[tool.bumpcalver
version_format = "{current_date}-{build_count:03"
""")
        temp_file_path = temp_file.name

    with mock.patch('os.path.exists', return_value=True):
        with mock.patch('builtins.open', new=mock.mock_open(read_data=open(temp_file_path).read())):
            with pytest.raises(toml.TomlDecodeError):
                load_config()

    os.remove(temp_file_path)


# Test create_git_tag()
def test_create_git_tag():
    version = "2023-09-30-001"
    files_to_commit = ["file1.txt", "file2.txt"]
    auto_commit = True

    with mock.patch("subprocess.run") as mock_run:
        create_git_tag(version, files_to_commit, auto_commit)

        # Check that subprocess.run was called with git commands
        calls = [
            mock.call(
                ["git", "rev-parse", "--is-inside-work-tree"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            ),
            mock.call(["git", "add"] + files_to_commit, check=True),
            mock.call(
                ["git", "commit", "-m", f"Bump version to {version}"], check=True
            ),
            mock.call(["git", "tag", version], check=True),
        ]
        mock_run.assert_has_calls(calls)


# Test create_git_tag() with auto_commit=False
def test_create_git_tag_no_auto_commit(capfd):
    version = "2023-09-30-001"
    files_to_commit = ["file1.txt", "file2.txt"]
    auto_commit = False

    with mock.patch("subprocess.run") as mock_run:
        create_git_tag(version, files_to_commit, auto_commit)

        # Check that subprocess.run was called with git commands
        calls = [
            mock.call(
                ["git", "rev-parse", "--is-inside-work-tree"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            ),
            mock.call(["git", "tag", version], check=True),
        ]
        mock_run.assert_has_calls(calls)

        out, err = capfd.readouterr()
        assert "Auto-commit is disabled. Tagging current commit." in out


# Test create_git_tag() when not in a Git repository
def test_create_git_tag_not_in_git_repo(capfd):
    version = "2023-09-30-001"
    files_to_commit = ["file1.txt", "file2.txt"]
    auto_commit = True

    with mock.patch(
        "subprocess.run", side_effect=[subprocess.CalledProcessError(1, "git")]
    ) as mock_run:
        create_git_tag(version, files_to_commit, auto_commit)

        # Check that subprocess.run was called with git commands
        mock_run.assert_called_once_with(
            ["git", "rev-parse", "--is-inside-work-tree"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        out, err = capfd.readouterr()
        assert "Not a Git repository. Skipping Git tagging." in out


# Test create_git_tag() with no files to commit
def test_create_git_tag_no_files_to_commit(capfd):
    version = "2023-09-30-001"
    files_to_commit = []
    auto_commit = True

    with mock.patch("subprocess.run") as mock_run:
        create_git_tag(version, files_to_commit, auto_commit)

        # Check that subprocess.run was called with git commands
        calls = [
            mock.call(
                ["git", "rev-parse", "--is-inside-work-tree"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            ),
            # Should still attempt to tag
            mock.call(["git", "tag", version], check=True),
        ]
        mock_run.assert_has_calls(calls)

        out, err = capfd.readouterr()
        assert "No files were updated. Skipping Git commit." in out


# Test create_git_tag() with subprocess.CalledProcessError during 'git add'
def test_create_git_tag_subprocess_error_during_add(capfd):
    version = "2023-09-30-001"
    files_to_commit = ["file1.txt"]
    auto_commit = True

    def side_effect(cmd, **kwargs):
        if "add" in cmd:
            raise subprocess.CalledProcessError(1, cmd)
        return mock.DEFAULT

    with mock.patch("subprocess.run", side_effect=side_effect) as mock_run:
        create_git_tag(version, files_to_commit, auto_commit)

        # Ensure that 'git add' was called and failed
        calls = [
            mock.call(
                ["git", "rev-parse", "--is-inside-work-tree"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            ),
            mock.call(["git", "add"] + files_to_commit, check=True),
        ]
        mock_run.assert_has_calls(calls)

        out, err = capfd.readouterr()
        assert "Error during Git operations:" in out


# Test create_git_tag() with subprocess.CalledProcessError during 'git commit'
def test_create_git_tag_subprocess_error_during_commit(capfd):
    version = "2023-09-30-001"
    files_to_commit = ["file1.txt"]
    auto_commit = True

    def side_effect(cmd, **kwargs):
        if "commit" in cmd:
            raise subprocess.CalledProcessError(1, cmd)
        return mock.DEFAULT

    with mock.patch("subprocess.run", side_effect=side_effect) as mock_run:
        create_git_tag(version, files_to_commit, auto_commit)

        # Ensure that 'git commit' was called and failed
        calls = [
            mock.call(
                ["git", "rev-parse", "--is-inside-work-tree"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            ),
            mock.call(["git", "add"] + files_to_commit, check=True),
            mock.call(
                ["git", "commit", "-m", f"Bump version to {version}"], check=True
            ),
        ]
        mock_run.assert_has_calls(calls)

        out, err = capfd.readouterr()
        assert "Error during Git operations:" in out


# Test create_git_tag() with subprocess.CalledProcessError during 'git tag'
def test_create_git_tag_subprocess_error_during_tag(capfd):
    version = "2023-09-30-001"
    files_to_commit = ["file1.txt"]
    auto_commit = True

    def side_effect(cmd, **kwargs):
        if "tag" in cmd:
            raise subprocess.CalledProcessError(1, cmd)
        return mock.DEFAULT

    with mock.patch("subprocess.run", side_effect=side_effect) as mock_run:
        create_git_tag(version, files_to_commit, auto_commit)

        # Ensure that 'git tag' was called and failed
        calls = [
            mock.call(
                ["git", "rev-parse", "--is-inside-work-tree"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            ),
            mock.call(["git", "add"] + files_to_commit, check=True),
            mock.call(
                ["git", "commit", "-m", f"Bump version to {version}"], check=True
            ),
            mock.call(["git", "tag", version], check=True),
        ]
        mock_run.assert_has_calls(calls)

        out, err = capfd.readouterr()
        assert "Error during Git operations:" in out


# Test main() function with no files specified
def test_main_no_files_specified():
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create an empty pyproject.toml
        with open("pyproject.toml", "w") as f:
            f.write(
                """
[tool.bumpcalver]
version_format = "{current_date}-{build_count:03}"
timezone = "UTC"
git_tag = true
auto_commit = true
"""
            )
        result = runner.invoke(main, ["--build"])
        assert result.exit_code == 0
        assert "No files specified in the configuration." in result.output


# Test main() function with various options
@pytest.mark.parametrize(
    "options, expected_version_prefix",
    [
        (["--build"], ""),  # Standard build
        (["--build", "--beta"], "beta-"),  # Beta versioning
        (["--build", "--timezone", "UTC"], ""),  # Specified timezone
        (["--build", "--git-tag"], ""),  # Force git tag
        (["--build", "--no-git-tag"], ""),  # Disable git tag
        (["--build", "--auto-commit"], ""),  # Force auto-commit
        (["--build", "--no-auto-commit"], ""),  # Disable auto-commit
    ],
)
def test_main_with_options(options, expected_version_prefix):
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create necessary files
        with open("pyproject.toml", "w") as f:
            f.write(
                """
[tool.bumpcalver]
version_format = "{current_date}-{build_count:03}"
timezone = "UTC"
git_tag = true
auto_commit = true

[[tool.bumpcalver.file]]
path = "version.py"
variable = "__version__"
"""
            )
        with open("version.py", "w") as f:
            f.write('__version__ = "0.1.0"\n')

        with mock.patch("src.bumpcalver.cli.create_git_tag") as mock_create_git_tag:
            result = runner.invoke(main, options)
            assert result.exit_code == 0
            assert "Updated version to " in result.output

            # Verify that the version was updated
            with open("version.py", "r") as f:
                content = f.read()
                expected_version = f'__version__ = "{expected_version_prefix}'
                assert expected_version in content

            # Check if create_git_tag was called based on options
            if "--no-git-tag" in options:
                mock_create_git_tag.assert_not_called()
            else:
                mock_create_git_tag.assert_called_once()


# Test main() function when pyproject.toml is missing
def test_main_pyproject_missing():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, ["--build"])
        assert result.exit_code == 0
        assert "No files specified in the configuration." in result.output


def test_main_pyproject_malformed():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("pyproject.toml", "w") as f:
            f.write(
                """
[tool.bumpcalver
version_format = "{current_date}-{build_count:03"
"""
            )
        result = runner.invoke(main, ["--build"], catch_exceptions=False)
        assert result.exit_code == 1
        assert "Error parsing pyproject.toml:" in result.output


# Test main() function with invalid timezone
def test_main_invalid_timezone():
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create pyproject.toml with invalid timezone
        with open("pyproject.toml", "w") as f:
            f.write(
                """
[tool.bumpcalver]
version_format = "{current_date}-{build_count:03}"
timezone = "Invalid/Timezone"

[[tool.bumpcalver.file]]
path = "version.py"
variable = "__version__"
"""
            )
        with open("version.py", "w") as f:
            f.write('__version__ = "0.1.0"\n')

        result = runner.invoke(main, ["--build"])
        assert result.exit_code == 0
        assert "Unknown timezone" in result.output
        assert "Updated version to " in result.output


def test_main_no_files_updated():
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create pyproject.toml with an invalid variable and git_tag = true
        with open("pyproject.toml", "w") as f:
            f.write(
                """
[tool.bumpcalver]
version_format = "{current_date}-{build_count:03}"
timezone = "UTC"
git_tag = true

[[tool.bumpcalver.file]]
path = "version.py"
variable = "__invalid__"
"""
            )
        with open("version.py", "w") as f:
            f.write('__version__ = "0.1.0"\n')

        with mock.patch("src.bumpcalver.cli.create_git_tag") as mock_create_git_tag:
            result = runner.invoke(main, ["--build"])
            assert result.exit_code == 0
            assert "Updated version to " in result.output

            # Check that create_git_tag() received an empty list
            mock_create_git_tag.assert_called_once()
            args, kwargs = mock_create_git_tag.call_args
            assert args[1] == []  # files_updated should be empty



# Test main() function with beta versioning
def test_main_beta_versioning():
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create necessary files
        with open("pyproject.toml", "w") as f:
            f.write(
                """
[tool.bumpcalver]
version_format = "{current_date}-{build_count:03}"
timezone = "UTC"

[[tool.bumpcalver.file]]
path = "version.py"
variable = "__version__"
"""
            )
        with open("version.py", "w") as f:
            f.write('__version__ = "0.1.0"\n')

        result = runner.invoke(main, ["--build", "--beta"])
        assert result.exit_code == 0
        assert "Updated version to beta-" in result.output

        # Verify that the version was updated
        with open("version.py", "r") as f:
            content = f.read()
            assert '__version__ = "beta-' in content
