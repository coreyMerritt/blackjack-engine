#!/bin/bash

if [[ "$1" ]]; then
  count="$1"
else
  count="100"
fi

if [[ "$2" ]]; then
  host="$2"
else
  host="localhost"
fi

session_id="$(./create_multi_sim_runner.sh $host | tr -d '"')"

curl -s --no-keepalive -X POST "http://$host:8000/session/$session_id/simulation/run/$count/benchmark" \
  -H "Content-Type: application/json" | jq

sstatus=0
while [[ $sstatus -ne 100 ]]; do
  sleep 1
  sstatus=$(curl -s -X GET "http://$host:8000/session/$session_id/simulation/results/check_multi" \
    -H "Content-Type: application/json" | jq .status)
  echo $sstatus
done

curl -s -X GET "http://$host:8000/session/$session_id/simulation/results/get_multi_formatted" \
    -H "Content-Type: application/json" | jq
