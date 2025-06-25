#!/bin/bash

set -e
set -E

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

if ! [[ "$3" ]]; then
  host="localhost"
else
  host="$3"
fi

if ! [[ "$4" ]]; then
  port="8000"
else
  port="$4"
fi

curl -s -X POST "http://$host:$port/session/$session_id/game/player/$player_id/double_down" \
  -H "Content-Type: application/json"

