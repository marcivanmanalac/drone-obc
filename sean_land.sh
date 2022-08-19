#!/bin/bash
STRING="Starting self-landing by Sean(NOT SITL)"
PYTHON="/usr/bin/python3.9"
FILE_ROOT="/home/pi/niwc/Computer_Companion/lolas_obc_files"
FILE="sean_obc_ng_main.py"



pushd . > /dev/null 2>&1
cd $FILE_ROOT

echo $STRING
$PYTHON "$FILE"
echo $STRING
sleep 1
popd > /dev/null 2>&1
