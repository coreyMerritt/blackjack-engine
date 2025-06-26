#!/bin/bash

source "/lib/bash-test/bash-test"

if [[ "$1" ]]; then
  host="$1"
else
  host="localhost"
fi

cd $bt_project_dir/zz-test-client

btStartTest "Can create a Game"
  session_id="$(bash 1-create-game.sh $host | jq -r)"

btStartTest "Can register a Player"
  player_id="$(bash 2-register-player.sh $session_id $host | jq -r)"

btStartTest "Can start a Game"
  bash 3-start-game.sh $session_id $host

btStartTest "Can place a Bet"
  bash 4-place-bet.sh $session_id $player_id 100 $host

btStartTest "Can run a Sim"
  bash run-simulation.sh $host

btStartTest "Can run a Multi-Sim"
  bash run-simulations.sh 2 $host
