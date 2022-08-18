"""
Parse raw bytes arrays from LoLas' modules into decoded messages

The main component is a state machine called "GenericMsgParser"
"""

class States:
    """
    enum of possible states for the state machine.

    States are designed to mean "waiting for ..." (WT4_...) :
        WT4_Start : waiting for the "start byte" to arrive
        WT4_Size : waiting for the byte with size of msg value to arrive
        WT4_Id : waiting for the byte with identification of msg value to arrive
        WT4_Payoad : waiting for the payload bytes to arrive
        WT4_Nbr : waiting for the byte with number of msg value to arrive
        WT4_CRC : waiting for the 2 bytes with CRC-16 value to arrive
        COMPLETED : the parsing of the incoming message is completed successfully
        WRONG_CRC : the 2 last bytes of the incoming message doesn't match with CRC-16
    """
    WT4_START = 1
    WT4_SIZE = 2
    WT4_ID = 3
    WT4_PAYLOAD = 4
    WT4_NBR = 5
    WT4_CRC = 6
    COMPLETED = 7
    WRONG_CRC = 8

class GenericMsgParser:
    """
    Simple state machine that parses raw bytes into msg generic elements

    Give it one byte at a time through the decode method, in order to get
    the state reached for each byte. This way progress can be recorded
    if a message appears in the middle of a byte sequence.

    Attributes
    ----------
    state : State
        Current state of the parser. See class States
    id : int
        Id of the parsed message
    payload : bytesarray
        Payload as the raw array of bytes from the parsed message
    nbr : int
        The message number of the parsed message
    _size : int
        Size of the incoming message
    _crc : bytesarray
        ending 2 bytes of the incoming message, representing the CRC value

    Methods
    -------
    parse(next_byte) -> States
        Parse the incoming bytes, one at a time
    reset() -> None
        reset the state machine to WT4_Start state
    """

    # Start flag used by LoLas to indicate start of message
    START_BYTE = 0x7f

    def __init__(self) -> None:
        self.state = States.WT4_START
        self._size = 0
        self.id = 0 # pylint: disable=C0103
        self.payload = bytearray()
        self.nbr = 0
        self._crc = bytearray()

    def reset(self):
        """ reset the state machine """
        self.state = States.WT4_START
        self._size = 0
        self.id = 0
        self.payload = bytearray()
        self.nbr = 0
        self._crc = bytearray()

    def parse(self, next_byte):
        """ Parse the incoming bytes, one at a time.

        returns the current state in order to provide information
        on the progress of parsing. see class States.
        """
        # STATE COMPLETED OR WRONG_CRC (means incoming msg ended, start again)
        if self.state == States.COMPLETED or self.state == States.WRONG_CRC:
            self.reset()
        # STATE START (wait indefinitely for the start byte)
        if self.state == States.WT4_START:
            if next_byte == GenericMsgParser.START_BYTE:
                self.state = States.WT4_SIZE
        # STATE SIZE
        elif self.state == States.WT4_SIZE:
            self._size = next_byte
            self.state = States.WT4_ID
        # STATE ID
        elif self.state == States.WT4_ID:
            self.id = next_byte
            self.state = States.WT4_PAYLOAD
        # STATE PAYLOAD
        elif self.state == States.WT4_PAYLOAD:
            self.payload.append(next_byte)
            # payload length is size - 2 because of id and nbr bytes
            if len(self.payload) >= self._size - 2:
                self.state = States.WT4_NBR
        # STATE NBR
        elif self.state == States.WT4_NBR:
            self.nbr = next_byte
            self.state = States.WT4_CRC
        # STATE CRC (wait for 2 bytes in order to check CRC)
        elif self.state == States.WT4_CRC:
            self._crc.append(next_byte)
            # crc-16 is 2 bytes long
            if len(self._crc) >= 2:
                byte_id = self.id.to_bytes(1, "little")
                byte_nbr = self.nbr.to_bytes(1, "little")
                checked_portion_of_msg = byte_id + self.payload + byte_nbr
                if crc16(checked_portion_of_msg) == self._crc:
                    self.state = States.COMPLETED
                else:
                    self.state = States.WRONG_CRC
        return self.state

def crc16(bytes_sequence):
    """
    CRC-16/BUYPASS, CRC-16-ANSI, CRC-16-IBM
    :param data: the bytes we want to compute the CRC for
    :return: 2 bytes CRC16 result
    """
    xor_in = 0x0000  # initial value
    xor_out = 0x0000  # final XOR value
    poly = 0x8005  # generator polinom (normal form)
    reg = xor_in
    for octet in bytes_sequence:
        # reflect in
        for i in range(8):
            topbit = reg & 0x8000
            if octet & (0x80 >> i):
                topbit ^= 0x8000
            reg <<= 1
            if topbit:
                reg ^= poly
        reg &= 0xFFFF
    # reflect out
    return (reg ^ xor_out).to_bytes(2, "little")
