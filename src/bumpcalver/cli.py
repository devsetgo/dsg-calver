# -*- coding: utf-8 -*-
"""
bumpcalver.cli
==============

This module provides a command-line interface (CLI) for calendar-based version bumping.
It includes functions to get the current date and time in a specified timezone, generate
build versions, update version strings in specified files, load configuration from a
`pyproject.toml` file, and create Git tags.

Functions:
    get_current_date(timezone=default_timzone): Returns the current date in the specified timezone.
    get_current_datetime_version(timezone=default_timzone): Returns the current date and time in the specified timezone.
    get_build_version(file_config, version_format, timezone=default_timzone): Generates a build version based on the current date and build count.
    update_version_in_files(new_version, file_configs): Updates the version string in the specified files.
    load_config(): Loads the configuration from the `pyproject.toml` file.
    create_git_tag(version, files_to_commit, auto_commit): Creates a Git tag with the new version.
    main(beta, build, timezone, git_tag, auto_commit): CLI entry point for version bumping.

Usage:
    Run the CLI with the desired options to bump the version in the specified files and optionally create a Git tag.

Example:
    $ bumpcalver --build --timezone UTC --git-tag --auto-commit
"""
import os
import re
import subprocess
import sys  # Added to handle exit
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import click
import toml

default_timzone = "America/New_York"

def get_current_date(timezone: str = default_timzone) -> str:
    """
    Returns the current date in the specified timezone.

    Args:
        timezone (str): The timezone to use for date calculations. Defaults to "America/New_York".

    Returns:
        str: The current date in the format "YYYY-MM-DD".

    Raises:
        ZoneInfoNotFoundError: If the specified timezone is not found.
    """
    try:
        # Attempt to get the timezone information
        tz = ZoneInfo(timezone)
    except ZoneInfoNotFoundError:
        # If the timezone is not found, use the default timezone
        print(f"Unknown timezone '{timezone}'. Using default '{default_timzone}'.")
        tz = ZoneInfo(default_timzone)

    # Get the current date in the specified timezone
    return datetime.now(tz).strftime("%Y-%m-%d")


def get_current_datetime_version(timezone: str = default_timzone) -> str:
    """
    Returns the current date and time in the specified timezone.

    Args:
        timezone (str): The timezone to use for date and time calculations. Defaults to "America/New_York".

    Returns:
        str: The current date and time in the format "YYYY-MM-DD-HHMM".

    Raises:
        ZoneInfoNotFoundError: If the specified timezone is not found.
    """
    try:
        # Attempt to get the timezone information
        tz = ZoneInfo(timezone)
    except ZoneInfoNotFoundError:
        # If the timezone is not found, use the default timezone
        print(f"Unknown timezone '{timezone}'. Using default '{default_timzone}'.")
        tz = ZoneInfo(default_timzone)

    # Get the current date and time in the specified timezone
    return datetime.now(tz).strftime("%Y-%m-%d-%H%M")


def get_build_version(file_config: dict, version_format: str, timezone: str = default_timzone) -> str:
    """
    Generates a build version based on the current date and build count.

    Args:
        file_config (dict): Configuration for the file containing the version string.
            Expected keys are "path" (str), "variable" (str, optional), and "pattern" (str, optional).
        version_format (str): The format string for the version. It should contain placeholders
            for "current_date" and "build_count".
        timezone (str): The timezone to use for date calculations. Defaults to "America/New_York".

    Returns:
        str: The generated build version in the specified format.

    Raises:
        ValueError: If the version format is invalid.
        KeyError: If required keys are missing in the file configuration.
    """
    current_date = get_current_date(timezone)
    build_count = 1

    file_path = file_config["path"]
    variable = file_config.get("variable")
    pattern = file_config.get("pattern")

    try:
        # Read the current version from the file
        with open(file_path, "r") as file:
            content = file.read()

            # Construct the regex pattern to find the version
            if variable:
                version_pattern = re.compile(
                    r'\b{}\s*=\s*["\'](?:beta-)?(\d{{4}}-\d{{2}}-\d{{2}})(?:-([^\s"\'/]+))?["\']'.format(
                        re.escape(variable)
                    )
                )
            elif pattern:
                version_pattern = re.compile(pattern)
            else:
                print(f"No variable or pattern specified for file {file_path}")
                return version_format.format(
                    current_date=current_date, build_count=build_count
                )

            # Search for the version in the file content
            version_match = version_pattern.search(content)
            if version_match:
                # Extract last_date and last_count based on captured groups
                last_date = version_match.group(1)
                last_count = version_match.group(2)
                if last_date == current_date:
                    try:
                        last_count = int(last_count or 0)
                        build_count = last_count + 1
                    except ValueError:
                        print(
                            f"Warning: Invalid build count '{last_count}' in {file_path}. Resetting to 1."
                        )
                        build_count = 1
                else:
                    build_count = 1
            else:
                print(
                    f"Version in {file_path} does not match expected format. Starting new versioning."
                )
    except FileNotFoundError:
        print(f"{file_path} not found")

    # Return the formatted version string
    return version_format.format(current_date=current_date, build_count=build_count)


def update_version_in_files(new_version: str, file_configs: list[dict]) -> list[str]:
    """
    Updates the version string in the specified files.

    Args:
        new_version (str): The new version string to be set in the files.
        file_configs (list[dict]): A list of file configurations. Each configuration is a dictionary
            that should contain the key "path" (str) and optionally "variable" (str) or "pattern" (str).

    Returns:
        list[str]: A list of relative paths of the files that were updated.

    Raises:
        FileNotFoundError: If a specified file is not found.
        Exception: If an error occurs while updating a file.
    """
    files_updated = []
    for file_config in file_configs:
        file_path = file_config["path"]
        variable = file_config.get("variable")
        pattern = file_config.get("pattern")

        # Construct the regex pattern
        if variable:
            if file_path.endswith("pyproject.toml"):
                version_pattern = re.compile(
                    r'(\[project\]\s*.*?\b{}\s*=\s*["\'])(.*?)(["\'])'.format(re.escape(variable)),
                    re.DOTALL
                )
            else:
                version_pattern = re.compile(
                    r'(\b{}\s*=\s*["\'])(.*?)(["\'])'.format(re.escape(variable))
                )
        elif pattern:
            version_pattern = re.compile(pattern, re.DOTALL)
        else:
            print(f"No variable or pattern specified for file {file_path}")
            continue

        try:
            # Read the content of the file
            with open(file_path, "r") as file:
                content = file.read()

            # Substitute the new version
            if variable:
                def replace_match(match):
                    return f"{match.group(1)}{new_version}{match.group(3)}"
                new_content = version_pattern.sub(replace_match, content)
            elif pattern:
                # Replace the captured group with new_version
                def replace_match(match):
                    old_version = match.group(1)
                    return match.group(0).replace(old_version, new_version)
                new_content = version_pattern.sub(replace_match, content)
            else:
                new_content = content  # No change

            # Write the updated content back to the file if changes were made
            if new_content != content:
                with open(file_path, "w") as file:
                    file.write(new_content)
                print(f"Updated {file_path}")
                # Store relative paths for git commands
                relative_path = os.path.relpath(file_path, start=os.getcwd())
                files_updated.append(relative_path)
            else:
                print(f"No changes made to {file_path}")
        except FileNotFoundError:
            print(f"{file_path} not found")
        except Exception as e:
            print(f"Error updating {file_path}: {e}")
    return files_updated

def load_config() -> dict:
    """
    Loads the configuration from the `pyproject.toml` file.

    The configuration is expected to be under the `[tool.bumpcalver]` section in the `pyproject.toml` file.
    It includes settings for version format, timezone, file configurations, Git tagging, and auto-commit.

    Returns:
        dict: A dictionary containing the configuration settings. The keys include:
            - "version_format" (str): The format string for the version.
            - "timezone" (str): The timezone for date calculations.
            - "file_configs" (list[dict]): A list of file configurations.
            - "git_tag" (bool): Whether to create a Git tag with the new version.
            - "auto_commit" (bool): Whether to automatically commit changes when creating a Git tag.

    Raises:
        toml.TomlDecodeError: If there is an error parsing the `pyproject.toml` file.
    """
    config = {}
    if os.path.exists("pyproject.toml"):
        try:
            # Open and parse the pyproject.toml file
            with open("pyproject.toml", "r") as f:
                pyproject = toml.load(f)

            # Extract the bumpcalver configuration
            bumpcalver_config = pyproject.get("tool", {}).get("bumpcalver", {})
            config["version_format"] = bumpcalver_config.get(
                "version_format", "{current_date}-{build_count:03}"
            )
            config["timezone"] = bumpcalver_config.get("timezone", default_timzone)
            config["file_configs"] = bumpcalver_config.get("file", [])
            config["git_tag"] = bumpcalver_config.get("git_tag", False)
            config["auto_commit"] = bumpcalver_config.get("auto_commit", False)
        except toml.TomlDecodeError as e:
            print(f"Error parsing pyproject.toml: {e}")
            raise  # Re-raise the exception
    return config



def create_git_tag(version: str, files_to_commit: list[str], auto_commit: bool) -> None:
    """
    Creates a Git tag with the new version.

    This function checks if the current directory is a Git repository, optionally commits the updated files,
    and creates a Git tag with the specified version.

    Args:
        version (str): The new version string to be used as the Git tag.
        files_to_commit (list[str]): A list of relative paths of the files to be committed.
        auto_commit (bool): Whether to automatically commit the updated files before creating the Git tag.

    Raises:
        subprocess.CalledProcessError: If an error occurs during Git operations.
    """
    try:
        # Check if in a Git repository
        subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        print("Not a Git repository. Skipping Git tagging.")
        return

    try:
        if auto_commit:
            if files_to_commit:
                # Stage only the updated files
                subprocess.run(["git", "add"] + files_to_commit, check=True)
                # Commit changes
                commit_message = f"Bump version to {version}"
                subprocess.run(["git", "commit", "-m", commit_message], check=True)
            else:
                print("No files were updated. Skipping Git commit.")
        else:
            print("Auto-commit is disabled. Tagging current commit.")

        # Create Git tag
        subprocess.run(["git", "tag", version], check=True)
        print(f"Created Git tag '{version}'")
    except subprocess.CalledProcessError as e:
        print(f"Error during Git operations: {e}")


@click.command()
@click.option("--beta", is_flag=True, help="Use beta versioning")
@click.option("--build", is_flag=True, help="Use build count versioning")
@click.option(
    "--timezone",
    help="Timezone for date calculations (default: value from config or America/New_York)",
)
@click.option(
    "--git-tag/--no-git-tag", default=None, help="Create a Git tag with the new version"
)
@click.option(
    "--auto-commit/--no-auto-commit",
    default=None,
    help="Automatically commit changes when creating a Git tag",
)
def main(beta: bool, build: bool, timezone: str, git_tag: bool, auto_commit: bool) -> None:
    """
    CLI entry point for version bumping.

    This function handles the command-line options for version bumping, including beta versioning,
    build count versioning, timezone specification, Git tagging, and auto-commit. It loads the
    configuration from the `pyproject.toml` file, generates the new version, updates the version
    in the specified files, and optionally creates a Git tag.

    Args:
        beta (bool): Use beta versioning if True.
        build (bool): Use build count versioning if True.
        timezone (str): The timezone for date calculations. Defaults to the value from the config or "America/New_York".
        git_tag (bool): Create a Git tag with the new version if True.
        auto_commit (bool): Automatically commit changes when creating a Git tag if True.

    Raises:
        toml.TomlDecodeError: If there is an error parsing the `pyproject.toml` file.
        ValueError: If there is an error generating the version.
        KeyError: If required keys are missing in the configuration.
    """
    try:
        # Load configuration from pyproject.toml
        config = load_config()
    except toml.TomlDecodeError as e:
        print(f"Error parsing pyproject.toml: {e}")
        sys.exit(1)

    # Extract configuration values with defaults
    version_format = config.get("version_format", "{current_date}-{build_count:03}")
    file_configs = config.get("file_configs", [])
    config_timezone = config.get("timezone", default_timzone)
    config_git_tag = config.get("git_tag", False)
    config_auto_commit = config.get("auto_commit", False)

    if not file_configs:
        print("No files specified in the configuration.")
        return

    # Use the timezone from the command line if provided; otherwise, use config
    timezone = timezone or config_timezone

    # Determine whether to create a Git tag
    if git_tag is None:
        git_tag = config_git_tag

    # Determine whether to auto-commit changes
    if auto_commit is None:
        auto_commit = config_auto_commit

    # Adjust the base directory
    project_root = os.getcwd()
    # Update file paths to be absolute
    for file_config in file_configs:
        file_config["path"] = os.path.join(project_root, file_config["path"])

    try:
        # Get the new version
        if build:
            # Use the first file config for getting the build count
            init_file_config = file_configs[0]
            new_version = get_build_version(init_file_config, version_format, timezone)
        else:
            new_version = get_current_datetime_version(timezone)

        if beta:
            new_version = "beta-" + new_version

        # Update the version in the specified files
        files_updated = update_version_in_files(new_version, file_configs)

        # Create a Git tag if enabled
        if git_tag:
            create_git_tag(new_version, files_updated, auto_commit)

        print(f"Updated version to {new_version} in specified files.")
    except (ValueError, KeyError) as e:
        print(f"Error generating version: {e}")
        sys.exit(1)
