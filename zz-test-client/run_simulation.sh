#!/bin/bash

curl -s -X POST "http://localhost:8000/simulation/run" \
  -H "Content-Type: application/json" \
  -d '{
        "rules": {
          "min_bet": 50,
          "max_bet": 600,
          "deck_count": 8,
          "shoe_reset_percentage": 20,
          "double_down_restrictions": {
            "first_two_cards_only": true,
            "allow_after_split": false,
            "nine_ten_eleven_only": true
          }
        },
        "ai_player_info": [
          {
            "money": 1000000,
            "basic_strategy_skill_level": 1
          }
        ],
        "money_goal": 999999999,
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

