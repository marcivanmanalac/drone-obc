#from dronekit-python docs
from dronekit import connect

# Connect to the vehicle (in this case a UDP endpoint)

#Pi side to FC
#vehicle = connect('/dev/Serial0',wait_ready=True, baud=57600)

#GCS side
vehicle = connect('com7', baud=57600)
