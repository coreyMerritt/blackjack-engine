#!/bin/bash

if [[ "$1" ]]; then
  count="$1"
else
  count="100"
fi

session_id="$(./create_multi_sim_runner.sh | tr -d '"')"

curl -s --no-keepalive -X POST "http://localhost:8000/session/$session_id/simulation/run/$count" \
  -H "Content-Type: application/json" | jq

sstatus=0
while [[ $sstatus -ne 100 ]]; do
  sleep 1
  sstatus=$(curl -s -X GET "http://localhost:8000/session/$session_id/simulation/results/check_multi" \
    -H "Content-Type: application/json" | jq .status)
  echo $sstatus
done

curl -s -X GET "http://localhost:8000/session/$session_id/simulation/results/get_multi_formatted" \
    -H "Content-Type: application/json" | jq

