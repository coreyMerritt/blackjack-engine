#!/bin/bash

set -e
set -E
set -x

package="$1"

sudo apt install -y "python3-$package" || true
python3 -m venv venv
source "venv/bin/activate"
pip install "$package"
pip freeze > "requirements.txt"

