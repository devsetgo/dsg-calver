import os
import re
from datetime import datetime
import click
import toml

def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

def get_current_datetime_version():
    return datetime.now().strftime("%Y-%m-%d-%H%M")

def get_build_version(file_config, version_format):
    current_date = get_current_date()
    build_count = 1

    file_path = file_config['path']
    variable = file_config.get('variable')
    pattern = file_config.get('pattern')

    # Read the current version from the file
    try:
        with open(file_path, "r") as file:
            content = file.read()

            # Construct the regex pattern to find the version
            if variable:
                version_pattern = re.compile(r'{}\s*=\s*["\'](?:beta-)?(\d{{4}}-\d{{2}}-\d{{2}})(?:-(\d{{3}}))?["\']'.format(re.escape(variable)))
            elif pattern:
                # Adjust pattern to capture date and build count
                version_pattern = re.compile(pattern)
            else:
                print(f"No variable or pattern specified for file {file_path}")
                return version_format.format(current_date=current_date, build_count=build_count)

            version_match = version_pattern.search(content)
            if version_match:
                # Extract last_date and last_count based on captured groups
                last_date = version_match.group(1)
                last_count = version_match.group(2)
                last_count = int(last_count or 0)
                if last_date == current_date:
                    build_count = last_count + 1
    except FileNotFoundError:
        print(f"{file_path} not found")

    return version_format.format(current_date=current_date, build_count=build_count)

def update_version_in_files(new_version, file_configs):
    for file_config in file_configs:
        file_path = file_config['path']
        variable = file_config.get('variable')
        pattern = file_config.get('pattern')

        # Construct the regex pattern
        if variable:
            # Match variable = "version" or 'version'
            version_pattern = re.compile(r'({}\s*=\s*["\'])(.*?)((?:["\']))'.format(re.escape(variable)))
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
                new_content = version_pattern.sub(r"\1" + new_version + r"\3", content)
            elif pattern:
                # Replace the captured group with new_version
                def replace_match(match):
                    old_version = match.group(1)
                    return match.group(0).replace(old_version, new_version)
                new_content = version_pattern.sub(replace_match, content)
            else:
                new_content = content  # No change
            with open(file_path, "w") as file:
                file.write(new_content)
            print(f"Updated {file_path}")
        except FileNotFoundError:
            print(f"{file_path} not found")
        except Exception as e:
            print(f"Error updating {file_path}: {e}")

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
    version_format = config.get("version_format", "{current_date}-{build_count:03}")
    file_configs = config.get("file", [])

    if not file_configs:
        print("No files specified in the configuration.")
        return

    # Adjust the base directory
    project_root = os.getcwd()
    # Update file paths to be absolute
    for file_config in file_configs:
        file_config['path'] = os.path.join(project_root, file_config['path'])

    # Get the new version
    if build:
        # Use the first file config for getting the build count
        init_file_config = file_configs[0]
        new_version = get_build_version(init_file_config, version_format)
    else:
        new_version = get_current_datetime_version()

    if beta:
        new_version = "beta-" + new_version

    # Update the version in the specified files
    update_version_in_files(new_version, file_configs)

    print(f"Updated version to {new_version} in specified files.")