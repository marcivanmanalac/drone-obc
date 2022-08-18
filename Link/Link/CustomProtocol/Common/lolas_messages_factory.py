import sys

# gestion des accès relatifs différents entre windows et linux
try:
    from ..UART.uart_interface import UARTInterface
    from ..CAN.can_interface import CANInterface
    from ..Common.common_messages import *
    from ..Common.messages_id import MessagesID
    from ..Common.messages_from_lolas import *
    from ..Common.messages_to_lolas import *
    from ..Common.lolas_studio_messages import *
    from ..Common.lolas_internal_messages import *

except Exception: #ImportError
    from UART.uart_interface import UARTInterface
    from CAN.can_interface import CANInterface
    from Common.common_messages import *
    from Common.messages_id import MessagesID
    from Common.messages_from_lolas import *
    from Common.messages_to_lolas import *
    from Common.lolas_studio_messages import *
    from Common.lolas_internal_messages import *


BUFFER_SAFETY_MARGIN = 0.8


class LoLasMessagesFactory:

    def __init__(self, port, protocol, IN_WAITING_LIMIT, OUT_WAITING_LIMIT):

        self.buffer_in_limit = BUFFER_SAFETY_MARGIN * IN_WAITING_LIMIT
        self.buffer_out_limit = BUFFER_SAFETY_MARGIN * OUT_WAITING_LIMIT

        self.comm_interface = None
        self.protocol = protocol
        self.port = port

        self.stack_out_messages = []
        self.stack_in_messages = []

        self.msg_id_storage = []
        for i in range(len(MessagesID)):
            self.msg_id_storage.append(0)

        self.empty_buffer_counter = 0

    def trying_to_connect(self):
        """
        Selects the right implementation of the protocol connector
        :return:
        """
        if self.protocol == "UART":
            self.comm_interface = UARTInterface(self.port, self)
        elif self.protocol == "CAN":
            self.comm_interface = CANInterface(0.1, self, 0xff)
        else:
            print("Unkown protocol, exiting...")
            sys.exit(0)

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
        # print("msg_ID ", msg_ID)
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
                new_message = LoLasAngularPosition(MessagesID.LOLAS_ANGULAR_POSITION, values, msg_number, values_are_bytes)

            elif msg_ID == MessagesID.FLIGHT_CONTROLLER_REQUESTS:
                new_message = FlightControlRequests(MessagesID.FLIGHT_CONTROLLER_REQUESTS, values, msg_number, values_are_bytes)

            elif msg_ID == MessagesID.AUTOPILOT_NAVIGATION_SENSORS:
                new_message = AutopilotNavigationSensors(MessagesID.AUTOPILOT_NAVIGATION_SENSORS, values, msg_number, values_are_bytes)

            elif msg_ID == MessagesID.LOLAS_PROXIMITY:
                new_message = LoLasProximity(MessagesID.LOLAS_PROXIMITY, values, msg_number, values_are_bytes)

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

            elif msg_ID == MessagesID.PARAMETERS_WRITE:
                new_message = WriteParametersMessage(MessagesID.PARAMETERS_WRITE, values, msg_number, values_are_bytes)

            elif msg_ID == MessagesID.PARAMETERS_READ:
                new_message = ReadParametersMessage(MessagesID.PARAMETERS_READ, values, msg_number, values_are_bytes)

            elif msg_ID == MessagesID.WRITE_PARAMETERS_INFO:
                new_message = WriteParametersInfo(MessagesID.WRITE_PARAMETERS_INFO, values, msg_number, values_are_bytes)

            elif msg_ID == MessagesID.READ_BACK_REQUEST:
                new_message = ReadBackRequest(MessagesID.READ_BACK_REQUEST, values, msg_number, values_are_bytes)

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
        if self.msg_id_storage[msg_ID.value] == 256:
            self.msg_id_storage[msg_ID.value] = 0
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
        if self.protocol == "UART":
            if self.comm_interface.lolas_interface.in_waiting > 3000:
                self.comm_interface.empty_buffer()
                return
            if self.comm_interface is not None:
                raw_messages = self.comm_interface.parse_messages()
                if len(raw_messages) > 0:
                    for raw_msg in raw_messages:
                        # raw_msg[0] : msg ID
                        # raw_msg[1] : payload
                        # raw_msg[2] : msg number
                        # raw_msg[3] : full payload in bytes
                        # raw_msg[4] : crc16
                        if raw_msg[4] != Message.crc16(raw_msg[3]):
                            print("!!!wrong crc, dumping!!!! message ID ", raw_msg[0])
                        else:
                            self.set_message(raw_msg[0], raw_msg[1], raw_msg[2], False, True)
        elif self.protocol == "CAN":
            if self.comm_interface is not None:
                raw_messages = self.comm_interface.parse_messages()

                # print(raw_messages)

                # raw_msg[0] : msg ID
                # raw_msg[1] : source
                # raw_msg[2] : msg_part
                # raw_msg[3] : msg.dlc
                # raw_msg[4] : msg.data
                if len(raw_messages) > 0:
                    # print("nb msg ", len(raw_messages))
                    # first detect if a two parts message was received
                    # TODO faut-il juste le faire en examinant la pile, ou bien en regardant une référence des ID de messages par morceaux?
                    pairs = []
                    skip_list = set()
                    for i in range(0, len(raw_messages)):
                        for j in range(0, len(raw_messages)):
                            if i != j:
                                if raw_messages[i][0] == raw_messages[j][0] and raw_messages[i][2] != raw_messages[j][2]:  # messages share the same ID but are different parts of such a message

                                    # has the pair already been identified?
                                    already_known = False
                                    # print("nb pairs ", len(pairs))
                                    for k in range(0, len(pairs)):
                                        if i in pairs[k]:
                                            already_known = True

                                    if not already_known:
                                        tmp = {i, j}
                                        pairs.append(tmp)
                                        skip_list.add(j)
                                        # print("couple ", i, " ", j)
                    # print("skip list ", skip_list)
                    for i in range(0, len(raw_messages)):
                        if i not in skip_list:
                            other_part = None
                            for k in range(0, len(pairs)):
                                if i in pairs[k]:

                                    candidate = pairs[k].pop()
                                    if candidate != i:
                                        other_part = candidate
                                    else:
                                        candidate = pairs[k].pop()
                                        other_part = candidate
                                    # print("index ", i, " , mate ", other_part)
                            # put the payloads together
                            if other_part is not None:
                                assembled_payload = raw_messages[i][4] + raw_messages[other_part][4]
                            else:
                                assembled_payload = raw_messages[i][4]
                            # print("merge payload : ",  assembled_payload)
                            self.set_message(raw_messages[i][0], assembled_payload, 0, False, True)  # todo message number sur la messagerie CAN? Le reconstruire à partir du timestamp?

        return len(self.stack_in_messages)

    def send_available_messages(self):
        """
        Sends all the messages in the outgoing messages stack
        :return: the number of messages sent
        """
        if self.comm_interface is not None:
            number_of_msg_sent = self.comm_interface.send_messages()
            return number_of_msg_sent
        else:
            print("Cannot send messages, no active interface")
            return 0

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

    def have_you_seen_data_recently(self, size_of_last_rec):
        if size_of_last_rec == 0:
            self.empty_buffer_counter += 1
        else:
            self.empty_buffer_counter = 0
        if self.empty_buffer_counter < 50:
            return True
        else:
            return False

    def start_acquisition(self):
        self.comm_interface.send_start_command()

    def stop_acquisition(self):
        self.comm_interface.send_stop_command()
