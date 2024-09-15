#!/bin/bash
set -e
set -x

# mkdocs
mkdocs build

# Copy Contribute to Github Contributing
cp /workspaces/devsetgo_lib/docs/index.md /workspaces/devsetgo_lib/README.md
cp /workspaces/devsetgo_lib/docs/contribute.md /workspaces/devsetgo_lib/CONTRIBUTING.md

mkdocs gh-deploy
