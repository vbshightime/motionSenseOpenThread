cd /home/pi/otlink

/usr/bin/python3 /home/pi/otlink/readFileInsertDB.sh
retVal=$?
echo "$retVal"
if [ $retVal -ne 0 ]; then
    echo "unable to read the logs from io.txt restart the service"
    #sudo systemctl reload-or-restart read_file.service
    exit 0
fi
