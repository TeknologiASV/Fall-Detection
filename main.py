from  files.dataProcess import *
import argparse
import time
import datetime as dt
import socket
##################################################################################

#get the programe arguments
device_name = socket.gethostname()

# set the zones parameters 

if device_name == 'RPi-test':
   level = 'level-1'
   condition = 'in'
   #p(x,y)
   p1 = (-2.5, 2.8)
   p2 = (2.8, 2.8)
   p3 = (-2.5, 2.4)
   p4 = (2.8, 2.4)
   m1 = (p2[1]-p1[1])/(p2[0]-p1[0])
   m2 = (p4[1]-p3[1])/(p4[0]-p3[0])
   n1 = p2[1] - p2[0] * m1
   n2 = p4[1] - p4[0] * m2
   # note zone: m1,m2,n1,n2 
   zone_parameters = {'zone':[[m1, m2, n1, n2, [p1,p2,p3,p4]]], 'doppler':-0.6, 'clustering_distance':0.5, 'frames':1, 'Fall_threshold':-0.0}
   debugging = True
   visualization = False
   csv_data = False
   fall_wait = 2 # sec


###########################################################################################
#processradar = radarProcess()

processdata = mmWaveData(level, condition, device_name, zone_parameters , debugging, visualization, csv_data, fall_wait)


###########################################################################################
# run the main program

processdata.mainLoop() # infine loop
