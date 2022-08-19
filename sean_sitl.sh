#!/bin/bash
STRING="Starting SITL by Sean in sitl directory"
PYTHON="/usr/bin/python3.9"
FILE_ROOT="/home/pi/sitl"
FILE="sean_obc_ng_main.py"



pushd . > /dev/null 2>&1
cd $FILE_ROOT

echo $STRING
$PYTHON "$FILE"
echo $STRING
sleep 1
popd > /dev/null 2>&1
