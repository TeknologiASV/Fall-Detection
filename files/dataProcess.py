#########################################################################

import time
import datetime as dt
from files.Kdtree import *
from files.clustring_model import *
import MySQLdb
import serial
import csv
from files.pplc_parser_1 import Pc3
from sklearn.cluster import DBSCAN

####################################################################


class mmWaveData:

    # initialize the cloud-point features
    def __init__(self, level, condition, device_name, parameters, debugging, visualization, csv_data, fall_wait):
                
        #########################################
        # initialization
        print('initialization ....')
        self.min_now = int(dt.datetime.now().minute)

        # Points parameters    
        self.debugging_data = debugging
        self.clustering_distance = parameters['clustering_distance']
        self.Fall_threshld = parameters['Fall_threshold']
        self.csv_file = "files/data/raw_data_v6.csv"

        ###############
        # raw data     
        self.raw_data = []

        ###############
        # rawdata

        self.radar = []
        self.v6 = []
        self.v7 = []
        self.v8 = []
        self.dck = False
        self.visualization = visualization

        #########################
        # device parmeters

        self.host_name = device_name
        self.level = level
        self.condition = condition
        self.fall_wait = fall_wait

        #############################
        # features

        self.x = 0
        self.y = 0
        self.z = 0
        self.elevation = 0
        self.azimuth =0
        self. Mrange =0
        self.z_counter = 0
        self.z_frame = 0
        self.fall_trigger = False
        self.z_cluster = []
        self.y_cluster = []
        self.x_cluster = []
        self.xyz_counter = 0
        #############################

        self.z_offset = 0.2
        self.xyz = []
        self.z_list = []
        self.y_list = []
        self.x_list = []
        self.z_avg = []
        self.y_avg = []
        self.x_avg = []
        self.frames_thresh = parameters['frames']
        self.frames = 0
        self.t1 = 0
        self.center_one = (0,0)
        self.center_two = (0,0)

        ###########################################

        # ROI coordination
        # note zone: m1,m2,n1,n2 
        self.number_of_zones = 1
        self.m1   = parameters['zone'][self.number_of_zones -1][0]
        self.m2   = parameters['zone'][self.number_of_zones -1][1]
        self.n1   = parameters['zone'][self.number_of_zones -1][2]
        self.n2   = parameters['zone'][self.number_of_zones -1][3]
        self.points = parameters['zone'][self.number_of_zones -1][4]
        self.ROI_doppler = parameters['doppler']
        self.clustering_count = 0
        self.file_counter = 0
        self.csv_data = csv_data

        #############################################
        # MySQL    

        self.sql_hostname = 'tasv-database.czjdmxerbddi.ap-southeast-1.rds.amazonaws.com'
        self.sql_username = 'tasv'
        self.sql_password = 'PublikaTASV'
        self.sql_database = 'fallDetection'
        self.cursor = 0
        try:
            self.conn = MySQLdb.connect( host=self.sql_hostname, user=self.sql_username, password=self.sql_password, db=self.sql_database )
        except:
            print('cannot connect to MySQL database!!')


    # Extract the radar data online    
    def process_data_online(self,v6,v7):
        
        #for i in range (len(v7)):
        #    print('target: ',i,', ID: ',v7[i][0], ', posX: ',v7[i][1],', posY: ',v7[i][2], 'posZ: ',v7[i][7])

        if v6 != []:
            
            X = np.empty((len(v6),6))

            for i in range (len(self.v6)):

                #extract the v6 elements
                self.elevation = v6[i][0] # evevation
                self.azimuth   = v6[i][1] # azimuth
                self.doppler   = v6[i][2] # doppler
                self.Mrange    = v6[i][3] # range
                self.snr       = v6[i][4] # snr

                #################################

                # check the snr value
                #print('snr: ',self.snr)

                #if self.snr >= 2.0 and self.snr <= 10.0:
                # Get the x,y,z values
                self.z = self.Mrange * math.sin(self.elevation) + self.z_offset
                self.x = self.Mrange * math.cos(self.elevation) * math.sin(self.azimuth)
                self.y = self.Mrange * math.cos(self.elevation) * math.cos(self.azimuth)

                # filter the weak points
                if self.snr >= 3.0 and self.snr <= 30.0:
                    self.xyz.append([self.x,self.y,self.z])
                    X[i] = (self.x,self.y,self.z,self.Mrange,self.doppler,self.snr) #[x,y,z,range,Doppler,noise]

                self.frames += 1 # increse the samples counter by 1 

            if (self.frames >= self.frames_thresh):

                try:

                    dbscan = DBSCAN(eps = self.clustering_distance, min_samples = (2*3),n_jobs=-1).fit(X[:,[0,1,2]]) # fitting the model
                    labels = dbscan.labels_ # getting the labels
                    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
                    print('Estimated number of clusters: %d' % n_clusters_)
                    n_noise_ = list(labels).count(-1)
                    print('Estimated number of noise points: %d' % n_noise_)
                    labelSet = set(labels)
                    print("Label Set:{:}".format(labelSet))

                    if n_clusters_ == 1:
                        print('dbscan: ',dbscan)
                        print('number of points: ',len(X))
                        print('labels',labels)
                        print('X: ',X[:,[0,1,2]])
                        for i in range(len(X)):
                            if labels[i] != -1:
                                self.x_list.append(X[i,[0]])
                                self.y_list.append(X[i,[1]])
                                self.z_list.append(X[i,[2]])

                        for i in range(len(self.z_list)):
                            self.z_avg.append(self.z_list[i][0])
                            self.y_avg.append(self.y_list[i][0])
                            self.x_avg.append(self.x_list[i][0])

                        zavg_numpy = np.array(self.z_avg)
                        print('z_avg: ',np.mean(zavg_numpy))
                        print('z_max: ',np.max(zavg_numpy))
                        self.center_two = (np.mean(self.x_avg), np.mean(self.y_avg))

                        
                        if np.max(zavg_numpy) <= self.Fall_threshld:
                            self.fall_trigger = True
                            print('Fall condition is true!!')
                            #time.sleep(0.5)

                        elif np.max(zavg_numpy) > self.Fall_threshld:
                            self.fall_trigger = False

                        
                        if self.center_one != self.center_two :
                            if self.center_one[0] != 0 and self.center_one[1] != 0:
                                distance_between_points = math.sqrt((self.center_two[0] - self.center_one[0])**2 + (self.center_two[1]-self.center_one[1])**2)
                                print ('distance_between_points: ', distance_between_points, 'm') # for debug only

                                PC_file = open('PC.txt','w+') 
                                PC_file.write(str(np.mean(self.x_avg))+','+str(np.mean(self.y_avg))+','+str(np.mean(self.z_avg)))
                                PC_file.close


                                if np.max(zavg_numpy) >= 0.1 and np.max(zavg_numpy) <= 2.2:
                                    f = open('distance_between_points.txt','w+')                    
                                    f.write(str(distance_between_points)+'\n')
                                    f.close()

                        elif self.center_one == self.center_two:
                            distance_between_points = 0

                        # update the onle point
                        self.center_one = self.center_two    

                except Exception as e:
                    # no input
                    print('Error: ',e)

                # clear cached data
                self.xyz.clear()
                self.xyz_counter += 1
                #new_xyz.clear()
                #self.z_avg.clear()
                #self.x_avg.clear()
                #self.y_avg.clear()

                if self.xyz_counter >= 4:
                    self.z_avg.clear()
                    self.y_avg.clear()
                    self.x_avg.clear()
                    self.xyz_counter = 0

                self.z_list.clear()
                self.x_list.clear()
                self.y_list.clear()
                self.frames = 0 # reset the frame count varaible
                self.raw_data.clear()

    ######################################################

    def push_data(self,Fall):
        
        timestamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S") # current push time

        # save a copy
        backup = open("{}_backup_data.txt".format(self.host_name), "a+")
        backup.write(timestamp + ', ' + str(Fall) + ', ' + str('no implemented') + ', ' + self.host_name + '\n') # store the value
        backup.close()

        self.insert_fall(timestamp, Fall, self.host_name)


    def uartGetdata(self,port_name='USB1',baudrate=921600,timeout=0.5):
        # get the sensor raw data

        print(f"######################## Program start at : {dt.datetime.now().strftime('%d %m %Y %H:%M:%S.%f')} ########################")

        port = serial.Serial("/dev/tty{}".format(port_name),baudrate=baudrate,timeout=timeout)
        tmd = Pc3(port)
        tmd.dbg = True
        port.flushInput()
        return tmd


    #######################################################################
    def insert_fall(self , Date, Fall, Device):

        query = "INSERT INTO fall(Date, Fall, Device) " \
                "VALUES (%s,%s,%s)"

        args = (Date, Fall, Device)

        try:
            self.conn = MySQLdb.connect( host=self.sql_hostname, user=self.sql_username, password=self.sql_password, db=self.sql_database, connect_timeout=28800 )
            self.cursor = self.conn.cursor()
            self.cursor.execute(query, args)
            self.conn.commit()
        
        except self.conn.Error as e:
            print('Error cannot connect to the server')
            self.conn.rollback()

        except:
            print('Cannot connect to MySQL database!!')


        finally:
            self.cursor.close()
            self.conn.close()

    ##################################################################################

    def mainLoop(self):
        
        tmd = self.uartGetdata()

        if self.csv_data:
            with open("files/data/file_counter.txt", "r") as fopen:
                self.file_counter += int(fopen.readline())

        init_time = time.time() 

        while True:
            
            if self.csv_data:

                try:
                    counter = open("files/data/file_counter.txt", "w+")
                    counter.write(str(self.file_counter)) # store the value
                    counter.close()
                    self.file_counter += 1

                except:
                    print('cannot open this file!')

            (self.dck,self.v6,self.v7,self.v8) = tmd.tlvRead(False)

            time_stamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if self.dck:

                if self.csv_data:

                    try:
                        with open("files/data/raw_data_{}.csv".format(self.file_counter),"a+") as v6_data:
                            writer_v6 = csv.writer(v6_data,delimiter=",",quoting=csv.QUOTE_ALL)
                            writer_v6.writerow([str(time_stamp),self.v6])

                        counter = open("files/data/file_counter.txt", "w+")
                        counter.write(str(self.file_counter)) # store the value
                        counter.close()
                        self.file_counter += 1

                    except:
                        print('cannot open this file!')

                self.process_data_online(self.v6, self.v7)

                self.t1 = 0

            else:
                #start_time = time.time() 
                self.t1 = int(time.time()) - self.t1 
                if (self.t1 < 1000) :
                    print('time with no movement: ', self.t1)
                # if the time at no reflection exceed the fall wait threshold then is probably a fal
                if (self.t1 < 1000) and (self.t1 >= self.fall_wait) and (self.fall_trigger == True):
                    print('fall detected!!')

                    try:
                        self.push_data(True)
                    except Exception as e:
                        print('Error: ',e)

                    self.fall_trigger = False
                    time.sleep(5)

