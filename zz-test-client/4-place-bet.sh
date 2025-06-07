#!/bin/bash

if ! [[ "$1" ]]; then
  echo -e "\n\t arg1=session_id, arg2=player_id"
else
  session_id="$1"
fi

if ! [[ "$2" ]]; then
  echo -e "\n\t arg1=session_id, arg2=player_id"
else
  player_id="$2"
fi

if [[ "$3" ]]; then
  bet="$3"
else
  bet=200
fi

curl -s -X POST "http://localhost:8000/session/$session_id/game/player/$player_id/bet/place/$bet" \
  -H "Content-Type: application/json"

