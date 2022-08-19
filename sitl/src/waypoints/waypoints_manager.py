import json
from src.waypoints.waypoint import Waypoint


class WaypointsManager:
    """
    This class interacts with the waypoints declaration file (json), and helps with loading, navigation among the
    waypoints list, etc.
    """

    def __init__(self):
        self.waypoints_list = []
        self.landing_required = False
        self.how_many_waypoints = 0
        self.index = 0

        self.load_waypoints()
        self.count_waypoints()
        self.print_waypoints()

    def load_waypoints(self):
        """
        Extracts the waypoints from the json file, and convert them into objects stored in a list.
        :return:
        """
        with open("src/waypoints/waypoints_declaration.json") as f:
            data = json.load(f)
        for json_waypoint in data['waypoints']:
            read_waypoint = Waypoint(json_waypoint[0]['X'], json_waypoint[1]['Y'], json_waypoint[2]['Z'],
                                     json_waypoint[3]['yaw'], json_waypoint[4]['tolerance'])
            self.waypoints_list.append(read_waypoint)
        if data['land'] == 1:
            self.landing_required = True

    def count_waypoints(self):
        self.how_many_waypoints = len(self.waypoints_list)

    def print_waypoints(self):
        print('# of waypoints found : ', self.how_many_waypoints)
        print(self.waypoints_list)
        print("Landing required : ", self.landing_required)

    def get_current_waypoint(self):
        # if index has been incremented too much, return last defined waypoint
        if self.index >= len(self.waypoints_list):
            return self.waypoints_list[len(self.waypoints_list) - 1]
        # or the waypoint for the actual index otherwise
        return self.waypoints_list[self.index]

    def reset_waypoints_index(self):
        self.index = 0

    def increment_waypoint_index(self):
        """
        Selects the next waypoint in the list, or the last one once at the end of the list.
        :return:
        """
        if self.index == len(self.waypoints_list)-1:
            return
        else:
            self.index += 1

    def has_reached_last_waypoint(self):
        if self.index >= len(self.waypoints_list)-1:
            return True
        else:
            return False
