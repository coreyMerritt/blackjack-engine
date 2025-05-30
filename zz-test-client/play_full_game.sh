#!/bin/bash

session_id="$(./session_create.sh | tr -d '"')"

main() {
  startGame
  gameplayLoop 
}

gameplayLoop() {
  bankroll=10000
  while [[ $bankroll -gt 0 ]]; do
    hand_value=$(placeBet "50")
    while [[ $hand_value -lt 17 ]]; do
      hand_value=$(hit)
    done

    if [[ $hand_value -lt 21 ]]; then
      bankroll=$(stand)
    else
      sleep 0.1
      bankroll=$(getMoney)
    fi
    echo $bankroll
    sleep 0.1
  done
}

startGame() {
  curl -s -X POST "http://localhost:8000/session/$session_id/game/start" \
  -H "Content-Type: application/json" 2>&1 >/dev/null
}

placeBet() {
  bet="$1"

  echo "$(curl -s -X POST "http://localhost:8000/session/$session_id/game/bet/place/$bet" \
  -H "Content-Type: application/json" |
  jq .hand_value)"
}

hit() {
  echo "$(curl -s -X POST "http://localhost:8000/session/$session_id/game/hit" \
  -H "Content-Type: application/json" |
  jq .hand_value)"
}

stand() {
  curl -s -X POST "http://localhost:8000/session/$session_id/game/stand" \
  -H "Content-Type: application/json" |
  jq .bankroll
}

getGame() {
  curl -s -X POST "http://localhost:8000/session/$session_id/game/get" \
  -H "Content-Type: application/json"
}

getMoney() {
  curl -s -X POST "http://localhost:8000/session/$session_id/game/get_bankroll" \
  -H "Content-Type: application/json" |
  jq .bankroll
}



main

