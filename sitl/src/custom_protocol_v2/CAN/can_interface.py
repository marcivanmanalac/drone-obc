import can
import os

try:
    from ..Common.messages_id import MessagesID, ComplexMessagesID
    from ..Common.message import Message
except Exception: #ImportError
    from Common.messages_id import MessagesID, ComplexMessagesID
    from Common.message import Message

SITL = False


class CANInterface:

    def __init__(self, timeout, message_factory_reference, source_addr):
        self.message_factory = message_factory_reference
        self.lolas_interface = self.connect_to_lolas()
        self.rec_timeout = timeout
        self.reader = can.BufferedReader()
        self.notifier = can.Notifier(self.lolas_interface, [self.reader])
        self.own_address = source_addr

    def parse_messages(self):
        """
        Parses the incoming messages and checks the crc
        :return: an array containing the raw messages (bytes) for further decoding
        """
        raw_messages = []
        if SITL:
            # message = Ping(0, [], 63)

            # tmp = list([])
            # tmp.append(MessagesID(1))
            # tmp.append(b'\x2f\x04\x1f\x01')
            # tmp.append(b'63')
            #
            # raw_messages.append(tmp)
            return raw_messages
        else:
            # for msg in self.lolas_interface:  # semble bloquant, préférer recv avec un timeout?
            # msg = self.lolas_interface.recv(self.rec_timeout)
            # if msg is not None:
            msg = self.reader.get_message(0.2)
            while msg is not None:
                msg_id = (msg.arbitration_id >> 4) & 0x00FF
                source = (msg.arbitration_id >> 12)
                msg_part = msg.arbitration_id & 0x0000F


                # packet_info_header = "Timestamp		arbitration"
                # packet_info = "" + str(msg.timestamp) + "	" + str(msg.arbitration_id)
                # header = ""
                # values = ""
                # for i in range(msg.dlc):
                #     header += "byte" + str(i) + "	"
                #     values += "" + str(msg.data[i]) + "	"
                # print("------------------")
                # print(packet_info_header)
                # print(packet_info)
                # print("msg id : " + str(msg_id))
                # print("source : " + str(source))
                # print("msg part : " + str(msg_part))
                # print("------")
                # print(header)
                # print(values)
                # print("------------------")

                # assemblage du message brut pour traitement par la factory
                tmp = list([])
                try:  # if the message if corrupted, the ID won't be parsed correctly, resulting in cast/valueError exception
                    msg_id = MessagesID(msg_id)
                except ValueError:
                    break  # in that case we leave it there and move to the next message
                tmp.append(msg_id)
                tmp.append(source)
                tmp.append(msg_part)
                tmp.append(msg.dlc)
                tmp.append(list(msg.data))

                raw_messages.append(tmp)

                # y a t il un autre message?
                msg = self.reader.get_message(0.1)
            return raw_messages

    def send_messages(self):
        """
        Writes out the available messages in the message factory to the port
        :return: the number of messages sent
        """
        number_of_msg_sent = 0

        if self.message_factory is not None:
            messages_to_be_sent = self.message_factory.get_out_waiting_messages()

            number_of_msg_sent = 0

            for message in messages_to_be_sent:
                # message.show()
                # if isinstance(ComplexMessagesID(int(message.id)), ComplexMessagesID):
                is_complex = False
                for complex_msg_id in ComplexMessagesID:
                    if int(message.id) == complex_msg_id.value:
                        is_complex = True

                if is_complex:
                    # print("message complexe")
                    number_of_parts = message.how_many_parts()

                    for i in range(0, number_of_parts):
                        bytes_sequence = message.as_reduced_bytes_sequence(i)

                        built_arbitration_id = self.build_arbitration_id(int(message.id), i)
                        # print(hex(built_arbitration_id))
                        msg = can.Message(arbitration_id=built_arbitration_id,
                                          data=bytes_sequence,
                                          extended_id=True)
                        try:
                            self.lolas_interface.send(msg)
                            number_of_msg_sent += 1
                        except OSError:
                            print("CAN message could not be sent")
                            break
                    return number_of_msg_sent
                else:
                    # print("message simple")
                    # print("message id ", message.id)
                    bytes_sequence = message.as_reduced_bytes_sequence(0)

                    built_arbitration_id = self.build_arbitration_id(int(message.id), 0)
                    # print(hex(built_arbitration_id))
                    msg = can.Message(arbitration_id=built_arbitration_id,
                                      data=bytes_sequence,
                                      extended_id=True)
                    try:
                        self.lolas_interface.send(msg)
                        number_of_msg_sent += 1
                    except OSError:
                        print("CAN message could not be sent")
                        break

        return number_of_msg_sent

    def build_arbitration_id(self, msg_id, part_number):
        first_part = self.own_address
        first_part = str(hex(first_part))

        # msg_id = str(msg_id)
        # second_part = msg_id[0]
        # second_part = str(hex(int(second_part)))
        second_part = str(hex(msg_id))

        # second_part_bis = msg_id[1]
        # second_part_bis = str(hex(int(second_part_bis)))

        third_part = 0xA
        if part_number == 1:
            third_part = 0xB
        elif part_number == 2:
            third_part = 0xC
        elif part_number == 3:
            third_part = 0xD

        third_part = str(hex(third_part))

        if len(second_part)-2 == 1:  # si id <15 on fait du padding avec un 0 pour respecter le format
            second_part = "0"+second_part[-1:]
            assy = "" + first_part + second_part + third_part[-1:]
        else:
            assy = ""+first_part+second_part[2:4]+third_part[-1:]
        # print(assy)

        return int(assy, 16)

    def append_hex(self, a, b):
        sizeof_b = 0

        # get size of b in bits
        while ((b >> sizeof_b) > 0):
            sizeof_b += 1

        # align answer to nearest 4 bits (hex digit)
        sizeof_b += sizeof_b % 4

        return (a << sizeof_b) | b


    def connect_to_lolas(self):
        # Bring up can0 interface at 1 Mbps
        try:
            os.system('sudo ip link set can0 type can bitrate 1000000')
            os.system('sudo ifconfig can0 up')
        except OSError:
            print('Cannot set up can0 interface')
            exit()

        try:
            bus = can.interface.Bus(channel='can0', bustype='socketcan')
        except OSError:
            print('Cannot find interface board.')
            exit()
        return bus

    def disconnect(self):
        # if SITL:
        #     return
        if self.lolas_interface is not None:
            os.system('sudo ifconfig can0 down')
            print('\n\rCan link closed')
        else:
            print("No active connection")

    # def empty_buffer(self):
    #     if SITL:
    #         return
    #     if self.lolas_interface is not None:
    #         self.lolas_interface.reset_input_buffer()
    #
    # def send_start_command(self):
    #     """
    #     Sends the start command to lolas, that will trigger messages emissions from lolas
    #     :return: None
    #     """
    #     if self.lolas_interface is None or SITL:
    #         return 0
    #     if self.message_factory is not None:
    #         self.lolas_interface.write(START_COMMMAND)
    #
    # def send_stop_command(self):
    #     """
    #     Sends the stop command to lolas, that will stop messages emissions from lolas
    #     :return: None
    #     """
    #     if self.lolas_interface is None or SITL:
    #         return 0
    #     if self.message_factory is not None:
    #         self.lolas_interface.write(STOP_COMMMAND)
