from src.custom_protocol_v2.Common.lolas_messages_factory import LoLasMessagesFactory
from .custom_protocol_v2.Common.messages_id import MessagesID
from .custom_protocol_v2.Common.message import Message

OUT_WAITING_LIMIT = 64  # number of bytes waiting to be sent
IN_WAITING_LIMIT = 64  # number of bytes waiting to be considered


class LoLasInterface:
    """
    This class provides a more abstracted interface with lolas, built on top of the messages factory.
    It provides a simple set of functions to interact with it.
    """

    def __init__(self, port, interface_implementation, shall_sim):

        self.simulate_lolas = shall_sim

        self.msg_factory = LoLasMessagesFactory(port, interface_implementation, IN_WAITING_LIMIT, OUT_WAITING_LIMIT)

        while self.msg_factory.trying_to_connect():
                print(interface_implementation + " interface on port " + port + " is not available. Trying to establish connection...")

        # LoLas status synthesis
        self.lolas_is_alive = True
        self.lolas_last_heart_beat = -9999
        self.heart_beat_monitor = 0
        self.current_mode = -1

        # LoLas healthwords
        self.drone_healthword = 0
        self.ground_healthword = 0
        self.fusion_healthword = 0

        self.pos_update = 0
        self.alti_update = 0
        self.yaw_update = 0

        # LoLas Flight info
        self.base_in_sight = 1
        # LoLas proximity
        self.weight_on_wheel = 0
        self.proxi_status = -1

        # lolas current position
        self.lolas_x = 0
        self.lolas_y = 0
        self.lolas_z = -999999
        self.lolas_yaw = -1
        if self.simulate_lolas:
            self.lolas_z = 5000
            self.lolas_yaw = 294
            self.simulated_x = -2976
            self.simulated_y = 2065
            self.memorized_simulated_x = self.simulated_x
            self.memorized_simulated_y = self.simulated_y
            self.pos_update = 1
            self.alti_update = 1
            self.yaw_update = 1
        self.simulated_closing_counter = 0

    def fetch(self):
        """
        In normal mode, gets the last values from the messages factory, and updates the values table.
        And monitors the lolas heart beat.
        In simulation mode, fakes the values of interest.
        :return:
        """

        if self.simulate_lolas:
            self.lolas_is_alive = True  # always alive
            self.current_mode = 2  # enabled

            self.lolas_x = self.simulated_x
            self.lolas_y = self.simulated_y

            self.pos_update = 1
            self.alti_update = 1
            self.yaw_update = 1

        else:
            self.msg_factory.has_incoming_message()

            self.heart_beat_monitor += 1

            for message in self.msg_factory.stack_in_messages:
                self.heart_beat_monitor = 0
                self.lolas_is_alive = True
                if message.id == MessagesID.STATUS:
                    self.update_lolas_status(message)
                elif message.id == MessagesID.LOLAS_PROXIMITY:
                    self.update_lolas_proximity(message)
                elif message.id == MessagesID.LOLAS_3D_POSITION:
                    self.update_lolas_measures(message)

            if self.heart_beat_monitor > 10:
                self.lolas_is_alive = False
                print("--- LOLAS IS DOWN ---")

            self.msg_factory.free_incoming_messages()

    def simulate_closing_drone(self):
        """
        Only used in simulation, simulates the evolution of lolas x and y, but also possible data loss.
        :return:
        """
        # simulate a closing position
        self.simulated_closing_counter += 1
        if 3 < self.simulated_closing_counter < 7:  # on simule la perte de l'estimation sur quelques tours
            self.simulated_x = 0
            self.simulated_y = 0
        else:
            self.simulated_x = self.memorized_simulated_x + 90
            self.simulated_y = self.memorized_simulated_y - 50
            self.memorized_simulated_x = self.simulated_x
            self.memorized_simulated_y = self.simulated_y

    def simulate_correct_z(self, offset_frd):
        """
        Only used in simulation, fakes a converging lolas z.
        :param offset_frd:
        :return:
        """
        self.lolas_z = self.lolas_z-(offset_frd * 1000)/10

    def update_lolas_status(self, message):
        if self.lolas_last_heart_beat != int.from_bytes(message.time_since_boot, byteorder=Message.INDIANNESS, signed=False):
            self.lolas_last_heart_beat = int.from_bytes(message.time_since_boot, byteorder=Message.INDIANNESS, signed=False)
            self.heart_beat_monitor = 0
        self.current_mode = message.current_mode
        self.drone_healthword = message.drone_system_health
        self.ground_healthword = message.ground_system_health

    @staticmethod
    def extract_position_update_bit(fusion_health_word):
        # tmp_str = '{:08b}'.format(ord(fusion_health_word))
        tmp_str = '{:08b}'.format(fusion_health_word)
        tmp_array = list(tmp_str)
        # print(int(tmp_array[0]))
        return int(tmp_array[7])

    @staticmethod
    def extract_altitude_update_bit(fusion_health_word):
        # tmp_str = '{:08b}'.format(ord(fusion_health_word))
        tmp_str = '{:08b}'.format(fusion_health_word)
        tmp_array = list(tmp_str)
        return int(tmp_array[6])

    @staticmethod
    def extract_yaw_update_bit(fusion_health_word):
        # tmp_str = '{:08b}'.format(ord(fusion_health_word))
        tmp_str = '{:08b}'.format(fusion_health_word)
        tmp_array = list(tmp_str)
        return int(tmp_array[5])

    def update_lolas_proximity(self, message):
        self.weight_on_wheel = message.weight_on_wheel
        self.proxi_status = message.status

    def update_lolas_measures(self, message):
        self.lolas_x = int.from_bytes(message.lolas_x, byteorder=Message.INDIANNESS, signed=True)
        self.lolas_y = int.from_bytes(message.lolas_y, byteorder=Message.INDIANNESS, signed=True)
        self.lolas_z = int.from_bytes(message.lolas_z, byteorder=Message.INDIANNESS, signed=True)
        self.lolas_yaw = int.from_bytes(message.lolas_yaw, byteorder=Message.INDIANNESS, signed=False)

        self.pos_update = self.extract_position_update_bit(message.fusion_health)
        self.alti_update = self.extract_altitude_update_bit(message.fusion_health)
        self.yaw_update = self.extract_yaw_update_bit(message.fusion_health)
        self.fusion_healthword = message.fusion_health

    def disconnect(self):
        self.msg_factory.dismiss_factory()

    def print_lolas_info(self):
        print("X        Y       Z       YAW")
        print("", self.lolas_x, "    ", self.lolas_y, "   ", self.lolas_z, "    ", self.lolas_yaw)
