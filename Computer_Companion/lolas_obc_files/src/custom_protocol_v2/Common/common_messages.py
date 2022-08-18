from .message import Message


class Ping(Message):

    def __init__(self, msg_id, values, msg_number, values_are_bytes):
        super().__init__(msg_id, values, msg_number)

        self.values_as_array_of_bytes = None

    def show(self):
        print("Ping message" + " #", self.msg_number)
        print("msg_number : " + str(self.msg_number))
        print("---")

    def as_reduced_bytes_sequence(self, part):
        tmp = b''

        return tmp


class Ack(Message):

    # ack_id                1 byte  unsigned
    # ack_msg_number        2 byte  unsigned
    # will_do               1 byte  unsigned

    def __init__(self, msg_id, values, msg_number, values_are_bytes):
        super().__init__(msg_id, values, msg_number)

        if values_are_bytes:
            self.ack_id = values[0]
            self.ack_msg_number = values[1:3]
            self.will_do = values[3]

            self.values_as_array_of_bytes = []
            self.values_as_array_of_bytes.append(self.ack_id)
            self.values_as_array_of_bytes.append(self.ack_msg_number)
            self.values_as_array_of_bytes.append(self.will_do)

        else:
            if self.is_values_array_valid(3, values):
                self.ack_id = int.to_bytes(values[0], 1, byteorder=Message.INDIANNESS)
                self.ack_msg_number = int.to_bytes(values[1], 2, byteorder=Message.INDIANNESS)
                self.will_do = int.to_bytes(values[2], 1, byteorder=Message.INDIANNESS)

                self.values_as_array_of_bytes = []
                self.values_as_array_of_bytes.append(self.ack_id)
                self.values_as_array_of_bytes.append(self.ack_msg_number)
                self.values_as_array_of_bytes.append(self.will_do)

            else:
                self.values_as_array_of_bytes = None
                self.ack_id = None
                self.ack_msg_number = None
                self.will_do = None
                return None

    def show(self):
        print("Ack message" + " #", self.msg_number)
        print("ack id : " + str(self.ack_id))
        print("ack msg number : ", int.from_bytes(self.ack_msg_number, byteorder=Message.INDIANNESS, signed=False))
        print("will do : " + str(self.will_do))
        print("---")

    def as_reduced_bytes_sequence(self, part):
        tmp = b''
        if part == 0:
            for bytes in self.values_as_array_of_bytes[0:4]:
                tmp += bytes

        return tmp


class NodeDeclaration(Message):

    # Equipment kind        1 byte  unsigned
    # UID                   4 bytes  unsigned
    # Known role            1 byte  unsigned
    # Firmware version      1 byte  unsigned
    # Parameters hashcode   1 byte  unsigned

    def __init__(self, msg_id, values, msg_number, values_are_bytes):
        super().__init__(msg_id, values, msg_number)

        if values_are_bytes and self.is_values_array_valid(8, values):
            self.equipment_kind = values[0]
            self.uid = values[1:5]
            self.role = values[5]
            self.firmware_version = values[6]
            self.parameters_hashcode = values[7]

            self.values_as_array_of_bytes = []
            self.values_as_array_of_bytes.append(self.equipment_kind)
            self.values_as_array_of_bytes.append(self.uid)
            self.values_as_array_of_bytes.append(self.role)
            self.values_as_array_of_bytes.append(self.firmware_version)
            self.values_as_array_of_bytes.append(self.parameters_hashcode)

        else:
            if self.is_values_array_valid(5, values):
                # self.ack_id = int.to_bytes(values[0], 1, byteorder=Message.INDIANNESS)
                # self.ack_msg_number = int.to_bytes(values[1], 2, byteorder=Message.INDIANNESS)
                # self.will_do = int.to_bytes(values[2], 1, byteorder=Message.INDIANNESS)

                self.equipment_kind = int.to_bytes(values[0], 1, byteorder=Message.INDIANNESS)
                self.uid = int.to_bytes(values[1], 4, byteorder=Message.INDIANNESS)
                self.role = int.to_bytes(values[2], 1, byteorder=Message.INDIANNESS)
                self.firmware_version = int.to_bytes(values[3], 1, byteorder=Message.INDIANNESS)
                self.parameters_hashcode = int.to_bytes(values[4], 1, byteorder=Message.INDIANNESS)

                self.values_as_array_of_bytes = []
                self.values_as_array_of_bytes.append(self.equipment_kind)

                self.values_as_array_of_bytes.append(self.uid)
                self.values_as_array_of_bytes.append(self.role)
                self.values_as_array_of_bytes.append(self.firmware_version)
                self.values_as_array_of_bytes.append(self.parameters_hashcode)

            else:
                self.values_as_array_of_bytes = None
                self.equipment_kind = None
                self.parameters_hashcode = None
                self.uid = None
                self.role = None
                self.firmware_version = None
                return None

    def show(self):
        print("Node declaration message" + " #", self.msg_number)
        print("equipment_kind : " + str(self.equipment_kind))
        print("uid : ", int.from_bytes(self.uid, byteorder=Message.INDIANNESS, signed=False))
        print("role : " + str(self.role))
        print("firmware_version : " + str(self.firmware_version))
        print("parameters_hashcode : " + str(self.parameters_hashcode))
        print("---")

    def as_reduced_bytes_sequence(self, part):
        tmp = b''

        return tmp