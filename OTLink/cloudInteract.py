import time
from datetime import datetime
import requests
import json
import sqlite3
from data_schema import motion_schema
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import configparser
from pathlib import Path
import logging
import os

# @brief: Setting up logging level
logging.basicConfig(level=logging.INFO)


# @brief: config parser info
config_key = configparser.ConfigParser()
config_key.read("configfile.ini")
aws_mqtt_config = config_key['aws_mqtt_info']
aws_http_config = config_key['aws_http_info']
sqlite_db_config = config_key['sqlite_db_info']

# @brief: SQLITE DB info parsed from config file
DB_TABLE_NAME = sqlite_db_config['table_name']
DB_FILE_PATH = sqlite_db_config['db_path']

# @brief: HTTP url, POST method parsed from config file
http_url = aws_http_config['http_host']

# @brief: mqtt url port and topic
#mqtt_url = aws_mqtt_config['mqtt_host']
#mqtt_port = aws_mqtt_config['mqtt_port']
#mqtt_topic_publish = aws_mqtt_config['mqtt_topic']
#mqtt_client_id = aws_mqtt_config['mqtt_client']
#logging.info("setting up client")
#myMQTTClient = AWSIoTMQTTClient(mqtt_client_id)
#logging.info("configuring endpoint")
#myMQTTClient.configureEndpoint(mqtt_url,mqtt_port)
#logging.info("setting up certificates for Authentication")
#myMQTTClient.configureCredentials(aws_mqtt_config['mqtt_ca_path'], aws_mqtt_config['mqtt_private_path'],aws_mqtt_config['mqtt_cert_path'])
#myMQTTClient.configureOfflinePublishQueueing(-1)
#myMQTTClient.configureDrainingFrequency(2)
#myMQTTClient.configureConnectDisconnectTimeout(10)
#myMQTTClient.configureMQTTOperationTimeout(5)

logging.info("Connecting to MQTT client")
#myMQTTClient.connect()

def connectToDB():
    try:
        print("Connecting to db")
        conn = sqlite3.connect(DB_FILE_PATH)
    except:
        print("Unable to connect to DB %s"%DB_FILE_PATH)
    return conn


def sendOfflinePayloads(connection,isOnline,tableName):
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    sqlGetData =  'SELECT * from %s where is_online="%s"'%(tableName,isOnline)
    cursor.execute(sqlGetData)
    result = [dict(row) for row in cursor.fetchall()]
    return result


if __name__ == '__main__':
    fileName = "/home/pi/thinghz/log.txt"
    filePath = Path(fileName)
    if not filePath.exists():
        os.system("touch {}".format(fileName))
    cust = motion_schema()
    startEvent =  datetime.now()
    dataSendStatus = ''
    lastScannedId = int(sqlite_db_config["last_scanned_id"])
    cust.beginTransaction()
    getDataToSentFormDB = cust.getPayloadByID(id=lastScannedId,tableName=DB_TABLE_NAME)
    cust.endTransaction()
    motion_payload_json_arr = []
    currentIdOfPayload = 0
    payloadCount = 0
    print(lastScannedId)
    for payload in getDataToSentFormDB:
        payload_json_obj = {}
        payload_json_obj["device_id"] = payload["device_id"]
        payload_json_obj["Accelx"] = payload["accel_x"]
        payload_json_obj["Accely"] = payload["accel_y"]
        payload_json_obj["Accelz"] = payload["accel_z"]
        payload_json_obj["sensor_profile"] = payload["sensor_profile"]
        payload_json_obj["timestamp"] = payload["time_stamp"]
        currentIdOfPayload = payload["ID"]
        motion_payload_json_arr.append(payload_json_obj)
        payloadCount+=1
    try:
        motion_payload_json_obj = {}
        print(currentIdOfPayload)
        lengthOfArray = len(motion_payload_json_arr)
        print(lengthOfArray)
        if lengthOfArray<=25 :
            print("length array is less than 25")
            print(lengthOfArray)
            motion_payload_json_obj['Data'] = motion_payload_json_arr
            res = requests.post(http_url, json = motion_payload_json_obj)
            print(res)
        else:
            print("length array is more than 25")
            split = lengthOfArray // 25
            print(split)
            for x in range(0,(split+1)):
                if (x%50) == 0:
                    print("add delay")
                    time.sleep(2)
                print(x)
                if ((x+1)>split):
                    print("its greater than split breaking, send that are left to send")
                    left = lengthOfArray % 25
                    if left == 0:
                        break
                    leftIndex = split*25
                    print(leftIndex)
                    print(leftIndex+left)
                    motion_payload_json_obj['Data'] = motion_payload_json_arr[leftIndex:(leftIndex+left)]
                    res = requests.post(http_url, json = motion_payload_json_obj)
                    print(res)
                    break
                startIndex = x
                endIndex = (x+1)
                jumpStart = startIndex*25
                jumpEnd = endIndex*25
                print(jumpStart)
                print(jumpEnd)
                motion_payload_json_obj['Data'] = motion_payload_json_arr[jumpStart:jumpEnd]
                res = requests.post(http_url, json = motion_payload_json_obj)
                print(res)
                indexToUpdate = jumpEnd + lastScannedId
                config_key.set('sqlite_db_info','last_scanned_id','{}'.format(indexToUpdate+1))
                print("data sent index {}".format(indexToUpdate))
                if not res.status_code == 200:
                    dataSendStatus = 'data not success'
                    break
                with open(r"configfile.ini",'w') as configfile:
                    config_key.write(configfile)
        if res and res.status_code == 200:
            dataSendStatus = 'dataSendSuccess'
            config_key.set('sqlite_db_info','last_scanned_id','{}'.format(currentIdOfPayload+1))
            config_key.set('sqlite_db_info','missed_data_count_id','{}'.format(0))
            with open(r"configfile.ini",'w') as configfile:
                config_key.write(configfile)
            cust.beginTransaction()
            cust.updateTableOnlineIndex(id=currentIdOfPayload,isOnline=1,tableName=DB_TABLE_NAME)
            cust.endTransaction()
        else:
            config_key.set('sqlite_db_info','missed_data_count_id','{}'.format(payloadCount))
            with open(r"configfile.ini",'w') as configfile:
                config_key.write(configfile)
        try:
            with open(fileName, 'a') as f:
                f.write("startDate:\t {}\n".format(startEvent))
                f.write("lastScanId:\t {}\n".format(lastScannedId))
                f.write("CurrentScanIdId:\t {}\n".format(currentIdOfPayload))
                f.write("numPayloadtoSent:\t {}\n".format(lengthOfArray))
                f.write("datasendStatus:\t {}\n".format(dataSendStatus))
        finally:
            f.close()
    except:
        logging.error("Exception occured while sending data to cloud")
        try:
            dataSendStatus = 'data not success'
            with open(fileName, 'a') as f:
                f.write("startDate:\t {}\n".format(startEvent))
                f.write("lastScanId:\t {}\n".format(lastScannedId))
                f.write("CurrentScanIdId:\t {}\n".format(currentIdOfPayload))
                f.write("numPayloadtoSent:\t {}\n".format(lengthOfArray))
                f.write("datasendStatus:\t {}\n".format(dataSendStatus))
        finally:
            f.close()

