#!/bin/bash

if ! [[ "$1" ]]; then
  echo -e "\n\tYou must provide a session_id"
else
  session_id="$1"
fi

curl -s -X POST "http://localhost:8000/session/$session_id/game/players/human/register" \
  -H "Content-Type: application/json" \
  -d '{
        "human_player_info": {
          "bankroll": 5000
        }
      }' | jq

