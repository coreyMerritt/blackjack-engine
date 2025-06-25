#!/bin/bash

set -e
set -E

if ! [[ "$1" ]]; then
  echo -e "\n\tYou must provide a session_id"
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

curl -s -X POST "http://$host:$port/session/$session_id/game/players/human/register" \
  -H "Content-Type: application/json" \
  -d '{
        "human_player_info": {
          "bankroll": 5000
        }
      }' | jq

