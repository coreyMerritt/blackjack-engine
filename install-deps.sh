#!/bin/bash

set -e
set -E
set -x

sudo apt update || true
sudo apt install python3.10-venv || sudo apt install python3.11-venv || true


[ -f requirements.txt ] || exit 1
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

