#!/bin/bash

if [[ "$1" ]]; then
  host="$1"
else
  host="localhost"
fi

session_id="$(./create_single_sim_runner.sh $host | tr -d '"')"

curl -s --no-keepalive -X POST "http://$host:8000/session/$session_id/simulation/run" \
  -H "Content-Type: application/json" | jq

sstatus=0
while [[ $sstatus -ne 100 && $sstatus -ne -100 ]]; do
  sleep 1
  sstatus=$(curl -s -X GET "http://$host:8000/session/$session_id/simulation/results/check_single" \
    -H "Content-Type: application/json" | jq .status)
  echo $sstatus
done

curl -s -X GET "http://$host:8000/session/$session_id/simulation/results/get_single_formatted" \
    -H "Content-Type: application/json" | jq
