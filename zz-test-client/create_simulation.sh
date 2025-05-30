#!/bin/bash

curl -s -X POST "http://localhost:8000/session/simulation/create" \
  -H "Content-Type: application/json" \
  -d '{
        "bankroll_goal": 50000,
        "rules": {
          "betting_rules": {
            "min_bet": 25,
            "max_bet": 25
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
            "double_on_any_two_cards": false,
            "double_on_nine_ten_eleven_only": true,
            "double_on_ten_eleven_only": false
          },
          "splitting_rules": {
            "maximum_hand_count": 4,
            "can_hit_aces": false
          },
          "surrender_rules": {
            "early_surrender_allowed": false,
            "late_surrender_allowed": false
          }
        },
        "ai_player_info": [
          {
            "bankroll": 5000,
            "basic_strategy_skill_level": 100,
            "card_counting_skill_level": 100,
            "deviations_skill_level": 100,
            "bet_spread": {
              "true_zero": 25,
              "true_one": 25,
              "true_two": 25,
              "true_three": 25,
              "true_four": 25,
              "true_five": 25,
              "true_six": 25
            }
          }
        ]
      }' | jq

