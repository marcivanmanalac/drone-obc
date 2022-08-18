from dronekit import *


class Drone:
    """
    This class provides an abstracted interface with the drone, on top of the dronekit API (or any other)
    """

    def __init__(self, context):
        """
        Initializes the interface and associated connection parameters
        :param context: connection parameters
        px4-sitl : SIL with PX4
        px4 : raspberry pi + mavlink router communicating with the PX4 stack
        copter-sitl : SIL with ArduCopter
        raspberry-serial : raspberry (HITL or not) without mavlink router
        """
        self.vehicle = None
        if context == "px4-sitl":
            self.connection_string = "udp:127.0.0.1:14540"
            self.baudrate = None
        elif context == "px4":
            self.connection_string = "udp:127.0.0.1:14550"
            self.baudrate = None
        elif context == "copter-sitl":
            self.connection_string = "tcp:127.0.0.1:5762"
            self.baudrate = None
        elif context == "raspberry-serial":
            self.connection_string = "/dev/ttyUSB0"
            self.baudrate = 921600
        else:
            print("unsupported execution context")
            self.connection_string = None
            self.baudrate = None

        self.is_connected = False

        self.memorized_heart_beat = 9999
        self.heart_beat_monitoring_counter = 0

    def connect(self):
        """
        Connects to the vehicle
        :return: None
        """
        try:
            if self.baudrate is None:
                self.vehicle = connect(self.connection_string, wait_ready=True)
            else:
                self.vehicle = connect(self.connection_string, wait_ready=True, baud=self.baudrate)
        except APIException:
            print("Impossible to establish connexion, timeout")
            pass

        if self.vehicle is not None:
            self.is_connected = True

    def end_connection(self):
        """
        Closes the connection to the vehicle
        :return: None
        """
        self.vehicle.close()

    def get_connection_status(self):
        """

        :return: True if the obc is connected to the autopilot, False otherwise
        """
        return self.is_connected

    def check_heart_beat(self):
        """
        Monitors the last heart beat values.
        :return: True if the values are changing, False otherwise
        """
        last_heart_beat = self.vehicle.last_heartbeat
        # print(last_heart_beat)

        if last_heart_beat != self.memorized_heart_beat and last_heart_beat < 1:
            self.memorized_heart_beat = last_heart_beat
            self.heart_beat_monitoring_counter = 0
            return True
        else:
            self.heart_beat_monitoring_counter += 1
            print("-- No new heart beat --")
            if self.heart_beat_monitoring_counter > 5:
                self.is_connected = False
                # self.heart_beat_monitoring_counter = 0
                return False
            else:
                return True

    def get_armed_status(self):
        return self.vehicle.armed

    def get_vehicle_reference(self):
        return self.vehicle

    def print_flight_monitoring(self):
        print("Mode : "+str(self.vehicle.mode.name))
        print(" Local Location: " + str(self.vehicle.location.local_frame) + "\n")  # NED
        print("Alti : ", self.vehicle.location.local_frame.down, " // Heading : ", self.vehicle.heading)

    def is_at_right_altitude(self, inverted_lolas_z, target, use_lolas_as_reference):
        """
        Compares a given altitude source with a target altitude
        :param inverted_lolas_z: lolas Z, in a downward pointing frame
        :param target: the expected altitude
        :param use_lolas_as_reference: if True, Lolas Z is used for the comparison, otherwise it is the local NED
        :return: True if the drone is at the expected altitude
        """
        z_tol = 0.2
        if use_lolas_as_reference:
            if (inverted_lolas_z / 1000) - z_tol < - target < (inverted_lolas_z / 1000) + z_tol:
                return True
            else:
                return False
        else:
            if self.vehicle.location.local_frame.down - z_tol < - target < self.vehicle.location.local_frame.down + z_tol:
                return True
            else:
                return False

    def send_ned_velocity(self, velocity_x, velocity_y, velocity_z, yaw_rate):
        """
        Move vehicle in direction based on specified velocity vectors and
        for the specified duration.

        This uses the SET_POSITION_TARGET_LOCAL_NED command with a type mask enabling only
        velocity components
        (http://dev.ardupilot.com/wiki/copter-commands-in-guided-mode/#set_position_target_local_ned).

        Note that from AC3.3 the message should be re-sent every second (after about 3 seconds
        with no message the velocity will drop back to zero). In AC3.2.1 and earlier the specified
        velocity persists until it is canceled. The code below should work on either version
        (sending the message multiple times does not cause problems).

        See the above link for information on the type_mask (0=enable, 1=ignore).
        At time of writing, acceleration and yaw bits are ignored.
        """
        msg = self.vehicle.message_factory.set_position_target_local_ned_encode(
            0,  # time_boot_ms (not used)
            0, 0,  # target system, target component
            mavutil.mavlink.MAV_FRAME_LOCAL_NED,  # frame
            0b0000011111000111,  # type_mask (only speeds enabled)
            0, 0, 0,  # x, y, z positions (not used)
            velocity_x, velocity_y, velocity_z,  # x, y, z velocity in m/s
            0, 0, 0,  # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
            0, yaw_rate)  # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)
        self.vehicle.send_mavlink(msg)

    def send_frd_velocity(self, velocity_x, velocity_y, velocity_z, yaw_rate):
        """
        Move vehicle in direction based on specified velocity vectors and
        for the specified duration.

        This uses the MAV_FRAME_BODY_NED command with a type mask enabling only
        velocity components
        """
        msg = self.vehicle.message_factory.set_position_target_local_ned_encode(
            0,  # time_boot_ms (not used)
            0, 0,  # target system, target component
            mavutil.mavlink.MAV_FRAME_BODY_NED,  # frame
            0b0000011111000111,  # type_mask (only speeds enabled)
            0, 0, 0,  # x, y, z positions (not used)
            velocity_x, velocity_y, velocity_z,  # x, y, z velocity in m/s
            0, 0, 0,  # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
            0, yaw_rate)  # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)
        self.vehicle.send_mavlink(msg)

    def disarm_if_required(self, last_waypoint_reached, disarm_from_lolas, lolas_z):
        """
        Triggers a disarm sequence (to be chosen) if the specified conditions are met.
        :param last_waypoint_reached:
        :param disarm_from_lolas:
        :param lolas_z:
        :return:
        """
        # Never disarm the vehicle if the onboard computer is not supposed to be in control
        if self.vehicle.mode.name != "OFFBOARD" and self.vehicle.mode.name != "GUIDED":
            return False
        # If disarm conditions are met
        if last_waypoint_reached and disarm_from_lolas and 0 < lolas_z < 400:
            # Disarm handled by the autopilot
            # self.vehicle.armed = False.
            # Forced disarmed, no matter the conditions
            self.force_disarm()
            return True
        else:
            return False

    def force_disarm(self):
        """
        CAUTION : the force disarm will put down the drone no matter its actual status.
        To be used with caution.
        :return:
        """
        msg = self.vehicle.message_factory.command_long_send(
            0,  # target_system
            0,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,  # command
            0,  # confirmation
            0,  # param1 (1 to indicate arm)
            21196,  # param2 (all other params meaningless)
            0,  # param3
            0,  # param4
            0,  # param5
            0,  # param6
            0)  # param7
        # send command to vehicle
        self.vehicle.send_mavlink(msg)

    def get_yaw(self):
        return self.vehicle.heading

    def get_altitude(self):
        return self.vehicle.location.local_frame.down
