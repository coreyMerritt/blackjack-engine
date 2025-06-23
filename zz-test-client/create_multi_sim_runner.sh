#!/bin/bash

if [[ "$1" ]]; then
  host="$1"
else
  host="localhost"
fi

curl -s -X POST "http://$host:8000/session/simulation/multi/create" \
  -H "Content-Type: application/json" \
  -d "{
        \"multi\": $(cat ./create_multi_sim_req.json),
        \"single\": $(cat ./create_single_sim_req.json)
      }" | jq
