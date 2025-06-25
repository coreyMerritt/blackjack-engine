#!/bin/bash

set -e
set -E

if ! [[ "$1" ]]; then
  host="localhost"
else
  host="$1"
fi

if ! [[ "$2" ]]; then
  port="8000"
else
  port="$2"
fi

session_id="$(./create-single-sim-runner.sh $host $port | tr -d '"')"

curl -s --no-keepalive -X POST "http://$host:$port/session/$session_id/simulation/run" \
  -H "Content-Type: application/json" | jq

sstatus=0
while [[ $sstatus -ne 100 && $sstatus -ne -100 ]]; do
  sleep 1
  sstatus=$(curl -s -X GET "http://$host:$port/session/$session_id/simulation/results/check_single" \
    -H "Content-Type: application/json" | jq -r)
  echo $sstatus
done

curl -s -X GET "http://$host:$port/session/$session_id/simulation/results/get_single_formatted" \
    -H "Content-Type: application/json" | jq
