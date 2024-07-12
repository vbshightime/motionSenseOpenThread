#!/bin/bash

FILE_PATH=/home/pi/otlink/io.txt

if [ -f "$FILE_PATH" ]; then
    echo "$FILE_PATH exists. remove the old one and create new"
    rm -rf $FILE_PATH
    touch $FILE_PATH
else
    echo "$FILE_PATH doesnot exist creat a new one"
    touch $FILE_PATH
fi

echo "adding resource as vibration"
sudo ot-ctl coap resource vibration
echo "starting coap Server"
sudo ot-ctl coap start
sudo ot-ctl >> $FILE_PATH
