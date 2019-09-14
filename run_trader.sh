#!/bin/bash

if [ $1 ] && [ -f $1 ]
then
    xterm -e "python3 main.py -ki 192.168.0.111 -kp 9999 --trader < $1"
else
    xterm -e "python3 main.py -ki 192.168.0.111 -kp 9999 --trader"
fi

