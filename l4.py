from pymavlink import mavutil
from time import sleep

print("Setting up MAVLink Connection")
sleep(1.5)
# Setup MAVLink to connect on udp 127.0.0.1:14552
conn = mavutil.mavlink_connection("udp:127.0.0.1:14552", autoreconnect=True, 
source_system=1, force_connected=False, 
source_component=mavutil.mavlink.MAV_COMP_ID_LOG)

# wait for the heartbeat msg to find the system ID
while True:
    if conn.wait_heartbeat(timeout=0.5) != None:
        # Got a heartbeat from remote MAVLink device, good to continue
        break

print("Got Heartbeat from ArduPilot (system {0} component {1})".format(conn.target_system,
                                                                 conn.target_system))

while True:
    msg = conn.recv_match(blocking=True, timeout=0.5)
    if msg:
        if msg.get_type() == 'STATUSTEXT':
            #print STATUSTEXT packet text
            print(msg.text)
        #print(msg.get_type()) //Uncomment to see messages coming through
