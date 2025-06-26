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

curl -s -X GET "http://$host:$port/data/single_sim/get_formatted" \
  -H "Content-Type: application/json" \
  -d "$(cat ./single.json)" | jq
