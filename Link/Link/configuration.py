try:
    from Link.CustomProtocol.Common.message import Message
except Exception: #ImportError
    from CustomProtocol.Common.message import Message


class ConfigurationManager:

    def __init__(self):
        # configuration file generic info
        self.firmware_version = ""
        self.networkType = ""
        self.configurationHash = ""
        self.parameters = list([])

    def update_configuration_info(self, firmware_version, are_ground_modules, configuration_hash):
        """
        Updates the generic info in the configuration file header
        :param firmware_version: as plain byte ( int of 3 digits max)
        :param are_ground_modules:
        :param configuration_hash: as plain byte
        :return:
        """

        # convert plain byte version number into dot-separated string version number
        print("raw firmware version ", firmware_version)
        if len(str(firmware_version)) == 3:
            self.firmware_version = ""+str(firmware_version)[0]+"."+""+str(firmware_version)[1]+"."+str(firmware_version)[2]
        else:
            self.firmware_version = "0.0.0"

        if are_ground_modules:
            self.networkType = "ground modules"
        else:
            self.networkType = "drone modules"

        self.configurationHash = str(configuration_hash)

    def set_configuration(self, read_parameters):
        # clear any previous configuration
        self.parameters = list([])
        for parameter in read_parameters:
            self.parameters.append(parameter)
        self.configurationHash = str(int.from_bytes(read_parameters[1], byteorder=Message.INDIANNESS, signed=False))

    def print_configuration(self):

        print("Configuration")
        print("Network type : ", self.networkType)
        print("Firmware version : ", self.firmware_version)
        print("Hash : ", self.configurationHash)

        for i in range(0, len(self.parameters)):
            print("parameter " + str(i) +" : " + str(self.parameters[i]))
