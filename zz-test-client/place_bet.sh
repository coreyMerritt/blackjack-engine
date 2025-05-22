#!/bin/bash

source ./game_start.sh

curl -s -X POST "http://localhost:8000/session/$session_id/place_bet/300" \
  -H "Content-Type: application/json" |
  jq

