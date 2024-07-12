import os
import subprocess
from subprocess import Popen
import time
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)

def coapStart():
    logging.info("adding coap resource")
    fileName = "/home/pi/io.txt"
    filePath = Path(fileName)
    if filePath.exists():
        os.remove(fileName)
        os.system("touch /home/pi/io.txt")
    else:
        os.system("touch /home/pi/io.txt")
    os.system('sudo ot-ctl coap resource vibration')
    logging.info("starting coap")
    os.system('sudo ot-ctl coap start')
    os.system('sudo ot-ctl >> /home/pi/io.txt')
    

if __name__ == '__main__':
    coapStart()
