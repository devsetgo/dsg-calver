# src/bumpcalver/cli.py

import logging
import os
import re
import subprocess
import sys
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import click
import toml

logger = logging.getLogger(__name__)

default_timezone = "America/New_York"


def get_current_date(timezone=default_timezone):
    try:
        tz = ZoneInfo(timezone)
    except ZoneInfoNotFoundError:
        print(f"Unknown timezone '{timezone}'. Using default '{default_timezone}'.")
        tz = ZoneInfo(default_timezone)
    return datetime.now(tz).strftime("%Y-%m-%d")


def get_current_datetime_version(timezone=default_timezone):
    try:
        tz = ZoneInfo(timezone)
    except ZoneInfoNotFoundError:
        print(f"Unknown timezone '{timezone}'. Using default '{default_timezone}'.")
        tz = ZoneInfo(default_timezone)
    return datetime.now(tz).strftime("%Y-%m-%d-%H%M")


def parse_version(version):
    pattern = re.compile(r"(?:beta-)?(\d{4}-\d{2}-\d{2})(?:-(\d+))?")
    match = pattern.match(version)
    if match:
        last_date = match.group(1)
        last_count = int(match.group(2) or 0)
        return last_date, last_count
    else:
        print(f"Version '{version}' does not match expected format.")
        return None, None


def read_version_from_python_file(file_path, variable):
    version_pattern = re.compile(
        rf'^\s*{re.escape(variable)}\s*=\s*["\'](.+?)["\']\s*$', re.MULTILINE
    )
    try:
        with open(file_path, "r") as file:
            content = file.read()
        match = version_pattern.search(content)
        if match:
            return match.group(1)
        else:
            return None
    except Exception as e:
        print(f"Error reading version from {file_path}: {e}")
        return None


def read_version_from_toml_file(file_path, section, variable):
    try:
        with open(file_path, "r") as f:
            data = toml.load(f)
        # Navigate to the correct section
        sections = section.split(".")
        current_section = data
        for sec in sections:
            current_section = current_section.get(sec, {})
        version = current_section.get(variable)
        return version
    except Exception as e:
        print(f"Error reading version from {file_path}: {e}")
        return None


def read_version_from_makefile(file_path, variable):
    version_pattern = re.compile(
        rf"^\s*{re.escape(variable)}\s*[:]?=\s*(.+?)\s*$", re.MULTILINE
    )
    try:
        with open(file_path, "r") as file:
            content = file.read()
        match = version_pattern.search(content)
        if match:
            return match.group(1)
        else:
            return None
    except Exception as e:
        print(f"Error reading version from {file_path}: {e}")
        return None


def get_build_version(file_config, version_format, timezone=default_timezone):
    current_date = get_current_date(timezone)
    build_count = 1
    file_path = file_config["path"]
    file_type = file_config.get("file_type")
    variable = file_config.get("variable")

    try:
        if file_type == "python":
            version = read_version_from_python_file(file_path, variable)
        elif file_type == "toml":
            section = file_config.get("section")
            version = read_version_from_toml_file(file_path, section, variable)
        elif file_type == "makefile":
            version = read_version_from_makefile(file_path, variable)
        # Add more file types as needed
        else:
            logger.warning(f"Unsupported file type '{file_type}' for build version.")
            version = None

        if version:
            last_date, last_count = parse_version(version)
            if last_date == current_date:
                try:
                    build_count = int(last_count) + 1
                except ValueError:
                    logger.warning(
                        f"Warning: Invalid build count '{last_count}' in {file_path}. Resetting to 1."
                    )
                    build_count = 1
            else:
                build_count = 1
        else:
            logger.warning(
                f"Could not read version from {file_path}. Starting new versioning."
            )
    except Exception as e:
        logger.error(f"Error reading version from {file_path}: {e}")
        build_count = 1

    return version_format.format(current_date=current_date, build_count=build_count)


def update_python_file(file_path, variable, new_version):
    version_pattern = re.compile(
        rf'^(\s*{re.escape(variable)}\s*=\s*)(["\'])(.+?)(["\'])\s*$', re.MULTILINE
    )
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        def replacement(match):
            return f"{match.group(1)}{match.group(2)}{new_version}{match.group(4)}"

        new_content, num_subs = version_pattern.subn(replacement, content)

        if num_subs > 0:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(new_content)
            print(f"Updated {file_path}")
            return True
        else:
            print(f"No version variable '{variable}' found in {file_path}")
            return False
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False


def update_toml_file(file_path, section, variable, new_version):
    try:
        with open(file_path, "r") as f:
            data = toml.load(f)

        # Navigate to the correct section
        sections = section.split(".")
        current_section = data
        for sec in sections:
            if sec not in current_section:
                print(f"Section '{section}' not found in {file_path}")
                return False
            current_section = current_section[sec]

        if variable in current_section:
            current_section[variable] = new_version
        else:
            print(
                f"Variable '{variable}' not found in section '{section}' of {file_path}"
            )
            return False

        with open(file_path, "w") as f:
            toml.dump(data, f)
        print(f"Updated {file_path}")
        return True
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False


def update_makefile(file_path, variable, new_version):
    version_pattern = re.compile(
        rf"^(\s*{re.escape(variable)}\s*[:]?=\s*)(.+?)\s*$", re.MULTILINE
    )
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        def replacement(match):
            return f"{match.group(1)}{new_version}"

        new_content, num_subs = version_pattern.subn(replacement, content)

        if num_subs > 0:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(new_content)
            print(f"Updated {file_path}")
            return True
        else:
            print(f"No variable '{variable}' found in {file_path}")
            return False
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False


def update_dockerfile(file_path, new_version):
    version_pattern = re.compile(
        r'^(LABEL\s+version\s*=\s*["\'])(.+?)(["\'])\s*$', re.MULTILINE
    )
    env_pattern = re.compile(r"^(ENV\s+VERSION\s+)(.+?)\s*$", re.MULTILINE)
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        new_content = content
        num_subs = 0

        # Try updating LABEL version
        def label_replacement(match):
            return f"{match.group(1)}{new_version}{match.group(3)}"

        new_content, subs = version_pattern.subn(label_replacement, new_content)
        num_subs += subs

        # Try updating ENV VERSION
        def env_replacement(match):
            return f"{match.group(1)}{new_version}"

        new_content, subs = env_pattern.subn(env_replacement, new_content)
        num_subs += subs

        if num_subs > 0:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(new_content)
            print(f"Updated {file_path}")
            return True
        else:
            print(f"No version label or ENV found in {file_path}")
            return False
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False


def update_version_in_files(new_version, file_configs):
    files_updated = []
    for file_config in file_configs:
        file_path = file_config["path"]
        file_type = file_config.get("file_type")
        if not file_type:
            print(f"No file_type specified for {file_path}")
            continue

        success = False

        if file_type == "python":
            variable = file_config.get("variable")
            if not variable:
                print(f"No variable specified for Python file {file_path}")
                continue
            success = update_python_file(file_path, variable, new_version)
        elif file_type == "toml":
            section = file_config.get("section")
            variable = file_config.get("variable")
            if not section or not variable:
                print(
                    f"Section and variable must be specified for TOML file {file_path}"
                )
                continue
            success = update_toml_file(file_path, section, variable, new_version)
        elif file_type == "makefile":
            variable = file_config.get("variable")
            if not variable:
                print(f"No variable specified for Makefile {file_path}")
                continue
            success = update_makefile(file_path, variable, new_version)
        elif file_type == "dockerfile":
            success = update_dockerfile(file_path, new_version)
        else:
            print(f"Unsupported file type '{file_type}' for {file_path}")
            continue

        if success:
            # Store relative paths for git commands
            relative_path = os.path.relpath(file_path, start=os.getcwd())
            files_updated.append(relative_path)
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
            config["timezone"] = bumpcalver_config.get("timezone", default_timezone)
            config["file_configs"] = bumpcalver_config.get("file", [])
            config["git_tag"] = bumpcalver_config.get("git_tag", False)
            config["auto_commit"] = bumpcalver_config.get("auto_commit", False)
        except toml.TomlDecodeError as e:
            print(f"Error parsing pyproject.toml: {e}")
            sys.exit(1)
    else:
        print("pyproject.toml not found. Using default configuration.")
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
    config = load_config()
    version_format = config.get("version_format", "{current_date}-{build_count:03}")
    file_configs = config.get("file_configs", [])
    config_timezone = config.get("timezone", default_timezone)
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


if __name__ == "__main__":
    main()
