#!/bin/sh -eu

# install python requirements

virtualenv venv
source venv/bin/activate
pip install -r < requirements.txt

# install js requirements

mkdir -p client/framework

# download the latest version of each library.
git submodule update --init --recursive
