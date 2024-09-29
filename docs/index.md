Python:

[![PyPI version fury.io](https://badge.fury.io/py/devsetgo-lib.svg)](https://pypi.python.org/pypi/devsetgo-lib/)
[![Downloads](https://static.pepy.tech/badge/devsetgo-lib)](https://pepy.tech/project/devsetgo-lib)
[![Downloads](https://static.pepy.tech/badge/devsetgo-lib/month)](https://pepy.tech/project/devsetgo-lib)
[![Downloads](https://static.pepy.tech/badge/devsetgo-lib/week)](https://pepy.tech/project/devsetgo-lib)

Support Python Versions

![Static Badge](https://img.shields.io/badge/Python-3.12%20%7C%203.11%20%7C%203.10%20%7C%203.9-blue)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

CI/CD Pipeline:

[![Testing - Main](https://github.com/devsetgo/devsetgo_lib/actions/workflows/testing.yml/badge.svg?branch=main)](https://github.com/devsetgo/devsetgo_lib/actions/workflows/testing.yml)
[![Testing - Dev](https://github.com/devsetgo/devsetgo_lib/actions/workflows/testing.yml/badge.svg?branch=dev)](https://github.com/devsetgo/devsetgo_lib/actions/workflows/testing.yml)

SonarCloud:

[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=devsetgo_devsetgo_lib&metric=coverage)](https://sonarcloud.io/dashboard?id=devsetgo_devsetgo_lib)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=devsetgo_devsetgo_lib&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=devsetgo_devsetgo_lib)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=devsetgo_devsetgo_lib&metric=alert_status)](https://sonarcloud.io/dashboard?id=devsetgo_devsetgo_lib)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=devsetgo_devsetgo_lib&metric=reliability_rating)](https://sonarcloud.io/dashboard?id=devsetgo_devsetgo_lib)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=devsetgo_devsetgo_lib&metric=vulnerabilities)](https://sonarcloud.io/dashboard?id=devsetgo_devsetgo_lib)



# BumpCalver CLI Documentation

## Overview

The **BumpCalver CLI** is a command-line interface for calendar-based version bumping. It automates the process of updating version strings in your project's files based on the current date and build count. Additionally, it can create Git tags and commit changes automatically. The CLI is highly configurable via a `pyproject.toml` file and supports various customization options to fit your project's needs.

---

## Table of Contents

- [Installation](#installation)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
  - [Example Configuration](#example-configuration)
- [Command-Line Usage](#command-line-usage)
  - [Options](#options)
- [Functions](#functions)
  - [`get_current_date()`](#get_current_date)
  - [`get_current_datetime_version()`](#get_current_datetime_version)
  - [`get_build_version()`](#get_build_version)
  - [`update_version_in_files()`](#update_version_in_files)
  - [`load_config()`](#load_config)
  - [`create_git_tag()`](#create_git_tag)
  - [`main()`](#main)
- [Examples](#examples)
- [Error Handling](#error-handling)
- [License](#license)

---

## Installation

To install the BumpCalver CLI, you can add it to your project's dependencies. If it's packaged as a Python module, you might install it via:

```bash
pip install bumpcalver
```

*Note: Replace the installation command with the actual method based on how the package is distributed.*

---

## Getting Started

1. **Configure Your Project**: Create or update the `pyproject.toml` file in your project's root directory to include the `[tool.bumpcalver]` section with your desired settings.

2. **Run the CLI**: Use the `bumpcalver` command with appropriate options to bump your project's version.

Example:

```bash
bumpcalver --build --git-tag --auto-commit
```

---

## Configuration

The BumpCalver CLI relies on a `pyproject.toml` configuration file located at the root of your project. This file specifies how versioning should be handled, which files to update, and other settings.

### Configuration Options

- `version_format` (string): Format string for the version. Should include `{current_date}` and `{build_count}` placeholders.
- `timezone` (string): Timezone for date calculations (e.g., `UTC`, `America/New_York`).
- `file` (list of tables): Specifies which files to update and how to find the version string.
  - `path` (string): Path to the file to be updated.
  - `variable` (string, optional): The variable name that holds the version string in the file.
  - `pattern` (string, optional): A regex pattern to find the version string.
- `git_tag` (boolean): Whether to create a Git tag with the new version.
- `auto_commit` (boolean): Whether to automatically commit changes when creating a Git tag.

### Example Configuration

```toml
[tool.bumpcalver]
version_format = "{current_date}-{build_count:03}"
timezone = "UTC"
git_tag = true
auto_commit = true

[[tool.bumpcalver.file]]
path = "version.py"
variable = "__version__"
```

---

## Command-Line Usage

The CLI provides several options to customize the version bumping process.

```bash
Usage: bumpcalver [OPTIONS]

Options:
  --beta                      Use beta versioning.
  --build                     Use build count versioning.
  --timezone TEXT             Timezone for date calculations (default: value
                              from config or America/New_York).
  --git-tag / --no-git-tag    Create a Git tag with the new version.
  --auto-commit / --no-auto-commit
                              Automatically commit changes when creating a Git
                              tag.
  --help                      Show this message and exit.
```

### Options

- `--beta`: Prefixes the version with `beta-`.
- `--build`: Increments the build count based on the current date.
- `--timezone`: Overrides the timezone specified in the configuration.
- `--git-tag` / `--no-git-tag`: Forces Git tagging on or off, overriding the configuration.
- `--auto-commit` / `--no-auto-commit`: Forces auto-commit on or off, overriding the configuration.

---
## Support

For issues or questions, please contact [support@example.com](mailto:support@example.com) or open an issue on the project's repository.

---

*Note: Replace placeholder texts like support email and repository links with actual information relevant to your project.*