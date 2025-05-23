#!/bin/bash

source ./place_bet.sh

curl -s -X POST "http://localhost:8000/session/$session_id/game/hit" \
  -H "Content-Type: application/json" |
  jq

