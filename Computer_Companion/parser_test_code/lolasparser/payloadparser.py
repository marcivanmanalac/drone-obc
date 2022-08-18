""" Tool for parsing the _payload_ bytes array from LoLas messages"""

class PayloadParser:
    """
    Standard class for parsing the _payload_ bytes array from LoLas messages.

    Each instance is specialized for a type of message by providing the description
    of the message at initialization. See lolasmsgdescription module.

    Attributes
    ----------
    values : dict
        A dictionnary with key as elements' name and their associated value
    units : dict
        A dictionnary with key as elements' name and their associated units
    ELEMENTS_DESCRIPTION : list
        A list of MsgElementDescription instances that describes each element in the message
    NBR_OF_BYTES_REQUIRED : int
        The exact number of bytes required for a complete payload (messages are fixed length)

    Methods
    -------
    parse(raw_payload) -> None
        Parse the entire raw_payload array
    reset() -> None
        Reset the values and units to empty list

    Examples
    --------
    # Instantiate a msg object of type Status
    # The general class is a PayloadParser
    # which is specialized using the message
    # description of the different elements
    # of a Status message
    msg_status = payloadparser.PayloadParser(lolasmsgdescription.MSG_DESCRIPTION_STATUS)
    """
    def __init__(self, elements_description) -> None:
        self.ELEMENTS_DESCRIPTION = elements_description
        self.values = {}
        self.units = {}
        self.NBR_OF_BYTES_REQUIRED = 0
        for elem in self.ELEMENTS_DESCRIPTION:
            self.values[elem.name] = None
            self.units[elem.name] = elem.units
            self.NBR_OF_BYTES_REQUIRED = self.NBR_OF_BYTES_REQUIRED + elem.nbr_of_bytes

    def parse(self, raw_payload):
        """
        Parse the entire raw_payload array of bytes to fill values and units.

        Raise ValueError in case of wrong payload size.
        """
        # check argument size
        if len(raw_payload) != self.NBR_OF_BYTES_REQUIRED:
            raise ValueError("Passed payload array is not of the right size")
        # parse payload with each element in message
        for elem in self.ELEMENTS_DESCRIPTION:
            value = int.from_bytes(raw_payload[:elem.nbr_of_bytes], "little", signed=elem.signed)
            del raw_payload[:elem.nbr_of_bytes]
            self.values[elem.name] = value

    def reset(self):
        """Reset the values and units to empty list"""
        for elem in self.ELEMENTS_DESCRIPTION:
            self.values[elem.name] = None
