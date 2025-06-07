#!/bin/bash

set -e
set -E
set -x

session="$1"
player_one="$2"
player_two="$3"
./4-place-bet.sh $session $player_one
sleep 0.5
./4-place-bet.sh $session $player_two
sleep 0.5
./5-insurance.sh $session $player_one
sleep 0.5
./5-insurance.sh $session $player_two
sleep 0.5
./6-surrender.sh $session $player_one
sleep 0.5
./6-surrender.sh $session $player_two

