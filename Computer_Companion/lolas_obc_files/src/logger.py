import datetime
from pymavlink import mavutil
import time


class Logger:

    def __init__(self, drone_reference, lolas_interface_reference, log_perfo):
        self.drone_reference = drone_reference
        self.lolas_interface_reference = lolas_interface_reference
        self.log_file = None
        self.mesure_perfo = None
        test = None
        if log_perfo:
            test = MeasureTime()
            self.mesure_perfo = test

            # Create COMMAND_ACK message listener.
            @drone_reference.on_message('COMMAND_ACK')
            def listener(self, name, message):
                test.update()
                # self.send_testpackets()
        self.filename = None
        self.flush_counter = 0
        self.start_time = 0

    def start(self):
        """
        Creates the log file and writes down the file header
        :return: None
        """
        self.log_file = self.create_file()
        if self.log_file:
            self.write_header()
            self.start_time = time.time()

    def stop(self):
        self.log_file.close()

    def send_testpackets(self):
        """
        Sends a message used to compute latency and propagation time between the OBC and the AP.
        :return: None
        """
        # Send message using `command_long_encode` (returns an ACK)
        msg = self.drone_reference.message_factory.command_long_encode(
            1, 1,  # target system, target component
            mavutil.mavlink.MAV_CMD_DO_SET_ROI,  # command
            0,  # confirmation
            0, 0, 0, 0,  # params 1-4
            0,
            0,
            0
        )

        self.drone_reference.send_mavlink(msg)

    def create_file(self):
        """
        Creates a log file, named after the current date, under the log directory.
        :return:
        """
        filename = "log/"
        filename += datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        # filename = "toto"
        filename += "_lolas_obc.csv"
        self.filename = filename
        return open(str(filename), "w+")

    def write_header(self):
        """
        Writes the header (the columns names) into the log file.
        :return:
        """
        # print("writing header")
        header = "OBC_time;"
        if self.mesure_perfo is not None:
            header += "Interval;"
        header += "NEDLocationNorth;NEDLocationEast;NEDLocationDown;" \
                 "Pitch;Yaw;Roll;drone_Vx;drone_Vy;drone_Vz;drone_Heading;LastHeartbeat;Mode;" \
                  "drone_health;pos_update;alti_update;yaw_update;fusion_health;ground_health;lolas_x;lolas_y;lolas_z;lolas_yaw;" \
                  "wow;proxi_status;lolas_mode;guidance_step;wpt_x_frd;wpt_y_frd;distance_to_wpt;yaw_departure;" \
                  "setpoint Vx;setpoint Vy;setpoint Vz;setpoint Vyaw\n"

        self.log_file.write(header)

    def log(self, guidance_step, base_x_frd, base_y_frd, distance_to_base, yaw_departure, vx, vy, vz, vyaw):
        """
        Puts together the values required to add a record entry to the log file, as a csv string.
        :param guidance_step:
        :param base_x_frd:
        :param base_y_frd:
        :param distance_to_base:
        :param yaw_departure:
        :param vx:
        :param vy:
        :param vz:
        :param vyaw:
        :return:
        """
        if self.mesure_perfo is not None:
            self.send_testpackets()

        csv_line = ""
        csv_line += str(time.time()-self.start_time) + ";"
        if self.mesure_perfo is not None:
            csv_line += self.mesure_perfo.get_measures_as_CSV()

        csv_line += str(self.drone_reference.location.local_frame.north)+";"
        csv_line += str(self.drone_reference.location.local_frame.east) + ";"
        csv_line += str(self.drone_reference.location.local_frame.down) + ";"
        csv_line += str(self.drone_reference.attitude.pitch) + ";"
        csv_line += str(self.drone_reference.attitude.yaw) + ";"
        csv_line += str(self.drone_reference.attitude.roll) + ";"
        csv_line += str(self.drone_reference.velocity[0]) + ";"
        csv_line += str(self.drone_reference.velocity[1]) + ";"
        csv_line += str(self.drone_reference.velocity[2]) + ";"
        csv_line += str(self.drone_reference.heading) + ";"
        csv_line += str(self.drone_reference.last_heartbeat) + ";"
        csv_line += str(self.drone_reference.mode.name) + ";"
        csv_line += str(self.lolas_interface_reference.drone_healthword) + ";"
        csv_line += str(self.lolas_interface_reference.pos_update) + ";"
        csv_line += str(self.lolas_interface_reference.alti_update) + ";"
        csv_line += str(self.lolas_interface_reference.yaw_update) + ";"
        csv_line += str(self.lolas_interface_reference.fusion_healthword) + ";"
        csv_line += str(self.lolas_interface_reference.ground_healthword) + ";"
        csv_line += str(self.lolas_interface_reference.lolas_x) + ";"
        csv_line += str(self.lolas_interface_reference.lolas_y) + ";"
        csv_line += str(self.lolas_interface_reference.lolas_z) + ";"
        csv_line += str(self.lolas_interface_reference.lolas_yaw) + ";"
        csv_line += str(self.lolas_interface_reference.weight_on_wheel) + ";"
        csv_line += str(self.lolas_interface_reference.proxi_status) + ";"
        csv_line += str(self.lolas_interface_reference.current_mode) + ";"
        csv_line += str(guidance_step) + ";"
        csv_line += str(base_x_frd) + ";"
        csv_line += str(base_y_frd) + ";"
        csv_line += str(distance_to_base) + ";"
        csv_line += str(yaw_departure) + ";"
        csv_line += str(vx) + ";"
        csv_line += str(vy) + ";"
        csv_line += str(vz) + ";"
        csv_line += str(vyaw) + ";"

        csv_line += "\n"
        # print("Adding to file : "+csv_line)
        self.log_file.write(csv_line)

        self.flush_counter += 1
        # toutes les 5 lignes, on écrit vraiment dans le fichier
        if self.flush_counter == 5:
            self.flush()
            self.flush_counter = 0

    def flush(self):
        """
        Closes and opens again the log file (with the pointer at the end of it).
        That triggers the actual writing of the lines. Otherwise they remain buffered, and that is not crash safe.
        :return:
        """
        self.log_file.close()
        self.log_file = open(str(self.filename), "a+")


class MeasureTime(object):
    """
    Utility class used to monitor the mavlink performance such as propagation time.
    """
    def __init__(self):
        self.prevtime = self.cur_usec()
        self.previnterval = 0
        self.numcount = 0
        self.reset()

    def reset(self):
        self.maxinterval = 0
        self.mininterval = 10000

    def update(self):
        now = self.cur_usec()
        self.numcount = self.numcount + 1
        self.previnterval = now - self.prevtime
        self.prevtime = now
        if self.numcount > 1:  # ignore first value where self.prevtime not reliable.
            self.maxinterval = max(self.previnterval, self.maxinterval)
            self.mininterval = min(self.mininterval, self.previnterval)
            # self.log()

    def cur_usec(self):
        """Returns current time in usecs"""
        # t = time.time()
        dt = datetime.datetime.now()
        t = dt.minute * 60 + dt.second + dt.microsecond / (1e6)
        return t

    def get_measures_as_CSV(self):
        csv_line = ""
        # csv_line += str(self.maxinterval) + ";"
        # csv_line += str(self.mininterval) + ";"
        csv_line += str(self.previnterval) + ";"

        return csv_line
