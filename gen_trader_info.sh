#!/bin/bash

[ $1 ] || { echo "Usage: $0 <trader_ID>"; exit; }

FILE="trader_$1.input"

printf "lu\nsc\nst\nmsg\n" > $FILE
for i in `seq 1 1000`
do 
    echo "st"
    echo "$1-msg-$i-$RANDOM"
    if [ $(($i%10)) -eq 0 ]
    then 
        echo "sc"
        echo "lu"
    fi
done >> $FILE

