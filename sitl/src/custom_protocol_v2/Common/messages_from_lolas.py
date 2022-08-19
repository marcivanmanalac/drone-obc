from .message import Message


class Status(Message):

    # drone system health word      1 byte      (-)     unsigned
    # ground system health word     1 byte      (-)     unsigned
    # Time since boot               4 bytes     (ms)    unsigned
    # Current mode                  1 byte      (-)     unsigned
    # Role                          1 byte      (-)     unsigned

    def __init__(self, msg_id, values, msg_number, values_are_bytes):
        super().__init__(msg_id, values, msg_number)

        if values_are_bytes:
            self.drone_system_health = values[0]
            self.ground_system_health = values[1]
            self.time_since_boot = values[2:6]
            self.current_mode = values[6]
            self.role = values[7]

            self.values_as_array_of_bytes = []
            self.values_as_array_of_bytes.append(self.drone_system_health)
            self.values_as_array_of_bytes.append(self.ground_system_health)
            self.values_as_array_of_bytes.append(self.time_since_boot)
            self.values_as_array_of_bytes.append(self.current_mode)
            self.values_as_array_of_bytes.append(self.role)

        else:
            if self.is_values_array_valid(5, values):
                self.drone_system_health = int.to_bytes(values[0], 1, byteorder=Message.INDIANNESS)
                self.ground_system_health = int.to_bytes(values[1], 1, byteorder=Message.INDIANNESS)
                self.time_since_boot = int.to_bytes(values[2], 4, byteorder=Message.INDIANNESS)
                self.current_mode = int.to_bytes(values[3], 1, byteorder=Message.INDIANNESS)
                self.role = int.to_bytes(values[4], 1, byteorder=Message.INDIANNESS)

                self.values_as_array_of_bytes = []
                self.values_as_array_of_bytes.append(self.drone_system_health)
                self.values_as_array_of_bytes.append(self.ground_system_health)
                self.values_as_array_of_bytes.append(self.time_since_boot)
                self.values_as_array_of_bytes.append(self.current_mode)
                self.values_as_array_of_bytes.append(self.role)

            else:
                self.drone_system_health = None
                self.ground_system_health = None
                self.time_since_boot = None
                self.current_mode = None
                self.role = None
                return None

    def show(self):
        print("Status message" + " #", self.msg_number)
        try:
            print("drone_system_health : " + '{:08b}'.format(ord(self.drone_system_health)))
            print("ground_system_health : " + '{:08b}'.format(ord(self.ground_system_health)))
        except TypeError:
            print("drone_system_health : " + '{0:08b}'.format(self.drone_system_health))
            print("ground_system_health : " + '{0:08b}'.format(self.ground_system_health))

        print("time_since_boot : " + str(int.from_bytes(self.time_since_boot, byteorder=Message.INDIANNESS, signed=False)))
        if self.current_mode == b"\x00":
            print("current_mode : " + "Startup")
        elif self.current_mode == b"\x01":
            print("current_mode : " + "Disabled")
        elif self.current_mode == b"\x02":
            print("current_mode : " + "Enabled")
        elif self.current_mode == b"\x03":
            print("current_mode : " + "Pairing")
        elif self.current_mode == b"\x04":
            print("current_mode : " + "Failure")
        elif self.current_mode == b"\x05":
            print("current_mode : " + "Configuration")
        else:
            print("current_mode : " + str(self.current_mode))
        print("Role : ", self.role)
        print("---")

    def as_reduced_bytes_sequence(self, part):
        tmp = b''

        return tmp


class LoLas3DPosition(Message):

    # X                             4 bytes     (mm)    signed
    # Y                             4 bytes     (mm)    signed
    # Z                             4 bytes     (mm)    signed
    # yaw                           2 bytes     (deg)   unsigned
    # Sigma XY                      2 bytes     (mm)    unsigned
    # Sigma Z                       2 bytes     (mm)    unsigned
    # Sigma yaw                     2 bytes     (mm)    unsigned
    # Fusion health word            1 byte      (-)     unsigned
    # IMU YAW                       2 bytes     (deg)   unsigned
    # Yaw validation                1 byte      (-)     unsigned

    def __init__(self, msg_id, values, msg_number, values_are_bytes):
        super().__init__(msg_id, values, msg_number)

        if values_are_bytes:
            self.lolas_x = values[0:4]
            self.lolas_y = values[4:8]
            self.lolas_z = values[8:12]
            self.lolas_yaw = values[12:14]

            self.lolas_sigma_xy = values[14:16]
            self.lolas_sigma_z = values[16:18]
            self.lolas_sigma_yaw = values[18:20]

            self.fusion_health = values[20]

            self.imu_yaw = values[21:23]
            self.yaw_validation = values[23]

            self.values_as_array_of_bytes = []
            self.values_as_array_of_bytes.append(self.lolas_x)
            self.values_as_array_of_bytes.append(self.lolas_y)
            self.values_as_array_of_bytes.append(self.lolas_z)
            self.values_as_array_of_bytes.append(self.lolas_yaw)

            self.values_as_array_of_bytes.append(self.lolas_sigma_xy)
            self.values_as_array_of_bytes.append(self.lolas_sigma_z)
            self.values_as_array_of_bytes.append(self.lolas_sigma_yaw)

            self.values_as_array_of_bytes.append(self.fusion_health)

            self.values_as_array_of_bytes.append(self.imu_yaw)
            self.values_as_array_of_bytes.append(self.yaw_validation)

        else:
            if self.is_values_array_valid(10, values):
                self.lolas_x = int.to_bytes(values[0], 4, byteorder=Message.INDIANNESS, signed=True)
                self.lolas_y = int.to_bytes(values[1], 4, byteorder=Message.INDIANNESS, signed=True)
                self.lolas_z = int.to_bytes(values[2], 4, byteorder=Message.INDIANNESS, signed=True)
                self.lolas_yaw = int.to_bytes(values[3], 2, byteorder=Message.INDIANNESS, signed=False)

                self.lolas_sigma_xy = int.to_bytes(values[4], 2, byteorder=Message.INDIANNESS, signed=False)
                self.lolas_sigma_z = int.to_bytes(values[5], 2, byteorder=Message.INDIANNESS, signed=False)
                self.lolas_sigma_yaw = int.to_bytes(values[6], 2, byteorder=Message.INDIANNESS, signed=False)

                self.fusion_health = int.to_bytes(values[7], 1, byteorder=Message.INDIANNESS)

                self.imu_yaw = int.to_bytes(values[8], 2, byteorder=Message.INDIANNESS, signed=False)
                self.yaw_validation = int.to_bytes(values[9], 1, byteorder=Message.INDIANNESS)

                self.values_as_array_of_bytes = []
                self.values_as_array_of_bytes.append(self.lolas_x)
                self.values_as_array_of_bytes.append(self.lolas_y)
                self.values_as_array_of_bytes.append(self.lolas_z)
                self.values_as_array_of_bytes.append(self.lolas_yaw)

                self.values_as_array_of_bytes.append(self.lolas_sigma_xy)
                self.values_as_array_of_bytes.append(self.lolas_sigma_z)
                self.values_as_array_of_bytes.append(self.lolas_sigma_yaw)

                self.values_as_array_of_bytes.append(self.fusion_health)

                self.values_as_array_of_bytes.append(self.imu_yaw)
                self.values_as_array_of_bytes.append(self.yaw_validation)
            else:
                self.lolas_x = None
                self.lolas_y = None
                self.lolas_z = None
                self.lolas_yaw = None

                self.lolas_sigma_xy = None
                self.lolas_sigma_z = None
                self.lolas_sigma_yaw = None

                self.fusion_health = None

                self.imu_yaw = None
                self.yaw_validation = None

                return None

    def show(self):
        print("LoLas Measures" + " #", self.msg_number)
        try:
            print("Estimated X : ", int.from_bytes(self.lolas_x, byteorder=Message.INDIANNESS, signed=True), ", deviation : ", int.from_bytes(self.lolas_sigma_xy, byteorder=Message.INDIANNESS, signed=False))
            print("Estimated Y : ", int.from_bytes(self.lolas_y, byteorder=Message.INDIANNESS, signed=True), ", deviation : ", int.from_bytes(self.lolas_sigma_xy, byteorder=Message.INDIANNESS, signed=False))
            print("Estimated Z : ", int.from_bytes(self.lolas_z, byteorder=Message.INDIANNESS, signed=True), ", deviation : ", int.from_bytes(self.lolas_sigma_z, byteorder=Message.INDIANNESS, signed=False))
            print("Estimated yaw : ", int.from_bytes(self.lolas_yaw, byteorder=Message.INDIANNESS, signed=False), ", deviation : ", int.from_bytes(self.lolas_sigma_yaw, byteorder=Message.INDIANNESS, signed=False))
        except TypeError:
            print("Estimated X : " + str(
                int.from_bytes(self.lolas_x, byteorder=Message.INDIANNESS, signed=True)) + ", deviation : ",
                  self.lolas_sigma_xy)
            print("Estimated Y : " + str(
                int.from_bytes(self.lolas_y, byteorder=Message.INDIANNESS, signed=True)) + ", deviation : ",
                  self.lolas_sigma_xy)
            print("Estimated Z : " + str(
                int.from_bytes(self.lolas_z, byteorder=Message.INDIANNESS, signed=True)) + ", deviation : ",
                  self.lolas_sigma_z)
            print("Estimated yaw : ", self.lolas_yaw, ", deviation : " + str(self.lolas_sigma_yaw))
        try:
            print("Fusion health word : " + '{:08b}'.format(ord(self.fusion_health)))
        except TypeError:
            print("Fusion health word : " + '{:08b}'.format(self.fusion_health))
        print("---")

    def as_reduced_bytes_sequence(self, part):
        tmp = b''

        return tmp

@DeprecationWarning
class LoLasSetpoints(Message):

    # target_X                      4 bytes      (mm)   signed
    # target_Y                      4 bytes      (mm)   signed
    # target_Z                      4 bytes      (mm)   signed
    # target_yaw                    1 byte       (deg)  unsigned
    # target_Vx                     2 bytes      (mm/s) signed
    # target_Vy                     2 bytes      (mm/s) signed
    # target_Vz                     2 bytes      (mm/s) signed
    # target_yaw_rate               1 byte       (deg/s)signed
    # selection_mask                1 byte
    # reference_frame_descriptor    1 byte              unsigned
    #   0 : local NED
    #   1 : MAV_FRAME_BODY_NED / MAV_FRAME_BODY_FRD

    def __init__(self, msg_id, values, msg_number, values_are_bytes):
        super().__init__(msg_id, values, msg_number)

        if values_are_bytes:
            self.target_X = values[0:4]
            self.target_Y = values[4:8]
            self.target_Z = values[8:12]
            self.target_yaw = values[12]

            self.target_Vx = values[13:15]
            self.target_Vy = values[15:17]
            self.target_Vz = values[17:19]
            self.target_yaw_rate = values[19]

            self.selection_mask = values[20]
            self.reference_frame_descriptor = values[21]

            self.values_as_array_of_bytes = []
            self.values_as_array_of_bytes.append(self.target_X)
            self.values_as_array_of_bytes.append(self.target_Y)
            self.values_as_array_of_bytes.append(self.target_Z)
            self.values_as_array_of_bytes.append(self.target_yaw)

            self.values_as_array_of_bytes.append(self.target_Vx)
            self.values_as_array_of_bytes.append(self.target_Vy)
            self.values_as_array_of_bytes.append(self.target_Vz)
            self.values_as_array_of_bytes.append(self.target_yaw_rate)

            self.values_as_array_of_bytes.append(self.selection_mask)
            self.values_as_array_of_bytes.append(self.reference_frame_descriptor)

        else:
            if self.is_values_array_valid(10, values):
                self.target_X = int.to_bytes(values[0], 4, byteorder=Message.INDIANNESS, signed=True)
                self.target_Y = int.to_bytes(values[1], 4, byteorder=Message.INDIANNESS, signed=True)
                self.target_Z = int.to_bytes(values[2], 4, byteorder=Message.INDIANNESS, signed=True)
                self.target_yaw = int.to_bytes(values[3], 1, byteorder=Message.INDIANNESS, signed=False)

                self.target_Vx = int.to_bytes(values[4], 2, byteorder=Message.INDIANNESS, signed=True)
                self.target_Vy = int.to_bytes(values[5], 2, byteorder=Message.INDIANNESS, signed=True)
                self.target_Vz = int.to_bytes(values[6], 2, byteorder=Message.INDIANNESS, signed=True)
                self.target_yaw_rate = int.to_bytes(values[7], 1, byteorder=Message.INDIANNESS, signed=True)

                self.selection_mask = int.to_bytes(values[8], 1, byteorder=Message.INDIANNESS)
                self.reference_frame_descriptor = int.to_bytes(values[9], 1, byteorder=Message.INDIANNESS)

                self.values_as_array_of_bytes = []
                self.values_as_array_of_bytes.append(self.target_X)
                self.values_as_array_of_bytes.append(self.target_Y)
                self.values_as_array_of_bytes.append(self.target_Z)
                self.values_as_array_of_bytes.append(self.target_yaw)

                self.values_as_array_of_bytes.append(self.target_Vx)
                self.values_as_array_of_bytes.append(self.target_Vy)
                self.values_as_array_of_bytes.append(self.target_Vz)
                self.values_as_array_of_bytes.append(self.target_yaw_rate)

                self.values_as_array_of_bytes.append(self.selection_mask)
                self.values_as_array_of_bytes.append(self.reference_frame_descriptor)
            else:
                self.target_X = None
                self.target_Y = None
                self.target_Z = None
                self.target_yaw = None

                self.target_Vx = None
                self.target_Vy = None
                self.target_Vz = None
                self.target_yaw_rate = None

                self.selection_mask = None
                self.reference_frame_descriptor = None

                return None

    def show(self):
        print("LoLas setpoints" + " #", self.msg_number)
        print("target_X : " + str(int.from_bytes(self.target_X, byteorder=Message.INDIANNESS, signed=True)))
        print("target_Y : " + str(int.from_bytes(self.target_Y, byteorder=Message.INDIANNESS, signed=True)))
        print("target_Z : " + str(int.from_bytes(self.target_Z, byteorder=Message.INDIANNESS, signed=True)))
        try:
            print("target_yaw : ", int.from_bytes(self.target_yaw, byteorder=Message.INDIANNESS, signed=False))
        except TypeError:
            print("target_yaw : ", self.target_yaw)

        print("target_Vx : " + str(int.from_bytes(self.target_Vx, byteorder=Message.INDIANNESS, signed=True)))
        print("target_Vy : " + str(int.from_bytes(self.target_Vy, byteorder=Message.INDIANNESS, signed=True)))
        print("target_Vz : " + str(int.from_bytes(self.target_Vz, byteorder=Message.INDIANNESS, signed=True)))
        try:
            print("target_yaw_rate : ", int.from_bytes(self.target_yaw_rate, byteorder=Message.INDIANNESS, signed=True))
        except TypeError:
            if self.target_yaw_rate > 127:
                tmp = (256 - self.target_yaw_rate) * (-1)
                print("target_yaw_rate : ", tmp)
            else:
                print("target_yaw_rate : ", self.target_yaw_rate)


        try:
            print("selection_mask : " + '{:08b}'.format(ord(self.selection_mask)))
        except TypeError:
            print("selection_mask : " + '{:08b}'.format(self.selection_mask))

        print("reference_frame_descriptor : " + str(self.reference_frame_descriptor))
        print("---")

    def as_reduced_bytes_sequence(self, part):
        tmp = b''

        return tmp


class LoLasProximity(Message):

    # weight_on_wheel               1 byte      (-)     unsigned
    # proximity distance            2 bytes     (mm)    unsigned
    # status                        1 byte      (-)     unsigned

    def __init__(self, msg_id, values, msg_number, values_are_bytes):
        super().__init__(msg_id, values, msg_number)

        if values_are_bytes:

            self.weight_on_wheel = values[0]
            self.proxi_distance = values[1:3]
            self.status = values[3]

            self.values_as_array_of_bytes = []
            self.values_as_array_of_bytes.append(self.weight_on_wheel)
            self.values_as_array_of_bytes.append(self.proxi_distance)
            self.values_as_array_of_bytes.append(self.status)

        else:
            if self.is_values_array_valid(3, values):

                self.weight_on_wheel = int.to_bytes(values[0], 1, byteorder=Message.INDIANNESS)
                self.proxi_distance = int.to_bytes(values[1], 2, byteorder=Message.INDIANNESS, signed=False)
                self.status = int.to_bytes(values[2], 1, byteorder=Message.INDIANNESS)

                self.values_as_array_of_bytes = []
                self.values_as_array_of_bytes.append(self.weight_on_wheel)
                self.values_as_array_of_bytes.append(self.proxi_distance)
                self.values_as_array_of_bytes.append(self.status)

    def show(self):
        print("LoLas Proximity" + " #", self.msg_number)
        print("weight_on_wheel : " + str(self.weight_on_wheel))
        print("proxi distance : " + str(self.proxi_distance))
        print("status : " + str(self.status))
        print("---")

    def as_reduced_bytes_sequence(self, part):
        tmp = b''

        return tmp


class GenericMessage1(Message):

    # generic field 1              4 byte unsigned
    # generic field 2              4 byte unsigned
    # generic field 3              4 byte unsigned
    # generic field 4              4 byte unsigned
    # generic field 5              4 byte unsigned
    # generic field 6              4 byte unsigned
    # generic field 7              4 byte unsigned
    # generic field 8              4 byte unsigned

    def __init__(self, msg_id, values, msg_number, values_are_bytes):
        super().__init__(msg_id, values, msg_number)

        if values_are_bytes:  # in this case 32 bytes
            if self.is_values_array_valid(32, values):
                self.generic_field_1 = values[0:4]
                self.generic_field_2 = values[4:8]
                self.generic_field_3 = values[8:12]
                self.generic_field_4 = values[12:16]
                self.generic_field_5 = values[16:20]
                self.generic_field_6 = values[20:24]
                self.generic_field_7 = values[24:28]
                self.generic_field_8 = values[28:32]

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
            print("Generic Message 1" + " #" + str(int.from_bytes(self.msg_number, byteorder=Message.INDIANNESS, signed=False)))
        except:
            print("Generic Message 1" + " #" + str(self.msg_number))
        try:
            print("generic_field_1 : " + str(int.from_bytes(self.generic_field_1, byteorder=Message.INDIANNESS, signed=False)))
            print("generic_field_2 : " + str(int.from_bytes(self.generic_field_2, byteorder=Message.INDIANNESS, signed=False)))
            print("generic_field_3 : " + str(int.from_bytes(self.generic_field_3, byteorder=Message.INDIANNESS, signed=False)))
            print("generic_field_4 : " + str(int.from_bytes(self.generic_field_4, byteorder=Message.INDIANNESS, signed=False)))
            print("generic_field_5 : " + str(int.from_bytes(self.generic_field_5, byteorder=Message.INDIANNESS, signed=False)))
            print("generic_field_6 : " + str(int.from_bytes(self.generic_field_6, byteorder=Message.INDIANNESS, signed=False)))
            print("generic_field_7 : " + str(int.from_bytes(self.generic_field_7, byteorder=Message.INDIANNESS, signed=False)))
            print("generic_field_8 : " + str(int.from_bytes(self.generic_field_8, byteorder=Message.INDIANNESS, signed=False)))
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


class GenericMessage2(Message):

    # generic field 1              4 byte signed
    # generic field 2              4 byte signed
    # generic field 3              4 byte signed
    # generic field 4              4 byte signed
    # generic field 5              1 byte unsigned
    # generic field 6              1 byte unsigned
    # generic field 7              1 byte unsigned
    # generic field 8              1 byte unsigned

    def __init__(self, msg_id, values, msg_number, values_are_bytes):
        super().__init__(msg_id, values, msg_number)

        if values_are_bytes:  # in this case 20 bytes
            if self.is_values_array_valid(20, values):
                self.generic_field_1 = values[0:4]
                self.generic_field_2 = values[4:8]
                self.generic_field_3 = values[8:12]
                self.generic_field_4 = values[12:16]
                self.generic_field_5 = values[16]
                self.generic_field_6 = values[17]
                self.generic_field_7 = values[18]
                self.generic_field_8 = values[19]

        else:
            if self.is_values_array_valid(8, values):

                self.values_as_array_of_bytes = []
                self.values_as_array_of_bytes.append(int.to_bytes(values[0], 4, byteorder=Message.INDIANNESS))
                self.values_as_array_of_bytes.append(int.to_bytes(values[1], 4, byteorder=Message.INDIANNESS))
                self.values_as_array_of_bytes.append(int.to_bytes(values[2], 4, byteorder=Message.INDIANNESS))
                self.values_as_array_of_bytes.append(int.to_bytes(values[3], 4, byteorder=Message.INDIANNESS))
                self.values_as_array_of_bytes.append(int.to_bytes(values[4], 1, byteorder=Message.INDIANNESS))
                self.values_as_array_of_bytes.append(int.to_bytes(values[5], 1, byteorder=Message.INDIANNESS))
                self.values_as_array_of_bytes.append(int.to_bytes(values[6], 1, byteorder=Message.INDIANNESS))
                self.values_as_array_of_bytes.append(int.to_bytes(values[7], 1, byteorder=Message.INDIANNESS))

    def show(self):
        print("Generic Message 2" + " #" + str(int.from_bytes(self.msg_number, byteorder=Message.INDIANNESS, signed=False)))
        print("msg id : ", self.id)
        print("generic_field_1 : " + str(int.from_bytes(self.generic_field_1, byteorder=Message.INDIANNESS, signed=True)))
        print("generic_field_2 : " + str(int.from_bytes(self.generic_field_2, byteorder=Message.INDIANNESS, signed=True)))
        print("generic_field_3 : " + str(int.from_bytes(self.generic_field_3, byteorder=Message.INDIANNESS, signed=True)))
        print("generic_field_4 : " + str(int.from_bytes(self.generic_field_4, byteorder=Message.INDIANNESS, signed=True)))
        print("generic_field_5 : " + str(self.generic_field_5))
        print("generic_field_6 : " + str(self.generic_field_6))
        print("generic_field_7 : " + str(self.generic_field_7))
        print("generic_field_8 : " + str(self.generic_field_8))
        print("---")

    def as_reduced_bytes_sequence(self, part):
        tmp = b''

        return tmp


class GenericMessage3(Message):

    # generic field 1              4 byte unsigned
    # generic field 2              4 byte unsigned
    # generic field 3              4 byte unsigned
    # generic field 4              4 byte unsigned
    # generic field 5              4 byte unsigned
    # generic field 6              4 byte unsigned
    # generic field 7              4 byte unsigned
    # generic field 8              4 byte unsigned

    def __init__(self, msg_id, values, msg_number, values_are_bytes):
        super().__init__(msg_id, values, msg_number)

        if values_are_bytes:  # in this case 32 bytes
            if self.is_values_array_valid(32, values):
                self.generic_field_1 = values[0:4]
                self.generic_field_2 = values[4:8]
                self.generic_field_3 = values[8:12]
                self.generic_field_4 = values[12:16]
                self.generic_field_5 = values[16:20]
                self.generic_field_6 = values[20:24]
                self.generic_field_7 = values[24:28]
                self.generic_field_8 = values[28:32]

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
        print("Generic Message 3" + " #" + str(int.from_bytes(self.msg_number, byteorder=Message.INDIANNESS, signed=False)))

        print("generic_field_1 : " + str(int.from_bytes(self.generic_field_1, byteorder=Message.INDIANNESS, signed=False)))
        print("generic_field_2 : " + str(int.from_bytes(self.generic_field_2, byteorder=Message.INDIANNESS, signed=False)))
        print("generic_field_3 : " + str(int.from_bytes(self.generic_field_3, byteorder=Message.INDIANNESS, signed=False)))
        print("generic_field_4 : " + str(int.from_bytes(self.generic_field_4, byteorder=Message.INDIANNESS, signed=False)))
        print("generic_field_5 : " + str(int.from_bytes(self.generic_field_5, byteorder=Message.INDIANNESS, signed=False)))
        print("generic_field_6 : " + str(int.from_bytes(self.generic_field_6, byteorder=Message.INDIANNESS, signed=False)))
        print("generic_field_7 : " + str(int.from_bytes(self.generic_field_7, byteorder=Message.INDIANNESS, signed=False)))
        print("generic_field_8 : " + str(int.from_bytes(self.generic_field_8, byteorder=Message.INDIANNESS, signed=False)))
        print("---")

    def as_reduced_bytes_sequence(self, part):
        tmp = b''

        return tmp


class GenericMessage4(Message):

    # generic field 1              4 byte signed
    # generic field 2              4 byte signed
    # generic field 3              4 byte signed
    # generic field 4              4 byte signed
    # generic field 5              1 byte unsigned
    # generic field 6              1 byte unsigned
    # generic field 7              1 byte unsigned
    # generic field 8              1 byte unsigned

    def __init__(self, msg_id, values, msg_number, values_are_bytes):
        super().__init__(msg_id, values, msg_number)

        if values_are_bytes:  # in this case 20 bytes
            if self.is_values_array_valid(20, values):
                self.generic_field_1 = values[0:4]
                self.generic_field_2 = values[4:8]
                self.generic_field_3 = values[8:12]
                self.generic_field_4 = values[12:16]
                self.generic_field_5 = values[16]
                self.generic_field_6 = values[17]
                self.generic_field_7 = values[18]
                self.generic_field_8 = values[19]

        else:
            if self.is_values_array_valid(8, values):

                self.values_as_array_of_bytes = []
                self.values_as_array_of_bytes.append(int.to_bytes(values[0], 4, byteorder=Message.INDIANNESS))
                self.values_as_array_of_bytes.append(int.to_bytes(values[1], 4, byteorder=Message.INDIANNESS))
                self.values_as_array_of_bytes.append(int.to_bytes(values[2], 4, byteorder=Message.INDIANNESS))
                self.values_as_array_of_bytes.append(int.to_bytes(values[3], 4, byteorder=Message.INDIANNESS))
                self.values_as_array_of_bytes.append(int.to_bytes(values[4], 1, byteorder=Message.INDIANNESS))
                self.values_as_array_of_bytes.append(int.to_bytes(values[5], 1, byteorder=Message.INDIANNESS))
                self.values_as_array_of_bytes.append(int.to_bytes(values[6], 1, byteorder=Message.INDIANNESS))
                self.values_as_array_of_bytes.append(int.to_bytes(values[7], 1, byteorder=Message.INDIANNESS))

    def show(self):
        print("Generic Message 4" + " #" + str(int.from_bytes(self.msg_number, byteorder=Message.INDIANNESS, signed=False)))
        print("msg id : ", self.id)
        print("generic_field_1 : " + str(int.from_bytes(self.generic_field_1, byteorder=Message.INDIANNESS, signed=True)))
        print("generic_field_2 : " + str(int.from_bytes(self.generic_field_2, byteorder=Message.INDIANNESS, signed=True)))
        print("generic_field_3 : " + str(int.from_bytes(self.generic_field_3, byteorder=Message.INDIANNESS, signed=True)))
        print("generic_field_4 : " + str(int.from_bytes(self.generic_field_4, byteorder=Message.INDIANNESS, signed=True)))
        print("generic_field_5 : " + str(self.generic_field_5))
        print("generic_field_6 : " + str(self.generic_field_6))
        print("generic_field_7 : " + str(self.generic_field_7))
        print("generic_field_8 : " + str(self.generic_field_8))
        print("---")

    def as_reduced_bytes_sequence(self, part):
        tmp = b''

        return tmp


class LoLasAngularPosition(Message):

    # Bearing                       2 bytes     (deg)    signed
    # Elevation                     2 bytes     (deg)    signed
    # Distance to base              4 bytes     (mm)    unsigned
    # Fusion health word            1 byte      (-)     unsigned

    def __init__(self, msg_id, values, msg_number, values_are_bytes):
        super().__init__(msg_id, values, msg_number)

        if values_are_bytes:
            self.bearing = values[0:2]
            self.elevation = values[2:4]
            self.distance2base = values[4:8]

            self.fusion_health = values[8]

            self.values_as_array_of_bytes = []
            self.values_as_array_of_bytes.append(self.bearing)
            self.values_as_array_of_bytes.append(self.elevation)
            self.values_as_array_of_bytes.append(self.distance2base)
            self.values_as_array_of_bytes.append(self.fusion_health)

        else:
            if self.is_values_array_valid(4, values):
                self.bearing = int.to_bytes(values[0], 2, byteorder=Message.INDIANNESS, signed=True)
                self.elevation = int.to_bytes(values[1], 2, byteorder=Message.INDIANNESS, signed=True)
                self.distance2base = int.to_bytes(values[2], 4, byteorder=Message.INDIANNESS, signed=False)
                self.fusion_health = int.to_bytes(values[3], 1, byteorder=Message.INDIANNESS)

                self.values_as_array_of_bytes = []
                self.values_as_array_of_bytes.append(self.bearing)
                self.values_as_array_of_bytes.append(self.elevation)
                self.values_as_array_of_bytes.append(self.distance2base)
                self.values_as_array_of_bytes.append(self.fusion_health)
            else:
                self.bearing = None
                self.elevation = None
                self.distance2base = None
                self.fusion_health = None

                return None

    def show(self):
        print("LoLas Measures" + " #", self.msg_number)
        try:
            print("Bearing : ", int.from_bytes(self.bearing, byteorder=Message.INDIANNESS, signed=True))
            print("Elevation : ", int.from_bytes(self.elevation, byteorder=Message.INDIANNESS, signed=True))
            print("Distance2Base : ", int.from_bytes(self.distance2base, byteorder=Message.INDIANNESS, signed=False))
        except TypeError:
            print("Bearing : " + str(
                int.from_bytes(self.bearing, byteorder=Message.INDIANNESS, signed=True)))
            print("Elevation : " + str(
                int.from_bytes(self.elevation, byteorder=Message.INDIANNESS, signed=True)))
            print("Distance2Base : " + str(
                int.from_bytes(self.distance2base, byteorder=Message.INDIANNESS, signed=False)))
        try:
            print("Fusion health word : " + '{:08b}'.format(ord(self.fusion_health)))
        except TypeError:
            print("Fusion health word : " + '{:08b}'.format(self.fusion_health))
        print("---")

    def as_reduced_bytes_sequence(self, part):
        tmp = b''

        return tmp
