#!/bin/bash

session_id="$(./create_simulation.sh | tr -d '"')"

curl -s --no-keepalive -X POST "http://localhost:8000/session/$session_id/simulation/run/100" \
  -H "Content-Type: application/json" | jq

sstatus=0
while [[ $sstatus -ne 100 ]]; do
  sstatus=$(curl -s -X GET "http://localhost:8000/session/$session_id/simulation/results/check" \
    -H "Content-Type: application/json" | jq .status)
  echo $sstatus
done

curl -s -X GET "http://localhost:8000/session/$session_id/simulation/results/get_formatted" \
    -H "Content-Type: application/json" | jq

