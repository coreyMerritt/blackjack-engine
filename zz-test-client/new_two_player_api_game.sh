#!/bin/bash

set -e
set -E
set -x

session="$(./1-create-game.sh | tr -d '"')"
sleep 0.5
player_one="$(./2-register-player.sh $session | jq .player_id | tr -d '"')"
sleep 0.5
player_two="$(./2-register-player.sh $session | jq .player_id | tr -d '"')"
sleep 0.5
./3-start-game.sh $session
sleep 0.5
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

echo -e "\n$session $player_one $player_two\n"

