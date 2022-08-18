"""
This is the same as lolasparser_raspi_example.py, but no nodered
How to use:
    Download lolas-public-repository from bitbucket
    Pip install pyserial
    Sudo raspi-config
    	Enable serial
    CD into  ~/lolas-public-repository/LoLas NG/Demo code
    	Create log directory
        Create log.csv file

Example of use of LoLas parser with LoLas and the raspberry pi CAN RS485 hat from Waveshare.

The script gets the bytes from the serial port, parses them and send the results to :
- a CSV file
We deleted the Nodered display application
- the console (option VERBOSE)

The script accepts two options (python LoLasconnected.py SITL VERBOSE) :
- SITL : simulates in software of the receiving bytes from LoLas
- VERBOSE : sends log the console

More information on the raspberry pi CAN RS485 hat from Waveshare here :
https://www.waveshare.com/w/upload/2/29/RS485-CAN-HAT-user-manuakl-en.pdf

WARNING : as we only use the RS485 hat for receiveing and not transmitting,
there is no need to control the GPIO pins of the Raspberry Pi. But it should be done otherwise.
"""

# System imports
import sys
import time
import csv
import socket
import json
# RS-485 imports
import serial
# LoLas parser imports
from lolasparser.lolasparser import LoLasParser
from utils import (ValuesReceivedSerializer, RAW_BYTES_SIMULATING_LOLAS)

###EDIT###
from lolasparser.payloadparser import PayloadParser as pp
##END EDIT###

# CONSOLE PARAMETERS
# ----------
# Should send verbose to console
# (Default value, is a script's option)
CONSOLE_VERBOSE_ACTIVATED = False

# RS-485 PARAMETERS
# ----------
# Simulation in software of the receiving bytes from LoLas
# (Default value, is a script's option)
SITL_ACTIVATED = False
# LOLAS baudrate on serial, see LoLas communication ICD
LOLAS_SERIAL_BAUDRATE = 115200
# LoLas complete cycle period in enable mode, in seconds
LOLAS_CYCLE = 0.16
# We use the first serial port of the Raspberry Pi board
UART_PORT = "/dev/serial0"
# TIME_OUT : time serial.read will wait for the requested nbr of bytes
# 0 : doesn't wait, returns immediatly after getting the bytes waiting in buffer
TIME_OUT = 0

# TCP PARAMETERS
# ----------
# TCP connection host : same machine
HOST = "localhost"
# TCP connection port : hardcoded in NodeRed
PORT = 16789
# NodeRed updating period, in seconds :
NODERED_UPDATE_PERIOD = 0.5

# CSV File parameters
# Warning, if changed, NodeRed won't be able to retreive the log
CSV_FILE_PATH = "logs/"
CSV_FILE_NAME = "log.csv"
# Flushing (force OS to write buffer immediatly)
# period to the csv file, in seconds :
CSV_FLUSH_PERIOD = 5

def send_dict_to_socket(dict_to_send):
    """
    Handle the sending of values to the TCP socket

    The message should be the UTF-8 conversion of a string of a json.
    Be sure to end it with a final new line character to tell NodeRed
    the end of the message.
    """
    json_msg_format = json.dumps(dict_to_send, ensure_ascii=False) + "\n"
    utf8_msg_format = bytes(json_msg_format, 'UTF-8')
###    nbr_of_bytes_sent = client.send(utf8_msg_format)
###    sending_ok = (nbr_of_bytes_sent == len(utf8_msg_format))
##    return sending_ok
    return
# Create a parser object for the LoLas messages
my_parser = LoLasParser()

# Create a helper to serialize the values received from LoLas
# in order to send them to the csv file
my_serializer = ValuesReceivedSerializer()

# Process script's call arguments
for arg in sys.argv:
    if arg == "SITL":
        SITL_ACTIVATED = True
    if arg == "VERBOSE":
        CONSOLE_VERBOSE_ACTIVATED = True

# Setting up the serial instance
if not SITL_ACTIVATED:
    uart_interface = serial.Serial(UART_PORT, LOLAS_SERIAL_BAUDRATE, timeout=TIME_OUT)

# Setting up the csv file and socket instances
with open(CSV_FILE_PATH + CSV_FILE_NAME, "w", newline="", encoding="UTF-8") as csvfile, socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    csvwriter = csv.writer(csvfile, delimiter=';')
###    client.connect((HOST, PORT))

    # Add a message called "Logger", that is not from LoLas
    # but from this script. Enable CSV file or NodeRed to know
    # it is live and running.
    my_serializer.add_msg("Logger", {"Logger_Time" : "s"})
    # And add all messages from LoLas that we will parse
    msg_names = my_parser.get_all_msg_names()
    for next_name in msg_names:
        my_serializer.add_msg(next_name, my_parser.get_msg_units(next_name))
    # Write the header lines in the CSV file
    csvwriter.writerow(my_serializer.get_names_list())
    csvwriter.writerow(my_serializer.get_units_list())

    # Record some important timestamps
    time_of_start = time.time()
    time_of_last_flush = time.time()
    time_of_last_nodered_update = time.time()

    # Main loop
    # ---------
    while(True):
        logger_msg_values = {"Logger_Time" : (time.time() - time_of_start)}

        if not SITL_ACTIVATED:
            RAW_BYTES = uart_interface.read_all()
        else:
            RAW_BYTES = RAW_BYTES_SIMULATING_LOLAS

        if CONSOLE_VERBOSE_ACTIVATED:
            print("Received bytes : ", RAW_BYTES)

        # Parse the bytes received
        msg_received = my_parser.parse(RAW_BYTES)
        for next_msg in msg_received:
            msg_values = my_parser.get_msg_values(next_msg)
            my_serializer.set_msg_values(next_msg, msg_values)
            if time.time() - time_of_last_nodered_update > NODERED_UPDATE_PERIOD:
                # Don't update timestamp now as we are inside a foor loop
                send_dict_to_socket(msg_values)

        if CONSOLE_VERBOSE_ACTIVATED:
            print("Received messages : ", msg_received)

        ###EDIT ###
        #Parse Payload received #
        pp_msg_received = pp.parse(RAW_BYTES)
        for pp_next_msg in pp_msg_received:
            msg_values = my_parser.get_msg_values(next_msg)
            my_serializer.set_msg_values(next_msg, msg_values)
            if time.time() - time_of_last_nodered_update > NODERED_UPDATE_PERIOD:
                # Don't update timestamp now as we are inside a foor loop
                send_dict_to_socket(msg_values)
        #print to CLI
        if CONSOLE_VERBOSE_ACTIVATED:
            print("Translated Payload : ", pp_msg_received)
        ###END EDIT###

        #Update the CSV file
        if msg_received:
            my_serializer.set_msg_values("Logger", logger_msg_values)
            csvwriter.writerow(my_serializer.get_values_list())
            my_serializer.reset_all_msg_values()

        # Ensure data are written to the log file regularly, in case of system failure
        if time.time() - time_of_last_flush > CSV_FLUSH_PERIOD:
            time_of_last_flush = time.time()
            csvfile.flush()

        if CONSOLE_VERBOSE_ACTIVATED:
            # Add an end of line at the end of a cycle
            print("")

        # Sleep during a little bit less than a complete LoLas cycle
        time.sleep(LOLAS_CYCLE / 2)
