#!/bin/bash

set -e
set -E

if ! [[ "$1" ]]; then
  echo -e "session_id not provided"
else
  session_id="$1"
fi

if ! [[ "$2" ]]; then
  host="localhost"
else
  host="$2"
fi

if ! [[ "$3" ]]; then
  port="8000"
else
  port="$3"
fi



curl -s -X GET "http://$host:$port/session/$session_id/game/get" \
  -H "Content-Type: application/json" | jq

