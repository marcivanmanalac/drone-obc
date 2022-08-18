from math import cos, sin, radians, sqrt


class TrajectoryComputer:
    """
    This class is in charge of coordinates and distances computation for guidance.
    Coordinates systems may vary from a function to another.
    """

    def __init__(self):

        self.initial_north = None
        self.initial_east = None
        self.base_x_frd = None
        self.base_y_frd = None

        self.wpt_x_frd = 0
        self.wpt_y_frd = 0
        self.dist_to_base = 9999  # init value is not zero, otherwise guidance may stop right away
        self.dist_to_wpt = 9999

    def compute_distance_to_base(self, lolas_x, lolas_y):
        """
        Computes the distance to the center of the base (0;0)
        :param lolas_x:
        :param lolas_y:
        :return: the distance to the base
        """
        if lolas_x == 0 and lolas_y == 0:  # in this case, it is likely that the position estimation is unavailable during this cycle
            return self.dist_to_base  # meaning return the previous computed distance
        else:  # otherwise compute and update the last known distance to base
            self.dist_to_base = sqrt(lolas_x*lolas_x+lolas_y*lolas_y) / 1000
            return self.dist_to_base

    def compute_distance_to_waypoint(self, x_lolas, y_lolas, wpt_x_lolas, wpt_y_lolas):
        """
        Computes the distance to the center of the waypoint (wpt_x_lolas;wpt_y_lolas)
        :param x_lolas:
        :param y_lolas:
        :param wpt_x_lolas:
        :param wpt_y_lolas:
        :return: the distance to the waypoint
        """
        if x_lolas == 0 and y_lolas == 0:  # in this case, it is likely that the position estimation is unavailable during this cycle
            return self.dist_to_wpt  # meaning return the previous computed distance
        else:  # otherwise compute and update the last known distance to the waypoint
            self.dist_to_wpt = sqrt((wpt_x_lolas-x_lolas)*(wpt_x_lolas-x_lolas)+(wpt_y_lolas-y_lolas)*(wpt_y_lolas-y_lolas)) / 1000
            return self.dist_to_wpt

    def compute_base_coordinates(self, x_lolas, y_lolas, yaw_lolas):
        """
        Computes the base coordinates (0;0 in lolas frame), in the frd frame
        :param x_lolas:
        :param y_lolas:
        :param yaw_lolas:
        :return: None, local frd variables for the base position are updated
        """
        # first rotate the coordinate system
        # then reverse signs
        self.base_x_frd = -(x_lolas * cos(radians(yaw_lolas)) + y_lolas * sin(radians(yaw_lolas))) / 1000
        # FRD Y has the opposite sign from lolas coordinates system
        self.base_y_frd = (-x_lolas * sin(radians(yaw_lolas)) + y_lolas * cos(radians(yaw_lolas))) / 1000

        print("Base coordinates : ", self.base_x_frd, ' / ', self.base_y_frd)

    def compute_wpt_coordinates(self, x_lolas, y_lolas, yaw_lolas, wpt_x_lolas, wpt_y_lolas):
        """
        Computes the waypoint coordinates (wpt_x_lolas;wpt_y_lolas in lolas frame), in the frd frame
        :param x_lolas:
        :param y_lolas:
        :param yaw_lolas:
        :param wpt_x_lolas:
        :param wpt_y_lolas:
        :return: None, local frd variables for the waypoint position are updated
        """
        self.wpt_x_frd = -((x_lolas-wpt_x_lolas) * cos(radians(yaw_lolas)) + (y_lolas-wpt_y_lolas) * sin(radians(yaw_lolas))) / 1000
        self.wpt_y_frd = (-(x_lolas-wpt_x_lolas) * sin(radians(yaw_lolas)) + (y_lolas-wpt_y_lolas) * cos(radians(yaw_lolas))) / 1000

    def get_base_x_frd(self):
        return self.base_x_frd

    def get_base_y_frd(self):
        return self.base_y_frd

    def get_wpt_x_frd(self):
        return self.wpt_x_frd

    def get_wpt_y_frd(self):
        return self.wpt_y_frd

    @staticmethod
    def get_setpoint_sign(xy_estimation):
        if xy_estimation == 0:
            return 0
        elif xy_estimation < 0:
            return -1
        else:
            return 1

    @staticmethod
    def get_setpoint_yaw_sign(lolas_yaw, waypoint_yaw):
        if lolas_yaw == waypoint_yaw:
            return 0
        # neutral area around the target, to ease regulation
        elif abs(lolas_yaw - waypoint_yaw) < 10:
            return 0
        elif lolas_yaw > waypoint_yaw:
            if abs(lolas_yaw - waypoint_yaw) > 180:
                return -1
            else:
                return 1
        else:
            if abs(lolas_yaw - waypoint_yaw) > 180:
                return 1
            else:
                return -1

    @staticmethod
    def get_setpoint_vz_sign(target_z, lolas_z):
        # allow a small tolerance around target z not to regulate up and down all the time
        if abs(target_z-lolas_z/1000) < 0.2:
            return 0
        else:
            if target_z < lolas_z/1000:
                # positive z is downward pointing
                return 1
            # elif target_z == lolas_z/1000:
            #     return 0
            else:
                return -1





