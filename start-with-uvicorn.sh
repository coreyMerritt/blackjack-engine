#!/usr/bin/env bash

set -x
set -e
set -E

PYTHON_BIN=".venv/bin/python"

if [ ! -x "$PYTHON_BIN" ]; then
  echo -e "\n\tError: Python not found in .venv. Is the venv set up?"
  exit 1
fi

PYTHONPATH=src "$PYTHON_BIN" -m uvicorn src.main:app --reload

