#!/bin/bash

if [[ "$1" ]]; then
  session_id="$1"
else
  source ./game_start.sh
fi

curl -s -X POST "http://localhost:8000/session/$session_id/game/bet/place/300" \
  -H "Content-Type: application/json" |
  jq

