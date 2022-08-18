#This is a generic script for logging sensor data from a sensor connected to a raspberry pi.
#To run this as a background process on the CLI, type 'python3 file_write_TSM.py &'
#type 'kill -9' followed by PID number to terminate process

#The script does the following.
#1)Creates a file for the sensor data onboard the computer companion
#2)Reads the incoming Serial data and stores it in a variable
#3)Creates a mavlink packet to forward to the ardupilot flight controller using pymavlink.

#!/usr/bin/env python
import time
import serial
import datetime
from os.path import exists
from pymavlink import mavutil

########Naming and creating file for Sensor Log################
dt =  str(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
filename = 'SENSOR_SAMPLE' + dt +'.txt'
f = open('PATH/TO/FILE'+filename , 'w')

#Set Up Serial Port for the sensor
#Ensure you are using the correct header name in '/dev' which the component is plugged in to.
#If the ETHUSB Hub Hat is attached, the ttyUSB number sometimes changes between zero and one.
ser = serial.Serial(
        '/dev/ttyUSB0',
        baudrate = 115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
)

# Setup MAVLink to connect on udp 127.0.0.1:14550
conn = mavutil.mavlink_connection("udp:127.0.0.1:14550", autoreconnect=True, source_system=self.source_system, force_connected=False, source_component=mavutil.mavlink.MAV_COMP_ID_PERIPHERAL)

# wait for the heartbeat msg to find the system ID
while True:
    if conn.wait_heartbeat(timeout=0.5) != None:
        # Got a heartbeat from remote MAVLink device, good to continue
        break

#The program will continue to write into the file until it is terminated.
while 1:
    data = str(ser.read(100))
    #debugs printer
    print(data)
    #writes to MAVLink as a STATUSTEXT message, encoded as ASCII
    conn.mav.statustext_send(mavutil.mavlink.MAV_SEVERITY_INFO, data.encode())


f.close()
