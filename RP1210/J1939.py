"""
J1939 functions for use with RP1210 APIs. Note that this implementation is RP1210-specific - i.e.
if you try to generate J1939 messages to transmit directly onto a CANbus, these functions will fail!

While a dict of J1939 PGNs would be convenient, they are not provided here because the list is a
copyright of SAE.
"""

from RP1210 import sanitize_msg_param

def toJ1939Message(pgn, priority, source, destination, data, data_size = 0) -> bytes:
    """
    Converts args to J1939 message suitable for RP1210_SendMessage function.

    String arguments are read as base-10! If you want to provide an argument in base-16, do it as
    an int or byte string.

    RP1210_SendMessage J1939 format:
    - PGN (3 bytes)
    - Priority (1 byte)
    - Source Address (1 byte)
    - Destination Address (1 byte)
    - Message Data (0 - 1785 byes)

    If you're not sure what to do with some of these arguments due to differences between PDU1 and
    PDU2 messages, you can most likely get away with leaving irrelevant portions blank - your RP1210
    adapter drivers will format the message for you.

    Arguments can be strings, ints, or bytes. This function will parse strings as UTF-8 characters,
    so don't provide it with letters or special characters unless that's what you mean to send.
    If you want to send it 0xFF, send it as an int and not "FF". Likewise, 0 != "0".
    """
    ret_val = sanitize_msg_param(pgn, 3, 'little')
    ret_val += sanitize_msg_param(priority, 1)
    ret_val += sanitize_msg_param(source, 1)
    ret_val += sanitize_msg_param(destination, 1)
    ret_val += sanitize_msg_param(data, data_size)
    return ret_val

def toJ1939Request(pgn_requested, source, destination = 255, priority = 6) -> bytes:
    """
    Formats a J1939 request message. This puts out a request for the specified PGN, and will prompt
    other devices on the network to respond.

    - pgn_requested: the parameter group you're requesting
    - source: the source address, e.g. your address on the CANBus
    - destination: 255 = global request; enter a different number to request from a specific address
    - priority: priority of request; default is 6
    """
    pgn_request = sanitize_msg_param(pgn_requested, 3, 'little') # must be little-endian
    return toJ1939Message(0x00EA00, priority, source, destination, pgn_request)

class DTC():
    """
    A convenience class for parsing or generating the diagnostic trouble code (DTC) in diagnostic
    message data. This class should work for DM1, DM2, and DM12 messages.
    
    To read SPN, FMI, and OC from a DTC, initialize this class with four bytes containing the DTC
    you want to parse: `dtc = DTC(dtc=data)`

    To generate a DTC, initialize this class with spn, fmi, and oc:
    `dtc = DTC(spn=532, fmi=4, oc=7)`

    It is also possible to generate an empty object `dtc = DTC()` and set its properties individually.

    Properties `data`, `spn`, `fmi`, and `oc` are all intelligently handled with setters. This means you
    can e.g. set `dtc.spn = 321`, and `dtc.data` will be updated accordingly.
    """

    def __init__(self, dtc : bytes = None, spn = 0, fmi = 0, oc = 0) -> None:
        self._spn = spn
        self._fmi = fmi
        self._oc = oc
        if dtc is None:
            self.data = self.to_bytes(spn, fmi, oc)
        else:
            self.data = sanitize_msg_param(dtc, 4)

    ##############
    # PROPERTIES #
    ##############
    #region properties

    @property
    def spn(self):
        """SPN (suspect parameter number)"""
        return self.get_spn(self.data)

    @spn.setter
    def spn(self, val : int):
        """SPN (suspect parameter number)"""
        self.data = self.to_bytes(val, self.fmi, self.oc)

    @property
    def fmi(self):
        """FMI (failure mode identifier)"""
        return self.get_fmi(self.data)

    @fmi.setter
    def fmi(self, val : int):
        """FMI (failure mode identifier)"""
        self.data = self.to_bytes(self.spn, val, self.oc)

    @property
    def oc(self):
        """OC (occurrence count)"""
        return self.get_oc(self.data)

    @oc.setter
    def oc(self, val : int):
        """OC (occurrence count)"""
        self.data = self.to_bytes(self.spn, self.fmi, val)

    #endregion

    ##################
    # DUNDER METHODS #
    ##################
    #region dundermethods

    def __iadd__(self, val : int):
        """Overload += so OC can be incremented directly."""
        oc = min(self.oc + val, 126) # limit to 126
        self.oc = max(oc, 0) # shouldn't be lower than 0 either
        return self

    def __str__(self) -> str:
        return str(self.data)

    def __bytes__(self) -> bytes:
        return self.data

    def __int__(self) -> int:
        return int.from_bytes(self.data)

    def __len__(self) -> int:
        return len(self.data)

    def __eq__(self, other) -> bool:
        try:
            return self.data == sanitize_msg_param(other, 4)
        except Exception:
            return False

    def __bool__(self) -> bool:
        return self.data != b'\x00\x00\x00\x00' and len(self.data) == 4

    #endregion

    ########################
    # STATIC/CLASS METHODS #
    ########################
    #region staticmethods

    @staticmethod
    def get_spn(dtc : bytes) -> int:
        """Parses and returns SPN from 4-byte DTC."""
        data = sanitize_msg_param(dtc, 4)
        # need to construct SPN from bytes 0-2
        ret_val = (data[2] >> 5 & 0b00000111) << 16
        ret_val += data[1] << 8
        ret_val += data[0]
        return ret_val

    @staticmethod
    def get_fmi(dtc : bytes) -> int:
        """Parses and returns FMI from 4-byte DTC."""
        data = sanitize_msg_param(dtc, 4)
        # parse FMI from byte 2
        return data[2] & 0b00011111 # return bits 0-4 of byte 2

    @staticmethod
    def get_oc(dtc : bytes) -> int:
        """Parses and returns OC from 4-byte DTC."""
        data = sanitize_msg_param(dtc, 4)
        # parse FMI from byte 3
        return int(data[3]) & 0b01111111 # return bits 0-6 of byte 5

    @staticmethod
    def get_cm(dtc : bytes) -> int:
        """Parses and returns CM from 4-byte DTC."""
        dtc = sanitize_msg_param(dtc, 4)
        # parse CM from byte 3
        return dtc[3] >> 7 & 1

    @staticmethod
    def to_bytes(spn : int, fmi : int, oc : int):
        """Generates 4-byte DTC from SPN, FMI, and OC."""
        ret_val = b''
        # bytes 0 and 1 are just SPN in little-endian format
        spn_bytes = sanitize_msg_param(spn, 3, 'little')
        ret_val += int.to_bytes(spn_bytes[0], 1, 'big')
        ret_val += int.to_bytes(spn_bytes[1], 1, 'big')
        # byte 2 is mix of SPN (3 bits) and fmi (5 bits)
        # we will handle this by doing bitwise operations on an int, then convert back to bytes
        byte4_int = (int(spn_bytes[2]) << 5) & 0b11100000
        byte4_int |= int(fmi) & 0b00011111
        ret_val += sanitize_msg_param(byte4_int)
        # byte 3 is mix of CM (1 bit) and OC (7 bits) - CM always set to 0
        ret_val += sanitize_msg_param(int(oc) & 0b01111111)
        return ret_val

    @staticmethod
    def to_int(spn : int, fmi : int, oc : int):
        """Generates 4-byte DTC from SPN, FMI, and OC as int."""
        ret_val = spn & 0b11111111
        ret_val = (ret_val << 8) + (spn >> 8 & 0b11111111)
        ret_val = (ret_val << 8) + ((spn >> 11 & 0b11100000) | (fmi & 0b00011111))
        ret_val = (ret_val << 8) + (oc & 0b01111111)
        return ret_val
    #endregion

class J1939Message():
    """
    A convenience class for parsing a J1939 message received from RP1210_ReadMessage.

    Message must include timestamp (4 bytes) in its leading bytes (this conforms w/ return value
    of RP1210_ReadMessage).

    - Initialize the object with the message received from ReadMessage.
    - If you used the command 'Set Echo Transmitted Messages' to turn echo on, set arg echo = True.
    """
    def __init__(self, j1939_message : bytes, echo = False) -> None:
        self.msg = j1939_message
        self.echo_offset = int(echo)

    ##############
    # PROPERTIES #
    ##############

    def getTimestamp(self) -> int:
        """Returns timestamp (4 bytes) as int."""
        return int.from_bytes(self.msg[0:4], 'big')

    def getPGN(self) -> int:
        """Returns PGN (3 bytes) as int."""
        start = 4 + self.echo_offset
        end = 6 + self.echo_offset
        pgn = self.msg[start:(end+1)]
        pgn_int = int.from_bytes(pgn, 'little')
        # PDU1 (destination specific) - RP1210 adapters handle this in a dumb way
        if pgn[1] < 0xF0 and pgn[0] == 0x00:
            pgn_int += self.getDestination()
        return pgn_int

    def getPriority(self) -> int:
        """Returns Priority (1 byte) as int."""
        loc = 7 + self.echo_offset
        return int(self.msg[loc]) & 0b111

    def getSource(self) -> int:
        """Returns Source Address (1 byte) as int."""
        loc = 8 + self.echo_offset
        return int(self.msg[loc])

    def getSourceAddress(self) -> int:
        """Returns Source Address (1 byte) as int."""
        return int(self.getSource())

    def getDestination(self) -> int:
        """Returns Destination Address (1 byte) as int."""
        loc = 9 + self.echo_offset
        return int(self.msg[loc])

    def getData(self) -> bytes:
        """Returns message data (0 - 1785 bytes) as bytes."""
        loc = 10 + self.echo_offset
        return self.msg[loc:]

    def isEcho(self) -> bool:
        """Returns True if the message is an echo of a message you transmitted, False if not."""
        if self.echo_offset == 1:
            return int.from_bytes(self.msg[4]) == 0x01
        return False

    def isRequest(self) -> bool:
        """Returns true if PGN matches J1939 Request PGN."""
        return self.getPGN() == 0xEA00

    def isDMRequest(self) -> bool:
        """Returns true if PGN matches Diagnostic Message Request PGN."""
        return self.getPGN() == 0xEA00

    def isDM1(self) -> bool:
        """Returns true if PGN matches DM1 (active DTC) PGN."""
        return self.getPGN() == 0xFECA
    
    def isDM2(self) -> bool:
        """Returns true if PGN matches DM2 (previously active DTC) PGN."""
        return self.getPGN() == 0xFECB
    
    def isDM3(self) -> bool:
        """Returns true if PGN matches DM3 (clear previously active DTCs) PGN."""
        return self.getPGN() == 0xFECC

    def isDM4(self) -> bool:
        """Returns true if PGN matches DM4 (freeze frame parameters) PGN."""
        return self.getPGN() == 0xFECD

    def isDM11(self) -> bool:
        """Returns true if PGN matches DM11 (clear active DTCs) PGN."""
        return self.getPGN() == 0xFED3

    def isDM12(self) -> bool:
        """Returns true if PGN matches DM12 (emission-related active DTCs) PGN."""
        return self.getPGN() == 0xFED4

class DiagnosticMessage():
    """
    A convenience class for parsing Diagnostic Messages DM1, DM2, and DM12.
    
    msg param types:
    - `J1939Message` - copies data directly from message data
    - `bytes` - data taken directly from RP1210_ReadMessage
    - `int` - data from J1939 message (w/o PGN, etc)
    """
    def __init__(self, msg = None) -> None:
        if msg is None:
            self.data = b'\x00\x00'
        elif isinstance(msg, J1939Message):
            self.data = msg.getData()
        elif isinstance(msg, bytes):
            self.data = J1939Message(msg).getData()
        else:
            self.data = sanitize_msg_param(msg)

    #############
    # FUNCTIONS #
    #############

    def mil(self):
        """MIL (malfunction indicator lamp) status (0-3)."""
        return (self.lamps[0] & 0b11000000) >> 6
    
    def rsl(self):
        """RSL (red stop lamp) status (0-3)."""
        return (self.lamps[0] & 0b00110000) >> 4

    def awl(self):
        """AWL (amber warning lamp) status (0-3)."""
        return (self.lamps[0] & 0b00001100) >> 2

    def pl(self):
        """PL (protection lamp) status (0-3)."""
        return (self.lamps[0] &0b00000011)

    ##################
    # DUNDER METHODS #
    ##################
    #region dundermethods

    def __getitem__(self, index : int) -> DTC:
        # O^2 since to_dtcs() generates a new array each time
        # generally relatively small, but probably worth optimizing anyway
        return self.to_dtcs(self.data)[index]
    
    def __setitem__(self, index : int, dtc : DTC):
        # like getitem, this is quite unoptimized
        data = b''
        # add lamps
        data += bytes(self.data[0])
        data += bytes(self.data[1])
        # copy old data into new data until we hit index
        for i in range(2, index * 4 + 2):
            data += bytes(self.data[i])
        # copy new dtc into data
        dtc = sanitize_msg_param(dtc)
        for i in range(0, 4):
            data += bytes(dtc[i])
        # copy rest of old data
        for i in range(index+4, len(self.data)):
            data += bytes(self.data[i])
        # set self.data = new data
        self.data = data

    def __iadd__(self, dtc : DTC):
        """Add DTCs to DiagnosticMessage."""
        self.data += sanitize_msg_param(dtc, 4)
        return self

    def __bytes__(self) -> bytes:
        return self.data

    def __int__(self) -> int:
        return int.from_bytes(self.data, 'big')

    def __str__(self) -> str:
        """Returns string representation of data."""
        return str(self.data)

    def __len__(self) -> int:
        """Returns number of DTCs stored in DiagnosticMessage object."""
        dtc_bytes = len(self.data) - 2
        num_dtcs = int(dtc_bytes / 4)
        return max(num_dtcs, 0)

    def __bool__(self) -> bool:
        return len(self.data) >= 6

    def __eq__(self, other) -> bool:
        try:
            return sanitize_msg_param(other) == sanitize_msg_param(self.data)
        except Exception:
            return False


    #endregion

    ##############
    # PROPERTIES #
    ##############
    #region properties

    @property
    def codes(self) -> list[DTC]:
        """List of DTC objects parsed from DiagnosticMessage."""
        return self.to_dtcs(self.data)

    @codes.setter
    def codes(self, val : bytes):
        """List of DTC objects parsed from DiagnosticMessage."""
        self.data = self.data[0:2] + val

    @property
    def lamps(self) -> bytes:
        """Byte 0 is lamp codes; Byte 1 is reserved."""
        if len(self.data) >= 2:
            return self.data[0:2]
        elif len(self.data) == 1:
            return int.to_bytes(self.data[0], 2, 'little')
        else:
            return b'\x00\x00'

    @lamps.setter
    def lamps(self, val : bytes):
        """Byte 0 is lamp codes; Byte 1 is reserved."""
        if isinstance(val, int) or len(val) == 1:
            lamp_code = sanitize_msg_param(val, 2, 'little')
        else:
            lamp_code = sanitize_msg_param(val, 2)
        self.data = lamp_code + self.data[2:]

    #endregion

    ########################
    # STATIC/CLASS METHODS #
    ########################
    #region staticmethods
    @staticmethod
    def to_dtcs(data : bytes) -> list[DTC]:
        """
        Parses given J1939 message data into a list of DTCs (diagnostic trouble codes).
        """
        dtcs = [] #type: list[DTC]
        for i in range(2, len(data), 4): # iterate in chunks of 4 bytes
            dtc = data[i:i+4]
            if len(dtc) == 4:
                dtcs.append(DTC(dtc))
        return dtcs

    #endregion

############################
# MOSTLY USELESS FUNCTIONS #
############################

def toJ1939Name(arbitrary_address : bool, industry_group : int, system_instance : int, system : int,
                function : int, function_instance : int, ecu_instance : int, mfg_code : int, id : int) -> bytes:
    """
    Each J1939-compliant ECU needs its own 64-bit name. This function is meant to help generate such
    a name based on the component bytes that make it up.
    """
    def add_bits(name, val, num_bits):
        mask = (1 << num_bits) - 1
        value = int.from_bytes(sanitize_msg_param(val), (num_bits + 7) // 8)
        return (name << num_bits) + (value & mask)
    name = 0b0
    # arbitrary address (1 bit)
    name = add_bits(name, arbitrary_address, 1)
    # industry group (3 bits)
    name = add_bits(name, industry_group, 3)
    # vehicle system instance (4 bits)
    name = add_bits(name, system_instance, 4)
    # vehicle system (7 bits)
    name = add_bits(name, system, 7)
    # reserved bit
    name = add_bits(name, 1, 1)
    # function (8 bits)
    name = add_bits(name, function, 8)
    # function instance (5 bits)
    name = add_bits(name, function_instance, 5)
    # ecu instance (3 bits)
    name = add_bits(name, ecu_instance, 3)
    # manufacturer code (11 bits)
    name = add_bits(name, mfg_code, 11)
    # identity number (21 bits)
    name = add_bits(name, id, 21)
    return sanitize_msg_param(name)

def getJ1939ProtocolString(protocol = 1, Baud = "Auto", Channel = -1,
                        SampleLocation = 95, SJW = 1,
                        PROP_SEG = 1, PHASE_SEG1 = 2, PHASE_SEG2 = 1,
                        TSEG1 = 2, TSEG2 = 1, SampleTimes = 1) -> bytes:
    """
    Generates fpchProtocol string for ClientConnect function. The default values you see above
    were made up on the spot and shouldn't necessarily be used.

    Keyword arguments have the same names as below (e.g. Baud, SampleLocation, PHASE_SEG1).

    IDSize is automatically set to 29 whenever relevant because that is its only valid value.

    This function also accepts a Channel argument!

    Examples:
    - protocol1 = J1939.getProtocolString(protocol = 1, Baud = "Auto")
    - protocol2 = J1939.getProtocolString(protocol = 3, Baud = 500, SampleLocation = 75, SJW = 3, IDSize = 29)
    """
    if Channel != -1:
        chan_arg = f",Channel={str(Channel)}"
    else:
        chan_arg = ""

    if protocol == 1:
        return bytes(f"J1939:Baud={str(Baud)}" + chan_arg, 'utf-8')
    elif protocol == 2:
        return bytes("J1939" + chan_arg, 'utf-8')
    elif protocol == 3:
        return bytes(f"J1939:Baud={str(Baud)},SampleLocation={str(SampleLocation)},SJW={str(SJW)},IDSize=29" + chan_arg, 'utf-8')
    elif protocol == 4:
        return bytes(f"J1939:Baud={str(Baud)},PROP_SEG={str(PROP_SEG)},PHASE_SEG1={str(PHASE_SEG1)},PHASE_SEG2={str(PHASE_SEG2)},SJW={str(SJW)},IDSize=29" + chan_arg, 'utf-8')
    elif protocol == 5:
        return bytes(f"J1939:Baud={str(Baud)},TSEG1={str(TSEG1)},TSEG2={str(TSEG2)},SampleTimes={str(SampleTimes)},SJW={str(SJW)},IDSize=29" + chan_arg, 'utf-8')
    else:
        return b"J1939" # default to protocol format 2, default channel

def getJ1939ProtocolDescription(protocol : int) -> str:
    """
    Returns a description of the protocol selected with protocol arg.
    
    Feed the result of RP1210Config.getJ1939FormatsSupported() into this function to get a description of what
    the format means.

    Honestly, I don't see anyone ever using this function.
    """
    if protocol == 1:
        return "Variable J1939 baud rate. Select 125, 250, 500, 1000, or Auto."
    elif protocol == 2:
        return "General default for J1939 baud rate (250k baud)."
    elif protocol == 3:
        return "Driver uses SampleLocation to calculate parameters."
    elif protocol == 4:
        return "Baud formula derived from BOSCH CAN specification."
    elif protocol == 5:
        return "Baud formula derived from Intel implementations."
    else:
        return "Invalid J1939 protocol format selected."
