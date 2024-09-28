# src/bumpcalver/cli.py

import os
import re
import subprocess
import sys  # Added to handle exit
from datetime import datetime

import click
import pytz
import toml


def get_current_date(timezone="America/New_York"):
    try:
        tz = pytz.timezone(timezone)
    except pytz.UnknownTimeZoneError:
        print(f"Unknown timezone '{timezone}'. Using default 'America/New_York'.")
        tz = pytz.timezone("America/New_York")
    return datetime.now(tz).strftime("%Y-%m-%d")


def get_current_datetime_version(timezone="America/New_York"):
    try:
        tz = pytz.timezone(timezone)
    except pytz.UnknownTimeZoneError:
        print(f"Unknown timezone '{timezone}'. Using default 'America/New_York'.")
        tz = pytz.timezone("America/New_York")
    return datetime.now(tz).strftime("%Y-%m-%d-%H%M")


def get_build_version(file_config, version_format, timezone="America/New_York"):
    current_date = get_current_date(timezone)
    build_count = 1

    file_path = file_config["path"]
    variable = file_config.get("variable")
    pattern = file_config.get("pattern")

    # Read the current version from the file
    try:
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

    return version_format.format(current_date=current_date, build_count=build_count)


def update_version_in_files(new_version, file_configs):
    files_updated = []
    for file_config in file_configs:
        file_path = file_config["path"]
        variable = file_config.get("variable")
        pattern = file_config.get("pattern")

        # Construct the regex pattern
        if variable:
            version_pattern = re.compile(
                r'(\b{}\s*=\s*["\'])(.*?)(["\'])'.format(re.escape(variable))
            )
        elif pattern:
            version_pattern = re.compile(pattern)
        else:
            print(f"No variable or pattern specified for file {file_path}")
            continue

        try:
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


def load_config():
    config = {}
    if os.path.exists("pyproject.toml"):
        try:
            with open("pyproject.toml", "r") as f:
                pyproject = toml.load(f)
            bumpcalver_config = pyproject.get("tool", {}).get("bumpcalver", {})
            config["version_format"] = bumpcalver_config.get(
                "version_format", "{current_date}-{build_count:03}"
            )
            config["timezone"] = bumpcalver_config.get("timezone", "America/New_York")
            config["file_configs"] = bumpcalver_config.get("file", [])
            config["git_tag"] = bumpcalver_config.get("git_tag", False)
            config["auto_commit"] = bumpcalver_config.get("auto_commit", False)
        except toml.TomlDecodeError as e:
            print(f"Error parsing pyproject.toml: {e}")
            raise  # Re-raise the exception
    return config


def create_git_tag(version, files_to_commit, auto_commit):
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
def main(beta, build, timezone, git_tag, auto_commit):
    try:
        config = load_config()
    except toml.TomlDecodeError as e:
        print(f"Error parsing pyproject.toml: {e}")
        sys.exit(1)
    version_format = config.get("version_format", "{current_date}-{build_count:03}")
    file_configs = config.get("file_configs", [])
    config_timezone = config.get("timezone", "America/New_York")
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
