from .message import Message


class RangesTransferMessage(Message):

    # range 1              4 byte unsigned
    # range 2              4 byte unsigned
    # range 3              4 byte unsigned
    # range 4              4 byte unsigned
    # range 5              4 byte unsigned
    # range 6              4 byte unsigned
    # range 7              4 byte unsigned
    # range 8              4 byte unsigned

    def __init__(self, msg_id, values, msg_number, values_are_bytes):
        super().__init__(msg_id, values, msg_number)

        if values_are_bytes:  # in this case 32 bytes
            if self.is_values_array_valid(32, values):
                self.range_1 = values[0:4]
                self.range_2 = values[4:8]
                self.range_3 = values[8:12]
                self.range_4 = values[12:16]
                self.range_5 = values[16:20]
                self.range_6 = values[20:24]
                self.range_7 = values[24:28]
                self.range_8 = values[28:32]

        else:
            if self.is_values_array_valid(8, values):

                self.values_as_array_of_bytes = []
                self.values_as_array_of_bytes.append(int.to_bytes(values[0], 4, byteorder=Message.INDIANNESS))
                self.values_as_array_of_bytes.append(int.to_bytes(values[1], 4, byteorder=Message.INDIANNESS))
                self.values_as_array_of_bytes.append(int.to_bytes(values[2], 4, byteorder=Message.INDIANNESS))
                self.values_as_array_of_bytes.append(int.to_bytes(values[3], 4, byteorder=Message.INDIANNESS))
                self.values_as_array_of_bytes.append(int.to_bytes(values[4], 4, byteorder=Message.INDIANNESS))
                self.values_as_array_of_bytes.append(int.to_bytes(values[5], 4, byteorder=Message.INDIANNESS))
                self.values_as_array_of_bytes.append(int.to_bytes(values[6], 4, byteorder=Message.INDIANNESS))
                self.values_as_array_of_bytes.append(int.to_bytes(values[7], 4, byteorder=Message.INDIANNESS))

    def show(self):
        try:
            print("Ranges Transfer Message" + " #" + str(int.from_bytes(self.msg_number, byteorder=Message.INDIANNESS, signed=False)))
        except:
            print("Ranges Transfer Message" + " #" + str(self.msg_number))
        try:
            print("range_1 : " + str(int.from_bytes(self.range_1, byteorder=Message.INDIANNESS, signed=False)))
            print("range_2 : " + str(int.from_bytes(self.range_2, byteorder=Message.INDIANNESS, signed=False)))
            print("range_3 : " + str(int.from_bytes(self.range_3, byteorder=Message.INDIANNESS, signed=False)))
            print("range_4 : " + str(int.from_bytes(self.range_4, byteorder=Message.INDIANNESS, signed=False)))
            print("range_5 : " + str(int.from_bytes(self.range_5, byteorder=Message.INDIANNESS, signed=False)))
            print("range_6 : " + str(int.from_bytes(self.range_6, byteorder=Message.INDIANNESS, signed=False)))
            print("range_7 : " + str(int.from_bytes(self.range_7, byteorder=Message.INDIANNESS, signed=False)))
            print("range_8 : " + str(int.from_bytes(self.range_8, byteorder=Message.INDIANNESS, signed=False)))
            print("---")
        except:
            pass

    def as_reduced_bytes_sequence(self, part):
        tmp = b''
        if part == 0:
            for bytes in self.values_as_array_of_bytes[0:2]:
                tmp += bytes

        elif part == 1:
            for bytes in self.values_as_array_of_bytes[2:4]:
                tmp += bytes

        elif part == 2:
            for bytes in self.values_as_array_of_bytes[4:6]:
                tmp += bytes

        elif part == 3:
            for bytes in self.values_as_array_of_bytes[6:8]:
                tmp += bytes

        return tmp
