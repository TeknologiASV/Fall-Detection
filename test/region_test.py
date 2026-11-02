##################################################################################

import serial
import csv
from  pplc_parser import Pc3
import datetime as dt
import csv
import math
import time

class testZone:

    # initialize the cloud-point features
    def __init__(self, x_min, x_max, y_min, y_max):
        
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.prev_id_list = []
        self.curr_id_list = []

                                                          
    def process_data_online(self,v6):
        
        for i in range (len(v6)):
            #extract the v6 elements
            self.elevation = v6[i][0] # evevation
            self.azimuth   = v6[i][1] # azimuth
            self.doppler   = v6[i][2] # doppler
            self.Mrange    = v6[i][3] # range

            #################################
           
            # Get the x,y,z values
            self.z = self.Mrange * math.sin(self.elevation)  
            self.x = self.Mrange * math.cos(self.elevation) * math.sin(self.azimuth)
            self.y = self.Mrange * math.cos(self.elevation) * math.cos(self.azimuth)
            
            
            print('x: ',self.x, ', y: ',self.y,', z: ',self.z)

    def process_tracking_online(self, v7):

        print('number of targets: ', len(v7))

        if len(v7) >= 1:

            for i in range (len(v7)):

                self.curr_id_list.append([v7[i][0]])
                time_stamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print('target: ',i,', ID: ',v7[i][0], ', posX: ',v7[i][1],', posY: ',v7[i][2])
                f = open('v7_debugging.txt','a+')
                f.write('time: ' + str(time_stamp)+ ', total targets: ' + str(len(v7)) + ', target: ' + str(i) + ', ID: ' + str(v7[i][0]) + ', posX: ' +\
                    str(v7[i][1]) + ', posY: ' + str(v7[i][2])+ '\n')


            f.close()

        self.prev_id_list = self.curr_id_list
        self.curr_id_list.clear()

    def run(self,port_name='USB1',baudrate=921600,timeout=0.5):
        # get the sensor raw data

        print(f"######################## Program start at : {dt.datetime.now().strftime('%d %m %Y %H:%M:%S.%f')} ########################")

        port = serial.Serial("/dev/tty{}".format(port_name),baudrate=baudrate,timeout=timeout)
        tmd = Pc3(port)
        tmd.dbg = True
        port.flushInput()

        #####################################################
        with open("count.txt", "r") as fopen:
            count = fopen.readline()

        print("Count: ", int(count))

        #####################################################
        time_start = dt.datetime.now()
        i = int(count)
        i += 1
        #####################################################

        with open("count.txt", "w") as fopen:
            fopen.write(str(i+1))

        hasIncreased = False


        ###########################################################
        while True: # infinite detection for loop

            #########################################
            # extract the raw data from the UART
            (self.dck,self.v6,self.v7,self.v8)=tmd.tlvRead(False)
            self.time_stamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            #########################################

            #print('dck status: ',self.dck) # for debug only
            time_end = dt.datetime.now()
            time_diff = time_end - time_start
            #########################################

            
            #store the raw data
            if ((dt.datetime.now().minute == 0) or (dt.datetime.now().minute == 20) or (dt.datetime.now().minute == 40)) and (dt.datetime.now().second == 0) and hasIncreased == False:
                hasIncreased = True
                # every 20 minutes, increase increment
                # save to new file
                i+=1
                with open("count.txt", "w") as fopen:
                    fopen.write(str(i))   
                time_start = dt.datetime.now()

            #########################################

            if ((dt.datetime.now().minute == 1) or (dt.datetime.now().minute == 26) or (dt.datetime.now().minute == 46)) and (dt.datetime.now().second == 0):

                hasIncreased = False
            #########################################

            # people counting on v6 data
            if self.dck:

               
                with open("v6_{}.csv".format(i),"a+") as data_v6:
                    writer_v6 = csv.writer(data_v6,delimiter=",",quoting=csv.QUOTE_ALL)
                    writer_v6.writerow([str(self.time_stamp), self.v6])

                #with open("v7_{}.csv".format(i),"a+") as data_v7:
                #    writer_v7 = csv.writer(data_v7,delimiter=",",quoting=csv.QUOTE_ALL)
                #    writer_v7.writerow([str(self.time_stamp), self.v7])
                
                self.process_data_online(self.v6) # make online prediction
                #self.process_tracking_online(self.v7) # make online prediction

       
############################################################################################################
# for testing
x_min = -8
x_max =  8
y_min =  0
y_max =  8

mmWave = testZone(x_min, x_max, y_min, y_max)
mmWave.run()