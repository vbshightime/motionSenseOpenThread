import sqlite3
from sqlite3 import OperationalError
from threading import Lock
import sys, os
import datetime
from datetime import date


#DB_FILE_PATH = os.path.join(DB_PATH, DB_NAME)
DB_FILE_PATH = "/home/pi/otlink/motion_db"


mutex = Lock()

class motion_schema(object):
    MOTION_TABLE_NAME = "motion"

    def connectDb(self):
        try:
            # pass
            print("Connecting to db")
            conn = sqlite3.connect(DB_FILE_PATH)
            #conn = sqlite3.connect("/home/pi/otlink/motion_db")

        except  :
            print("Unable to connect to DB %s"%DB_FILE_PATH)
            raise

        return conn

    def beginTransaction(self):
        try:
            mutex.acquire()
            self.conn = self.connectDb()
            print("starting a db transaction")
        except:
            print("Unable to begin Transaction %s"%DB_FILE_PATH)
            raise

    def endTransaction(self):
        try:
            self.conn.commit()
            self.conn.close()
            print("ending a db transaction")
            mutex.release()
        except:
            print("Unable to end Transaction %s"%DB_FILE_PATH)
            raise

    def closeTransaction(self):
        try:
            self.conn.close()
            print("closing a db connection without commit")
            mutex.release()
        except:
            print("Unable to close Transaction %s"%DB_FILE_PATH)
            mutex.release()



    def createTable(self,table_name):
            print("Creating required tables")
            c = self.conn.cursor()

            sql = """create table if not exists %(table)s (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id varchar(40) default NULL ,
            accel_x INTEGER default 0 ,
            accel_y INTEGER default 0 ,
            accel_z INTEGER default 0 ,
            sensor_profile default 0 ,
            is_online INTEGER default 0 ,
            time_stamp timestamp NOT NULL UNIQUE
            );"""%{'table':table_name}

            try:
                c.execute(sql)

                print(" Table created")
            except:
                print("Error Tables create fail ")

    def dropTable(self, table_name):
            print("Droping table %s"%table_name)
            c = self.conn.cursor()
            sql =  'drop table ' + table_name
            try:
                c.execute(sql)
                self.updateIndex(1,table_name)
                print("table deleted %s "%(sql))
            except  :
                print("Error unable to drop table")

    def deleteData(self, tableName, id):
        print("Deleting details from Customer DB")
        conn  = self.connectDb()
        c = conn.cursor()
        sql =  '''delete from  motion where ID < ?'''
        print("Deleting Query For Table %s:  %s" %(tableName,sql))
        try:
            status = c.execute(sql,(id,))
            conn.commit()
            conn.close()
            print("Deleting details from table %s"%tableName)
            return True
        except  :
            print("Deletion of data from DB fail")
        return False

    def checkTableExists(self,sql_conn,tableNAME):
        c = sql_conn.cursor()
        sql = '''select count(*) from sqlite_master where type='table' and name = "%s"'''%(tableNAME)
        try:
            print("sql query is :%s" %sql)
            #cursor = sql_conn.cursor()
            c.execute(sql)
            records = c.fetchone()[0]
            print("Table count in db is: %s" %(records))
            if (int(records) == 1):
                return True
            else:
                return False
        except:
            print('Error executing query to check if table exists or not !!')
            return False

    def updateTableOnlineIndex(self,id,isOnline,tableName):
        print("Updating table %s"%(tableName))
        try:
            data_tuple = (isOnline,id)
            print(data_tuple)
            if(tableName):
                sql ='''update motion set is_online = ? where ID = ?'''
            else:
                print("No DB name entered")
            print("sql is : %s"%(sql))
            cursor = self.conn.cursor()
            cursor.execute(sql,data_tuple)
            self.conn.commit()
        except:
            print("error updating the table")
            raise

    
    def updateAllTableOnlineIndex(self,id,isOnline,tableName):
        print("Updating table %s"%(tableName))
        try:
            data_tuple = (isOnline,id)
            print(data_tuple)
            if(tableName):
                sql ='''update motion set is_online = ? where ID >= ?'''
            else:
                print("No DB name entered")
            print("sql is : %s"%(sql))
            cursor = self.conn.cursor()
            cursor.execute(sql,data_tuple)
            self.conn.commit()
        except:
            print("error updating the table")
            raise

    def insertIntoDb(self,tableName,device_id,sensor_profile,accel_x,accel_y,accel_z,is_online,time_stamp):
        print("Inserting data into db in table :%s ."%(tableName))
        try:
            data_tuple = (device_id,sensor_profile,accel_x,accel_y,accel_z,is_online,time_stamp)
            print(time_stamp)
            if( tableName):
                sql = 'insert into '+ tableName +  '(device_id,sensor_profile,accel_x,accel_y,accel_z,is_online,time_stamp) values (?,?,?,?,?,?,?,?,?,?)'
            else:
                print("No db name Entered !!")
            print("sql is : %s" %sql)

            c = self.conn.cursor()
            c.execute(sql,data_tuple)

            print("data inserted into table: %s" %tableName)

        except OperationalError as e:
            if "no such table" in str(e):
                print("no table exists, creating tables%s"%str(e))
                self.createTable()
                #self.conn.commit()
                print("connection Commited.")
                self.insertIntoDb(tableName,device_id,sensor_profile,accel_x,accel_y,accel_z)

            else:
                print("sql error %s"%str(e))
                raise
        except  :
            print("Error in Inserting details in db ")
            raise

    def getMotionData(self,device_id,tableName):
        try:
            print("Getting Motion details from DB")
            conn  = self.connectDb()
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            sqlGetData =  'SELECT * from %s where DEVICE_ID="%s"'%(tableName,device_id)
            c.execute(sqlGetData)
            result = [dict(row) for row in c.fetchall()]
            conn.close()
            return result

        except OperationalError as e:
            if "no such table" in str(e):
                print("no table exists %s"%str(e))
                result = 0
                return result
            else:
                raise
        except:
            print("Unable to get data from motion table.")
        return False

    def getOfflineData(self, isOffline, tableName):
        try:
            print("Getting offline details from DB")
            conn  = self.connectDb()
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            sqlGetData =  'SELECT * from %s where is_online=%d'%(tableName,isOffline)
            c.execute(sqlGetData)
            result = [dict(row) for row in c.fetchall()]
            conn.close()
            return result
        except OperationalError as e:
            if "no such table" in str(e):
                print("no table exists %s"%str(e))
                result = 0
                return result
            else:
                raise
        except:
            print("Unable to get data from motion table.")
        return False


    def getPayloadByID(self,id,tableName):
        try:
            print("Getting offline details from DB")
            conn  = self.connectDb()
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            sqlGetData =  'SELECT * from %s where ID>=%d'%(tableName,id)
            c.execute(sqlGetData)
            result = [dict(row) for row in c.fetchall()]
            conn.close()
            return result
        except OperationalError as e:
            if "no such table" in str(e):
                print("no table exists %s"%str(e))
                result = 0
                return result
            else:
                raise
        except:
            print("Unable to get data from motion table.")
            result = 0
            return result




def main():
    ObjCustCount = motion_schema()

if __name__ == '__main__':
    main()

