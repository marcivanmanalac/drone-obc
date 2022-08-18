from abc import ABC, abstractmethod


class Message(ABC):

    INDIANNESS = 'little'  # 'little' or 'big'

    @abstractmethod
    def __init__(self, msg_id, values, msg_number):
        self.id = msg_id
        self.msg_number = msg_number
        self.values = values
        self.values_as_array_of_bytes = None
        pass

    @abstractmethod
    def show(self):
        pass

    def is_values_array_valid(self, expected_len, values_array):
        """
        Checks whether the array containing the values of interest is of the expected length
        :param expected_len: in array elements
        :param values_array: the array to be tested
        :return: true if the length matches, false otherwise
        """
        if expected_len != len(values_array):
            print("invalid array size")
            return False
        else:
            return True

    def payload_size(self, bytes_sequence):
        """
        Computes de size of the payload (msg ID and msg number included) as a number of bytes for further reading
        :param bytes_sequence: the full payload (msg ID and msg number included) in bytes
        :return: the number of bytes contained in the sequence
        """
        return int.to_bytes(len(bytes_sequence), 1, byteorder=self.INDIANNESS)

    def as_bytes_sequence(self):
        """
        Concatenates the message ID, the payload and the message number as bytes
        :return: bytes
        """
        tmp = b''
        tmp += int.to_bytes(self.id.value, 1, byteorder=self.INDIANNESS)

        if self.values_as_array_of_bytes is not None:
            for bytes in self.values_as_array_of_bytes:
                tmp += bytes
                # print(str(tmp))
        # print(str(self.msg_number))
        tmp += int.to_bytes(self.msg_number, 1, byteorder=self.INDIANNESS)
        # print(str(tmp))
        return tmp

    def reduced_payload_size(self):
        return len(self.as_bytes_sequence())-2

    def how_many_parts(self):
        payload_size = self.reduced_payload_size()
        if payload_size <= 8:
            return 1
        elif payload_size <= 16:
            return 2
        elif payload_size <= 24:
            return 3
        elif payload_size <= 32:
            return 4
        else:
            return None

    @abstractmethod
    def as_reduced_bytes_sequence(self, part):
        """
        Concatenates only the payload as bytes, or event subpart of the payload (complex CAN messages)
        :param part: the partial payload to be returned
        :return: the payload as bytes sequence (max 8 bytes to be compliant with CAN standard)
        """
        pass

    @staticmethod
    def crc16(data):
        """
        CRC-16/BUYPASS, CRC-16-ANSI, CRC-16-IBM
        :param data: the bytes we want to compute the CRC for
        :return: 2 bytes CRC16 result
        """
        xor_in = 0x0000  # initial value
        xor_out = 0x0000  # final XOR value
        poly = 0x8005  # generator polinom (normal form)

        reg = xor_in
        for octet in data:
            # reflect in
            for i in range(8):
                topbit = reg & 0x8000
                if octet & (0x80 >> i):
                    topbit ^= 0x8000
                reg <<= 1
                if topbit:
                    reg ^= poly
            reg &= 0xFFFF
            # reflect out
        return reg ^ xor_out
