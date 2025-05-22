#!/bin/bash

if [[ "$1" ]]; then
  session_id="$1"
else
  echo -e "\n\tProvide session as arg1."
fi

if [[ "$2" ]]; then
  bet="$2"
else
  echo -e "\n\tProvide bet as arg2."
fi

curl -X POST "http://localhost:8000/session/$session_id/place_bet/$bet" \
  -H "Content-Type: application/json"
echo

