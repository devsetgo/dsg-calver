# src/bumpcalver/cli.py

import os
import re
from datetime import datetime
import click
import toml

def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

def get_current_datetime_version():
    return datetime.now().strftime("%Y-%m-%d-%H%M")

def get_build_version(init_file, version_format):
    current_date = get_current_date()
    build_count = 1

    # Read the current version from the file
    try:
        with open(init_file, "r") as file:
            content = file.read()
            version_match = re.search(
                r'__version__\s*=\s*["\'](?:beta-)?(\d{4}-\d{2}-\d{2})-(\d{3})["\']',
                content,
            )
            if version_match:
                last_date, last_count = version_match.groups()
                last_count = int(last_count)
                if last_date == current_date:
                    build_count = last_count + 1
    except FileNotFoundError:
        print(f"{init_file} not found")

    return version_format.format(current_date=current_date, build_count=build_count)

def update_version_in_files(new_version, files):
    version_pattern = re.compile(r'(__version__\s*=\s*["\'])(.*?)(["\'])')
    for file_path in files:
        try:
            with open(file_path, "r") as file:
                content = file.read()
            new_content = version_pattern.sub(r"\g<1>" + new_version + r"\3", content)
            with open(file_path, "w") as file:
                file.write(new_content)
        except FileNotFoundError:
            print(f"{file_path} not found")

def load_config():
    if os.path.exists("pyproject.toml"):
        with open("pyproject.toml", "r") as f:
            config = toml.load(f)
        return config.get("tool", {}).get("bumpcalver", {})
    return {}

@click.command()
@click.option("--beta", is_flag=True, help="Use beta versioning")
@click.option("--build", is_flag=True, help="Use build count versioning")
def main(beta, build):
    config = load_config()
    files_to_update = config.get("files", ["src/__init__.py"])
    version_format = config.get("version_format", "{current_date}-{build_count:03}")

    # Adjust the base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(base_dir, "..", ".."))
    files_to_update = [os.path.join(project_root, f) for f in files_to_update]

    # Check if any of the files exist
    init_file = None
    for file_path in files_to_update:
        if os.path.exists(file_path):
            init_file = file_path
            break

    if not init_file:
        print("None of the specified files were found.")
        return

    # Get the new version
    if build:
        new_version = get_build_version(init_file, version_format)
    else:
        new_version = get_current_datetime_version()

    if beta:
        new_version = "beta-" + new_version

    # Update the version in the specified files
    update_version_in_files(new_version, files_to_update)

    print(f"Updated version to {new_version} in specified files.")
