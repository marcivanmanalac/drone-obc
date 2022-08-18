""" Parse raw bytes array from LoLas and output messages and status. """

import time
from .genericparser import (GenericMsgParser, States as GenericParserStates)
from .lolasmsgdescription import (MSG_ID_TO_NAMES, MSG_ID_TO_DESCRIPTION, MSG_NAME_TO_IDS)
from .payloadparser import (PayloadParser)

class LoLasParser:
    """
    Parse raw bytes array from LoLas

    Stores the last messages received from LoLas and their
    respective arriving timestamp

    Attributes
    ----------
    _desired_ids : list of int
        List of all IDs to be parsed
    _generic_parser : GenericMsgParser
        The parser used for parsing the generic LoLas msg
        structure
    _payload_parsers : dict of int : PayloadParser
        Dict of payload parsers for each type of messages
        keys are ID of message, value is its related payload
        parser {id : payload_parser}
    _timestamps : dict of int : float
        Dict of the last time the message arrived {id : timestamp}

    Methods
    -------
    parse(incoming_bytes, timestamp = None) -> list of int
        Parse the incoming bytes array and return parsed messages IDs.
        Use timestamp if it exits, or record local time if not
    get_all_msg_names() -> list of str
        List all the names of the messages to be parsed
    get_msg_values(msg_name) -> dict of str : int
        Return msg-name's dict of {elem_name : elem_value}
    get_msg_timestamp(msg_name) -> float
        Return msg_name's timestamp
    get_msg_units(msg_name) -> dict of str : str
        Return msg-name's dict of {elem_name : elem_units}
    """
    def __init__(self) -> None:
        self._generic_parser = GenericMsgParser()
        # get all possible IDs
        self._desired_ids = list(MSG_ID_TO_DESCRIPTION)
        self._payload_parsers = {}
        # initalize one payload parser per type of message
        for msg_id in self._desired_ids:
            elements_description = MSG_ID_TO_DESCRIPTION[msg_id]
            self._payload_parsers[msg_id] = PayloadParser(elements_description)
        # initialize all timestamps to None value
        self._timestamps = dict.fromkeys(self._desired_ids, None)

    def parse(self, incoming_bytes, timestamp = None):
        """
        Parse the incoming bytes array incoming_bytes.

        Should be called regularly, even with an empty byte arrays, in order
        to maintain its status updated.

        Timestamp serves as a dependancy injection on the time. It can be
        left to None in normal operation and will be set to current time.

        Return the IDs of the messages that have been parsed during this call
        """
        if not timestamp:
            timestamp = time.time()

        # parsing process
        msg_received_ids = []
        for next_byte in incoming_bytes:
            parser_state = self._generic_parser.parse(next_byte)
            received_a_desired_msg = (parser_state == GenericParserStates.COMPLETED
            and self._generic_parser.id in self._desired_ids)
            if received_a_desired_msg:
                msg_id = self._generic_parser.id
                msg_payload = self._generic_parser.payload
                self._timestamps[msg_id] = timestamp
                try:
                    self._payload_parsers[msg_id].parse(msg_payload)
                except ValueError:
                    # if the msg_payload doesn't match with the msg size
                    pass
                msg_received_ids.append(msg_id)

        msg_received_names = []
        for next_id in msg_received_ids:
            msg_received_names.append(MSG_ID_TO_NAMES[next_id])
        return msg_received_names

    def get_all_msg_names(self):
        """ Return a list of all the names of the messages to be parser """
        msg_names = []
        for next_id in self._desired_ids:
            msg_names.append(MSG_ID_TO_NAMES[next_id])
        return msg_names

    def get_msg_values(self, msg_name):
        """ Returns the last values of the corresponding message """
        msg_id = MSG_NAME_TO_IDS[msg_name]
        return self._payload_parsers[msg_id].values

    def get_msg_units(self, msg_name):
        """ Returns the units of the corresponding message """
        msg_id = MSG_NAME_TO_IDS[msg_name]
        return self._payload_parsers[msg_id].units

    def get_msg_timestamp(self, msg_name):
        """ Returns the timestamp of the last corresponding message """
        msg_id = MSG_NAME_TO_IDS[msg_name]
        return self._timestamps[msg_id]
