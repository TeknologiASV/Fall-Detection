###############################################################################################

import paho.mqtt.client as mqtt
import time
import ast
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
#import winsound
from datetime import datetime
import math
import numpy as np
import os

#################################################################################################

def on_message(client,userdata,message):
    global receive_msg, receive_trigger, pacing_detect_receive_trigger, pacing_detect_message,  distance, dist_receive_trigger
    if message.topic=="Points":
        #print("Received message: ", str(message.payload.decode("utf-8")))
        receive_msg = ast.literal_eval(message.payload.decode("utf-8"))
        if len(receive_msg) > 0:
            receive_trigger = 1
        else:
            receive_trigger = 0
    
    if message.topic == "Pacing":
        print("Pacing Info: ", str(message.payload.decode("utf-8")))
       
    if message.topic == "PacingDetect":
        print("Pacing: ", str(message.payload.decode("utf-8")))
        pacing_detect_message = str(message.payload.decode("utf-8"))
        if len(pacing_detect_message) > 0:
            pacing_detect_receive_trigger = 1
        else:
            pacing_detect_receive_trigger = 0

    if message.topic == "Distance":
        #print("Distance Info: ", str(message.payload.decode("utf-8")))
        distance=float(message.payload.decode("utf-8"))
        dist_message = str(message.payload.decode("utf-8"))
        #print(f"Distance: {distance}")
        if len(dist_message) > 0:
            dist_receive_trigger = 1
        else:
            dist_receive_trigger = 0

broker_address = "test.mosquitto.org"
#broker_address = "172.24.104.166" #rpi-1
#broker_address = "192.168.195.152" #rpi-2
#broker_address = "192.168.195.66" #rpi-zero
client = mqtt.Client("Laptop")
client.connect(broker_address)
print("start")


##### Set Plot Params #####
plt.style.use('dark_background')
fig = plt.figure()
ax = fig.add_subplot(111, projection = '3d')
#ax = fig.add_subplot(111)
#fig.patch.set_facecolor('xkcd:gray')
#ax.set_facecolor('xkcd:gray')
ax.w_xaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
ax.w_yaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
ax.w_zaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
ax.w_zaxis.line.set_lw(0.)
ax.set_zticks([])
ax.set(xlim = (-3,3), ylim = (0,5), zlim = (0,3))
ax.set_xlabel('X Axis')
ax.set_ylabel('Y Axis')
#ax.set_zlabel('Z Axis')
ax.axis('off')
ax.tick_params(axis='x', colors='white')
ax.tick_params(axis='y', colors='white')
ax.tick_params(axis='z', colors='black')
#ax.axis('off')
ax.view_init(90, 90)
#ax.get_zaxis().set_visible(False)

# Office Borders
#top = [5,5] # The Rectangle Top Line [y1, y2]
#bottom = [0,0] # The Rectangle Bottom Line [y1, y2]
#x_2 = [-3,3] # Rectangle [x1, x2] => w.r.t => x1, y1 and x2, y2
#left = [-3,-3] # The Rectangle Left Line [y1, y2]
#right = [3,3] # The Rectangle Right Line [y1, y2]
#y_2 = [0,5] # Rectangle [y1, y2] => w.r.t => x1, y1 and x2, y2
#z_2 = [0,0]

#MQTT_Visualisation_Pacing.py# Sensor 
top_sensor = [0.1,0.1]
bottom_sensor = [0,0]
x_sensor = [-0.1,0.1]
	
left_sensor = [-0.1,-0.1]
right_sensor = [0.1,0.1]
y_sensor = [0,0.1]
z_sensor = [1.2,1.2]

# Line Plotting for room 
#ax.plot(x_2,top,z_2,'black') 
#ax.plot(x_2,bottom,z_2,'black')
#ax.plot(right,y_2,z_2,'black') 
#ax.plot(left,y_2,z_2,'black') 

# Line Plotting for Sensor 
ax.plot(x_sensor,top_sensor,z_sensor,'b') 
ax.plot(x_sensor,bottom_sensor,z_sensor,'b')
ax.plot(right_sensor,y_sensor,z_sensor,'b') 
ax.plot(left_sensor,y_sensor,z_sensor,'b')
#ax.text(0,0,4,'T-ASV step count demo',color='r',fontsize='x-large')

receive_trigger = 0
receive_msg = []
pacing_detect_receive_trigger = 0
fall_thresh = 0.4
dist_receive_trigger = 0
number_of_steps = 0
zone_dur_list = [0,0]
fall_counter = 0
fall_1 = 0
fall_2 = 0
dur = 0
timer = 0
sit_dur = 0
walk_dur = 0
check_dur = 0
prev_dur = 0
detect = 0
fall_detection_trigger = False
past_dist = 0
new_steps = 0
check_disappear =[]
pacing_info = "NIL"

last_receive_count = 0

steps = 0
avg_height =[]
avg_distance =[]
center_one = (0,0)
center_two = (0,0)
distance_between_points = 0
x_last = []
y_last = []
z_last = []
z_total= []
while True:
    client.loop_start()
    client.subscribe("Points")
    client.subscribe("Pacing")
    client.subscribe("PacingDetect")
    client.subscribe("Distance")

    client.on_message = on_message
    #######


    if receive_trigger == 1:
        if timer == 0:
            start_time = datetime.now()
            timer = 1
        tmp_time = datetime.now()
        tmp_duration = tmp_time-start_time
        tmp_duration = tmp_duration.total_seconds()
        tmp_duration = int(math.floor(tmp_duration))
        dur = tmp_duration - prev_dur
        if detect == 0:
            if check_dur != dur:
                    walk_dur += dur
                    check_dur = dur
        #print(f"duration : {dur}")
        x = []
        y = []
        z = []
        max_height = [] 

        for i in range(len(receive_msg)):
            x.append(receive_msg[i][0])
            y.append(receive_msg[i][1])
            z.append(receive_msg[i][2])
            max_height.append(np.amax(z)) # get the max of z
        ax.scatter(x,y,z, c ='r', marker = 'o', s = 14)
        #print('mean of z: ', np.mean(z))
        # check if the mean <= Fall threshhold 
        receive_trigger = 0
        last_receive_count = 0
        # take 10 frames
        if len(x) > 10:
            x_last = x
            y_last = y
            z_last = z

            # for each 10 frame get the avg max
            
            avg_height = np.mean(max_height)

            #p1(x1,y1) ,p2(x2,y2)
            # center_two is a set
            # center two = new step
            center_two = (np.mean(x_last), np.mean(y_last))
            

            # update center one
            # point one = old step
            if center_one != center_two :
                #calculate the distance
                #distance = sqrt((x2-x1)^2 +  (y2-x1)^2)
                #the distance in meter
                # calculate the distance only if center one not (0,0)
                if center_one[0] != 0 and center_one[0] != 0:
                    distance_between_points = math.sqrt((center_two[0] - center_one[0])**2 + (center_two[1]-center_one[1])**2)
                    print ('distance_between_points: ', distance_between_points, 'm') # for debug only

                
            elif center_one == center_two:
                distance_between_points = 0

            # update the onle point
            center_one = center_two

        # calculate the number of steps
        if (float(avg_height) * 0.5 >= 0.6) and (distance_between_points >= 0.3) :
            number_of_steps+= round(distance_between_points/0.34)

        #print ('number of steps: ', number_of_steps) # for debug only
        # take the mean of last 10 frames
        print('avg max calc: ',avg_height)
        print('avg max np: ',np.amax(z_last))
        print('thresh: ',avg_height * 0.5)
        #print('Lying: ', np.amax(z_last) * 0.5)
        #print('min point: ', np.amin(z_last))
        #if np.mean(z_last) < np.amax(z_last) * 0.5:
        #if  np.mean(z_last) <= np.amax(z_last) * 0.5:
        if  (float(avg_height) * 0.5 <= fall_thresh) and (np.amax(z_last) < 0.7):
            # switch the trigger to on
            fall_detection_trigger = True
            #Check the fall detection # also check the region
            if(fall_detection_trigger==True):
                print('Fall detected!!')
                plt.figtext(0.60, 0.06, 'Fall: Detected', ha="left", fontsize=16, bbox={"facecolor":"red", "alpha":1.0, "pad":5})
                fall_counter+=1
                #time.sleep(3)
                plt.show(block=False)
                plt.pause(3)
                time.sleep(6)
                fall_detection_trigger = False

        if pacing_detect_receive_trigger == 1:
            pacing_info = pacing_detect_message
            pacing_detect_receive_trigger = 0

        if dist_receive_trigger == 1:
            if distance >= past_dist:
                dist_diff = distance - past_dist
                past_dist = distance
            else:
                dist_diff = distance - 0
                past_dist = 0
            steps = round(dist_diff/0.348)
            #check if the person is standing
            if(avg_height * 0.5 >= 0.6):
                new_steps += steps
                #print(f"steps: {steps} new steps: {new_steps}")

        receive_msg = []
        prev_dur = tmp_duration

    elif receive_trigger == 0:
        last_receive_count +=1
        if len(x_last)>0:
            for i in range (len(x_last)):
                if (-3< x_last[i] < -3 and 0<y_last[i]<3)  or (1 < x_last[i] < 3 and 0 < y_last[i] < 3):
                    check_disappear.append(x_last[i])
            if len(check_disappear) > 5 and last_receive_count > 2:
                ax.scatter(0,0,0, c ='w', marker = 'o', s = 14)
                #plt.figtext(0.70, 0.03, 'No Activity: ', ha="left", fontsize=28, bbox={"facecolor":"red", "alpha":1, "pad":5})
                check_disappear = []

            elif last_receive_count > 1:
                # check if the cloud points less than 0.3
                #if np.mean(z_last) <= 0.5:
                plt.figtext(0.60, 0.06, 'No Activity: ', ha="left", fontsize=16, bbox={"facecolor":"blue", "alpha":1, "pad":5})
                ax.scatter(x_last,y_last,z_last, c ='y', marker = 'o', s = 14)
 


    #textstr = "Pacing: %s\nDuration: %ss\nSteps: %d"%(pacing_info,walk_dur,new_steps)
    #textstr = "Pacing: %s\nSteps: %d"%(pacing_info,new_steps)
    #textstr = "Steps: %d"%(new_steps)

    # Pacing Text
    #plt.gcf().text(0.5, 0.1, textstr, fontsize=14)
    plt.figtext(0.25, 0.01, 'Steps: {}'.format(new_steps), ha="left", fontsize=16, bbox={"facecolor":"gray", "alpha":1.0, "pad":5})
    #plt.figtext(0.25, 0.01, textstr, ha="left", fontsize=20, bbox={"alpha":1.0, "pad":5})
    #plt.figtext(0.3, 0.9, 'T-ASV Steps Count Demo', ha="left", fontsize=12, bbox={"facecolor":"red", "alpha":0.5, "pad":5})
    #Fall counter feature
    plt.figtext(0.6, 0.01, 'Fall Counter: {}'.format(fall_counter), ha="left", fontsize=16, bbox={"facecolor":"gray", "alpha":1.0, "pad":5}) 
    #plt.figtext(0.25, 0.01, 'Steps: {}'.format(number_of_steps), ha="left", fontsize=16, bbox={"facecolor":"gray", "alpha":1.0, "pad":5})
    #plt.figtext(0.70, 0.03, 'Fall: NILL', ha="left", fontsize=28, bbox={"facecolor":"gray", "alpha":1.0, "pad":5})
    #plt.figtext(0.70, 0.05, ': ', ha="left", fontsize=28, bbox={"facecolor":"white", "alpha":0.5, "pad":5})


    plt.show(block=False)
    plt.subplots_adjust(bottom=0.2)

    plt.pause(0.0001)
    plt.cla()
    for txt in fig.texts:
        txt.set_visible(False)


    plt.style.use('dark_background')
    ax.set(xlim = (-3, 3), ylim = (0,6), zlim = (0,3))


    #ax.text(1, 2.4, 0, s='Living Room', color = 'g', fontsize = 'x-large')
    # Line Plotting for Sensor 
    ax.plot(x_sensor,top_sensor,z_sensor,'b') 
    ax.plot(x_sensor,bottom_sensor,z_sensor,'b')
    ax.plot(right_sensor,y_sensor,z_sensor,'b') 
    ax.plot(left_sensor,y_sensor,z_sensor,'b')


    # Line Plotting for room 
    #ax.plot(x_2,top,z_2,'black') 
    #ax.plot(x_2,bottom,z_2,'black')
    #ax.plot(right,y_2,z_2,'black') 
    #ax.plot(left,y_2,z_2,'black')
    #ax.text(0.5, 1.5, 0,'Living Room', fontsize=15)
    #print(receive_msg)
    #time.sleep(0.001)
    client.loop_stop()
