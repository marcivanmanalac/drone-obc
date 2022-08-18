from .message import Message


class FlightControlRequests(Message):

    # mode_change       1 byte  unsigned
    # start_guidance    1 bit
    # abort_landing     1 bit  les bits sont sur le même byte

    def __init__(self, msg_id, values, msg_number, values_are_bytes):
        super().__init__(msg_id, values, msg_number)

        if values_are_bytes:  # in this case a two bytes, containing the desired mode and the bits of interest
            self.mode_change = values[0]

            tmp = []
            if Message.INDIANNESS == 'big':
                for i in range(8):
                    tmp.append((values[1] >> i) & 1)
            else:
                for i in reversed(range(8)):
                    tmp.append((values[1] >> i) & 1)

            self.start_guidance = tmp[1]
            self.abort_landing = tmp[0]

            self.values_as_array_of_bytes = []
            self.values_as_array_of_bytes.append(values[0])
            self.values_as_array_of_bytes.append(values[1])

        else:
            if self.is_values_array_valid(3, values):
                self.mode_change = int.to_bytes(values[0], 1, byteorder=Message.INDIANNESS)
                self.start_guidance = values[1]
                self.abort_landing = values[2]

                integer_equivalent = values[1] * 2 + values[2] * 1

                self.values_as_array_of_bytes = []
                self.values_as_array_of_bytes.append(self.mode_change)
                self.values_as_array_of_bytes.append(int.to_bytes(integer_equivalent, 1, byteorder=Message.INDIANNESS))

    def show(self):
        print("Requests from flight control" + " #", self.msg_number)
        print("mode_change : " + str(self.mode_change))
        print("start_guidance : " + str(self.start_guidance))
        print("abort_landing : " + str(self.abort_landing))
        print("---")

    def as_reduced_bytes_sequence(self, part):
        tmp = b''

        return tmp


class AutopilotNavigationSensors(Message):

    # pitch             1 byte  (deg)   signed
    # roll              1 byte  (deg)   signed
    # heading           2 byte  (deg)   unsigned  GPS_RAW_INT ( #24 )??
    # drone_vx          2 byte  (mm/s)  signed
    # drone_vy          2 byte  (mm/s)  signed
    # drone_vz          2 byte  (mm/s)  signed
    # GPS info Besoin à confirmer, non implémenté dans un premier temps

    def __init__(self, msg_id, values, msg_number, values_are_bytes):
        super().__init__(msg_id, values, msg_number)

        if values_are_bytes:
            self.pitch = values[0]
            self.roll = values[1]
            self.heading = values[2:4]

            self.drone_vx = values[4:6]
            self.drone_vy = values[6:8]
            self.drone_vz = values[8:10]

            self.values_as_array_of_bytes = []
            self.values_as_array_of_bytes.append(self.pitch)
            self.values_as_array_of_bytes.append(self.roll)
            self.values_as_array_of_bytes.append(self.heading)
            self.values_as_array_of_bytes.append(self.drone_vx)
            self.values_as_array_of_bytes.append(self.drone_vy)
            self.values_as_array_of_bytes.append(self.drone_vz)

        else:
            if self.is_values_array_valid(6, values):

                self.pitch = int.to_bytes(values[0], 1, byteorder=Message.INDIANNESS, signed=True)
                self.roll = int.to_bytes(values[1], 1, byteorder=Message.INDIANNESS, signed=True)
                self.heading = int.to_bytes(values[2], 2, byteorder=Message.INDIANNESS, signed=False)

                self.drone_vx = int.to_bytes(values[3], 2, byteorder=Message.INDIANNESS, signed=True)
                self.drone_vy = int.to_bytes(values[4], 2, byteorder=Message.INDIANNESS, signed=True)
                self.drone_vz = int.to_bytes(values[5], 2, byteorder=Message.INDIANNESS, signed=True)

                self.values_as_array_of_bytes = []
                self.values_as_array_of_bytes = []
                self.values_as_array_of_bytes.append(self.pitch)
                self.values_as_array_of_bytes.append(self.roll)
                self.values_as_array_of_bytes.append(self.heading)
                self.values_as_array_of_bytes.append(self.drone_vx)
                self.values_as_array_of_bytes.append(self.drone_vy)
                self.values_as_array_of_bytes.append(self.drone_vz)

    def show(self):
        print("Navigation sensors" + " #", self.msg_number)
        try:
            print("drone pitch : ", int.from_bytes(self.pitch, byteorder=Message.INDIANNESS, signed=True))
            print("drone roll : ", int.from_bytes(self.roll, byteorder=Message.INDIANNESS, signed=True))
            print("drone heading : ", int.from_bytes(self.heading, byteorder=Message.INDIANNESS, signed=False))
        except TypeError:

            if self.pitch > 127:
                tmp = (256 - self.pitch) * (-1)
                print("drone pitch : ", tmp)
            else:
                print("drone pitch : ", self.pitch)

            if self.roll > 127:
                tmp = (256 - self.roll) * (-1)
                print("drone roll : ", tmp)
            else:
                print("drone roll : ", self.roll)

            print("drone heading : ", self.heading)

        print("drone vx : " + str(int.from_bytes(self.drone_vx, byteorder=Message.INDIANNESS, signed=True)))
        print("drone vy : " + str(int.from_bytes(self.drone_vy, byteorder=Message.INDIANNESS, signed=True)))
        print("drone vz : " + str(int.from_bytes(self.drone_vz, byteorder=Message.INDIANNESS, signed=True)))
        print("---")

    def as_reduced_bytes_sequence(self, part):
        tmp = b''

        return tmp
