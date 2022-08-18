import serial
try:
    import RPi.GPIO as GPIO
except:
    pass

try:
    from ..Common.messages_id import MessagesID
    from ..Common.message import Message
except Exception: #ImportError
    from Common.messages_id import MessagesID
    from Common.message import Message

START_FLAG = b"\x7f"
START_COMMMAND = b"\xaa"
STOP_COMMMAND = b"\xcc"
lolas_baud = 115200
# vrai pour utiliser le mode software in the loop : pas de lolas physiquement connectÃ©
SITL = False

# RS485 configuraton
EN_485 = 4

class UARTInterface:

    def __init__(self, port, message_factory_reference):
        self.port = port
        self.message_factory = message_factory_reference
        # self.message_ID_reference = message_ID_reference
        self.lolas_interface = self.connect_to_lolas()

        # RS485 setup
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(EN_485, GPIO.OUT)
            GPIO.output(EN_485, GPIO.LOW)
        except:
            print("could not setup RS485")
            pass

    def parse_messages(self):
        """
        Parses the incoming messages and checks the crc
        :return: an array containing the raw messages (bytes) for further decoding
        """
        raw_messages = []
        if SITL:
            # message = Ping(0, [], 63)

            tmp = list([])
            tmp.append(MessagesID(1))
            tmp.append(b'\x2f\x04\x1f\x01')
            tmp.append(b'63')

            raw_messages.append(tmp)
            return raw_messages
        else:
            # while True:
            while self.lolas_interface.in_waiting:
                byte = self.lolas_interface.read(1)  # sur windows en usb
                # print(byte)
                if byte == b"|":  # EOF
                    break
                elif byte == START_FLAG:  # start bytes # sur windows en usb
                    # print("start")
                    payload_length = self.lolas_interface.read(1)
                    # print("raw payload length : " + str(payload_length))
                    msg_ID = self.lolas_interface.read(1)
                    # print("raw msg ID : " + str(msg_ID))

                    # print("interpreted msg ID : " + str(msg_ID))
                    payload = self.lolas_interface.read(int.from_bytes(payload_length, byteorder=Message.INDIANNESS) - 2)
                    # print("raw payload : " + str(payload))
                    msg_number = self.lolas_interface.read(1)
                    # print("raw msg number : " + str(msg_number))

                    full_raw_payload = msg_ID + payload + msg_number
                    # print(full_raw_payload)
                    try:  # if the message if corrupted, the ID won't be parsed correctly, resulting in cast/valueError exception
                        msg_ID = MessagesID(int.from_bytes(msg_ID, byteorder=Message.INDIANNESS))
                    except ValueError:
                        break  # in that case we leave it there and move to the next message

                    crc = self.lolas_interface.read(2)

                    tmp = list([])
                    tmp.append(msg_ID)
                    tmp.append(payload)
                    tmp.append(msg_number)
                    tmp.append(full_raw_payload)
                    tmp.append(int.from_bytes(crc, byteorder=Message.INDIANNESS, signed=False))

                    raw_messages.append(tmp)

            # print("" + str(len(raw_messages)) + " messages read")
            return raw_messages

    def send_messages(self):
        """
        Writes out the available messages in the message factory to the port
        :return: the number of messages sent
        """
        if self.lolas_interface is None or SITL:
            return 0
        if self.message_factory is not None:
            messages_to_be_sent = self.message_factory.get_out_waiting_messages()

            number_of_msg_sent = 0

            for message in messages_to_be_sent:
                # message.show()
                number_of_msg_sent += 1
                bytes_sequence = message.as_bytes_sequence()
                # todo gérer les fréquences d'envoi propre à chaque message
                self.lolas_interface.write(START_FLAG)
                self.lolas_interface.write(message.payload_size(bytes_sequence))
                self.lolas_interface.write(bytes_sequence)

                crc = int.to_bytes(Message.crc16(bytes_sequence), 2, byteorder=Message.INDIANNESS)
                self.lolas_interface.write(crc)
                # print("envoi")
                # print("sent start : " + str(START_FLAG))
                # print("sent payload size : " + str(message.payload_size()))
                # print("sent bytes : " + str(message.as_bytes_sequence()))
        return number_of_msg_sent

    def connect_to_lolas(self):
        if SITL:
            return None
        return serial.Serial(self.port, lolas_baud, timeout=2)

    def disconnect(self):
        if SITL:
            return
        if self.lolas_interface is not None:
            # self.lolas_interface.write(b'q')
            GPIO.output(EN_485, GPIO.HIGH)
            GPIO.cleanup()
            self.empty_buffer()
            self.lolas_interface.close()
        else:
            print("No active connection")

    def empty_buffer(self):
        if SITL:
            return
        if self.lolas_interface is not None:
            self.lolas_interface.reset_input_buffer()

    def send_start_command(self):
        """
        Sends the start command to lolas, that will trigger messages emissions from lolas
        :return: None
        """
        if self.lolas_interface is None or SITL:
            return 0
        if self.message_factory is not None:
            self.lolas_interface.write(START_COMMMAND)

    def send_stop_command(self):
        """
        Sends the stop command to lolas, that will stop messages emissions from lolas
        :return: None
        """
        if self.lolas_interface is None or SITL:
            return 0
        if self.message_factory is not None:
            self.lolas_interface.write(STOP_COMMMAND)
