#!/bin/bash

if [[ "$1" ]]; then
  session_id="$1"
else
  session_id="$(./session_create.sh | tr -d '"')"
fi

curl -s -X POST "http://localhost:8000/session/$session_id/game/start" \
  -H "Content-Type: application/json"

