import os
import MySQLdb
import socket 
import datetime as dt
import time

device_name = socket.gethostname()
step = 0
distance = 0
_sum = 0
counter = 0
string_new_PC = ''
string_old_PC = ''
sql_hostname = 'tasv-database.czjdmxerbddi.ap-southeast-1.rds.amazonaws.com'
sql_username = 'tasv'
sql_password = 'PublikaTASV'
sql_database = 'fallDetection'
cursor = 0

try:
    conn = MySQLdb.connect( host=sql_hostname, user=sql_username, password=sql_password, db=sql_database )
except:
    print('cannot connect to MySQL database!!')


def insert_PC(Date, x_point,y_point,z_point, Device):
    query = "INSERT INTO pointCloud(Date, x_point, y_point, z_point, Device) " \
            "VALUES (%s,%s,%s,%s,%s)"
    args = (Date, x_point, y_point, z_point, Device)
    try:
        conn = MySQLdb.connect( host=sql_hostname, user=sql_username, password=sql_password, db=sql_database)
        cursor = conn.cursor()
        cursor.execute(query, args)
        conn.commit()
    
    except Exception as e:
        print('Error: ',e)
        conn.rollback()

    finally:
        cursor.close()
        conn.close()


while True:

    if os.path.isfile("PC.txt"):
        if (os.stat("distance_between_points.txt").st_size != 0):
            
            try:
                with open("PC.txt", "r") as fopen:
                    string_new_PC = fopen.readline()

                    if string_new_PC != string_old_PC:
                        print('old: ',string_old_PC,', new: ',string_new_PC)
                        PC = list(string_new_PC.split(','))
                        x = float(PC[0])
                        y = float(PC[1])
                        z = float(PC[2])
                        timestamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        insert_PC(timestamp, x, y, z, device_name)
                        time.sleep(0.1)

                    
                    string_old_PC = string_new_PC
                    
            except Exception as e:
                print("Error: ", e) 




