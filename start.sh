#!/bin/bash
source ./venv/bin/activate
exec ./venv/bin/uvicorn main:app --reload

