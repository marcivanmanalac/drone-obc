"""
Tests suite for the main LoLas parser

Should be executed on the target to validate the parsing
on the final architecture.
"""

import unittest
import time
from lolasparser.lolasparser import LoLasParser

#create an array of bytes simulating the input from a LoLas Module
#it contains 4 differents messages of type 13, 9, 4 and 3. No error.
RAW_BYTES = bytearray.fromhex(
    "7f 22 0d 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"
    "00 00 00 00 00 00 00 00 00 00 4d a2 bd 7f 06 09 01 60 00 00 4d ce 39 7f 1a"
    "04 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 d8 3f 01 00"
    "4d 0e 7f 7f 0a 03 0a 00 04 65 13 00 02 00 4d 52 05"
    )

class TestLoLasParser(unittest.TestCase):
    """ Test the class LoLasParser"""
    def setUp(self):
        self.parser = LoLasParser()
        self.timestamp = time.time()
        self.msg_names = self.parser.get_all_msg_names()

    def test_values_at_statup(self):
        """ Test parser initialization """
        self.assertTrue(self.msg_names)
        values_list = []
        timestamps_list = []
        for next_name in self.msg_names:
            values = self.parser.get_msg_values(next_name)
            timestamp = self.parser.get_msg_timestamp(next_name)
            values_list.extend(list(values.values()))
            timestamps_list.append(timestamp)
        self.assertTrue(values_list)
        all_none_values = True
        for next_value in values_list:
            if next_value is not None:
                all_none_values = False
                break
        self.assertTrue(all_none_values)
        all_none_values = True
        for next_timestamp in timestamps_list:
            if next_timestamp is not None:
                all_none_values = False
                break
        self.assertTrue(all_none_values)
    
    def test_normal_parsing(self):
        """ Assert that the ids from parsed message are well received """
        msg_ids = self.parser.parse(RAW_BYTES, self.timestamp)
        msg_names = ["Proximity", "3D_Position", "Status"]
        self.assertEqual(msg_ids, msg_names)
        for next_name in msg_names:
            next_timestamp = self.parser.get_msg_timestamp(next_name)
            self.assertEqual(next_timestamp, self.timestamp)

    def test_msg_parsing_error(self):
        """ Simulate errors on the RS-485 connection"""
        RAW_BYTES_WITH_ERRORS = b'7f 0a 03 0a 00 04 65 13 00 02 00 4d 52 15'
        msg_ids = self.parser.parse(RAW_BYTES_WITH_ERRORS, self.timestamp)
        self.assertFalse(msg_ids)

if __name__ == '__main__':
    unittest.main()
