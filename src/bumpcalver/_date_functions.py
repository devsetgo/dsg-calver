import logging
import re
from datetime import datetime
from typing import Dict, Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from bumpcalver._file_types import (
    read_version_from_makefile,
    read_version_from_python_file,
    read_version_from_toml_file,
)

default_timezone: str = "America/New_York"


def parse_version(version: str) -> tuple[str, int]:
    """Parse a version string.

    This function parses a version string that may include a 'beta-' prefix, a date in 'YYYY-MM-DD' format,
    and an optional count. It returns the date and the count as a tuple. If the version string does not match
    the expected format, it returns (None, None).

    Args:
        version (str): The version string to parse.

    Returns:
        tuple[str, int]: A tuple containing the date as a string and the count as an integer. If the version
                         string does not match the expected format, it returns (None, None).
    """
    # Compile the regex pattern to match the version string
    pattern = re.compile(r"(?:beta-)?(\d{4}-\d{2}-\d{2})(?:-(\d+))?")

    # Match the version string against the pattern
    match = pattern.match(version)

    if match:
        # Extract the date and count from the match groups
        last_date = match.group(1)
        last_count = int(match.group(2) or 0)
        return last_date, last_count
    else:
        # Print a message if the version string does not match the expected format
        print(f"Version '{version}' does not match expected format.")
        return None, None


def get_current_date(timezone: str = default_timezone) -> str:
    """Get the current date in a specified timezone.

    This function returns the current date formatted as 'YYYY-MM-DD' in the specified timezone.
    If the specified timezone is not found, it defaults to 'America/New_York'.

    Args:
        timezone (str): The timezone to use. Defaults to 'America/New_York'.

    Returns:
        str: The current date in the specified timezone formatted as 'YYYY-MM-DD'.
    """
    try:
        # Attempt to get the specified timezone
        tz = ZoneInfo(timezone)
    except ZoneInfoNotFoundError:
        # If the timezone is not found, print a message and use the default timezone
        print(f"Unknown timezone '{timezone}'. Using default '{default_timezone}'.")
        tz = ZoneInfo(default_timezone)

    # Get the current date in the specified timezone and format it as 'YYYY-MM-DD'
    return datetime.now(tz).strftime("%Y-%m-%d")


def get_current_datetime_version(timezone: str = default_timezone) -> str:
    """Get the current datetime version in a specified timezone.

    This function returns the current datetime formatted as 'YYYY-MM-DD-HHMM' in the specified timezone.
    If the specified timezone is not found, it defaults to 'America/New_York'.

    Args:
        timezone (str): The timezone to use. Defaults to 'America/New_York'.

    Returns:
        str: The current datetime in the specified timezone formatted as 'YYYY-MM-DD-HHMM'.
    """
    try:
        # Attempt to get the specified timezone
        tz = ZoneInfo(timezone)
    except ZoneInfoNotFoundError:
        # If the timezone is not found, print a message and use the default timezone
        print(f"Unknown timezone '{timezone}'. Using default '{default_timezone}'.")
        tz = ZoneInfo(default_timezone)

    # Get the current datetime in the specified timezone and format it as 'YYYY-MM-DD-HHMM'
    return datetime.now(tz).strftime("%Y-%m-%d-%H%M")


def get_build_version(
    file_config: Dict[str, Optional[str]],
    version_format: str,
    timezone: str = default_timezone,
) -> str:
    """Get the build version based on the configuration and format.

    This function reads the version from a specified file, determines the build count
    for the current date, and returns the build version formatted according to the
    provided version format.

    Args:
        file_config (Dict[str, Optional[str]]): The file configuration containing:
            - path (str): The path to the file.
            - file_type (Optional[str]): The type of the file (e.g., 'python', 'toml', 'makefile').
            - variable (Optional[str]): The variable name to look for in the file.
            - section (Optional[str]): The section in the TOML file (if applicable).
        version_format (str): The format string for the version.
        timezone (str): The timezone to use for the current date. Defaults to 'America/New_York'.

    Returns:
        str: The formatted build version.
    """
    # Get the current date in the specified timezone
    current_date: str = get_current_date(timezone)
    build_count: int = 1  # Initialize build count to 1
    file_path: str = file_config["path"]
    file_type: Optional[str] = file_config.get("file_type")
    variable: Optional[str] = file_config.get("variable")

    try:
        # Read the version from the specified file type
        if file_type == "python":
            version: Optional[str] = read_version_from_python_file(file_path, variable)
        elif file_type == "toml":
            section: Optional[str] = file_config.get("section")
            version = read_version_from_toml_file(file_path, section, variable)
        elif file_type == "makefile":
            version = read_version_from_makefile(file_path, variable)
        # Add more file types as needed
        else:
            logging.warning(f"Unsupported file type '{file_type}' for build version.")
            version = None

        if version:
            # Parse the version to get the last date and count
            last_date: Optional[str]
            last_count: Optional[int]
            last_date, last_count = parse_version(version)
            if last_date == current_date:
                try:
                    # Increment the build count if the date matches the current date
                    build_count = int(last_count) + 1
                except ValueError:
                    logging.warning(
                        f"Warning: Invalid build count '{last_count}' in {file_path}. Resetting to 1."
                    )
                    build_count = 1
            else:
                build_count = 1
        else:
            logging.warning(
                f"Could not read version from {file_path}. Starting new versioning."
            )
    except Exception as e:
        logging.error(f"Error reading version from {file_path}: {e}")
        build_count = 1

    # Return the formatted build version
    return version_format.format(current_date=current_date, build_count=build_count)
