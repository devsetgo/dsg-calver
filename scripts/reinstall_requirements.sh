#!/bin/bash
set -e
set -x

# remove current libraries
pip3 uninstall -r requirements.txt -y

# install requirements
pip3 install -r requirements.txt
