import os
import sys
from typing import Any, Dict

import toml

from .utils import default_timezone, parse_dot_path


def load_config() -> Dict[str, Any]:
    config: Dict[str, Any] = {}

    config_file = None
    if os.path.exists("pyproject.toml"):
        config_file = "pyproject.toml"
    elif os.path.exists("bumpcalver.toml"):
        config_file = "bumpcalver.toml"

    if config_file:
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                loaded_config: Dict[str, Any] = toml.load(f)

            if config_file == "pyproject.toml":
                bumpcalver_config: Dict[str, Any] = loaded_config.get("tool", {}).get(
                    "bumpcalver", {}
                )
            else:
                bumpcalver_config: Dict[str, Any] = loaded_config

            config["version_format"] = bumpcalver_config.get(
                "version_format", "{current_date}-{build_count:03}"
            )
            config["timezone"] = bumpcalver_config.get("timezone", default_timezone)
            config["file_configs"] = bumpcalver_config.get("file", [])
            config["git_tag"] = bumpcalver_config.get("git_tag", False)
            config["auto_commit"] = bumpcalver_config.get("auto_commit", False)

            # Print paths for debugging
            for file_config in config["file_configs"]:
                original_path = file_config["path"]
                file_type = file_config.get("file_type", "")
                file_config["path"] = parse_dot_path(original_path, file_type)
                print(
                    f"Original path: {original_path} -> Converted path: {file_config['path']}"
                )

        except toml.TomlDecodeError as e:
            print(f"Error decoding {config_file}: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Error loading configuration from {config_file}: {e}", file=sys.stderr)
    else:
        print("No configuration file found. Please create either pyproject.toml or bumpcalver.toml.", file=sys.stderr)

    return config