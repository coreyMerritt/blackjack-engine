#!/bin/bash

set -e
set -E

if [[ "$1" ]]; then
  count="$1"
else
  count="100"
fi

if ! [[ "$2" ]]; then
  host="localhost"
else
  host="$2"
fi

if ! [[ "$3" ]]; then
  port="8000"
else
  port="$3"
fi

session_id="$(./create-multi-sim-runner.sh $host $port | tr -d '"')"

curl -s --no-keepalive -X POST "http://$host:$port/session/$session_id/simulation/run/$count" \
  -H "Content-Type: application/json" | jq

sstatus=0
while [[ $sstatus -ne 100 ]]; do
  sleep 1
  sstatus=$(curl -s -X GET "http://$host:$port/session/$session_id/simulation/results/check_multi" \
    -H "Content-Type: application/json" | jq -r)
  echo $sstatus
done

curl -s -X GET "http://$host:$port/session/$session_id/simulation/results/get_multi_formatted" \
    -H "Content-Type: application/json" | jq
