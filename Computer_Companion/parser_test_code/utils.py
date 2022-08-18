"""
Utilitaries to use LoLas Parser

- ValuesReceivedSerializer :
    class to serialize the messages received
    from LoLas in order to send them to a csv file
- RAW_BYTES_SIMULATING_LOLAS :
    a bytes array simulating messages arriving from LoLas
"""

class MessageRecord:
    """ Record the content of a message """
    def __init__(self, names, units) -> None:
        self.elem_names = names
        self.elem_units = units
        self.elem_values = []
        self.reset_values()

    def reset_values(self):
        """ Reset the content of the recorded message """
        self.elem_values = [None for i in self.elem_names]

    def set_values(self, values):
        """ Set the content of the recorded message """
        self.elem_values = values

class ValuesReceivedSerializer:
    """
    Serialize the values received from LoLas

    In order to send them in to csv file.

    Attributes
    ----------
    _msg_units : dict of str : dict of str : int
        {msg_name : {elem_name : elem_units}}
    _msg_values : dict of str : dict of str : int
        {msg_name : {elem_name : elem_value}}

    Methods
    -------
    add_msg(msg_name, msg_units) -> Void
    get_values_list() -> list of int
    set_msg_values(msg_name) -> Void
    reset_all() -> Void
    """
    def __init__(self) -> None:
        self._msg_records = {}

    def add_msg(self, msg_name, msg_units):
        """
        Add the msg_name to the records

        msg units is a dict of str : str
        representing {elem_name : elem_units}
        """
        elem_names = list(msg_units.keys())
        elem_units = list(msg_units.values())
        self._msg_records[msg_name] = MessageRecord(elem_names, elem_units)

    def get_names_list(self):
        """ Get a list with the names of all the elements in all the messages"""
        returned_list = []
        for next_record in self._msg_records.values():
            returned_list.extend(next_record.elem_names)
        return returned_list

    def get_units_list(self):
        """ Get a list with the units of all the elements in all the messages"""
        returned_list = []
        for next_record in self._msg_records.values():
            returned_list.extend(next_record.elem_units)
        return returned_list

    def get_values_list(self):
        """ Get a list with the valuess of all the elements in all the messages"""
        returned_list = []
        for next_record in self._msg_records.values():
            returned_list.extend(next_record.elem_values)
        return returned_list

    def set_msg_values(self, msg_name, msg_values):
        """
        Set the msg_name's values to msg_values

        msg_values is a dict of str : int
        representing {elem_name : elem_value}

        Warning : this function suppose that msg_values is in the same order
        as the initialization of the message record was
        """
        record = self._msg_records[msg_name]
        elem_values = list(msg_values.values())
        record.set_values(elem_values)

    def reset_all_msg_values(self):
        """ Erase the values of all elements of all recorded msg"""
        for next_record in self._msg_records.values():
            next_record.reset_values()

# create an array of bytes simulating the input from a LoLas Module
# it contains 4 differents messages of type 13, 9, 4 and 3 in that order.
# No error.
RAW_BYTES_SIMULATING_LOLAS = bytes.fromhex(
    "7f 22 0d 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"
    "00 00 00 00 00 00 00 00 00 00 4d a2 bd 7f 06 09 01 60 00 00 4d ce 39 7f 1a"
    "04 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 d8 3f 01 00"
    "4d 0e 7f 7f 0a 03 0a 00 04 65 13 00 02 00 4d 52 05"
    )
