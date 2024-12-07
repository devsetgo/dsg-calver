import os
from datetime import datetime
from unittest import mock

from src.bumpcalver.utils import get_build_version, get_current_datetime_version
from src.bumpcalver.handlers import update_version_in_files

# List of date formats to test
date_formats = [
    "%Y.%m.%d",  # Full year, month, and day
    "%y.%m.%d",  # Year without century, month, and day
    "%y.Q%q",    # Year and quarter
    "%y.%m",     # Year and month
    "%y.%j",     # Year and day of the year
    "%Y.%m.%d",  # Year without century, month, and day
    "%Y.Q%q",    # Year and quarter
    "%Y.%m",     # Year and month
    "%Y.%j",     # Year and day of the year
]

def test_all_date_formats_written_to_files():
    # Commented out the temporary directory handling
    # with tempfile.TemporaryDirectory() as temp_dir:
    temp_dir = "tests/test_files"
    os.makedirs(temp_dir, exist_ok=True)

    for date_format in date_formats:
        # Create a file in the specified directory
        temp_file_path = os.path.join(temp_dir, f"version_{date_format.replace('%', '')}.txt")
        with open(temp_file_path, "w") as temp_file:
            temp_file.write("__version__ = '0.0.0'\n")

        # Mock configuration
        mock_config = {
            "version_format": "{current_date}-{build_count:03}",
            "date_format": date_format,
            "file_configs": [
                {
                    "path": temp_file_path,
                    "file_type": "python",
                    "variable": "__version__",
                }
            ],
            "timezone": "America/New_York",
            "git_tag": False,
            "auto_commit": False,
        }

        # Mock the current date
        mock_date = datetime(2024, 12, 7)
        with mock.patch('src.bumpcalver.utils.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_date
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            # Generate the version string
            get_current_datetime_version(mock_config["timezone"], mock_config["date_format"])
            new_version = get_build_version(
                mock_config["file_configs"][0],
                mock_config["version_format"],
                mock_config["timezone"],
                mock_config["date_format"]
            )

            # Update the version in the file
            update_version_in_files(new_version, mock_config["file_configs"])

            # Verify the file content
            with open(temp_file_path, "r") as temp_file:
                content = temp_file.read()
                assert f"__version__ = '{new_version}'" in content

        # Commented out the temporary file cleanup
        # os.remove(temp_file_path)
