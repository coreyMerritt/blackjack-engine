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
  insurance="$3"
else
  insurance="false"
fi

curl -s -X POST "http://localhost:8000/session/$session_id/game/player/$player_id/insurance/$insurance" \
  -H "Content-Type: application/json"

