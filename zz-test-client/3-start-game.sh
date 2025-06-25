#!/bin/bash

set -e
set -E

if [[ "$1" ]]; then
  session_id="$1"
else
  session_id="$(./session_create.sh | tr -d '"')"
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

curl -s -X POST "http://$host:$port/session/$session_id/game/start" \
  -H "Content-Type: application/json"

