#!/bin/bash

curl -s -X POST "http://localhost:8000/session/create" \
  -H "Content-Type: application/json" \
  -d '{
        "deck_count": 8,
        "ai_player_info": [
          {
            "bankroll": 1000000,
            "basic_strategy_skill_level": 10
          }
        ],
        "min_bet": 50,
        "max_bet": 600,
        "shoe_reset_percentage": 20,
        "human_player_info": {
          "bankroll": 10000
        }
      }'

