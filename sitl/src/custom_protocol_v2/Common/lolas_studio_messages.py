from .message import Message


class WriteParametersMessage(Message):

    # parameter 1                 1 byte unsigned
    # parameter 2                 1 byte unsigned
    # parameter 3                 1 byte unsigned
    # parameter 4                 1 byte unsigned
    # parameter 5                 2 bytes unsigned
    # parameter 6                 2 bytes unsigned
    # parameter 7                 2 bytes unsigned

    def __init__(self, msg_id, values, msg_number, values_are_bytes):
        super().__init__(msg_id, values, msg_number)

        if values_are_bytes:
            if self.is_values_array_valid(10, values):
                self.parameter_1 = values[0]
                self.parameter_2 = values[1]
                self.parameter_3 = values[2]
                self.parameter_4 = values[3]
                self.parameter_5 = values[4:6]
                self.parameter_6 = values[6:8]
                self.parameter_7 = values[8:10]

        else:
            if self.is_values_array_valid(7, values):
                self.parameter_1 = values[0]
                self.parameter_2 = values[1]
                self.parameter_3 = values[2]
                self.parameter_4 = values[3]
                self.parameter_5 = values[4]
                self.parameter_6 = values[5]
                self.parameter_7 = values[6]

                self.values_as_array_of_bytes = []
                self.values_as_array_of_bytes.append(int.to_bytes(values[0], 1, byteorder=Message.INDIANNESS))
                self.values_as_array_of_bytes.append(int.to_bytes(values[1], 1, byteorder=Message.INDIANNESS))
                self.values_as_array_of_bytes.append(int.to_bytes(values[2], 1, byteorder=Message.INDIANNESS))
                self.values_as_array_of_bytes.append(int.to_bytes(values[3], 1, byteorder=Message.INDIANNESS))
                self.values_as_array_of_bytes.append(int.to_bytes(values[4], 2, byteorder=Message.INDIANNESS))
                self.values_as_array_of_bytes.append(int.to_bytes(values[5], 2, byteorder=Message.INDIANNESS))
                self.values_as_array_of_bytes.append(int.to_bytes(values[6], 2, byteorder=Message.INDIANNESS))

    def show(self):
        print("Write parameters message" + " #", self.msg_number)

        print("parameter_1 : ", self.parameter_1)
        print("parameter_2 : ", self.parameter_2)
        print("parameter_3 : ", self.parameter_3)
        print("parameter_4 : ", self.parameter_4)
        print("parameter_5 : ", self.parameter_5)
        print("parameter_6 : ", self.parameter_6)
        print("parameter_7 : ", self.parameter_7)
        print("---")

    def as_reduced_bytes_sequence(self, part):
        tmp = b''
        if part == 0:
            for bytes in self.values_as_array_of_bytes[0:4]:
                tmp += bytes

        elif part == 1:
            for bytes in self.values_as_array_of_bytes[4:10]:
                tmp += bytes

        return tmp


class ReadParametersMessage(Message):

    # parameter 1                 4 bytes unsigned
    # parameter 2                 1 byte unsigned
    # parameter 3                 1 byte unsigned
    # parameter 4                 1 byte unsigned
    # parameter 5                 1 byte unsigned
    # parameter 6                 2 bytes unsigned
    # parameter 7                 2 bytes unsigned
    # parameter 8                 2 bytes unsigned

    def __init__(self, msg_id, values, msg_number, values_are_bytes):
        super().__init__(msg_id, values, msg_number)

        if values_are_bytes:
            if self.is_values_array_valid(14, values):
                self.parameter_1 = values[0:4]
                self.parameter_2 = values[4:5]
                self.parameter_3 = values[5:6]
                self.parameter_4 = values[6:7]
                self.parameter_5 = values[7:8]
                self.parameter_6 = values[8:10]
                self.parameter_7 = values[10:12]
                self.parameter_8 = values[12:14]

        else:
            if self.is_values_array_valid(10, values):
                self.parameter_1 = values[0]
                self.parameter_2 = values[1]
                self.parameter_3 = values[2]
                self.parameter_4 = values[3]
                self.parameter_5 = values[4]
                self.parameter_6 = values[5]
                self.parameter_7 = values[6]
                self.parameter_8 = values[7]

                self.values_as_array_of_bytes = []
                self.values_as_array_of_bytes.append(int.to_bytes(values[0], 4, byteorder=Message.INDIANNESS))
                self.values_as_array_of_bytes.append(int.to_bytes(values[1], 1, byteorder=Message.INDIANNESS))
                self.values_as_array_of_bytes.append(int.to_bytes(values[2], 1, byteorder=Message.INDIANNESS))
                self.values_as_array_of_bytes.append(int.to_bytes(values[3], 1, byteorder=Message.INDIANNESS))
                self.values_as_array_of_bytes.append(int.to_bytes(values[4], 1, byteorder=Message.INDIANNESS))
                self.values_as_array_of_bytes.append(int.to_bytes(values[5], 2, byteorder=Message.INDIANNESS))
                self.values_as_array_of_bytes.append(int.to_bytes(values[6], 2, byteorder=Message.INDIANNESS))
                self.values_as_array_of_bytes.append(int.to_bytes(values[7], 2, byteorder=Message.INDIANNESS))

    def show(self):
        print("Read parameters message" + " #", self.msg_number)

        print("parameter_1 : ", self.parameter_1)
        print("parameter_2 : ", self.parameter_2)
        print("parameter_3 : ", self.parameter_3)
        print("parameter_4 : ", self.parameter_4)
        print("parameter_5 : ", self.parameter_5)
        print("parameter_6 : ", self.parameter_6)
        print("parameter_7 : ", self.parameter_7)
        print("parameter_8 : ", self.parameter_8)
        print("---")

    def as_reduced_bytes_sequence(self, part):
        tmp = b''

        return tmp


class WriteParametersInfo(Message):

    # write result                                  1 byte unsigned
    # number of parameters written                  1 byte unsigned

    def __init__(self, msg_id, values, msg_number, values_are_bytes):
        super().__init__(msg_id, values, msg_number)

        if values_are_bytes:
            if self.is_values_array_valid(2, values):
                self.write_result = values[0]
                self.number_parameters_written = values[1]

        else:
            if self.is_values_array_valid(2, values):
                self.write_result = values[0]
                self.number_parameters_written = values[1]

                self.values_as_array_of_bytes = []
                self.values_as_array_of_bytes.append(int.to_bytes(values[0], 1, byteorder=Message.INDIANNESS))
                self.values_as_array_of_bytes.append(int.to_bytes(values[1], 1, byteorder=Message.INDIANNESS))

    def show(self):
        print("Write parameters info" + " #", self.msg_number)

        print("write_result : ", self.write_result)
        print("number_parameters_written : ", self.number_parameters_written)
        print("---")

    def as_reduced_bytes_sequence(self, part):
        tmp = b''

        return tmp


class ReadBackRequest(Message):

    # None                                  None

    def __init__(self, msg_id, values, msg_number, values_are_bytes):
        super().__init__(msg_id, values, msg_number)

        self.values_as_array_of_bytes = None

    def show(self):
        print("Read Back Request" + " #", self.msg_number)
        print("---")

    def as_reduced_bytes_sequence(self, part):
        tmp = b''

        return tmp
