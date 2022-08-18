# from utils import Modes, RequestCodes, ResultCodes
import time
# import serial
import os
from os import path as osPath
from app_configuration import *
from Link.modules import ModulesManager
from Link.configuration import ConfigurationManager
from shutil import copyfile
from time import sleep
import json

# gestion des accès relatifs différents entre windows et linux
#management of different relative access between windows and linux
try:
    from Link.CustomProtocol.Common.lolas_messages_factory import LoLasMessagesFactory
    from Link.CustomProtocol.Common.messages_id import MessagesID
    from Link.CustomProtocol.Common.message import Message
except Exception: #ImportError
    from CustomProtocol.Common.lolas_messages_factory import LoLasMessagesFactory
    from CustomProtocol.Common.messages_id import MessagesID
    from CustomProtocol.Common.message import Message

PORT = "/dev/ttyS0"
PROTOCOL = "UART"
OUT_WAITING_LIMIT = 5*32  # number of bytes waiting to be sent
IN_WAITING_LIMIT = 5*32  # number of bytes waiting to be considered


class Link:

    def __init__(self, should_replicate, should_emulate_drone_network, dds_connector):
        print("role link")
        self.replicate = should_replicate
        self.is_drone_network = should_emulate_drone_network

        # create required directories if they do not exist
        if not osPath.exists(PATH_TO_TMP_ACTIVE_CONFIGURATION_DIRECTORY):
            os.mkdir(PATH_TO_TMP_ACTIVE_CONFIGURATION_DIRECTORY)
        if not osPath.exists(PATH_TO_ACTIVE_CONFIGURATION_DIRECTORY):
            os.mkdir(PATH_TO_ACTIVE_CONFIGURATION_DIRECTORY)
        if not osPath.exists(PATH_TO_NEW_CONFIGURATION_DESTINATION_DIRECTORY):
            os.mkdir(PATH_TO_NEW_CONFIGURATION_DESTINATION_DIRECTORY)

        if dds_connector is not None:
            self.diagOutputDDS = dds_connector.getOutput("MyPublisher::MyDiagWriter")
            self.commandsInputDDS = dds_connector.getInput("MySubscriber::MyCommandReader")

        self.shall_stream = False
        self.shall_build_maintenance_file = False
        self.counter = 0

        # Initialize diag variables
        self.x = 0
        self.y = 0
        self.z = 0
        self.yaw = 0
        # self.fusion_healthword = 0
        self.yaw_update_bit = 0
        # self.drone_healthword = 0
        self.drone_segment_ok = 0
        self.ground_segment_ok = 0
        self.paired = 0
        self.sync_bit = 0
        self.pos_lock_bit = 0
        self.wow = 0

        # the resulting qualities and their buffers
        self.sync_quality = 0
        self.pos_lock_quality = 0
        self.yaw_update_quality = 0

        self.sync_quality_buff = [0] * 30
        self.pos_lock_quality_buff = [0] * 30
        self.yaw_update_quality_buff = [0] * 30
        self.shared_buffer_index = 0

        # Instanciate a message manager
        self.msg_factory = LoLasMessagesFactory(PORT, PROTOCOL, IN_WAITING_LIMIT, OUT_WAITING_LIMIT)

        # Instanciate a module manager
        self.module_manager = ModulesManager()

        # Instanciate a configuration manager for the current configuration
        self.current_configuration = ConfigurationManager()
        # Instanciate a configuration manager for the new configuration
        self.new_configuration = ConfigurationManager()

        self.configuration_requested = False
        self.diag_requested = False
        self.reset = False

        while self.msg_factory.trying_to_connect():
            print(PROTOCOL + " interface on port " + PORT + " is not available. Trying to establish connection...")

    @staticmethod
    def clean_directories():
        try:
            for file in os.listdir(PATH_TO_ACTIVE_CONFIGURATION_DIRECTORY):
                if file.endswith(".json"):
                    # print(os.path.join(PATH_TO_ACTIVE_CONFIGURATION_DIRECTORY, file))
                    os.remove(os.path.join(PATH_TO_ACTIVE_CONFIGURATION_DIRECTORY, file))
        except FileNotFoundError:
            print("Current directory is missing")
            pass

        try:
            for file in os.listdir(PATH_TO_NEW_CONFIGURATION_DESTINATION_DIRECTORY):
                if file.endswith(".json"):
                    # print(os.path.join(PATH_TO_NEW_CONFIGURATION_DESTINATION_DIRECTORY, file))
                    os.remove(os.path.join(PATH_TO_NEW_CONFIGURATION_DESTINATION_DIRECTORY, file))
        except FileNotFoundError:
            print("New directory is missing")
            pass

        try:
            for file in os.listdir(PATH_TO_TMP_ACTIVE_CONFIGURATION_DIRECTORY):
                if file.endswith(".json"):
                    os.remove(os.path.join(PATH_TO_TMP_ACTIVE_CONFIGURATION_DIRECTORY, file))
        except FileNotFoundError:
            print("Tmp directory is missing")
            pass

    def mock_generate(self):
        try:
            if self.is_drone_network:
                copyfile(MOCK_CURRENT_DRONE_CONFIGURATION_FILE, PATH_TO_ACTIVE_CONFIGURATION_FILE)
            else:
                copyfile(MOCK_CURRENT_GROUND_CONFIGURATION_FILE, PATH_TO_ACTIVE_CONFIGURATION_FILE)
        except FileNotFoundError:
            print("Mock error : could not generate mock file (current configuration file)")
            pass

    def generate_current_configuration_file(self):
        if not osPath.exists(PATH_TO_TMP_ACTIVE_CONFIGURATION_DIRECTORY):
            os.mkdir(PATH_TO_TMP_ACTIVE_CONFIGURATION_DIRECTORY)

        # first create a temporary working copy of the template file into a temporary directory
        # print("gen net type ", self.configuration.networkType)
        if self.current_configuration.networkType == "ground modules":  # ground network
            copyfile(TEMPLATE_CURRENT_GROUND_CONFIGURATION_FILE, PATH_TO_TMP_ACTIVE_CONFIGURATION_FILE)
        elif self.current_configuration.networkType == "drone modules":
            copyfile(TEMPLATE_CURRENT_DRONE_CONFIGURATION_FILE, PATH_TO_TMP_ACTIVE_CONFIGURATION_FILE)
        else:
            return

        # load the content of the working file
        with open(PATH_TO_TMP_ACTIVE_CONFIGURATION_FILE, "r") as jsonFile:
            data = json.load(jsonFile)

        if data is not None:
            data["firmwareVersion"] = self.current_configuration.firmware_version
            data["configurationHash"] = self.current_configuration.configurationHash
            data["networkDescription"] = []
            for i in range(0, len(self.module_manager.modules)):
                # print(self.module_manager.modules[i].uid)
                # print(int.from_bytes(self.module_manager.modules[i].uid, byteorder=Message.INDIANNESS, signed=False))
                data["networkDescription"].append({'uid': int.from_bytes(self.module_manager.modules[i].uid, byteorder=Message.INDIANNESS, signed=False), 'role': self.module_manager.modules[i].role})

            data["parameters"] = []
            # for i in range(0, len(self.current_configuration.parameters)):
            #     if i < 5:
            #         data["parameters"].append({'key'+str(i): int.from_bytes(self.current_configuration.parameters[i], byteorder=Message.INDIANNESS, signed=False)})
            #     else:
            #         data["parameters"].append({'key' + str(i): self.current_configuration.parameters[i]})

            if self.current_configuration.networkType == "ground modules":  # ground network
                # start with parsing the multi parameters byte
                bin_tmp = bin(int.from_bytes(self.current_configuration.parameters[2], byteorder=Message.INDIANNESS,
                                             signed=False))[2:].zfill(8)

                tmp = list([])
                tmp.append(int(bin_tmp[7]))
                tmp.append(int(bin_tmp[6]))
                tmp.append(int(bin_tmp[5]))
                tmp.append(int(bin_tmp[4]))
                tmp.append(int(bin_tmp[3]))
                tmp.append(int(bin_tmp[2]))
                tmp.append(int(bin_tmp[1]))
                tmp.append(int(bin_tmp[0]))
                # print("multi bits : ", tmp)

                en_ultrasonic = "True"
                en_pairing = "True"

                if tmp[0] == 0:
                    en_ultrasonic = "False"

                if tmp[5] == 0:
                    en_pairing = "False"

                # key 0 : en us
                data["parameters"].append({'key0': en_ultrasonic})
                # key 1 : en keyed pairing
                data["parameters"].append({'key1': en_pairing})
                # key 2 : paring key
                data["parameters"].append({'key2': int.from_bytes(self.current_configuration.parameters[3],
                                                                  byteorder=Message.INDIANNESS, signed=False)})

                print("Ground data : ", data["parameters"])

            elif self.current_configuration.networkType == "drone modules":  # drone network
                # skip the first two parameters (uid and hash) as they are not part of the editable parameters
                # start with parsing the multi parameters byte
                bin_tmp = bin(int.from_bytes(self.current_configuration.parameters[2], byteorder=Message.INDIANNESS, signed=False))[2:].zfill(8)
                # print("multi bits : ", bin_tmp)
                tmp = list([])
                tmp.append(int(bin_tmp[7]))
                tmp.append(int(bin_tmp[6]))
                tmp.append(int(bin_tmp[5]))
                tmp.append(int(bin_tmp[4]))
                tmp.append(int(bin_tmp[3]))
                tmp.append(int(bin_tmp[2]))
                tmp.append(int(bin_tmp[1]))
                tmp.append(int(bin_tmp[0]))
                # print("multi bits : ", tmp)

                en_ultrasonic = "True"
                en_uwb = "True"
                en_proximity_sensor = "True"
                en_DM_IMU = "True"
                en_GND_IMU = "True"
                en_pairing = "True"

                if tmp[0] == 0:
                    en_ultrasonic = "False"

                if tmp[1] == 0:
                    en_uwb = "False"

                if tmp[2] == 0:
                    en_proximity_sensor = "False"

                if tmp[3] == 0:
                    en_DM_IMU = "False"

                if tmp[4] == 0:
                    en_GND_IMU = "False"

                if tmp[5] == 0:
                    en_pairing = "False"

                # key 0 : en us
                data["parameters"].append({'key0': en_ultrasonic})
                # key 1 : en uwb
                data["parameters"].append({'key1': en_uwb})
                # key 2 : en proximity sensor
                data["parameters"].append({'key2': en_proximity_sensor})
                # key 3 : DM height
                data["parameters"].append({'key3': int.from_bytes(self.current_configuration.parameters[5], byteorder=Message.INDIANNESS, signed=False)})
                # key 4 : Ground radius
                data["parameters"].append({'key4': int.from_bytes(self.current_configuration.parameters[6],
                                                                  byteorder=Message.INDIANNESS, signed=False)})
                # key 5 : DM distance
                data["parameters"].append({'key5': int.from_bytes(self.current_configuration.parameters[7],
                                                                  byteorder=Message.INDIANNESS, signed=False)})
                # key 6 : en DM IMU
                data["parameters"].append({'key6': en_DM_IMU})
                # key 7 : en ground IMU
                data["parameters"].append({'key7': en_GND_IMU})
                # key 8 : en keyed pairing
                data["parameters"].append({'key8': en_pairing})
                # key 9 : paring key
                data["parameters"].append({'key9': int.from_bytes(self.current_configuration.parameters[3],
                                                                  byteorder=Message.INDIANNESS, signed=False)})

                print("Drone data : ", data["parameters"])

        # write it back
        with open(PATH_TO_TMP_ACTIVE_CONFIGURATION_FILE, "w") as jsonFile:
            json.dump(data, jsonFile, sort_keys=False, indent=4)

        # finally move the file for studio to find it
        copyfile(PATH_TO_TMP_ACTIVE_CONFIGURATION_FILE, PATH_TO_ACTIVE_CONFIGURATION_FILE)

    def handle_new_configuration(self):
        new_config = False

        # while not new_config:
        try:
            if len([name for name in os.listdir(PATH_TO_NEW_CONFIGURATION_DESTINATION_DIRECTORY) if os.path.isfile(os.path.join(PATH_TO_NEW_CONFIGURATION_DESTINATION_DIRECTORY, name))]) == 0:
                # sleep(1)
                return False
            else:
                for file in os.listdir(PATH_TO_NEW_CONFIGURATION_DESTINATION_DIRECTORY):
                    if file.endswith(".json"):
                        print("New configuration file available")
                        print("should replicate : ", self.replicate)
                        if self.replicate == 1:
                            # self.replicate_hashcode()
                            # self.replicate_parameters()
                            # self.replicate_network_configuration()

                            # load the content of the received file
                            with open(PATH_TO_NEW_CONFIGURATION_DESTINATION_FILE, "r") as jsonFile:
                                data = json.load(jsonFile)

                            self.new_configuration.configurationHash = int(data['configurationHash'])

                            #todo : mettre à l'échelle pour la gestion d'un réseau de modules
                            self.module_manager.modules[0].role = data['networkDescription'][0]['role']

                            self.new_configuration.parameters.clear()
                            print("is drone network : ",self.is_drone_network)
                            if self.current_configuration.networkType == "drone modules":
                                for i in range(0, 10):  # 10 keys
                                    self.new_configuration.parameters.append(data['parameters'][i]['key'+str(i)])
                            else:
                                for i in range(0, 3):  # 3 keys
                                    print(i)
                                    self.new_configuration.parameters.append(data['parameters'][i]['key' + str(i)])

                            self.new_configuration.print_configuration()

                        # new_config = True
                        return True
                    else:
                        return False
        except FileNotFoundError:
            print("New directory is missing")
            return False
        except json.decoder.JSONDecodeError:
            print("Error while parsing the json file containing the new configuration")
            return False

    def replicate_parameters(self):
        data = None
        # récupération du hascode dans le nouveau fichier
        with open(PATH_TO_NEW_CONFIGURATION_DESTINATION_FILE) as f:
            data = json.load(f)

        new_parameters = data["parameters"]

        # f.close()

        # print("new parameters : ", new_parameters)

        # modification du fichier de référence qui sera utilisé par mock_generate
        if self.is_drone_network:
            file_path = MOCK_CURRENT_DRONE_CONFIGURATION_FILE
        else:
            file_path = MOCK_CURRENT_GROUND_CONFIGURATION_FILE
        with open(file_path, "r") as f:
            data = json.load(f)

        data["parameters"] = new_parameters

        with open(file_path, "w") as f:
            json.dump(data, f, sort_keys=False, indent=4)

    def replicate_network_configuration(self):
        data = None
        # récupération du hascode dans le nouveau fichier
        with open(PATH_TO_NEW_CONFIGURATION_DESTINATION_FILE) as f:
            data = json.load(f)

        new_network_description = data["networkDescription"]

        # f.close()

        # print("new networkDescription : ", new_network_description)

        # modification du fichier de référence qui sera utilisé par mock_generate
        if self.is_drone_network:
            file_path = MOCK_CURRENT_DRONE_CONFIGURATION_FILE
        else:
            file_path = MOCK_CURRENT_GROUND_CONFIGURATION_FILE
        with open(file_path, "r") as f:
            data = json.load(f)

        data["networkDescription"] = new_network_description

        with open(file_path, "w") as f:
            json.dump(data, f, sort_keys=False, indent=4)

    def replicate_hashcode(self):
        data = None
        # récupération du hascode dans le nouveau fichier
        with open(PATH_TO_NEW_CONFIGURATION_DESTINATION_FILE) as f:
            data = json.load(f)

        new_hash = data["configurationHash"]

        # f.close()

        print("new hash : ", new_hash)

        # modification du fichier de référence qui sera utilisé par mock_generate
        if self.is_drone_network:
            file_path = MOCK_CURRENT_DRONE_CONFIGURATION_FILE
        else:
            file_path = MOCK_CURRENT_GROUND_CONFIGURATION_FILE
        with open(file_path, "r") as f:
            data = json.load(f)

        data["configurationHash"] = new_hash

        with open(file_path, "w") as f:
            json.dump(data, f, sort_keys=False, indent=4)
        # f.close()

    def send_fake_diag_measures(self):
        millis = int(round(time.time()))  # time in seconds

        self.diagOutputDDS.instance.setString("parametername", "X")
        self.diagOutputDDS.instance.setString("source", "link")
        self.diagOutputDDS.instance.setNumber("timestamp", millis)
        self.diagOutputDDS.instance.setNumber("value", (self.counter+643) % 10000)
        self.diagOutputDDS.instance.setString("unit", "mm")
        self.diagOutputDDS.write()

        self.diagOutputDDS.instance.setString("parametername", "Y")
        self.diagOutputDDS.instance.setString("source", "link")
        self.diagOutputDDS.instance.setNumber("timestamp", millis)
        self.diagOutputDDS.instance.setNumber("value", (self.counter+4931) % 10000)
        self.diagOutputDDS.instance.setString("unit", "mm")
        self.diagOutputDDS.write()

        self.diagOutputDDS.instance.setString("parametername", "Z")
        self.diagOutputDDS.instance.setString("source", "link")
        self.diagOutputDDS.instance.setNumber("timestamp", millis)
        self.diagOutputDDS.instance.setNumber("value", (self.counter+536) % 10000)
        self.diagOutputDDS.instance.setString("unit", "mm")
        self.diagOutputDDS.write()

        self.diagOutputDDS.instance.setString("parametername", "Yaw")
        self.diagOutputDDS.instance.setString("source", "link")
        self.diagOutputDDS.instance.setNumber("timestamp", millis)
        self.diagOutputDDS.instance.setNumber("value", (self.counter+126) % 360)
        self.diagOutputDDS.instance.setString("unit", "degrees")
        self.diagOutputDDS.write()

        self.diagOutputDDS.instance.setString("parametername", "sync_quality")
        self.diagOutputDDS.instance.setString("source", "link")
        self.diagOutputDDS.instance.setNumber("timestamp", millis)
        self.diagOutputDDS.instance.setNumber("value", (self.counter+89) % 100)
        self.diagOutputDDS.instance.setString("unit", "%")
        self.diagOutputDDS.write()

        self.diagOutputDDS.instance.setString("parametername", "3d_lock_quality")
        self.diagOutputDDS.instance.setString("source", "link")
        self.diagOutputDDS.instance.setNumber("timestamp", millis)
        self.diagOutputDDS.instance.setNumber("value", (self.counter+45) % 100)
        self.diagOutputDDS.instance.setString("unit", "%")
        self.diagOutputDDS.write()

        self.diagOutputDDS.instance.setString("parametername", "yaw_update_quality")
        self.diagOutputDDS.instance.setString("source", "link")
        self.diagOutputDDS.instance.setNumber("timestamp", millis)
        self.diagOutputDDS.instance.setNumber("value", (self.counter+10) % 100)
        self.diagOutputDDS.instance.setString("unit", "%")
        self.diagOutputDDS.write()

        self.diagOutputDDS.instance.setString("parametername", "drone_segment_ok")
        self.diagOutputDDS.instance.setString("source", "link")
        self.diagOutputDDS.instance.setNumber("timestamp", millis)
        self.diagOutputDDS.instance.setNumber("value", (self.counter+1) % 2)
        self.diagOutputDDS.instance.setString("unit", "boolean")
        self.diagOutputDDS.write()

        self.diagOutputDDS.instance.setString("parametername", "ground_segment_ok")
        self.diagOutputDDS.instance.setString("source", "link")
        self.diagOutputDDS.instance.setNumber("timestamp", millis)
        self.diagOutputDDS.instance.setNumber("value", self.counter % 2)
        self.diagOutputDDS.instance.setString("unit", "boolean")
        self.diagOutputDDS.write()

        self.diagOutputDDS.instance.setString("parametername", "paired")
        self.diagOutputDDS.instance.setString("source", "link")
        self.diagOutputDDS.instance.setNumber("timestamp", millis)
        self.diagOutputDDS.instance.setNumber("value", (self.counter+1) % 2)
        self.diagOutputDDS.instance.setString("unit", "boolean")
        self.diagOutputDDS.write()

        self.diagOutputDDS.instance.setString("parametername", "wow")
        self.diagOutputDDS.instance.setString("source", "link")
        self.diagOutputDDS.instance.setNumber("timestamp", millis)
        self.diagOutputDDS.instance.setNumber("value", 1)
        self.diagOutputDDS.instance.setString("unit", "boolean")
        self.diagOutputDDS.write()

        self.counter +=1

    def parse_commands(self):
        self.commandsInputDDS.take()
        numOfSamples = self.commandsInputDDS.samples.getLength()

        for j in range(1, numOfSamples + 1):
            try:
                # récupération des paramètres par dictionnaire
                # retrieving settings by dictionary
                sample = self.commandsInputDDS.samples.getDictionary(j)

                print("source : " + sample['source'])
                print("timestamp : ", sample['timestamp'])
                print("cmd : "+sample['cmd'])
                print("arg : " + sample['arg'])

                if sample['cmd'] == "START":
                    self.shall_stream = True
                elif sample['cmd'] == "STOP":
                    self.shall_stream = False
                elif sample['cmd'] == "MAINTENANCE":
                    self.shall_build_maintenance_file = True
                elif sample['cmd'] == "DIAGNOSIS":
                    self.diag_requested = True
                elif sample['cmd'] == "CONFIGURATION":
                    self.configuration_requested = True
                elif sample['cmd'] == "RESET":
                    self.reset = True
            except json.decoder.JSONDecodeError:
                print("affichage des commandes : erreur d'accès au dictionnaire")

    def build_maintenance_file(self):
        try:
            copyfile(MOCK_MAINTENANCE_FILE, PATH_TO_ACTIVE_MAINTENANCE_FILE)
        except FileNotFoundError:
            print("Mock error : could not generate mock file (maintenance file)")
            pass

    def pollNetwork(self):

        if self.msg_factory.has_incoming_message():
            if self.msg_factory.is_flooded():
                self.msg_factory.free_incoming_messages()
                print("Warning abnormal number of messages in and waiting")
                # todo reset du buffer de réception si cela venant à se produire?
                # todo voire déconnexion?
                # todo reset of the receive buffer if this happens?
                # todo or even disconnect?
            for msg in self.msg_factory.stack_in_messages:
                if msg.id == MessagesID.NODE_DECLARATION:
                    # TODO stocker les informations de chacun des nodes declaration dans modules manager
                    self.module_manager.clear_modules_list()
                    self.module_manager.declare_module(msg.uid, msg.equipment_kind, msg.role)
                    self.module_manager.print_modules_list()
                    self.current_configuration.update_configuration_info(msg.firmware_version, msg.equipment_kind, msg.parameters_hashcode)
                    self.msg_factory.free_incoming_messages()  # TODO : cela peut-il empêcher de voir tous les messages envoyés par les autres modules?
                    return True
            self.msg_factory.free_incoming_messages()

        if self.msg_factory.connection_is_active():
            self.msg_factory.set_message(MessagesID.PING, [0], self.msg_factory.get_available_msg_number(MessagesID.PING), True, False)

            number_of_msg_sent = self.msg_factory.send_available_messages()

            # self.msg_factory.show_messages()

            self.msg_factory.pop_outgoing_messages(number_of_msg_sent)
            self.msg_factory.free_incoming_messages()

        return False

    def pollForConfiguration(self):

        if self.msg_factory.has_incoming_message():
            if self.msg_factory.is_flooded():
                self.msg_factory.free_incoming_messages()
                print("Warning abnormal number of messages in and waiting")
            for msg in self.msg_factory.stack_in_messages:
                if msg.id == MessagesID.PARAMETERS_READ:
                    print("Current configuration received")

                    parameters_list = list([])
                    parameters_list.append(msg.parameter_1)
                    parameters_list.append(msg.parameter_2)
                    parameters_list.append(msg.parameter_3)
                    parameters_list.append(msg.parameter_4)
                    parameters_list.append(msg.parameter_5)
                    parameters_list.append(msg.parameter_6)
                    parameters_list.append(msg.parameter_7)
                    parameters_list.append(msg.parameter_8)

                    self.current_configuration.set_configuration(parameters_list)

                    self.current_configuration.print_configuration()
                    self.msg_factory.free_incoming_messages()
                    return True
            self.msg_factory.free_incoming_messages()

        if self.msg_factory.connection_is_active():
            self.msg_factory.set_message(MessagesID.READ_BACK_REQUEST, [0], self.msg_factory.get_available_msg_number(MessagesID.READ_BACK_REQUEST), True, False)

            number_of_msg_sent = self.msg_factory.send_available_messages()

            # self.msg_factory.show_messages()

            self.msg_factory.pop_outgoing_messages(number_of_msg_sent)
            self.msg_factory.free_incoming_messages()

        return False

    def transfer_new_configuration(self):
        if self.msg_factory.connection_is_active():

            if self.current_configuration.networkType == "drone modules":
                # convert the raw parameters list received from studio into the custom protocol format
                en_ultrasonic = self.new_configuration.parameters[0]
                en_uwb = self.new_configuration.parameters[1]
                en_proximity_sensor = self.new_configuration.parameters[2]
                dm_height = self.new_configuration.parameters[3]
                ground_radius = self.new_configuration.parameters[4]
                dm_distance = self.new_configuration.parameters[5]
                en_DM_IMU = self.new_configuration.parameters[6]
                en_GND_IMU = self.new_configuration.parameters[7]
                en_pairing = self.new_configuration.parameters[8]
                pairing_key = self.new_configuration.parameters[9]

                if en_ultrasonic == "False":
                    en_ultrasonic = 0
                else:
                    en_ultrasonic = 1

                if en_uwb == "False":
                    en_uwb = 0
                else:
                    en_uwb = 1

                if en_proximity_sensor == "False":
                    en_proximity_sensor = 0
                else:
                    en_proximity_sensor = 1

                if en_DM_IMU == "False":
                    en_DM_IMU = 0
                else:
                    en_DM_IMU = 1

                if en_GND_IMU == "False":
                    en_GND_IMU = 0
                else:
                    en_GND_IMU = 1

                if en_pairing == "False":
                    en_pairing = 0
                else:
                    en_pairing = 1

                multibits_integer_equivalent = en_pairing*32 + en_GND_IMU * 16 + en_DM_IMU * 8 + en_proximity_sensor * 4 + en_uwb * 2 + en_ultrasonic

                # gathering all the parameters in the right order
                tmp = []
                tmp.append(self.new_configuration.configurationHash)
                tmp.append(multibits_integer_equivalent)
                tmp.append(int(pairing_key))
                tmp.append(int(self.module_manager.modules[0].role))  # à décliner pour tous les modules du réseau
                tmp.append(int(dm_height))
                tmp.append(int(ground_radius))
                tmp.append(int(dm_distance))

                print(tmp)

                self.msg_factory.set_message(MessagesID.PARAMETERS_WRITE, tmp, self.msg_factory.get_available_msg_number(MessagesID.PARAMETERS_WRITE), True, False)

                number_of_msg_sent = self.msg_factory.send_available_messages()

                # self.msg_factory.show_messages()

                self.msg_factory.pop_outgoing_messages(number_of_msg_sent)
                self.msg_factory.free_incoming_messages()

            else:
                # convert the raw parameters list received from studio into the custom protocol format
                en_ultrasonic = self.new_configuration.parameters[0]
                en_pairing = self.new_configuration.parameters[1]
                pairing_key = self.new_configuration.parameters[2]

                if en_ultrasonic == "False":
                    en_ultrasonic = 0
                else:
                    en_ultrasonic = 1

                if en_pairing == "False":
                    en_pairing = 0
                else:
                    en_pairing = 1

                multibits_integer_equivalent = en_pairing * 32 + en_ultrasonic

                # gathering all the parameters in the right order
                tmp = []
                tmp.append(self.new_configuration.configurationHash)
                tmp.append(multibits_integer_equivalent)
                tmp.append(int(pairing_key))
                tmp.append(int(self.module_manager.modules[0].role))  # à décliner pour tous les modules du réseau
                tmp.append(0)
                tmp.append(0)
                tmp.append(0)

                print(tmp)

                self.msg_factory.set_message(MessagesID.PARAMETERS_WRITE, tmp,
                                             self.msg_factory.get_available_msg_number(MessagesID.PARAMETERS_WRITE),
                                             True, False)

                number_of_msg_sent = self.msg_factory.send_available_messages()

                # self.msg_factory.show_messages()

                self.msg_factory.pop_outgoing_messages(number_of_msg_sent)
                self.msg_factory.free_incoming_messages()
        return

    def reset_requests(self):
        self.diag_requested = False
        self.shall_stream = False
        self.configuration_requested = False
        self.reset = False

    def send_ping(self):
        if self.msg_factory.connection_is_active():
            self.msg_factory.set_message(MessagesID.PING, [0], self.msg_factory.get_available_msg_number(MessagesID.PING), True, False)

            number_of_msg_sent = self.msg_factory.send_available_messages()

            # self.msg_factory.show_messages()

            self.msg_factory.pop_outgoing_messages(number_of_msg_sent)
            self.msg_factory.free_incoming_messages()

    def send_empty_ack(self):
        if self.msg_factory.connection_is_active():
            self.msg_factory.set_message(MessagesID.ACK, [0, 0, 0],
                                         self.msg_factory.get_available_msg_number(MessagesID.ACK), True, False)

            number_of_msg_sent = self.msg_factory.send_available_messages()

            # self.msg_factory.show_messages()

            self.msg_factory.pop_outgoing_messages(number_of_msg_sent)
            self.msg_factory.free_incoming_messages()

    # def send_ranges_transfer(self):
    #
    #     if self.msg_factory.connection_is_active():
    #
    #         tmp = []
    #         tmp.append(0)
    #         tmp.append(0)
    #         tmp.append(0)
    #         tmp.append(0)
    #         tmp.append(0)
    #         tmp.append(0)
    #         tmp.append(0)
    #         tmp.append(0)
    #
    #         self.msg_factory.set_message(MessagesID.RANGES_TRANSFER, tmp, self.msg_factory.get_available_msg_number(MessagesID.RANGES_TRANSFER), True, False)
    #
    #         number_of_msg_sent = self.msg_factory.send_available_messages()
    #
    #         print("sending ranges transfer")
    #
    #         self.msg_factory.pop_outgoing_messages(number_of_msg_sent)
    #         self.msg_factory.free_incoming_messages()

    def getDiagnosisMessages(self):
        try:
            rec_msg = self.msg_factory.has_incoming_message()

            if rec_msg:
                for message in self.msg_factory.stack_in_messages:

                    if message.id == MessagesID.LOLAS_3D_POSITION:
                        # print("X : ", message.lolas_x)
                        # print("Y : ", message.lolas_y)
                        # print("Z : ", message.lolas_z)
                        # print("YAW : ", message.lolas_yaw)
                        # print("fusion : ", message.fusion_health)
                        yaw_update_bit = (message.fusion_health >> 2) & 0x1
                        # print("yaw_update_bit : ", yaw_update_bit)

                        self.x = int.from_bytes(message.lolas_x, byteorder=message.INDIANNESS, signed=True)
                        self.y = int.from_bytes(message.lolas_y, byteorder=message.INDIANNESS, signed=True)
                        self.z = int.from_bytes(message.lolas_z, byteorder=message.INDIANNESS, signed=True)
                        self.yaw = int.from_bytes(message.lolas_yaw, byteorder=message.INDIANNESS, signed=True)
                        # self.fusion_healthword = message.fusion_health
                        self.yaw_update_bit = yaw_update_bit

                    elif message.id == MessagesID.STATUS:
                        # print("drone health : ", message.drone_system_health)
                        # print("ground health : ", message.ground_system_health)
                        paired_bit = (message.drone_system_health >> 3) & 0x1
                        sync_bit = (message.drone_system_health >> 6) & 0x1
                        pos_lock_bit = (message.drone_system_health >> 7) & 0x1
                        # print("paired : ", paired_bit)
                        # print("sync_bit : ", sync_bit)
                        # print("pos_lock_bit : ", pos_lock_bit)

                        if message.drone_system_health >= 223:
                            self.drone_segment_ok = 1
                        else:
                            self.drone_segment_ok = 0

                        # todo changer la valeur pour 255 lorsque les GM échangeront leurs status
                        if message.ground_system_health == 31:
                            self.ground_segment_ok = 1
                        else:
                            self.ground_segment_ok = 0

                        self.paired = paired_bit
                        self.sync_bit = sync_bit
                        self.pos_lock_bit = pos_lock_bit

                    elif message.id == MessagesID.LOLAS_PROXIMITY:
                        self.wow = message.weight_on_wheel

            self.msg_factory.free_incoming_messages()

        except:
            print("flow reading impossible")

    def broadcast_diag_samples(self):
        # compute qualities
        self.compute_qualities()
        # send the samples via DDS link
        millis = int(round(time.time()))  # time in seconds

        self.diagOutputDDS.instance.setString("parametername", "X")
        self.diagOutputDDS.instance.setString("source", "link")
        self.diagOutputDDS.instance.setNumber("timestamp", millis)
        self.diagOutputDDS.instance.setNumber("value", self.x)
        self.diagOutputDDS.instance.setString("unit", "mm")
        self.diagOutputDDS.write()

        self.diagOutputDDS.instance.setString("parametername", "Y")
        self.diagOutputDDS.instance.setString("source", "link")
        self.diagOutputDDS.instance.setNumber("timestamp", millis)
        self.diagOutputDDS.instance.setNumber("value", self.y)
        self.diagOutputDDS.instance.setString("unit", "mm")
        self.diagOutputDDS.write()

        self.diagOutputDDS.instance.setString("parametername", "Z")
        self.diagOutputDDS.instance.setString("source", "link")
        self.diagOutputDDS.instance.setNumber("timestamp", millis)
        self.diagOutputDDS.instance.setNumber("value", self.z)
        self.diagOutputDDS.instance.setString("unit", "mm")
        self.diagOutputDDS.write()

        self.diagOutputDDS.instance.setString("parametername", "Yaw")
        self.diagOutputDDS.instance.setString("source", "link")
        self.diagOutputDDS.instance.setNumber("timestamp", millis)
        self.diagOutputDDS.instance.setNumber("value", self.yaw)
        self.diagOutputDDS.instance.setString("unit", "degrees")
        self.diagOutputDDS.write()

        self.diagOutputDDS.instance.setString("parametername", "sync_quality")
        self.diagOutputDDS.instance.setString("source", "link")
        self.diagOutputDDS.instance.setNumber("timestamp", millis)
        self.diagOutputDDS.instance.setNumber("value", self.sync_quality)
        self.diagOutputDDS.instance.setString("unit", "%")
        self.diagOutputDDS.write()

        self.diagOutputDDS.instance.setString("parametername", "3d_lock_quality")
        self.diagOutputDDS.instance.setString("source", "link")
        self.diagOutputDDS.instance.setNumber("timestamp", millis)
        self.diagOutputDDS.instance.setNumber("value", self.pos_lock_quality)
        self.diagOutputDDS.instance.setString("unit", "%")
        self.diagOutputDDS.write()

        self.diagOutputDDS.instance.setString("parametername", "yaw_update_quality")
        self.diagOutputDDS.instance.setString("source", "link")
        self.diagOutputDDS.instance.setNumber("timestamp", millis)
        self.diagOutputDDS.instance.setNumber("value", self.yaw_update_quality)
        self.diagOutputDDS.instance.setString("unit", "%")
        self.diagOutputDDS.write()

        self.diagOutputDDS.instance.setString("parametername", "drone_segment_ok")
        self.diagOutputDDS.instance.setString("source", "link")
        self.diagOutputDDS.instance.setNumber("timestamp", millis)
        self.diagOutputDDS.instance.setNumber("value", self.drone_segment_ok)
        self.diagOutputDDS.instance.setString("unit", "boolean")
        self.diagOutputDDS.write()

        self.diagOutputDDS.instance.setString("parametername", "ground_segment_ok")
        self.diagOutputDDS.instance.setString("source", "link")
        self.diagOutputDDS.instance.setNumber("timestamp", millis)
        self.diagOutputDDS.instance.setNumber("value", self.ground_segment_ok)
        self.diagOutputDDS.instance.setString("unit", "boolean")
        self.diagOutputDDS.write()

        self.diagOutputDDS.instance.setString("parametername", "paired")
        self.diagOutputDDS.instance.setString("source", "link")
        self.diagOutputDDS.instance.setNumber("timestamp", millis)
        self.diagOutputDDS.instance.setNumber("value", self.paired)
        self.diagOutputDDS.instance.setString("unit", "boolean")
        self.diagOutputDDS.write()

        self.diagOutputDDS.instance.setString("parametername", "wow")
        self.diagOutputDDS.instance.setString("source", "link")
        self.diagOutputDDS.instance.setNumber("timestamp", millis)
        self.diagOutputDDS.instance.setNumber("value", self.wow)
        self.diagOutputDDS.instance.setString("unit", "boolean")
        self.diagOutputDDS.write()

    def compute_qualities(self):

         # ajout du dernier bit connu au buffer
        self.sync_quality_buff[self.shared_buffer_index] = self.sync_bit
        self.pos_lock_quality_buff[self.shared_buffer_index] = self.pos_lock_bit
        self.yaw_update_quality_buff[self.shared_buffer_index] = self.yaw_update_bit

        # gestion de l'index de parcours du buffer
        if self.shared_buffer_index < 29:
            self.shared_buffer_index += 1
        else:
            self.shared_buffer_index = 0

        # calcul des pourcentages résultants
        self.sync_quality = self.average_percentage(self.sync_quality_buff)
        self.pos_lock_quality = self.average_percentage(self.pos_lock_quality_buff)
        self.yaw_update_quality = self.average_percentage(self.yaw_update_quality_buff)

    @staticmethod
    def average_percentage(buffer):
        total = 0
        for value in buffer:
            total += value
        average = total / len(buffer)

        return average * 100
