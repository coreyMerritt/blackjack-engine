#!/bin/bash

session_id="$(./create_single_sim_runner.sh | tr -d '"')"

curl -s --no-keepalive -X POST "http://localhost:8000/session/$session_id/simulation/run" \
  -H "Content-Type: application/json" | jq

sstatus=0
while [[ $sstatus -ne 100 && $sstatus -ne -100 ]]; do
  sleep 1
  sstatus=$(curl -s -X GET "http://localhost:8000/session/$session_id/simulation/results/check_single" \
    -H "Content-Type: application/json" | jq .status)
  echo $sstatus
done

curl -s -X GET "http://localhost:8000/session/$session_id/simulation/results/get_single_formatted" \
    -H "Content-Type: application/json" | jq

