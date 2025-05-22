#!/bin/bash

source ./game_start.sh

if [[ "$1" ]]; then
  bet="$1"
else
  echo -e "\n\tProvide bet as arg1."
fi

curl -X POST "http://localhost:8000/session/$session_id/place_bet/$bet" \
  -H "Content-Type: application/json" |
  jq
echo

