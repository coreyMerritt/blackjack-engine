#!/bin/bash

if [[ "$1" ]]; then
  host="$1"
else
  host="localhost"
fi

curl -s -X GET "http://$host:8000/data/single_sim/get_formatted" \
  -H "Content-Type: application/json" \
  -d "$(cat ./create_single_sim_req.json)" | jq
