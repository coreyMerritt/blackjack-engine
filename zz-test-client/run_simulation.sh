#!/bin/bash

session_id="$(./create_simulation.sh | tr -d '"')"

curl -s -X POST "http://localhost:8000/session/$session_id/simulation/run/2" \
  -H "Content-Type: application/json" | jq

sleep 30

curl -s -X POST "http://localhost:8000/session/$session_id/simulation/results_formatted" \
  -H "Content-Type: application/json" | jq
