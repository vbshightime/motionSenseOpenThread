#!/bin/sh
# note :: run as root
# this script is to be run on a fresh pi image
OTLINK_DIR=/home/pi/otlink
CRON_SCRIPT_CMD="* * * * * python3 /home/pi/otlink/cloudInteract.py"

cd $OTLINK_DIR

#enable and start read_file service
sudo install -m 644 read_file.service /etc/systemd/system/
sudo systemctl enable read_file.service

#enable and start cloud_interact service
sudo install -m 644 cloud_interact.service /etc/systemd/system
sudo systemctl enable cloud_interact.service

#enable and start cloud_iteract timer
sudo install -m 644 cloud_interact.timer /etc/systemd/system
sudo systemctl enable cloud_interact.timer
sudo systemctl start cloud_interact.timer
#enable and start coap_server_cli service
#sudo install -m 644 coap_server_cli.service /etc/systemd/system/
#sudo systemctl enable coap_server_cli.service
USER_PROFILE_COAP=$(cat /etc/xdg/lxsession/LXDE-pi/autostart | grep "coap_server.sh")

echo $USER_PROFILE_COAP

if [ $USER_PROFILE_COAP -z ]
then
    echo "coap server cli not in user profile"
    echo "@sudo lxterminal -e /home/pi/otlink/coap_server.sh" >> /etc/xdg/lxsession/LXDE-pi/autostart
fi

#start cron job
#(crontab -u $(whoami) -l; echo "$CRON_SCRIPT_CMD" ) | crontab -u $(whoami) -
#install python requirements
#pip3 install -r requirements.txt

sync
sleep 5
#sudo reboot
