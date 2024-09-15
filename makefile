# Variables
REPONAME = devsetgo_lib

PYTHON = python3
PIP = $(PYTHON) -m pip
PYTEST = $(PYTHON) -m pytest

EXAMPLE_PATH = examples
SERVICE_PATH = dsg_lib
TESTS_PATH = tests
SQLITE_PATH = _sqlite_db
LOG_PATH = log

PORT = 5000
WORKER = 8
LOG_LEVEL = debug

REQUIREMENTS_PATH = requirements.txt
# DEV_REQUIREMENTS_PATH = requirements/dev.txt

.PHONY: autoflake black cleanup create-docs flake8 help install isort run-example run-example-dev speedtest test

autoflake: ## Remove unused imports and unused variables from Python code
	autoflake --in-place --remove-all-unused-imports  --ignore-init-module-imports --remove-unused-variables -r $(SERVICE_PATH)
	autoflake --in-place --remove-all-unused-imports  --ignore-init-module-imports --remove-unused-variables -r $(TESTS_PATH)
	autoflake --in-place --remove-all-unused-imports  --ignore-init-module-imports --remove-unused-variables -r $(EXAMPLE_PATH)

black: ## Reformat Python code to follow the Black code style
	black $(SERVICE_PATH)
	black $(TESTS_PATH)
	black $(EXAMPLE_PATH)

bump-minor: ## Bump the minor version number x.1.0
	bump2version minor

bump-release: ## Bump the release version number x.x.x-beta.1
	bump2version release

bump-patch: ## Bump the patch version number x.x.1
	bump2version patch

cleanup: isort ruff autoflake ## Run isort, ruff, autoflake

create-docs: ## Build and deploy the project's documentation
	python3 scripts/changelog.py
	mkdocs build
	cp /workspaces/$(REPONAME)/README.md /workspaces/$(REPONAME)/docs/index.md
	cp /workspaces/$(REPONAME)/CONTRIBUTING.md /workspaces/$(REPONAME)/docs/contribute.md
	cp /workspaces/$(REPONAME)/CHANGELOG.md /workspaces/$(REPONAME)/docs/release-notes.md
	mkdocs gh-deploy

create-docs-local: ## Build and deploy the project's documentation
	python3 scripts/changelog.py
	mkdocs build
	cp /workspaces/devsetgo_lib/README.md /workspaces/devsetgo_lib/docs/index.md
	cp /workspaces/devsetgo_lib/CONTRIBUTING.md /workspaces/devsetgo_lib/docs/contribute.md

flake8: ## Run flake8 to check Python code for PEP8 compliance
	flake8 --tee . > htmlcov/_flake8Report.txt

help:  ## Display this help message
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

install: ## Install the project's dependencie
	$(PIP) install -r $(REQUIREMENTS_PATH)

reinstall: ## Install the project's dependencie
	$(PIP) uninstall -r $(REQUIREMENTS_PATH) -y
	$(PIP) install -r $(REQUIREMENTS_PATH)

isort: ## Sort imports in Python code
	isort $(SERVICE_PATH)
	isort $(TESTS_PATH)
	isort $(EXAMPLE_PATH)


speedtest: ## Run a speed test
	if [ ! -f speedtest/http_request.so ]; then gcc -shared -o speedtest/http_request.so speedtest/http_request.c -lcurl -fPIC; fi
	python3 speedtest/loop.py

test: ## Run the project's tests
	pre-commit run -a
	pytest
	sed -i 's|<source>/workspaces/$(REPONAME)</source>|<source>/github/workspace</source>|' /workspaces/$(REPONAME)/coverage.xml
	genbadge coverage -i /workspaces/$(REPONAME)/coverage.xml
	flake8 --tee . > htmlcov/_flake8Report.txt


build: ## Build the project
	python -m build

ruff: ## Format Python code with Ruff
	ruff check --fix --exit-non-zero-on-fix --show-fixes $(SERVICE_PATH)
	ruff check --fix --exit-non-zero-on-fix --show-fixes $(TESTS_PATH)
	ruff check --fix --exit-non-zero-on-fix --show-fixes $(EXAMPLE_PATH)


ex-fastapi: ## Run the example fast application
	uvicorn examples.fastapi_example:app --port ${PORT} --reload  --log-level $(LOG_LEVEL)
	# uvicorn examples.fastapi_example:app --port ${PORT} --workers ${WORKER}  --log-level $(LOG_LEVEL)

ex-log: ## Run the example logging script
	cp /workspaces/devsetgo_lib/examples/log_example.py /workspaces/devsetgo_lib/ex.py
	python3 ex.py
	rm /workspaces/devsetgo_lib/ex.py


ex-cal: ## Run the example calendar script
	cp /workspaces/devsetgo_lib/examples/cal_example.py /workspaces/devsetgo_lib/ex.py
	python3 ex.py
	rm /workspaces/devsetgo_lib/ex.py

ex-csv: ## Run the example calendar script
	cp /workspaces/devsetgo_lib/examples/csv_example.py /workspaces/devsetgo_lib/ex.py
	python3 ex.py
	rm /workspaces/devsetgo_lib/ex.py

ex-json: ## Run the example calendar script
	cp /workspaces/devsetgo_lib/examples/json_example.py /workspaces/devsetgo_lib/ex.py
	python3 ex.py
	rm /workspaces/devsetgo_lib/ex.py

ex-pattern: ## Run the example calendar script
	cp /workspaces/devsetgo_lib/examples/pattern_example.py /workspaces/devsetgo_lib/ex.py
	python3 ex.py
	rm /workspaces/devsetgo_lib/ex.py

ex-text: ## Run the example calendar script
	cp /workspaces/devsetgo_lib/examples/text_example.py /workspaces/devsetgo_lib/ex.py
	python3 ex.py
	rm /workspaces/devsetgo_lib/ex.py

ex-email: ## Run the example calendar script
	cp /workspaces/devsetgo_lib/examples/validate_emails.py /workspaces/devsetgo_lib/ex.py
	python3 ex.py
	rm /workspaces/devsetgo_lib/ex.py

ex-all: ## Run all the examples, but fastapi

	make ex-log
	make ex-cal
	make ex-csv
	make ex-json
	make ex-pattern
	make ex-text
	make ex-email
