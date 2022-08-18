#This is a test program for sending from the pi to the gcs via udp ethernet

#from mavlink docs
from pymavlink import mavutil

# Start a connection listening to a UDP port
the_connection = mavutil.mavlink_connection('udp:169.254.4.198:14550')

# Wait for the first heartbeat
#   This sets the system and component ID of remote system for the link
the_connection.wait_heartbeat()
print("Heartbeat from system (system %u component %u)" % (the_connection.target_system, the_connection.target_component))

# Once connected, use 'the_connection' to get and send messages
while 1:
    #this displays all of the data
    #msg = the_connection.recv_match(blocking=True)

    #this requests ALL data streams
    the_connection.mav.request_data_stream_send(the_connection.target_system,the_connection.target_component,mavutil.mavlink.MAV_DATA_STREAM_ALL,args.rate,1)
    print(msg)
