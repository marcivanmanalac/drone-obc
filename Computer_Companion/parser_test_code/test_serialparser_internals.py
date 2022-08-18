"""
Tests suite for the LoLas parser internal functions

Should be executed on the target to validate the parsing
on the final architecture.
"""

import unittest
from lolasparser import genericparser
from lolasparser import payloadparser
from lolasparser import lolasmsgdescription

class TestGenericMsgParser(unittest.TestCase):
    """ Test class GenericMsgParser """

    #create an array of bytes simulating the input from a LoLas Module
    #it contains 4 differents messages of type 13, 9, 4 and 3. No error.
    RAW_BYTES = bytes.fromhex(
        "7f 22 0d 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"
        "00 00 00 00 00 00 00 00 00 00 4d a2 bd 7f 06 09 01 60 00 00 4d ce 39 7f 1a"
        "04 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 d8 3f 01 00"
        "4d 0e 7f 7f 0a 03 0a 00 04 65 13 00 02 00 4d 52 05"
        )

    def test_normal_parsing(self):
        """Assert that the ids from parsed message are well received """
        parser = genericparser.GenericMsgParser()
        id_parsed = []
        for byte in TestGenericMsgParser.RAW_BYTES:
            if parser.parse(byte) == genericparser.States.COMPLETED:
                id_parsed.append(parser.id)
        self.assertEqual(id_parsed, [13, 9, 4, 3])

    def test_wrong_crc(self):
        """ check the detection of a wrong crc """
        parser = genericparser.GenericMsgParser()
        wrong_crc_counter = 0
        corrupted_raw_bytes = bytearray(TestGenericMsgParser.RAW_BYTES)
        # corrupt message 1
        corrupted_raw_bytes[5] = corrupted_raw_bytes[5] + 10
        # corrupt message 2
        corrupted_raw_bytes[50] = corrupted_raw_bytes[50] + 10
        for byte in corrupted_raw_bytes:
            if parser.parse(byte) == genericparser.States.WRONG_CRC:
                wrong_crc_counter = wrong_crc_counter + 1
        self.assertGreaterEqual(wrong_crc_counter, 2)

class TestPayloadParser(unittest.TestCase):
    """ Test class PayloadParser """
    def setUp(self):
        self.msg_1 = payloadparser.PayloadParser(lolasmsgdescription.MSG_DESCRIPTION_STATUS)
    
    def test_parsing_status(self):
        """ check the parsing of a simple status payload """
        # simple byte list representing the payload of a status message
        # {'Drone health': 255, 'Ground health': 0, 'Time': 2, 'Mode': 5, 'Role': 1}
        bytes_list = [255, 0, 2, 0, 0, 0, 5, 1]
        self.msg_1.parse(bytes_list)
        correct_value = {'Drone_health': 255, 'Ground_health': 0, 'Time': 2, 'Mode': 5, 'Role': 1}
        self.assertEqual(self.msg_1.values, correct_value)

    def test_handling_msg_size_error(self):
        """ send an payload of wrong size, should just pass """
        wrong_bytes_list = [255, 5, 1]
        self.assertRaises(ValueError, self.msg_1.parse, wrong_bytes_list)
        correct_value = {'Drone_health': None, 'Ground_health': None, 'Time': None, 'Mode': None, 'Role': None}
        self.assertEqual(self.msg_1.values, correct_value)

    def test_reset(self):
        """ check reset is done properly """
        bytes_list = [255, 0, 2, 0, 0, 0, 5, 1]
        self.msg_1.parse(bytes_list)
        self.msg_1.reset()
        correct_value = {'Drone_health': None, 'Ground_health': None, 'Time': None, 'Mode': None, 'Role': None}
        self.assertEqual(self.msg_1.values, correct_value)

if __name__ == '__main__':
    unittest.main()
