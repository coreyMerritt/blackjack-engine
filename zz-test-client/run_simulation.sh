#!/bin/bash

curl -s -X POST "http://localhost:8000/simulation/run" \
  -H "Content-Type: application/json" \
  -d '{
        "money_goal": 999999999,
        "rules": {
          "betting_rules": {
            "min_bet": 50,
            "max_bet": 600
          },
          "dealer_rules": {
            "dealer_hits_soft_seventeen": true,
            "deck_count": 8,
            "shoe_reset_percentage": 20,
            "blackjack_pays_multiplier": 1.5
          },
          "double_down_rules": {
            "double_after_hit": false,
            "double_after_split_except_aces": true,
            "double_after_split_including_aces": false,
            "double_on_ten_eleven_only": false,
            "double_on_nine_ten_eleven_only": false,
            "double_on_any_two_cards": true
          },
          "splitting_rules": {
            "maximum_hand_count": 4,
            "can_hit_aces": false
          },
          "surrender_rules": {
            "early_surrender_allowed": false,
            "late_surrender_allowed": true
          }
        },
        "ai_player_info": [
          {
            "money": 1000,
            "basic_strategy_skill_level": 100,
            "bet_spread": {
              "true_zero": 50,
              "true_one": 100,
              "true_two": 200,
              "true_three": 300,
              "true_four": 400,
              "true_five": 500,
              "true_six": 600
            }
          }
        ]
      }' | jq

