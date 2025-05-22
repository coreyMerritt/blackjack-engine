#!/bin/bash

curl -X POST "http://localhost:8000/session/create" \
  -H "Content-Type: application/json" \
  -d '{
        "deck_count": 8,
        "ai_player_count": 2,
        "min_bet": 50,
        "max_bet": 600
      }'
echo

