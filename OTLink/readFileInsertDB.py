import time
from datetime import datetime
import json
import sqlite3
import logging
from data_schema import motion_schema
from pathlib import Path

DB_TABLE_NAME = 'motion'
DB_FILE_PATH = "/home/pi/otlink/motion_db"
noNewDataCounter = 0

logging.basicConfig(level=logging.INFO)

def convert_to_bytes(euidString):
    byteValue = ""
    for element in euidString:
        byteValue += (format(ord(element), "x"))
    return byteValue


def follow(thefile):
    #global noNewDataCounter
    thefile.seek(0,2)
    while True:
        line = thefile.readline()
        if not line:
            #noNewDataCounter+=1
            #time.sleep(0.1)
            #if noNewDataCounter==30:
            #    noNewDataCounter = 0
            #    exit(1)
            continue
        yield line


def insertDataToDB(motionData,cust,isOnline):
    try:
        logging.info("Begin transaction")
        cust.beginTransaction()
        logging.info('inserting data for %s in table %s',motionData["device_id"],DB_TABLE_NAME)
        cust.insertIntoDb(tableName=DB_TABLE_NAME,device_id=motionData["device_id"],sensor_profile=motionData["sensor_profile"], \
                           accel_x=motionData["Accelx"], accel_y=motionData["Accely"], \
                           accel_z=motionData["Accelz"],is_online=isOnline,time_stamp=motionData["timestamp"]  \)
        logging.info("Insergting data done, now ending transcation")
        cust.endTransaction()
        return True
    except:
        logging.error("Some exception occured while trying to insert data in %s for %s",DB_TABLE_NAME,motionData["device_id"])
        cust.closeTransaction()
        return False

def connectToDB():
    try:
        logging.info('Connecting to db: %s',DB_FILE_PATH)
        conn = sqlite3.connect(DB_FILE_PATH)
    except:
        logging.error('Unable to connect to DB %s',DB_FILE_PATH)
    return conn

def createTable(cust):
    try:
        cust.beginTransaction()
        cust.createTable(table_name=DB_TABLE_NAME)
        cust.endTransaction()
    except:
        logging.error('Some error occured while creating table %s',DB_TABLE_NAME)

if __name__ == '__main__':
    cust = motion_schema()
    conn = connectToDB()
    if not cust.checkTableExists(conn,DB_TABLE_NAME):
        logging.info('Table does not exists creating table %s',DB_TABLE_NAME)
        createTable(cust)
    logfile = open("/home/pi/otlink/io.txt","r")
    loglines = follow(logfile)
    decode_bytes = ""
    for line in loglines:
        line_str = str(line)
        try:
            payload_index = line_str.index('payload:')
            print(payload_index)
            payload_trim = (line_str[(payload_index+9):])
            print(payload_trim)
            euid_to_bytes = convert_to_bytes(payload_trim[28:44])
            payload_to_decode = payload_trim[:28] + euid_to_bytes + payload_trim[44:]
            decode_bytes = bytes.fromhex(payload_to_decode).decode("ascii")
        except:
            logging.error("Can not decode, not a hexadecimals")
        try:
            timeAndProfile = {}
            #timeAndProfile['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            timeAndProfile['sensor_profile'] = 1
            jsonPayload = json.loads(decode_bytes)
            print(jsonPayload)
            print(jsonPayload['time'])
            time = jsonPayload['time']
            timestamp = time[0:2] + "-" + time[2:4] + "-" + time[4:6] + " " + time[6:8]+ ":" + time[8:10] + ":" + time[10:]
            jsonPayload['time'] = timestamp
            jsonPayload.update(timeAndProfile)
            logging.info("compiled JSON: %s",json.dumps(jsonPayload))
            insertDataToDB(jsonPayload,cust,0)
        except:
            logging.error("exception occured while compiling JOSN")
