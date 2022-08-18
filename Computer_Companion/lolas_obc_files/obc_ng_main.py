"""
Internest 2022
LoLas NG onboard computer demo code
Deployed on raspberry pi + waveshare RS485 shield for testing

pip install RPi.GPIO

"""

import time
from src.logger import Logger
from src.drone import Drone
from src.lolas_interface import LoLasInterface
from src.trajectory_computer import TrajectoryComputer
from src.waypoints.waypoints_manager import WaypointsManager

import serial
import statistics
import sys

CONSTANT_SPEED = 0.3    # m/s
Z_CONSTANT_SPEED = 0.4  # m/s
YAW_RATE = 0.2    # rad/s
#change TARGET_Z_HOVERING_BEFORE_LAND from 1 meter to 0.05 meters == 2 inches?
TARGET_Z_HOVERING_BEFORE_LAND = 1.0  # m

PORT = "/dev/ttyS0"  # raspberry pi port that is mapped to handle the shield

INTERFACE_IMPLEMENTATION = "RS485"
#switch to True or False to enable/disable SITL/HITL
SIMULATE = False


def guidance():

    print("Waiting for offboard")

    # Wait for the drone to be switch to offbard mode
    # Or to be disarmed, or autopilot heart beat loss
    while drone.get_vehicle_reference().mode.name != "OFFBOARD":
        drone.send_frd_velocity(0, 0, 0, 0)#keeps drone still
        lolas_interface.fetch() #gets lolas messages and monitors heartbeat. fakes values if simulation mode
        time.sleep(0.2)#wait 2ms
        if not drone.get_armed_status() or not drone.check_heart_beat():#check arm & heartbeat
            print("Disarmed or no heart beat") #will let us know if changes occur
            return

    print("Starting logger")
    logger.start()

    guidance_step = "INIT"

    trajectory_computer = TrajectoryComputer()#instantiate the trajectory cpu

    mean_yaw = 0
    #gets all data from lolas interface
    while lolas_interface.lolas_is_alive \
            and drone.get_armed_status() \
            and drone.get_vehicle_reference().mode.name == "OFFBOARD"\
            and drone.get_connection_status():

        # print("Status : ", drone.get_connection_status())
        # print("Heart beat check : ", drone.check_heart_beat())

        lolas_interface.fetch()

        if lolas_interface.current_mode == 2:  # ENABLED

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

                # Moving forward with guidance if the yaw has been computed at least 10 times during the INIT phase
                # retrying INIT otherwise
                if len(yaw_buffer) > 5:
                    mean_yaw = statistics.mean(yaw_buffer)

                    trajectory_computer.compute_base_coordinates(lolas_interface.lolas_x, lolas_interface.lolas_y, mean_yaw)

                    logger.log(guidance_step, trajectory_computer.get_base_x_frd(),
                               trajectory_computer.get_base_y_frd(), 0, mean_yaw, 0, 0, 0, 0)
                    waypointsManager.reset_waypoints_index()
                    guidance_step = "MOVE TO WAYPOINT"
                else:
                    print('WARNING COULD NOT INIT : POOR YAW ESTIMATION')
                    print('RETRYING INIT')

            elif guidance_step == "HOLD":
                # Waiting step, can be used as a transition without sending specific setpoints
                # Weak monitoring about current position : can route the execution back to MOVE TO WAYPOINT
                # if the drone drifted too much
                print("Guidance : HOLD")

                drone.send_frd_velocity(0, 0, 0, 0)
                lolas_interface.fetch()

                # Update the waypoint position relatively to the drone's current position
                if lolas_interface.lolas_x != 0 and lolas_interface.lolas_y != 0 and lolas_interface.yaw_update == 1:
                    trajectory_computer.compute_wpt_coordinates(lolas_interface.lolas_x, lolas_interface.lolas_y,
                                                                lolas_interface.lolas_yaw, waypoint.X, waypoint.Y)
                # Compute the current distance to the objective (waypoint)
                dist = trajectory_computer.compute_distance_to_waypoint(lolas_interface.lolas_x,
                                                                        lolas_interface.lolas_y, waypoint.X, waypoint.Y)
                logger.log(guidance_step,
                           trajectory_computer.get_wpt_x_frd(), trajectory_computer.get_wpt_y_frd(), dist,
                           mean_yaw, 0, 0, 0, 0)

                drone.send_frd_velocity(0, 0, 0, 0)

                # The drone has drifted away, going back to MOVE TO WAYPOINT to converge
                if dist > waypoint.tolerance and not SIMULATE:
                    guidance_step = "MOVE TO WAYPOINT"

                else:
                    # Selecting next waypoint
                    waypointsManager.increment_waypoint_index()
                    # wait a bit before continuing to next waypoint
                    start = time.time()
                    drone.send_frd_velocity(0, 0, 0, 0)
                    while now - start < 2:
                        now = time.time()
                        drone.send_frd_velocity(0, 0, 0, 0)
                        lolas_interface.fetch()
                        logger.log(guidance_step, trajectory_computer.get_wpt_x_frd(),
                                   trajectory_computer.get_wpt_y_frd(), dist, mean_yaw, 0, 0, 0, 0)
                        time.sleep(0.1)

                    drone.send_frd_velocity(0, 0, 0, 0)

                    # Finally branch to either the next waypoint, or to possible scenario terminations (hold or land)
                    if waypointsManager.has_reached_last_waypoint():
                        # au choix land ou hold
                        if waypointsManager.landing_required:
                            guidance_step = "LAND"
                        else:
                            guidance_step = "HOLD"
                    else:
                        guidance_step = "MOVE TO WAYPOINT"
                    drone.send_frd_velocity(0, 0, 0, 0)

            elif guidance_step == "MOVE TO WAYPOINT":
                # During this step, the drone will converge toward the current waypoint
                # It will then assess if the waypoint is reached or not
                drone.send_frd_velocity(0, 0, 0, 0)
                print("Guidance : WAYPOINT ", waypointsManager.index+1, " / ", waypointsManager.how_many_waypoints)

                waypoint_reached = False

                if SIMULATE:
                    start = time.time()

                # first, get current waypoint definition
                waypoint = waypointsManager.get_current_waypoint()
                stability_counter = 0

                # while the waypoint is not reached and the conditions are not met for long enough
                # and the communication with the autopilot is active
                # continue
                while not (waypoint_reached and stability_counter >= 30) and drone.check_heart_beat():
                    # get last info from lolas
                    lolas_interface.fetch()

                    if SIMULATE:
                        frd_z_offset = -waypoint.Z / 1000 + (lolas_interface.lolas_z / 1000)
                        lolas_interface.simulate_correct_z(frd_z_offset)

                    # default setpoints are 0
                    setpoint_vx = 0
                    setpoint_vy = 0
                    setpoint_yaw = 0

                    # Update the waypoint position relatively to the drone's current position
                    if lolas_interface.lolas_x != 0 and lolas_interface.lolas_y != 0 and lolas_interface.yaw_update == 1:
                        trajectory_computer.compute_wpt_coordinates(lolas_interface.lolas_x, lolas_interface.lolas_y,
                                                                     lolas_interface.lolas_yaw, waypoint.X, waypoint.Y)
                        setpoint_yaw = trajectory_computer.get_setpoint_yaw_sign(lolas_interface.lolas_yaw, waypoint.yaw) * YAW_RATE

                    # Compute the current distance to the objective (waypoint)
                    dist = trajectory_computer.compute_distance_to_waypoint(lolas_interface.lolas_x,
                                                                        lolas_interface.lolas_y, waypoint.X, waypoint.Y)

                    # If the drone is not in the XY tolerance zone, compute the setpoints to get closer
                    if dist > waypoint.tolerance:
                        setpoint_vx = trajectory_computer.get_setpoint_sign(trajectory_computer.get_wpt_x_frd()) * CONSTANT_SPEED
                        setpoint_vy = trajectory_computer.get_setpoint_sign(trajectory_computer.get_wpt_y_frd()) * CONSTANT_SPEED
                        # In simulation, we fake that the drone is effectively getting closer
                        if SIMULATE:
                            lolas_interface.simulate_closing_drone()
                            if time.time()-start > 6:
                                waypoint_reached = True
                                stability_counter = 30
                                print("Waypoint ", waypointsManager.index + 1, " reached. Stability : ",
                                      stability_counter)
                    # If the conditions are met, declare that the waypoint is reached and assess the stability
                    elif dist <= waypoint.tolerance and dist != 0 and drone.is_at_right_altitude(-lolas_interface.lolas_z, waypoint.Z / 1000, True):
                        waypoint_reached = True
                        stability_counter += 1
                        print("Waypoint ", waypointsManager.index+1, " reached. Stability : ", stability_counter)

                    # If the lolas Z information is available, compute a new setpoint (may be 0)
                    # And send all the velocity setpoints
                    if lolas_interface.alti_update == 1:
                        # offset_frd = drone.correct_altitude(TARGET_Z_HOVERING, lolas_interface.lolas_z)
                        setpoint_vz = trajectory_computer.get_setpoint_vz_sign(waypoint.Z / 1000, lolas_interface.lolas_z) * Z_CONSTANT_SPEED
                        drone.send_frd_velocity(setpoint_vx, setpoint_vy, setpoint_vz, setpoint_yaw)
                    else:
                        drone.send_frd_velocity(0, 0, 0, setpoint_yaw)

                    logger.log(guidance_step+str(waypointsManager.index+1),
                               trajectory_computer.get_wpt_x_frd(), trajectory_computer.get_wpt_y_frd(), dist,
                               mean_yaw, setpoint_vx, setpoint_vy, setpoint_vz, setpoint_yaw)

                    time.sleep(0.1)

                # Once the waypoint is reached for long enough, go to the HOLD step before next waypoint
                guidance_step = "HOLD"
                drone.send_frd_velocity(0, 0, 0, 0)

            elif guidance_step == "LAND":
                # This step stabilizes the drone low over the base while keeping the drone at the center of it (X=Y=0)
                # And then enables the final descent (not implemented here)
                drone.send_frd_velocity(0, 0, 0, 0)
                print("Guidance : LAND")
                while not drone.is_at_right_altitude(-lolas_interface.lolas_z, TARGET_Z_HOVERING_BEFORE_LAND, True) and drone.get_vehicle_reference().mode.name == "OFFBOARD":
                    if SIMULATE:
                        frd_z_offset = -TARGET_Z_HOVERING_BEFORE_LAND + (lolas_interface.lolas_z / 1000)
                        lolas_interface.simulate_correct_z(frd_z_offset)
                    else:
                        lolas_interface.fetch()

                    setpoint_vx = 0
                    setpoint_vy = 0

                    if lolas_interface.lolas_x != 0 and lolas_interface.lolas_y != 0 and lolas_interface.yaw_update == 1:
                        trajectory_computer.compute_base_coordinates(lolas_interface.lolas_x, lolas_interface.lolas_y,
                                                                     lolas_interface.lolas_yaw)
                    dist = trajectory_computer.compute_distance_to_base(lolas_interface.lolas_x,
                                                                        lolas_interface.lolas_y)

                    if dist > waypoint.tolerance:
                        setpoint_vx = trajectory_computer.get_setpoint_sign(trajectory_computer.get_base_x_frd()) * CONSTANT_SPEED
                        setpoint_vy = trajectory_computer.get_setpoint_sign(trajectory_computer.get_base_y_frd()) * CONSTANT_SPEED

                    if lolas_interface.alti_update == 1:
                        # offset_frd = drone.correct_altitude(TARGET_Z_HOVERING, lolas_interface.lolas_z)
                        setpoint_vz = trajectory_computer.get_setpoint_vz_sign(TARGET_Z_HOVERING_BEFORE_LAND, lolas_interface.lolas_z) * Z_CONSTANT_SPEED
                        drone.send_frd_velocity(setpoint_vx, setpoint_vy, setpoint_vz, 0)

                        logger.log(guidance_step,
                                   trajectory_computer.get_base_x_frd(), trajectory_computer.get_base_y_frd(), dist,
                                   mean_yaw, setpoint_vx, setpoint_vy, setpoint_vz, 0)
                    else:
                        drone.send_frd_velocity(0, 0, 0, 0)
                    time.sleep(0.1)

                print("LAND ALTITUDE REACHED, LANDING")
                # Several options here
                # First one would be to ask the autopilot to manage the landing
                # drone.vehicle.mode = "LAND"
                # Another one would be to rely on lolas and the OBC
                while lolas_interface.weight_on_wheel!=1:
                # Sending a Z setpoint until touch down
                    Z_CONSTANT_SPEED_FOR_LANDING = 0.2
                    setpoint_vz = trajectory_computer.get_setpoint_vz_sign(TARGET_Z_HOVERING_BEFORE_LAND, lolas_interface.lolas_z) * Z_CONSTANT_SPEED_FOR_LANDING
                    drone.send_frd_velocity(setpoint_vx, setpoint_vy, setpoint_vz, 0)

                # For safety : should be doubled with a forced disarm based on a timer for instance
                if drone.disarm_if_required(lolas_interface.last_waypoint_reached(), lolas_interface.weight_on_wheel, lolas_interface.lolas_z):
                     print("--- REQUESTING DISARM ---")
                

            else:
                print('WARNING - UNKNOWN GUIDANCE STEP')

        elif lolas_interface.current_mode == 3:  # PAIRING
            print("Pairing ongoing : sending hold FRD setpoints")
            drone.send_frd_velocity(0, 0, 0, 0)
            time.sleep(0.1)

        # drone.print_flight_monitoring()
        lolas_interface.print_lolas_info()

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
    # Starting the logger
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
