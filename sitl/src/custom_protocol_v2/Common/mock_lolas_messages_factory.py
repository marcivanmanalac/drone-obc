"""
A mocking class for lolas messages factory that can be used for SITL purposes
"""
import time
# gestion des accès relatifs différents entre windows et linux
try:
    from src.custom_protocol_v2.UART.uart_interface import UARTInterface
    from src.custom_protocol_v2.Common.common_messages import *
    from src.custom_protocol_v2.Common.messages_id import MessagesID
    from src.custom_protocol_v2.Common.messages_from_lolas import *
    from src.custom_protocol_v2.Common.messages_to_lolas import *
    from src.custom_protocol_v2.Common.lolas_internal_messages import *

except Exception: #ImportError
    # from UART.uart_interface import UARTInterface
    from Common.common_messages import Ping, Ack
    from Common.messages_id import MessagesID
    from Common.messages_from_lolas import *
    from Common.messages_to_lolas import *
    from Common.lolas_internal_messages import *


BUFFER_SAFETY_MARGIN = 0.8


class MockLoLasMessagesFactory:

    def __init__(self, port, protocol, IN_WAITING_LIMIT, OUT_WAITING_LIMIT):

        self.buffer_in_limit = BUFFER_SAFETY_MARGIN * IN_WAITING_LIMIT
        self.buffer_out_limit = BUFFER_SAFETY_MARGIN * OUT_WAITING_LIMIT

        self.comm_interface = None
        self.protocol = protocol
        self.port = port

        self.stack_out_messages = []
        self.stack_in_messages = []

        self.boot_origin = int(round(time.time() * 1000))

        self.msg_id_storage = []
        for i in range(len(MessagesID)):
            self.msg_id_storage.append(0)

        # gestion temporelle du comportement lolas simulé
        self.time_to_change_behaviour = 5000  # on change de comportement toutes les "time_to_change_behaviour/1000" secondes
        self.elapsed_time = 0
        self.start_time = 0

        self.guidance_is_active = False

        self.mission = "land_with_lolas_loss"  # "land_with_setpoints_loss" | "land_with_radio_loss" | "land_with_lolas_loss"

    # def trying_to_connect(self):
    #     """
    #     Selects the right implementation of the protocol connector
    #     :return:
    #     """
    #     if self.protocol == "UART":
    #         self.comm_interface = UARTInterface(self.port, self)
    #     else:
    #         print("Unkown protocol, exiting...")
    #         sys.exit(0)

    def set_message(self, msg_ID, values, msg_number, is_outgoing, values_are_bytes):
        """
        Creates a message of the right kind and adds it onto the in or out stack
        :param msg_ID:
        :param values: values either as bytes or as user values (integers or so)
        :param msg_number: the message number, either read or allocated by the message factory
        :param is_outgoing: True if the message is to be sent, False if the message has been received
        :param values_are_bytes: True if the values are raw bytes read from the comm connector
        :return: True if everything went ok, False otherwise
        """

        if isinstance(msg_ID, MessagesID):
            # todo gérer les différents types de messages ici
            if msg_ID == MessagesID.PING:
                new_message = Ping(MessagesID.PING, values, msg_number, values_are_bytes)

            elif msg_ID == MessagesID.ACK:
                new_message = Ack(MessagesID.ACK, values, msg_number, values_are_bytes)

            elif msg_ID == MessagesID.STATUS:
                new_message = Status(MessagesID.STATUS, values, msg_number, values_are_bytes)

            elif msg_ID == MessagesID.LOLAS_3D_POSITION:
                new_message = LoLas3DPosition(MessagesID.LOLAS_3D_POSITION, values, msg_number, values_are_bytes)

            elif msg_ID == MessagesID.LOLAS_ANGULAR_POSITION:
                new_message = LoLasAngularPosition(MessagesID.LOLAS_ANGULAR_POSITION, values, msg_number,
                                                   values_are_bytes)

            elif msg_ID == MessagesID.FLIGHT_CONTROLLER_REQUESTS:
                new_message = FlightControlRequests(MessagesID.FLIGHT_CONTROLLER_REQUESTS, values, msg_number,
                                                    values_are_bytes)

            elif msg_ID == MessagesID.AUTOPILOT_NAVIGATION_SENSORS:
                new_message = AutopilotNavigationSensors(MessagesID.AUTOPILOT_NAVIGATION_SENSORS, values, msg_number,
                                                         values_are_bytes)

            elif msg_ID == MessagesID.LOLAS_FLIGHT_INFO:
                new_message = LoLasFlightInfo(MessagesID.LOLAS_FLIGHT_INFO, values, msg_number, values_are_bytes)

            elif msg_ID == MessagesID.STATUS:
                new_message = Status(MessagesID.STATUS, values, msg_number, values_are_bytes)

            elif msg_ID == MessagesID.GENERIC_1:
                new_message = GenericMessage1(MessagesID.GENERIC_1, values, msg_number, values_are_bytes)

            elif msg_ID == MessagesID.GENERIC_2:
                new_message = GenericMessage2(MessagesID.GENERIC_2, values, msg_number, values_are_bytes)

            elif msg_ID == MessagesID.GENERIC_3:
                new_message = GenericMessage3(MessagesID.GENERIC_3, values, msg_number, values_are_bytes)

            elif msg_ID == MessagesID.GENERIC_4:
                new_message = GenericMessage4(MessagesID.GENERIC_4, values, msg_number, values_are_bytes)

            elif msg_ID == MessagesID.NODE_DECLARATION:
                new_message = NodeDeclaration(MessagesID.NODE_DECLARATION, values, msg_number, values_are_bytes)

            elif msg_ID == MessagesID.RANGES_TRANSFER:
                new_message = RangesTransferMessage(MessagesID.RANGES_TRANSFER, values, msg_number, values_are_bytes)

            else:
                print("Unimplemented message ID, dumping it..")
                return False
            if is_outgoing:
                self.stack_out_messages.append(new_message)
            else:
                self.stack_in_messages.append(new_message)
            return True
        else:
            print("Unkown message ID, dumping it..")
            return False

    def get_available_msg_number(self, msg_ID):
        """
        Gives a message number to be allocated to a new message
        :param msg_ID: The kind of message we want a number for
        :return: A usable message number
        """
        self.msg_id_storage[msg_ID.value] += 1
        return self.msg_id_storage[msg_ID.value]

    def is_busy(self):
        """
        Compares the outgoing stack of messages to be sent with the buffer out size, including a hardcoded safety margin
        :return: True if too many out going messages are waiting
        """
        if len(self.stack_out_messages) > self.buffer_out_limit:
            return True
        else:
            return False

    def is_flooded(self):
        """
        Compares the in waiting stack of messages to be used with the buffer in size, including a hardcoded safety margin
        :return: True if too many in waiting messages are waiting
        """
        if len(self.stack_in_messages) > self.buffer_in_limit:
            return True
        else:
            return False

    def has_incoming_message(self):
        """
        Parses available messages and adds them to the in stack
        :return: the number of messages in the in stack
        """

        # situation normale et constante tant que le guidage n'est pas activé
        if not self.guidance_is_active:
            # self.set_message(MessagesID.STATUS, [255, 255, int(round(time.time() * 1000)) - self.boot_origin, 4],
            #                  self.get_available_msg_number(MessagesID.STATUS), False, False)
            # self.set_message(MessagesID.LOLAS_MEASURES, [300, 400, 4000, 0, 150, 160, 170, 1, 2, 3, 255],
            #                  self.get_available_msg_number(MessagesID.LOLAS_MEASURES), False, False)
            # self.set_message(MessagesID.LOLAS_FLIGHT_INFO, [1, 0, 0, 0, 3],
            #                  self.get_available_msg_number(MessagesID.LOLAS_FLIGHT_INFO), False, False)
            # todo : faire vivre des messages lolas 3d position, LOLAS_FLIGHT_INFO, STATUS
            pass

        else:  # en cas d'activation du guidage

            if self.mission == "hover":
                print("mission hovering à implémenter")
                # todo : faire vivre des messages lolas 3d position, LOLAS_FLIGHT_INFO, STATUS

            # if self.mission == "land":
            #
            #     # on initialise l'origine des temps pour le comportement
            #     if self.start_time == 0:
            #         self.start_time = int(round(time.time() * 1000))
            #
            #     if self.elapsed_time < self.time_to_change_behaviour * 1:  # premier step
            #         self.set_message(MessagesID.STATUS, [255, 255,  int(round(time.time() * 1000)) - self.boot_origin, 5],
            #                          self.get_available_msg_number(MessagesID.STATUS), False, False)
            #         self.set_message(MessagesID.LOLAS_MEASURES, [300, 400, 4000, 0, 150, 160, 170, 1, 2, 3, 255],
            #                          self.get_available_msg_number(MessagesID.LOLAS_MEASURES), False, False)
            #         self.set_message(MessagesID.LOLAS_SETPOINTS, [0, 0, 0, 0, 100, -100, 300, -1, 4, 1],
            #                          self.get_available_msg_number(MessagesID.LOLAS_SETPOINTS), False, False)
            #         self.set_message(MessagesID.LOLAS_FLIGHT_INFO, [1, 0, 0, 1, 3],
            #                          self.get_available_msg_number(MessagesID.LOLAS_FLIGHT_INFO), False, False)
            #
            #     elif self.elapsed_time < self.time_to_change_behaviour * 2:  # deuxième step
            #         self.set_message(MessagesID.STATUS, [255, 255, int(round(time.time() * 1000)) - self.boot_origin, 5],
            #                          self.get_available_msg_number(MessagesID.STATUS), False, False)
            #         self.set_message(MessagesID.LOLAS_MEASURES, [300, 400, 2500, 0, 150, 160, 170, 1, 2, 3, 255],
            #                          self.get_available_msg_number(MessagesID.LOLAS_MEASURES), False, False)
            #         self.set_message(MessagesID.LOLAS_SETPOINTS, [0, 0, 0, 0, 100, -100, 300, -1, 4, 1],
            #                          self.get_available_msg_number(MessagesID.LOLAS_SETPOINTS), False, False)
            #         self.set_message(MessagesID.LOLAS_FLIGHT_INFO, [1, 0, 0, 2, 3],
            #                          self.get_available_msg_number(MessagesID.LOLAS_FLIGHT_INFO), False, False)
            #     elif self.elapsed_time < self.time_to_change_behaviour * 3:  # troisième step
            #         self.set_message(MessagesID.STATUS, [255, 255, int(round(time.time() * 1000)) - self.boot_origin, 5],
            #                          self.get_available_msg_number(MessagesID.STATUS), False, False)
            #         self.set_message(MessagesID.LOLAS_MEASURES, [300, 400, 1000, 0, 150, 160, 170, 1, 2, 3, 255],
            #                          self.get_available_msg_number(MessagesID.LOLAS_MEASURES), False, False)
            #         self.set_message(MessagesID.LOLAS_SETPOINTS, [0, 0, 0, 0, 0, 0, 150, 0, 4, 1],
            #                          self.get_available_msg_number(MessagesID.LOLAS_SETPOINTS), False, False)
            #         self.set_message(MessagesID.LOLAS_FLIGHT_INFO, [1, 0, 0, 3, 3],
            #                          self.get_available_msg_number(MessagesID.LOLAS_FLIGHT_INFO), False, False)
            #     elif self.elapsed_time < self.time_to_change_behaviour * 4:  # quatrième step
            #         self.set_message(MessagesID.STATUS, [255, 255, int(round(time.time() * 1000)) - self.boot_origin, 5],
            #                          self.get_available_msg_number(MessagesID.STATUS), False, False)
            #         self.set_message(MessagesID.LOLAS_MEASURES, [300, 400, 300, 0, 150, 160, 170, 1, 2, 3, 255],
            #                          self.get_available_msg_number(MessagesID.LOLAS_MEASURES), False, False)
            #         self.set_message(MessagesID.LOLAS_SETPOINTS, [0, 0, 0, 0, 0, 0, 10, 0, 4, 1],
            #                          self.get_available_msg_number(MessagesID.LOLAS_SETPOINTS), False, False)
            #         self.set_message(MessagesID.LOLAS_FLIGHT_INFO, [1, 1, 0, 3, 3],
            #                          self.get_available_msg_number(MessagesID.LOLAS_FLIGHT_INFO), False, False)
            #     else:
            #         self.set_message(MessagesID.STATUS, [255, 255, int(round(time.time() * 1000)) - self.boot_origin, 5],
            #                          self.get_available_msg_number(MessagesID.STATUS), False, False)
            #
            # elif self.mission == "land_with_radio_loss":
            #
            #     # on initialise l'origine des temps pour le comportement
            #     if self.start_time == 0:
            #         self.start_time = int(round(time.time() * 1000))
            #
            #     if self.elapsed_time < self.time_to_change_behaviour * 1:  # premier step
            #         self.set_message(MessagesID.STATUS, [255, 255,  int(round(time.time() * 1000)) - self.boot_origin, 5],
            #                          self.get_available_msg_number(MessagesID.STATUS), False, False)
            #         self.set_message(MessagesID.LOLAS_MEASURES, [300, 400, 4000, 0, 150, 160, 170, 1, 2, 3, 255],
            #                          self.get_available_msg_number(MessagesID.LOLAS_MEASURES), False, False)
            #         self.set_message(MessagesID.LOLAS_SETPOINTS, [0, 0, 0, 0, 100, -100, 300, -1, 4, 1],
            #                          self.get_available_msg_number(MessagesID.LOLAS_SETPOINTS), False, False)
            #         self.set_message(MessagesID.LOLAS_FLIGHT_INFO, [1, 0, 0, 1, 3],
            #                          self.get_available_msg_number(MessagesID.LOLAS_FLIGHT_INFO), False, False)
            #
            #     elif self.elapsed_time < self.time_to_change_behaviour * 2:  # deuxième step
            #         self.set_message(MessagesID.STATUS, [255, 255, int(round(time.time() * 1000)) - self.boot_origin, 5],
            #                          self.get_available_msg_number(MessagesID.STATUS), False, False)
            #         self.set_message(MessagesID.LOLAS_MEASURES, [300, 400, 2500, 0, 150, 160, 170, 1, 2, 3, 255],
            #                          self.get_available_msg_number(MessagesID.LOLAS_MEASURES), False, False)
            #         self.set_message(MessagesID.LOLAS_SETPOINTS, [0, 0, 0, 0, 100, -100, 300, -1, 4, 1],
            #                          self.get_available_msg_number(MessagesID.LOLAS_SETPOINTS), False, False)
            #         self.set_message(MessagesID.LOLAS_FLIGHT_INFO, [1, 0, 0, 2, 3],
            #                          self.get_available_msg_number(MessagesID.LOLAS_FLIGHT_INFO), False, False)
            #     elif self.elapsed_time < self.time_to_change_behaviour * 3:  # troisième step
            #         self.set_message(MessagesID.STATUS, [127, 127, int(round(time.time() * 1000)) - self.boot_origin, 5],
            #                          self.get_available_msg_number(MessagesID.STATUS), False, False)
            #         self.set_message(MessagesID.LOLAS_MEASURES, [300, 400, 1000, 0, 150, 160, 170, 1, 2, 3, 255],
            #                          self.get_available_msg_number(MessagesID.LOLAS_MEASURES), False, False)
            #         self.set_message(MessagesID.LOLAS_SETPOINTS, [0, 0, 0, 0, 0, 0, 150, 0, 4, 1],
            #                          self.get_available_msg_number(MessagesID.LOLAS_SETPOINTS), False, False)
            #         self.set_message(MessagesID.LOLAS_FLIGHT_INFO, [1, 0, 0, 3, 3],
            #                          self.get_available_msg_number(MessagesID.LOLAS_FLIGHT_INFO), False, False)
            #     elif self.elapsed_time < self.time_to_change_behaviour * 4:  # quatrième step
            #         self.set_message(MessagesID.STATUS, [127, 127, int(round(time.time() * 1000)) - self.boot_origin, 5],
            #                          self.get_available_msg_number(MessagesID.STATUS), False, False)
            #         self.set_message(MessagesID.LOLAS_MEASURES, [300, 400, 1000, 0, 150, 160, 170, 1, 2, 3, 255],
            #                          self.get_available_msg_number(MessagesID.LOLAS_MEASURES), False, False)
            #         self.set_message(MessagesID.LOLAS_SETPOINTS, [0, 0, 0, 0, 0, 0, 10, 0, 4, 1],
            #                          self.get_available_msg_number(MessagesID.LOLAS_SETPOINTS), False, False)
            #         self.set_message(MessagesID.LOLAS_FLIGHT_INFO, [1, 1, 0, 3, 3],
            #                          self.get_available_msg_number(MessagesID.LOLAS_FLIGHT_INFO), False, False)
            #     else:
            #         self.set_message(MessagesID.STATUS, [127, 127, int(round(time.time() * 1000)) - self.boot_origin, 5],
            #                          self.get_available_msg_number(MessagesID.STATUS), False, False)
            #
            # elif self.mission == "land_with_setpoints_loss":
            #
            #     # on initialise l'origine des temps pour le comportement
            #     if self.start_time == 0:
            #         self.start_time = int(round(time.time() * 1000))
            #
            #     if self.elapsed_time < self.time_to_change_behaviour * 1:  # premier step
            #         self.set_message(MessagesID.STATUS, [255, 255,  int(round(time.time() * 1000)) - self.boot_origin, 5],
            #                          self.get_available_msg_number(MessagesID.STATUS), False, False)
            #         self.set_message(MessagesID.LOLAS_MEASURES, [300, 400, 4000, 0, 150, 160, 170, 1, 2, 3, 255],
            #                          self.get_available_msg_number(MessagesID.LOLAS_MEASURES), False, False)
            #         self.set_message(MessagesID.LOLAS_SETPOINTS, [0, 0, 0, 0, 100, -100, 300, -1, 4, 1],
            #                          self.get_available_msg_number(MessagesID.LOLAS_SETPOINTS), False, False)
            #         self.set_message(MessagesID.LOLAS_FLIGHT_INFO, [1, 0, 0, 1, 3],
            #                          self.get_available_msg_number(MessagesID.LOLAS_FLIGHT_INFO), False, False)
            #
            #     elif self.elapsed_time < self.time_to_change_behaviour * 2:  # deuxième step
            #         self.set_message(MessagesID.STATUS, [255, 255, int(round(time.time() * 1000)) - self.boot_origin, 5],
            #                          self.get_available_msg_number(MessagesID.STATUS), False, False)
            #         self.set_message(MessagesID.LOLAS_MEASURES, [300, 400, 2500, 0, 150, 160, 170, 1, 2, 3, 255],
            #                          self.get_available_msg_number(MessagesID.LOLAS_MEASURES), False, False)
            #         self.set_message(MessagesID.LOLAS_SETPOINTS, [0, 0, 0, 0, 100, -100, 300, -1, 4, 1],
            #                          self.get_available_msg_number(MessagesID.LOLAS_SETPOINTS), False, False)
            #         self.set_message(MessagesID.LOLAS_FLIGHT_INFO, [1, 0, 0, 2, 3],
            #                          self.get_available_msg_number(MessagesID.LOLAS_FLIGHT_INFO), False, False)
            #     elif self.elapsed_time < self.time_to_change_behaviour * 3:  # troisième step
            #         self.set_message(MessagesID.STATUS, [255, 255, int(round(time.time() * 1000)) - self.boot_origin, 5],
            #                          self.get_available_msg_number(MessagesID.STATUS), False, False)
            #         self.set_message(MessagesID.LOLAS_MEASURES, [300, 400, 1000, 0, 150, 160, 170, 1, 2, 3, 255],
            #                          self.get_available_msg_number(MessagesID.LOLAS_MEASURES), False, False)
            #         self.set_message(MessagesID.LOLAS_FLIGHT_INFO, [1, 0, 0, 3, 3],
            #                          self.get_available_msg_number(MessagesID.LOLAS_FLIGHT_INFO), False, False)
            #     else:
            #         self.set_message(MessagesID.STATUS, [255, 255, int(round(time.time() * 1000)) - self.boot_origin, 5],
            #                          self.get_available_msg_number(MessagesID.STATUS), False, False)
            #
            # elif self.mission == "land_with_lolas_loss":
            #
            #     # on initialise l'origine des temps pour le comportement
            #     if self.start_time == 0:
            #         self.start_time = int(round(time.time() * 1000))
            #
            #     if self.elapsed_time < self.time_to_change_behaviour * 1:  # premier step
            #         self.set_message(MessagesID.STATUS, [255, 255,  int(round(time.time() * 1000)) - self.boot_origin, 5],
            #                          self.get_available_msg_number(MessagesID.STATUS), False, False)
            #         self.set_message(MessagesID.LOLAS_MEASURES, [300, 400, 4000, 0, 150, 160, 170, 1, 2, 3, 255],
            #                          self.get_available_msg_number(MessagesID.LOLAS_MEASURES), False, False)
            #         self.set_message(MessagesID.LOLAS_SETPOINTS, [0, 0, 0, 0, 100, -100, 300, -1, 4, 1],
            #                          self.get_available_msg_number(MessagesID.LOLAS_SETPOINTS), False, False)
            #         self.set_message(MessagesID.LOLAS_FLIGHT_INFO, [1, 0, 0, 1, 3],
            #                          self.get_available_msg_number(MessagesID.LOLAS_FLIGHT_INFO), False, False)
            #
            #     elif self.elapsed_time < self.time_to_change_behaviour * 2:  # deuxième step
            #         self.set_message(MessagesID.STATUS, [255, 255, int(round(time.time() * 1000)) - self.boot_origin, 5],
            #                          self.get_available_msg_number(MessagesID.STATUS), False, False)
            #         self.set_message(MessagesID.LOLAS_MEASURES, [300, 400, 2500, 0, 150, 160, 170, 1, 2, 3, 255],
            #                          self.get_available_msg_number(MessagesID.LOLAS_MEASURES), False, False)
            #         self.set_message(MessagesID.LOLAS_SETPOINTS, [0, 0, 0, 0, 100, -100, 300, -1, 4, 1],
            #                          self.get_available_msg_number(MessagesID.LOLAS_SETPOINTS), False, False)
            #         self.set_message(MessagesID.LOLAS_FLIGHT_INFO, [1, 0, 0, 2, 3],
            #                          self.get_available_msg_number(MessagesID.LOLAS_FLIGHT_INFO), False, False)
            #     elif self.elapsed_time < self.time_to_change_behaviour * 3:  # troisième step
            #         self.set_message(MessagesID.STATUS, [255, 255, self.start_time- self.boot_origin, 5],
            #                          self.get_available_msg_number(MessagesID.STATUS), False, False)
            #         self.set_message(MessagesID.LOLAS_MEASURES, [300, 400, 1000, 0, 150, 160, 170, 1, 2, 3, 255],
            #                          self.get_available_msg_number(MessagesID.LOLAS_MEASURES), False, False)
            #         self.set_message(MessagesID.LOLAS_FLIGHT_INFO, [1, 0, 0, 3, 3],
            #                          self.get_available_msg_number(MessagesID.LOLAS_FLIGHT_INFO), False, False)
            #     else:
            #         self.set_message(MessagesID.STATUS, [255, 255, self.start_time- self.boot_origin, 5],
            #                          self.get_available_msg_number(MessagesID.STATUS), False, False)

            self.elapsed_time = int(round(time.time() * 1000)) - self.start_time

        return len(self.stack_in_messages)

    def send_available_messages(self):
        """
        Sends all the messages in the outgoing messages stack
        :return: the number of messages sent
        """
        # if self.comm_interface is not None:
        #     number_of_msg_sent = self.comm_interface.send_messages()
        #     return number_of_msg_sent
        # else:
        #     print("Cannot send messages, no active interface")
        #     return 0
        return

    def show_messages(self):
        """
        Displays all the in and out messages in the stacks
        :return:
        """
        if len(self.stack_out_messages) == 0:
            print("No outgoing message available")
        else:
            print("Showing outgoing messages")
            for message in self.stack_out_messages:
                message.show()
        print("--------------")

        if len(self.stack_in_messages) == 0:
            print("No in waiting message available")
        else:
            print("Showing ingoing messages")
            for message in self.stack_in_messages:
                message.show()
        print("--------------")

    def dismiss_factory(self):
        if self.comm_interface is not None:
            self.comm_interface.disconnect()
        return

    def get_out_waiting_messages(self):
        return self.stack_out_messages

    def connection_is_active(self):
        if self.comm_interface is None:
            return False
        else:
            return True

    def pop_outgoing_messages(self, how_many):
        """
        Removes a specified number of messages from the outgoing stack
        :param how_many: the number of messages to be removed
        :return:
        """
        length = len(self.stack_out_messages)
        self.stack_out_messages = self.stack_out_messages[how_many:length]

    def free_incoming_messages(self):
        """
        Resets the in waiting messages stack
        :return:
        """
        self.stack_in_messages = []
