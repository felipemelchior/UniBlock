#!/bin/bash

echo "<optional> shell$: $0 <miner.input> <trader1.input> <trader2.input> ..."

#bash run_keeper.sh &> /dev/null &

sleep 3

bash run_miner.sh $1 &> /dev/null &

bash run_miner.sh $1 &> /dev/null &

bash run_miner.sh $1 &> /dev/null &

sleep 3

bash run_trader.sh $2 &> /dev/null &

bash run_trader.sh $3 &> /dev/null &

bash run_trader.sh $4 &> /dev/null &

bash run_trader.sh $5 &> /dev/null &

