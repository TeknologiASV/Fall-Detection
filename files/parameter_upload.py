import serial
import time
import numpy as np


CLIport = {}
Dataport = {}
byteBuffer = np.zeros(2**15,dtype = 'uint8')
byteBufferLength = 0;

def serialConfig(configFileName):
    # Open the serial ports for the configuration and the data ports
    # Raspberry pi
    global CLIport
    global Dataport
    CLIport = serial.Serial('/dev/ttyUSB0', 115200)
    Dataport = serial.Serial('/dev/ttyUSB1', 921600)
    # Read the configuration file and send it to the board
    config = [line.rstrip('\r\n') for line in open(configFileName)]
    for i in config:
        CLIport.write((i+'\n').encode())
        print(i)
        time.sleep(0.01)
    return CLIport, Dataport







configFileName = 'chirp_configs/ISK_6m_default.cfg'
serialConfig(configFileName)