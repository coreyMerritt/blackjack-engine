#!/bin/bash

if [[ "$1" ]]; then
  session_id="$1"
else
  echo -e "\n\tNo session_id given"
fi

curl -X POST "http://localhost:8000/deal/$session_id" \
  -H "Content-Type: application/json"
echo

