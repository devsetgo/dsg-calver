"""
BumpCalver CLI.

This module provides a command-line interface for BumpCalver, a tool for calendar-based version bumping.
It allows users to update version strings in their project's files based on the current date and build count.
Additionally, it can create Git tags and commit changes automatically.

Functions:
    main: The main entry point for the CLI.

Example:
    To bump the version using the current date and build count:
        $ bumpcalver --build

    To create a beta version:
        $ bumpcalver --build --beta

    To use a specific timezone:
        $ bumpcalver --build --timezone Europe/London

    To bump the version, commit changes, and create a Git tag:
        $ bumpcalver --build --git-tag --auto-commit
"""

import os
import sys
from typing import Any, Dict, List, Optional

import click

from .config import load_config
from .git_utils import create_git_tag
from .handlers import update_version_in_files
from .utils import default_timezone, get_build_version, get_current_datetime_version


@click.command()
@click.option("--beta", is_flag=True, help="Add -beta to version")
@click.option("--rc", is_flag=True, help="Add -rc to version")
@click.option("--release", is_flag=True, help="Add -release to version")
@click.option("--custom", default=None, help="Add -<WhatEverYouWant> to version")
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
def main(
    beta: bool,
    rc: bool,
    build: bool,
    release: bool,
    custom: str,
    timezone: Optional[str],
    git_tag: Optional[bool],
    auto_commit: Optional[bool],
) -> None:
    selected_options = [beta, rc, release]
    if custom:
        selected_options.append(True)

    if sum(bool(option) for option in selected_options) > 1:
        raise click.UsageError(
            "Only one of --beta, --rc, --release, or --custom can be set at a time."
        )

    config: Dict[str, Any] = load_config()
    version_format: str = config.get(
        "version_format", "{current_date}-{build_count:03}"
    )
    date_format: str = config.get("date_format", "%Y.%m.%d")
    file_configs: List[Dict[str, Any]] = config.get("file_configs", [])
    config_timezone: str = config.get("timezone", default_timezone)
    config_git_tag: bool = config.get("git_tag", False)
    config_auto_commit: bool = config.get("auto_commit", False)

    if not file_configs:  # pragma: no cover
        print("No files specified in the configuration.")
        return

    timezone = timezone or config_timezone
    if git_tag is None:
        git_tag = config_git_tag
    if auto_commit is None:
        auto_commit = config_auto_commit

    project_root: str = os.getcwd()
    for file_config in file_configs:
        file_config["path"] = os.path.join(project_root, file_config["path"])

    try:
        if build:
            print("Build option is set. Calling get_build_version.")
            init_file_config: Dict[str, Any] = file_configs[0]
            new_version: str = get_build_version(
                init_file_config, version_format, timezone, date_format
            )
        else:
            print("Build option is not set. Calling get_current_datetime_version.")
            new_version = get_current_datetime_version(timezone, date_format)

        if beta:
            new_version += ".beta"
        elif rc:
            new_version += ".rc"
        elif release:
            new_version += ".release"
        elif custom:
            new_version += f".{custom}"

        print(f"Calling update_version_in_files with version: {new_version}")
        files_updated: List[str] = update_version_in_files(new_version, file_configs)
        print(f"Files updated: {files_updated}")

        if git_tag:
            create_git_tag(new_version, files_updated, auto_commit)

        print(f"Updated version to {new_version} in specified files.")
    except (ValueError, KeyError) as e:
        print(f"Error generating version: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
