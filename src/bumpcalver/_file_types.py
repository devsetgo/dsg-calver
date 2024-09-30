"""
Module for reading version strings from various file types.

This module provides functions to read version strings from different types of files,
including Python files, TOML files, and Makefiles. Each function searches for a version
string assigned to a specified variable and returns the version string if found.

Functions:
    read_version_from_python_file(file_path: str, variable: str) -> Optional[str]:
        Reads the version string from a Python file.

    read_version_from_toml_file(file_path: str, section: str, variable: str) -> Optional[str]:
        Reads the version string from a TOML file.

    read_version_from_makefile(file_path: str, variable: str) -> Optional[str]:
        Reads the version string from a Makefile.
"""
import re
from typing import Optional

import toml


def read_version_from_python_file(file_path: str, variable: str) -> Optional[str]:
    """Read the version from a Python file.

    This function reads a specified Python file and searches for a version string
    assigned to a given variable. The version string is expected to be in the format:
    variable = "version" or variable = 'version'.

    Args:
        file_path (str): The path to the Python file.
        variable (str): The variable name to look for.

    Returns:
        Optional[str]: The version string if found, else None.
    """
    # Compile a regex pattern to match the version assignment in the Python file
    version_pattern = re.compile(
        rf'^\s*{re.escape(variable)}\s*=\s*["\'](.+?)["\']\s*$', re.MULTILINE
    )

    try:
        # Open the file and read its content
        with open(file_path, "r") as file:
            content = file.read()

        # Search for the version pattern in the file content
        match = version_pattern.search(content)

        if match:
            # If a match is found, return the version string
            return match.group(1)
        else:
            # If no match is found, return None
            return None
    except Exception as e:
        # Print an error message if an exception occurs
        print(f"Error reading version from {file_path}: {e}")
        return None


def read_version_from_toml_file(
    file_path: str, section: str, variable: str
) -> Optional[str]:
    """Read the version from a TOML file.

    This function reads a specified TOML file and searches for a version string
    within a given section and variable. The section can be nested, specified
    using dot notation (e.g., "tool.poetry").

    Args:
        file_path (str): The path to the TOML file.
        section (str): The section in the TOML file, which can be nested using dot notation.
        variable (str): The variable name to look for within the section.

    Returns:
        Optional[str]: The version string if found, else None.
    """
    try:
        # Open the TOML file and load its content
        with open(file_path, "r") as f:
            data = toml.load(f)

        # Navigate to the correct section
        sections = section.split(".")
        current_section = data
        for sec in sections:
            current_section = current_section.get(sec, {})

        # Get the version from the specified variable within the section
        version = current_section.get(variable)
        return version
    except Exception as e:
        # Print an error message if an exception occurs
        print(f"Error reading version from {file_path}: {e}")
        return None


def read_version_from_makefile(file_path: str, variable: str) -> Optional[str]:
    """Read the version from a Makefile.

    This function reads a specified Makefile and searches for a version string
    assigned to a given variable. The version string is expected to be in the format:
    variable = version or variable: version.

    Args:
        file_path (str): The path to the Makefile.
        variable (str): The variable name to look for.

    Returns:
        Optional[str]: The version string if found, else None.
    """
    # Compile a regex pattern to match the version assignment in the Makefile
    version_pattern = re.compile(
        rf"^\s*{re.escape(variable)}\s*[:]?=\s*(.+?)\s*$", re.MULTILINE
    )

    try:
        # Open the Makefile and read its content
        with open(file_path, "r") as file:
            content = file.read()

        # Search for the version pattern in the file content
        match = version_pattern.search(content)

        if match:
            # If a match is found, return the version string
            return match.group(1)
        else:
            # If no match is found, return None
            return None
    except Exception as e:
        # Print an error message if an exception occurs
        print(f"Error reading version from {file_path}: {e}")
        return None


def update_python_file(file_path: str, variable: str, new_version: str) -> bool:
    """Update the version variable in a Python file.

    This function updates the version string assigned to a specified variable
    in a given Python file. The version string is expected to be in the format:
    variable = "version" or variable = 'version'.

    Args:
        file_path (str): The path to the Python file.
        variable (str): The variable name to look for.
        new_version (str): The new version string to set.

    Returns:
        bool: True if the version was successfully updated, False otherwise.
    """
    # Compile a regex pattern to match the version assignment in the Python file
    version_pattern: re.Pattern = re.compile(
        rf'^(\s*{re.escape(variable)}\s*=\s*)(["\'])(.+?)(["\'])\s*$', re.MULTILINE
    )

    try:
        # Open the file and read its content
        with open(file_path, "r", encoding="utf-8") as file:
            content: str = file.read()

        # Define a replacement function to update the version string
        def replacement(match: re.Match) -> str:
            return f"{match.group(1)}{match.group(2)}{new_version}{match.group(4)}"

        # Substitute the old version with the new version in the file content
        new_content: str
        num_subs: int
        new_content, num_subs = version_pattern.subn(replacement, content)

        if num_subs > 0:
            # If substitutions were made, write the new content back to the file
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(new_content)
            print(f"Updated {file_path}")
            return True
        else:
            # If no substitutions were made, print a message and return False
            print(f"No version variable '{variable}' found in {file_path}")
            return False
    except Exception as e:
        # Print an error message if an exception occurs and return False
        print(f"Error updating {file_path}: {e}")
        return False


def update_toml_file(
    file_path: str, section: str, variable: str, new_version: str
) -> bool:
    """Update the version variable in a TOML file.

    This function updates the version string assigned to a specified variable
    within a given section in a TOML file. The section can be nested, specified
    using dot notation (e.g., "tool.poetry").

    Args:
        file_path (str): The path to the TOML file.
        section (str): The section in the TOML file, which can be nested using dot notation.
        variable (str): The variable name to look for within the section.
        new_version (str): The new version string to set.

    Returns:
        bool: True if the version was successfully updated, False otherwise.
    """
    try:
        # Open the TOML file and load its content
        with open(file_path, "r", encoding="utf-8") as f:
            data: dict = toml.load(f)

        # Navigate to the correct section
        sections: list[str] = section.split(".")
        current_section: dict = data
        for sec in sections:
            if sec not in current_section:
                # Print a message if the section is not found and return False
                print(f"Section '{section}' not found in {file_path}")
                return False
            current_section = current_section[sec]

        if variable in current_section:
            # Update the variable with the new version
            current_section[variable] = new_version
        else:
            # Print a message if the variable is not found and return False
            print(
                f"Variable '{variable}' not found in section '{section}' of {file_path}"
            )
            return False

        # Write the updated content back to the TOML file
        with open(file_path, "w", encoding="utf-8") as f:
            toml.dump(data, f)
        print(f"Updated {file_path}")
        return True
    except Exception as e:
        # Print an error message if an exception occurs and return False
        print(f"Error updating {file_path}: {e}")
        return False


def update_makefile(file_path: str, variable: str, new_version: str) -> bool:
    """Update the version variable in a Makefile.

    This function updates the version string assigned to a specified variable
    in a given Makefile. The version string is expected to be in the format:
    variable = version or variable: version.

    Args:
        file_path (str): The path to the Makefile.
        variable (str): The variable name to look for.
        new_version (str): The new version string to set.

    Returns:
        bool: True if the version was successfully updated, False otherwise.
    """
    # Compile a regex pattern to match the version assignment in the Makefile
    version_pattern: re.Pattern = re.compile(
        rf"^(\s*{re.escape(variable)}\s*[:]?=\s*)(.+?)\s*$", re.MULTILINE
    )

    try:
        # Open the Makefile and read its content
        with open(file_path, "r", encoding="utf-8") as file:
            content: str = file.read()

        # Define a replacement function to update the version string
        def replacement(match: re.Match) -> str:
            return f"{match.group(1)}{new_version}"

        # Substitute the old version with the new version in the file content
        new_content: str
        num_subs: int
        new_content, num_subs = version_pattern.subn(replacement, content)

        if num_subs > 0:
            # If substitutions were made, write the new content back to the file
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(new_content)
            print(f"Updated {file_path}")
            return True
        else:
            # If no substitutions were made, print a message and return False
            print(f"No variable '{variable}' found in {file_path}")
            return False
    except Exception as e:
        # Print an error message if an exception occurs and return False
        print(f"Error updating {file_path}: {e}")
        return False


def update_dockerfile(file_path: str, new_version: str) -> bool:
    """Update the version in a Dockerfile.

    This function updates the version string in a Dockerfile. It looks for the version
    in LABEL and ENV instructions and replaces it with the new version.

    Args:
        file_path (str): The path to the Dockerfile.
        new_version (str): The new version string to set.

    Returns:
        bool: True if the version was successfully updated, False otherwise.
    """
    # Compile a regex pattern to match the LABEL version in the Dockerfile
    version_pattern: re.Pattern = re.compile(
        r'^(LABEL\s+version\s*=\s*["\'])(.+?)(["\'])\s*$', re.MULTILINE
    )
    # Compile a regex pattern to match the ENV VERSION in the Dockerfile
    env_pattern: re.Pattern = re.compile(r"^(ENV\s+VERSION\s+)(.+?)\s*$", re.MULTILINE)

    try:
        # Open the Dockerfile and read its content
        with open(file_path, "r", encoding="utf-8") as file:
            content: str = file.read()

        new_content: str = content
        num_subs: int = 0

        # Define a replacement function to update the LABEL version
        def label_replacement(match: re.Match) -> str:
            return f"{match.group(1)}{new_version}{match.group(3)}"

        # Substitute the old LABEL version with the new version in the file content
        new_content, subs = version_pattern.subn(label_replacement, new_content)
        num_subs += subs

        # Define a replacement function to update the ENV VERSION
        def env_replacement(match: re.Match) -> str:
            return f"{match.group(1)}{new_version}"

        # Substitute the old ENV VERSION with the new version in the file content
        new_content, subs = env_pattern.subn(env_replacement, new_content)
        num_subs += subs

        if num_subs > 0:
            # If substitutions were made, write the new content back to the file
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(new_content)
            print(f"Updated {file_path}")
            return True
        else:
            # If no substitutions were made, print a message and return False
            print(f"No version label or ENV found in {file_path}")
            return False
    except Exception as e:
        # Print an error message if an exception occurs and return False
        print(f"Error updating {file_path}: {e}")
        return False

