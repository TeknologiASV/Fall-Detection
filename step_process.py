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
string_new_distance = ''
string_old_distance = ''
sql_hostname = 'tasv-database.czjdmxerbddi.ap-southeast-1.rds.amazonaws.com'
sql_username = 'tasv'
sql_password = 'PublikaTASV'
sql_database = 'fallDetection'
cursor = 0
try:
    conn = MySQLdb.connect( host=sql_hostname, user=sql_username, password=sql_password, db=sql_database )
except:
    print('cannot connect to MySQL database!!')


def insert_step(Date, step, Device):
    query = "INSERT INTO step(Date, step, Device) " \
            "VALUES (%s,%s,%s)"
    args = (Date, step, Device)
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

    if os.path.isfile("distance_between_points.txt"):
        if (os.stat("distance_between_points.txt").st_size != 0):
            
            try:
                with open("distance_between_points.txt", "r") as fopen:
                    string_new_distance = fopen.readline()

                    if string_new_distance != string_old_distance:
                        if float(string_new_distance.strip('\n')) >= 0.10:
                            distance += float(string_new_distance.strip('\n'))
                            counter+=1
                            if counter >= 4:
                                step = int(distance/0.43)
                                _sum +=step
                                print("step: ",step)
                                print("sum: ",_sum)
                                timestamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                insert_step(timestamp, step, device_name)
                                distance = 0
                                counter = 0

                            time.sleep(0.20)
                    
                    string_old_distance = string_new_distance 
                    
            except Exception as e:
                print("Error: ", e) 




