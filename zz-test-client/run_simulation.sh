#!/bin/bash

curl -s -X POST "http://localhost:8000/simulation/run" \
  -H "Content-Type: application/json" \
  -d '{
        "deck_count": 8,
        "ai_player_count": 2,
        "min_bet": 50,
        "max_bet": 600,
        "shoe_reset_percentage": 20,
        "money_goal": 999999999,
        "player_info": {
          "money": 10000000
        },
        "bet_spread": {
          "true_zero": 50,
          "true_one": 100,
          "true_two": 200,
          "true_three": 300,
          "true_four": 400,
          "true_five": 500,
          "true_six": 600
        }
      }' | jq

