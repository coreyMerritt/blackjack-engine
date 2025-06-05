#!/bin/bash

if ! [[ "$1" ]]; then
  echo -e "\n\t arg1=session_id, arg2=player_id"
else
  session_id="$1"
fi

curl -s -X GET "http://localhost:8000/session/$session_id/game/get" \
  -H "Content-Type: application/json" | jq

