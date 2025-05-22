#!/bin/bash

session_id="$(./session_create.sh | tr -d '"')"

curl -s -X POST "http://localhost:8000/session/$session_id/game/start" \
  -H "Content-Type: application/json"

