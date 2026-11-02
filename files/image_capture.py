# take image sapmle for dataset labeling
###########################
from picamera import Color
from picamera import PiCamera
from time import sleep
import datetime
from datetime import datetime as dt

###########################
# Initiate the camera module with pre-defined settings.
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 15

def capture_photo(file_capture, text):
    
    # Add date as timestamp on the generated files.
    camera.annotate_foreground = Color('green')
    camera.annotate_foreground = Color('black')
    camera.annotate_text = text
    # Capture an image as the thumbnail.
    sleep(5)
    camera.capture(file_capture)
    print("\r\nImage Captured! \r\n")

##############################################################

def capture_video(file_capture, text,rec_time):
    start = dt.now() # start time
    camera.annotate_background = Color('green')
    camera.annotate_foreground = Color('black')
    camera.start_recording(file_capture)
    print("recording ...")
    while (dt.now() - start).seconds < rec_time:
        camera.annotate_text = dt.now().strftime("%H:%M:%S %D")
        #sleep(rec_time)
        camera.wait_recording(0.2)
    print('finished recording ...')
    print("vid saved in {} ...".format(file_capture))
    camera.stop_recording()
# Get the current date as the timestamp to generate unique file names.

'''
while True:
    date = datetime.datetime.now().strftime('%m-%d-%Y_%H.%M.%S')
    capture_img_path = 'data/images/img_' + date + '.jpg'
    capture_vid_path = 'data/images/vid_' + date + '.h264'
    capture_photo(capture_img_path, date)
    #sleep(20)
'''

x = input('Enter recording time in min ? ')
rec_time = int(x) * 60 # 20 min
date = datetime.datetime.now().strftime('%m-%d-%Y_%H.%M.%S')
capture_vid_path = '/home/pi/mmWave-People-Counting/mmWave_ML_detection/data/images/vid_' + date + '.h264'
capture_video(capture_vid_path, date,rec_time)
###########################################