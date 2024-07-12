import sqlite3
from data_schema import motion_schema
import configparser
from pathlib import Path

config_key = configparser.ConfigParser()
config_key.read("configfile.ini")
sqlite_db_config = config_key['sqlite_db_info']
aDayData = 43200
lastScannedId = int(sqlite_db_config["last_scanned_id"])
DB_TABLE_NAME = sqlite_db_config['table_name']
DB_FILE_PATH = sqlite_db_config['db_path']

if __name__ == '__main__':
    try:
        cust = motion_schema()
        if lastScannedId > aDayData:
            cust.beginTransaction()
            cust.deleteData(tablename=DB_TABLE_NAME,id=(lastScannedId-aDayData))
            cust.endTransaction()
        exit(0)
    except:
        exit(1)
