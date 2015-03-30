#!/bin/sh

# install python requirements

virtualenv venv
source venv/bin/activate
pip install -r < requirements.txt

# install js requirements

for PACKAGE in dojo dijit dojox; do
    git clone --recursive git@github.com:dojo/$PACKAGE client/framework/$PACKAGE
done
