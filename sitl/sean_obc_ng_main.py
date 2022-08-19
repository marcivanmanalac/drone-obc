"""
Internest 2022
LoLas NG onboard computer demo code
Deployed on raspberry pi + waveshare RS485 shield for testing

pip install RPi.GPIO

"""

import time
from tokenize import PseudoExtras
from turtle import pos
from src.logger import Logger
from src.drone import Drone
from src.lolas_interface import LoLasInterface
from src.trajectory_computer import TrajectoryComputer
from src.waypoints.waypoints_manager import WaypointsManager

import serial
import statistics
import sys

import math #sean
import keyboard #sean


CONSTANT_SPEED                  = 0.3    # m/s
Z_CONSTANT_SPEED                = 0.4  # m/s
YAW_RATE                        = 0.2    # rad/s

TARGET_Z_HOVERING_BEFORE_LAND   = 1.0  # m

#PORT = "/dev/ttyS0"  # raspberry pi port that is mapped to handle the shield
PORT = "/dev/serial0" #sean

INTERFACE_IMPLEMENTATION = "RS485"

#SIMULATE = False
SIMULATE = True #sean


def guidance():

    print("Waiting for offboard")

    # Wait for the drone to be switch to offbard mode
    # Or to be disarmed, or autopilot heart beat loss
    while drone.get_vehicle_reference().mode.name != "OFFBOARD":
        drone.send_frd_velocity(0, 0, 0, 0)
        lolas_interface.fetch()
        time.sleep(0.2)
        #if not drone.get_armed_status() or not drone.check_heart_beat():
        #    print("Disarmed or no heart beat")
        #    return

        #print(drone.vehicle.location.local_frame) #sean

    print("Starting logger")
    logger.start()

    guidance_step = "INIT"

    trajectory_computer = TrajectoryComputer()

    mean_yaw = 0

    first_loop = True

    # main guidance loop
    while True:

        # print("Status : ", drone.get_connection_status())
        # print("Heart beat check : ", drone.check_heart_beat())

        lolas_interface.fetch()

        # lolas enabled, drone armed, offboard mode, drone connected
        if lolas_interface.current_mode == 2                                \
                and drone.get_armed_status()                                \
                and drone.get_vehicle_reference().mode.name == "OFFBOARD"   \
                and drone.get_connection_status():

            if guidance_step == "INIT":
                # This step helps to check the yaw availability in the current conditions,
                # as it will be intensively used for further computation
                print("Guidance : INIT")
                mean_yaw = 0
                start = time.time()
                now = start
                yaw_buffer = list()
                while now-start < 2:  # checking yaw availability during 2 seconds
                    now = time.time()
                    lolas_interface.fetch()
                    if lolas_interface.yaw_update != 0:
                        yaw_buffer.append(lolas_interface.lolas_yaw)
                    drone.send_frd_velocity(0, 0, 0, 0)
                    time.sleep(0.1)
                    logger.log(guidance_step, 0, 0, 0, mean_yaw, 0, 0, 0, 0)

                # Moving forward with guidance if the yaw has been computed at least 5 times during the INIT phase
                # retrying INIT otherwise
                if len(yaw_buffer) > 5:
                    mean_yaw = statistics.mean(yaw_buffer)
                    ### mean could be messed up if yaw is jumping between 0 and 360...

                    trajectory_computer.compute_base_coordinates(lolas_interface.lolas_x, lolas_interface.lolas_y, mean_yaw)

                    logger.log(guidance_step, trajectory_computer.get_base_x_frd(),
                               trajectory_computer.get_base_y_frd(), 0, mean_yaw, 0, 0, 0, 0)
                    waypointsManager.reset_waypoints_index()
                    guidance_step = "MOVE TO WAYPOINT"
                else:
                    print('WARNING COULD NOT INIT : POOR YAW ESTIMATION')
                    print('RETRYING INIT')


            #==========================================================================================================================================
            #==========================================================================================================================================
            #==========================================================================================================================================
            
            # sean
            elif guidance_step == "MOVE TO WAYPOINT": 
                # During this step, the drone will go to the waypoint
                # It will then assess if the waypoint is reached or not
                # putting all functions in this code so I don't have to create multiple sean files / mess with other files

                # initialize variables on first loop
                if first_loop:
                    print("Guidance : MOVE TO WAYPOINT")
                    # reset drone commands
                    drone.send_frd_velocity(0, 0, 0, 0)

                    # user variables

                    # number of points to average for smoothing (bigger = smoother but less responsive)
                    # lolas captures data at around 10Hz (10 points per second) *I think? at least the logger does*
                    # 4 *SEEMS* like a good balance looking at our lab test graph
                    moving_average_period   = 4

                    # desired position in m (probably (0,0), z can be changed)
                    desired_x               = 0                 # m
                    desired_y               = 0                 # m
                    desired_z               = 10                # m

                    # max speeds
                    velocity_max_xy         = 5                 # m/s
                    velocity_max_z          = 1                 # m/s

                    # PID coefficients - need to tune
                    kp_xy                   = 0.35
                    ki_xy                   = 0.001  #0.001
                    kd_xy                   = 0.1
                    kp_z                    = 1
                    ki_z                    = 0
                    kd_z                    = 0

                    # waypoint tolerance for stability check
                    tolerance_xy            = 0.2               # m
                    tolerance_z             = 0.2               # m

                    # other variables
                    error_xy                = 0                 # m
                    error_z                 = 0                 # m
                    last_error_xy           = 0                 # m
                    last_error_z            = 0                 # m
                    derivative_xy           = 0
                    derivative_z            = 0
                    integral_xy             = 0
                    integral_z              = 0
                    integral_limit_xy       = 10
                    integral_limit_z        = 10
                    velocity_x              = 0                 # m/s
                    velocity_y              = 0                 # m/s
                    velocity_z              = 0                 # m/s
                    yaw_rate                = 0                 # rad/s?
                    position_x_list         = []
                    position_y_list         = []
                    position_z_list         = []
                    last_non_zero_z         = 0
                    zero_counter_z          = 0

                    # variables initialized
                    first_loop = False

                    start = time.time()

                    from simple_pid import PID
                    pid_xy = PID()
                    pid_xy.setpoint = 0
                    pid_xy.sample_time = 0.01
                    pid_xy.tunings = (1,0,0)
                    pid_xy.output_limits = (-5,5)
                
                # save time before loop starts
                ### used to measure loop time
                #start = time.time()

                #==========================
                #===== Centering Loop =====
                #==========================

                # update lolas status
                lolas_interface.fetch()
                
                # get current position (local NED from simulator)
                if SIMULATE:
                    ####### CHANGE THIS LATER to match coordinate systems
                    position_x          =  drone.vehicle.location.local_frame.north
                    position_y          =  drone.vehicle.location.local_frame.east
                    position_z          = -drone.vehicle.location.local_frame.down
                    yaw                 =  drone.vehicle.heading

                    # simulate moving platform in x direction
                    #desired_x      += 0.1
                    #print(desired_x, "     ", position_x)

                # get current position from lolas (convert mm to m)
                else:
                    ####### CHANGE THIS LATER - match coordinate system
                    #position_y          = lolas_interface.lolas_x / 1000
                    #position_x          = lolas_interface.lolas_y / 1000
                    position_z          = lolas_interface.lolas_z / 1000
                    yaw                 = lolas_interface.lolas_yaw

                    # calculate base coordinates relative to drone
                    trajectory_computer.compute_base_coordinates(lolas_interface.lolas_x, lolas_interface.lolas_y, lolas_interface.lolas_yaw)
                    position_x = trajectory_computer.get_base_x_frd()
                    position_y = trajectory_computer.get_base_y_frd()
                    #print(position_x)
                
                #==========================#
                #===== Moving Average =====#
                #==========================#
                # take moving average to smooth out data points (lolas data requires smoothing)
                ### lab test data shows large amounts of noise
                ### https://www.geeksforgeeks.org/how-to-calculate-moving-averages-in-python/
                
                # add current position to a list
                position_x_list.append(position_x)
                position_y_list.append(position_y)
                
                # dealing with cases where lolas z is giving 0 (lab data shows frequent 0s)
                ### too frequent that it significantly affects the moving average
                if position_z == 0:
                    zero_counter_z     += 1
                    # last 5+ z data points were 0 (too much error)
                    if zero_counter_z > 5:
                        # artificially set current position to target z
                        ### stop moving in z direction to avoid crash
                        position_z      = desired_z
                    else:
                        # artificially set current position to last-known non-zero position
                        position_z      = last_non_zero_z
                # z != 0: reset counter and set last-known non-zero position to current position
                else:
                    last_non_zero_z     = position_z
                    zero_counter_z      = 0

                position_z_list.append(position_z)

                # list size depends on # of points to average (moving_average_period)
                # delete 1st entry to keep list only to the required size
                while len(position_x_list) > (moving_average_period):
                    position_x_list.pop(0)
                while len(position_y_list) > (moving_average_period):
                    position_y_list.pop(0)
                while len(position_z_list) > (moving_average_period):
                    position_z_list.pop(0)

                # calculate moving averages (sum of the last period# of positions / period#)
                ### round to 3 digits
                moving_average_x        = round(sum(position_x_list) / moving_average_period, 3)
                moving_average_y        = round(sum(position_y_list) / moving_average_period, 3)
                moving_average_z        = round(sum(position_z_list) / moving_average_period, 3)
                
                # use moving average for position
                ### can replace moving_average above with position and remove this part
                ### this makes for easier testing to compare without moving average
                position_x              = moving_average_x
                position_y              = moving_average_y
                position_z              = moving_average_z


                # calculate distance from landing pad
                dist_xy                 = math.sqrt((position_x * position_x) + (position_y * position_y))
                dist_z                  = abs(position_z)

                #=====================================
                # PID Controller with simple-PID
                #=====================================
                velocity_xy = pid_xy(dist_xy)
                print(velocity_xy)



                #==========================
                #===== PID Controller =====
                #==========================
                # might change to use simple-pid Python library (https://pypi.org/project/simple-pid/)
                # or implement this code in its own class

                # calculate error from desired position
                error_x                     = desired_x - position_x
                error_y                     = desired_y - position_y
                error_z                     = desired_z - position_z

                # calculate xy distance from desired position (0,0)
                error_xy = math.sqrt((error_x * error_x) + (error_y * error_y))   # distance equation with (0,0) desired coordinates
                
                # integral
                integral_xy                += error_xy
                integral_z                 += error_z

                # limit integral value from getting too large
                if integral_xy > integral_limit_xy:
                    integral_xy             = integral_limit_xy
                if integral_z  > integral_limit_z:
                    integral_z              = integral_limit_z

                # derivative
                derivative_xy               = error_xy - last_error_xy
                derivative_z                = error_z  - last_error_z
                
                # set previous error = current error
                last_error_xy               = error_xy
                last_error_z                = error_z

                # don't move drone if xy error is within tolerance
                ### helps filter out lolas noise
                if error_xy < tolerance_xy:
                    velocity_x              = 0
                    velocity_y              = 0
                # calculate PID outputs for x and y
                else:
                    # PID output for total xy velocity
                    #velocity_xy             = (error_xy * kp_xy) + (integral_xy * ki_xy) + (derivative_xy * kd_xy)

                    # limit max velocity to set value
                    #if velocity_xy > velocity_max_xy:
                    #    velocity_xy         = velocity_max_xy
                    
                    # calculate x and y components for velocity and direction
                    if error_y < 0: 
                        # add pi to correct quadrants 1 and 4 (+x+y = Q1, -x+y = Q4)
                        velocity_x          = velocity_xy * math.sin(math.pi + math.atan(error_x/error_y)) 
                        velocity_y          = velocity_xy * math.cos(math.pi + math.atan(error_x/error_y))
                    # avoid division by 0
                    elif position_y == 0:
                        velocity_y          = 0
                    # error_y > 0
                    else:
                        velocity_x          = velocity_xy * math.sin(math.atan(error_x/error_y)) 
                        velocity_y          = velocity_xy * math.cos(math.atan(error_x/error_y))
                
                # don't move drone if z error is within tolerance
                ### helps filter out lolas noise
                ### error_z can be negative but error_xy is distance
                if abs(error_z) < tolerance_z:
                    velocity_z              = 0
                # calculate PID output for z
                else:
                    # PID output for z velocity
                    velocity_z              = (error_z  * kp_z)  + (integral_z  * ki_z)  + (derivative_z  * kd_z)
                    
                    # limit max velocity to set value
                    if velocity_z  > velocity_max_z:
                        velocity_z          = velocity_max_z
                    if velocity_z  < -velocity_max_z:
                        velocity_z          = -velocity_max_z

                #print("x: ", "{:.5f}".format(velocity_x), "  y: ", "{:.5f}".format(velocity_y), "  z: ", "{:.5f}".format(velocity_z))

                # don't send z velocity if lolas Z data isn't available
                if lolas_interface.alti_update == 0:
                    velocity_z              = 0

                # send command to drone (using local NED coordinate system)
                #drone.send_ned_velocity(velocity_x, velocity_y, -velocity_z, yaw_rate)
                velocity_z = 0
                
                drone.send_frd_velocity(velocity_x, velocity_y, velocity_z, yaw_rate)
                
                if error_xy < tolerance_xy and abs(error_z) < tolerance_z:
                    print("waypoint reached. stability counter: ", stability_counter)
                    stability_counter  += 1
                    if stability_counter >= 30:
                        #guidance_step       = "LAND"
                        guidance_step       = "MOVE TO WAYPOINT"
                else:
                    stability_counter       = 0


                # keyboard inputs for PID tuning
                if keyboard.is_pressed("q"):
                    kp_xy += .01
                    print("kp_xy = ", kp_xy)
                elif keyboard.is_pressed("a"):
                    kp_xy -= .01
                    if kp_xy < 0:
                        kp_xy = 0
                    print("kp_xy = ", kp_xy)
                elif keyboard.is_pressed("w"):
                    ki_xy += .001
                    print("ki_xy = ", ki_xy)
                elif keyboard.is_pressed("s"):
                    ki_xy -= .001
                    if ki_xy < 0:
                        ki_xy = 0
                    print("ki_xy = ", ki_xy)
                elif keyboard.is_pressed("e"):
                    kd_xy += .01
                    print("kd_xy = ", kd_xy)
                elif keyboard.is_pressed("d"):
                    kd_xy -= .01
                    if kd_xy < 0:
                        kd_xy = 0
                    print("kd_xy = ", kd_xy)
                elif keyboard.is_pressed("r"):
                    desired_x = 10
                    print("des_x = ", desired_x)
                elif keyboard.is_pressed("f"):
                    desired_x = 0
                    print("des_x = ", desired_x)

                #print("time: ", time.time() - start)

                # slow down loop (0.05s for ~20 Hz loop)
                ### 0.1s chosen by internest
                ###     might add in timer for consistent loop timings
                ###     e.g. if I want 0.5 second loops, measure the time it 
                ###     takes for loop to complete and sleep for the remainder
                ###         time.sleep(0.5 - loop_time)
                ###     or add dt term for derivative and integral
                ###         integral += error * dt
                ###         derivative = (error - last_error) / dt
                time.sleep(0.05)



            #==========================================================================================================================================
            #==========================================================================================================================================
            #==========================================================================================================================================


            elif guidance_step == "LAND":
                # This step stabilizes the drone low over the base while keeping the drine at the center of it (X=Y=0)
                # And then enables the final descent (not implemented here)
                drone.send_frd_velocity(0, 0, 0, 0)
                print("Guidance : LAND")
                

                print("LAND ALTITUDE REACHED, LANDING")
                # Several options here
                # First one would be to ask the autopilot to manage the landing
                drone.vehicle.mode = "LAND"
                # Another one would be to rely on lolas and the OBC
                # Sending a Z setpoint until touch down
                # Disarming once WoW is 1 (lolas proximity sensor has to be enabled)
                # For safety : should be doubled with a forced disarm based on a timer for instance
                # if drone.disarm_if_required(lolas_interface.last_waypoint_reached(),
                #                             lolas_interface.weight_on_wheel, lolas_interface.lolas_z):
                #     print("--- REQUESTING DISARM ---")

            else:
                print('WARNING - UNKNOWN GUIDANCE STEP')

        elif lolas_interface.current_mode == 3:  # PAIRING
            print("Pairing ongoing : sending hold FRD setpoints")
            drone.send_frd_velocity(0, 0, 0, 0)
            time.sleep(0.5)
        else:
            # stop drone
            drone.send_frd_velocity(0, 0, 0, 0)
            # print status to see why guidance isn't running
            print ( "drone armed status: "      ,   drone.get_armed_status(),                   \
                    "    ",                                                                     \
                    "flight mode: "             ,   drone.get_vehicle_reference().mode.name,    \
                    "    ",                                                                     \
                    "connection status: "       ,   drone.get_connection_status())
            time.sleep(0.5)

        # drone.print_flight_monitoring()
        # lolas_interface.print_lolas_info()

    
    ### this part won't run right now since I set the while loop to true

    # Exiting the while loop
    print("Stopping setpoints generation")

    # If the while loop ended because of lolas (e.g. heart beat lost),
    # we maintain the drone in offboard mode with steady setpoints
    # until a further notice (custom logic to be placed here)
    if not lolas_interface.lolas_is_alive:
        while drone.get_vehicle_reference().mode.name == "OFFBOARD" and drone.get_armed_status():
            print("[CRITICAL] LOLAS IS DOWN : TAKE BACK CONTROL !")
            drone.send_frd_velocity(0, 0, 0, 0)
            time.sleep(0.2)

print('Loading waypoints...')
waypointsManager = WaypointsManager()

# Instantiating the drone interface
# Trying the connect to the drone, with the given connection context (see the drone class for further details)

drone = Drone("raspberry-serial")
#drone = Drone("px4-sitl")
#drone = Drone("px4")
#drone = Drone("copter-sitl")

try:
    while not drone.get_connection_status():
        try:
            print("Trying to reach the vehicle...", )
            drone.connect()
        except:
            print("Retrying....")
            time.sleep(2)
            pass
    # if not drone.get_connection_status():
    #     print("Impossible to establish connexion @ " + drone.get_connection_settings())

    # Opening lolas interface
    try:
        lolas_interface = LoLasInterface(PORT, INTERFACE_IMPLEMENTATION, SIMULATE)
    except (OSError, serial.SerialException):
        raise ()
        print("Unable to join LoLas, exiting...")
        drone.end_connection()
        sys.exit(0)
    # Create the logger object
    logger = Logger(drone.get_vehicle_reference(), lolas_interface, False)

    print("Waiting for the drone to be armed")
    while not drone.get_armed_status():
        lolas_interface.msg_factory.free_incoming_messages()
        time.sleep(0.3)

    # Once the drone is armed, get ready to start guidance
    if drone.get_armed_status():
        guidance()
        lolas_interface.disconnect()
        print("Stopping logger")
        logger.stop()

    print("Disconnecting the vehicle")
    drone.end_connection()

# User interrupt using CTRL-C
except KeyboardInterrupt:
    logger.stop()
    drone.end_connection()
    lolas_interface.disconnect()
