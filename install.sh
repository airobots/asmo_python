#!/bin/sh -eu

# Install python requirements

virtualenv venv
source venv/bin/activate
pip install -r < requirements.txt

# Install js requirements

# Git submodule can download dojo repositiories,
# but we may also want to check out specific tags for compatibility.
git submodule update --init --recursive
