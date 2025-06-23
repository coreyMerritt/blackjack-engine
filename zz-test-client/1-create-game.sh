#!/bin/bash

curl -s -X POST "http://localhost:8000/session/game/create" \
  -H "Content-Type: application/json" \
  -d "$(cat ./create_single_sim_req.json)" | jq

