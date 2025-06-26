#!/bin/bash

source "/lib/bash-test/bash-test"

cd $bt_project_dir/zz-test-client

btStartTest "Can create a Game"
  session_id="$(bash 1-create-game.sh | jq -r)"

btStartTest "Can register a Player"
  player_id="$(bash 2-register-player.sh $session_id | jq -r)"

btStartTest "Can start a Game"
  bash 3-start-game.sh $session_id

btStartTest "Can place a Bet"
  bash 4-place-bet.sh $session_id $player_id

btStartTest "Can run a Sim"
  bash run-simulation.sh

btStartTest "Can run a Multi-Sim"
  bash run-simulations.sh 2
