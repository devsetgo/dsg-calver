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



# DevSetGo Common Library

`devsetgo_lib` is a versatile library designed to provide common functions for Python applications. Its main goal is to increase reusability and reduce the need to rewrite the same functions across multiple applications. This also allows for quick defect resolution and propagation of fixes across all dependent projects.

## Key Features

### **Common Functions**:
  - **File Operations**:
    - **CSV, JSON, and Text File Functions**: Create, read, write, and manipulate various file types with ease.
    - **Folder Functions**: Create and remove directories, list directory contents, and manage file system operations efficiently.

  - **Logging**:
    Comprehensive logging setup using the [Loguru Library]('https://loguru.readthedocs.io/en/stable/overview.html'). Provides extensive customization options for log configuration, including log rotation, retention, and formatting. Includes improvements for multiprocessing environments to ensure log messages are handled correctly across multiple processes.

  - **Calendar Functions**:
      Convert between month names and numbers seamlessly.

  - **Pattern Matching**:
      Powerful tools for searching patterns in text using regular expressions.


### **FastAPI Endpoints**:
  - Pre-built endpoints for system health checks, status, and uptime monitoring.
  - Functions to generate HTTP response codes easily.

### **Async Database**:
  - Configuration and management of asynchronous database sessions.
  - CRUD operations with async support.

---
## Installation

To install `devsetgo_lib`, use pip:

```sh
pip install devsetgo-lib

# For async database setup with SQLite or PostgreSQL
pip install devsetgo-lib[sqlite]
pip install devsetgo-lib[postgres]

# Experimental support for other databases
pip install devsetgo-lib[oracle]
pip install devsetgo-lib[mssql]
pip install devsetgo-lib[mysql]

# For adding FastAPI endpoints
pip install devsetgo-lib[fastapi]

# Install everything
pip install devsetgo-lib[all]
```

## Usage

Here's a quick example to demonstrate how you can use some of the key features of `devsetgo_lib`:

```python
from devsetgo_lib.common_functions import file_functions, logging_config, patterns, calendar_functions

# File Operations
file_functions.create_sample_files("example", 100)
content = file_functions.read_from_file("example.csv")
print(content)

# Logging
logging_config.config_log(logging_directory='logs', log_name='app.log', logging_level='DEBUG')
logger = logging.getLogger('app_logger')
logger.info("This is an info message")

# Pattern Matching
text = "Hello, my name is 'John Doe' and I live in 'New York'."
results = patterns.pattern_between_two_char(text, "'", "'")
print(results)

# Calendar Functions
print(calendar_functions.get_month(1))  # Output: 'January'
print(calendar_functions.get_month_number('January'))  # Output: 1
```

For detailed documentation on each module and function, please refer to the [official documentation](https://devsetgo.github.io/devsetgo_lib/print_page/).

## Contributing

We welcome contributions! Please see our [contributing guidelines](CONTRIBUTING.md) for more details.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contact

For any questions or issues, please open an issue on GitHub or contact us at [devsetgo@example.com](mailto:devsetgo@example.com).
