# -*- coding: utf-8 -*-
from datetime import datetime
import re
import click
import os


def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")


def get_current_datetime_version():
    return datetime.now().strftime("%Y-%m-%d-%H%M")


def get_build_version(init_file):
    current_date = get_current_date()
    build_count = 1

    # Read the current version from the __init__.py file
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

    return f"{current_date}-{build_count:03}"


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


@click.command()
@click.option("--beta", is_flag=True, help="Use beta versioning")
@click.option("--build", is_flag=True, help="Use build count versioning")
def main(beta, build):
    # List of files to update
    base_dir = os.path.dirname(os.path.abspath(__file__))
    files_to_update = [
        os.path.join(base_dir, "../src/__init__.py"),
        os.path.join(base_dir, "../makefile"),
        # Add more file paths as needed
    ]

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
        new_version = get_build_version(init_file)
    else:
        new_version = get_current_datetime_version()

    if beta:
        new_version = "beta-" + new_version

    # Update the version in the specified files
    update_version_in_files(new_version, files_to_update)

    print(f"Updated version to {new_version} in specified files.")


if __name__ == "__main__":
    main()