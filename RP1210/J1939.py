"""
J1939 functions for use with RP1210 APIs. Note that this implementation is RP1210-specific - i.e.
if you try to generate J1939 messages to transmit directly onto a CANbus, these functions will fail!

While a dict of J1939 PGNs would be convenient, they are not provided here because the list is a
copyright of SAE.
"""

from RP1210 import sanitize_msg_param

def toJ1939Message(pgn, pri, sa, da, data, data_size = 0) -> bytes:
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
    PDU2 messages, you can most likely get away with leaving irrelevant portions blank (set to 0);
    your RP1210 adapter drivers will format the message for you.

    Arguments can be strings, ints, or bytes. This function will parse strings as UTF-8 characters,
    so don't provide it with letters or special characters unless that's what you mean to send.
    If you want to send it 0xFF, send it as an int and not "FF". Likewise, 0 != "0".
    """
    ret_val = sanitize_msg_param(pgn, 3, 'little')
    ret_val += sanitize_msg_param(pri, 1)
    ret_val += sanitize_msg_param(sa, 1)
    ret_val += sanitize_msg_param(da, 1)
    ret_val += sanitize_msg_param(data, data_size)
    return ret_val

def toJ1939Request(pgn_requested, sa, da = 255, pri = 6, size = 3) -> bytes:
    """
    Formats a J1939 request message. This puts out a request for the specified PGN, and will prompt
    other devices on the network to respond.

    - pgn_requested: the parameter group you're requesting
    - source: the source address, e.g. your address on the CANBus
    - destination: 255 = global request; enter a different number to request from a specific address
    - priority: priority of request; default is 6
    """
    pgn_request = sanitize_msg_param(pgn_requested, 3, 'little') # must be little-endian
    if size > 3:
        pgn_request += b'\xFF' * (size - 3)
    return toJ1939Message(0x00EA00, pri, sa, da, pgn_request, size)

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
        return int.from_bytes(self.data, 'big')

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
    def to_bytes(spn : int, fmi : int, oc : int) -> bytes:
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
    def to_int(spn : int, fmi : int, oc : int) -> int:
        """Generates 4-byte DTC from SPN, FMI, and OC as int."""
        ret_val = spn & 0b11111111
        ret_val = (ret_val << 8) + (spn >> 8 & 0b11111111)
        ret_val = (ret_val << 8) + ((spn >> 11 & 0b11100000) | (fmi & 0b00011111))
        ret_val = (ret_val << 8) + (oc & 0b01111111)
        return ret_val
    #endregion

class J1939Message():
    """
    A class for parsing or generating an RP1210 J1939 message.
    ---
    Parsing a J1939 message:
    ```
    msg = J1939Message(client.rx()) # where client is instance of RP1210Client
    msg_pgn = msg.pgn # access properties directly
    ... # etc, for all properties in 'Accessible properties' below
    ```
    - If you used the command 'Set Echo Transmitted Messages' to turn echo on, set arg echo = True.

    Generating a J1939 message:
    ```
    msg_data = ... # bytes
    msg = J1939Message(data=msg_data, pgn=0xEA00, sa=0xF9, da=0xBC, pri=3)
    client.tx(msg) # where client is instance of RP1210Client
    ```
    - This class will intelligently handle PDU1 vs PDU2, so DA is not always needed
    - Priority will default to 6 if it is not specified
    - Size will default to 8 if it is not specified
    ---
    Params:
    - `RP1210_ReadMessage_bytes`: bytes returned by RP1210_ReadMessage
    - `data`: message data, usually 8 bytes (bytes)
    - `pgn`: parameter group number (int)
    - `da`: destination address (int)
    - `sa`: source address (int)
    - `pri`: message priority (defaults to 6) (int)
    - `size`: data size (defaults to 8) - 0xFF bytes will be appended to fill space (int)
    ---
    Accessible properties:
    - `msg`: the full contents of the RP1210 message, not including the 4-byte timestamp (bytes)
    - `pgn`: Parameter Group Number (int)
    - `da`: Destination Address (int)
    - `sa`: Source Address (int)
    - `pri`: Priority (int) - see NOTE
    - `data`: Message Data (bytes)
    - `size`: Data Size (int)
    - `res` : Reserved bit (int)
    - `dp` : Data Page bit (int)
    - `timestamp`: 4-byte timestamp from RP1210_ReadMessage (int)
    ---
    Functions:
    - `pdu()` - returns PDU type (PDU 1 or PDU 2)
    - `pf()` - returns PDU Format byte as int
    - `ps()` - returns PDU Specific byte as int
    - `timestamp_bytes()` - returns timestamp as 4-byte string of bytes (for external formatting)
    - `isEcho()` - returns True if message is an echo of a message you sent
    - `isRequest()` - returns True if message is a J1939 Request, False if not.
    ---
    NOTE (from RP1210C 15.5):

    In accordance with Section 5.2.1 of J 1939/21, the priority should be masked off by the VDA and set to zero. 
    However VDA vendors can send back the actual message priority if they so desire. Because the priority 
    may or may not be provided by the VDA, applications should function correctly regardless of the presence 
    of the priority information.

    NOTE: When PGN and other values like DA conflict, the most recently assigned value will take precedence.
    When ambiguous, this class will default to assigning the destination address to the PGN rather than from it.
    """
    def __init__(self, RP1210_ReadMessage_bytes : bytes = None,
                    pgn : int = None, da : int = None, sa : int = None, data : bytes = None,
                    pri : int = 6, size : int = 8,
                    echo = False) -> None:
        # init everything
        self._msg = b''
        self._pgn = pgn
        self._da = da
        if sa is None:
            self._sa = 0xFF # sa defaults to 0xFF if it is never set from anywhere else
        else:
            self._sa = sa
        self._pri = pri
        if data: # if data is provided, process it
            self._data = sanitize_msg_param(data)
            if len(self._data) < size:
                self._data += b'\xFF' * (size - len(self._data)) # fill with 0xFF based on size
        else: # covers when data is not set and/or when RP1210_ReadMessage_bytes doesn't set it
            self._data = b'\xFF' * size # fill with 0xFF based on size
        self._res = 0 # reserved bit
        self._dp = 0 # data page bit
        self.timestamp = 0 # will only be overwritten if RP1210_ReadMessage_bytes is provided
        self._isecho = False
        # process bytes from RP1210_ReadMessage
        if RP1210_ReadMessage_bytes:
            self._assign_from_rp1210_readmessage(RP1210_ReadMessage_bytes, int(echo))
        else: # assign message from pgn, da, sa, pri, size, etc
            if pgn is not None:
                self._assign_from_pgn(assign_da=da is None) # only assign to DA if DA is none
            if self._da is None:
                self._da = 0xFF
            self._assign_to_pgn()
            self._assign_to_msg()
        # this is a bit messy

    #####################
    # PROTECTED METHODS #
    #####################

    def _assign_from_rp1210_readmessage(self, RP1210_ReadMessage_bytes : bytes, echo : int):
        if not isinstance(RP1210_ReadMessage_bytes, bytes):
            RP1210_ReadMessage_bytes = sanitize_msg_param(RP1210_ReadMessage_bytes)
        if len(RP1210_ReadMessage_bytes) < 10 + echo:
            missing_length = 10 + echo - len(RP1210_ReadMessage_bytes)
            RP1210_ReadMessage_bytes += b'\x00' * missing_length
        self.timestamp = int.from_bytes(RP1210_ReadMessage_bytes[0:4], 'big')
        self._msg = RP1210_ReadMessage_bytes[4+echo:]
        if echo and RP1210_ReadMessage_bytes[4] == 0x01:
            self._isecho = True
        self._assign_from_msg()
        
    def _assign_from_msg(self):
        """
        Updates all relevant properties from `msg` property.
        """
        self._pgn = int.from_bytes(self._msg[0:3], 'little')
        self._pri = int(self._msg[3]) & 0b111
        self._sa = int(self._msg[4])
        self._da = int(self._msg[5])
        if len(self._msg) > 6:
            self._data = self._msg[6:]
        else:
            self._data = b''
        # assign dp and res bits from PGN without updating DA
        self._assign_from_pgn(assign_da=False)
        self._assign_to_pgn(assign_da=True)

    def _assign_to_msg(self):
        self._msg = toJ1939Message(self._pgn, self._pri, self._sa, self._da, self._data, self.size)

    def _assign_from_pgn(self, assign_da = True):
        if assign_da:
            if self.pdu() == 1: # destination specific
                self._da = self.ps() # ps() = PDU Specific byte
            elif self.pdu() == 2: # broadcast
                self._da = 0xFF
        self._dp = (self._pgn >> 16) & 0b01 # data page bit
        self._res = (self._pgn >> 16) & 0b10 # reserved bit

    def _assign_to_pgn(self, assign_da = True):
        if assign_da and self.pdu() == 1: # destination specific
            self._pgn = (self._pgn & 0xFFFF00) + self._da # replace ps byte w/ da
        self._pgn = (self._pgn & 0x00FFFF) + ((self._dp + (self._res << 1)) << 16) # dp & r bits

    ##############
    # PROPERTIES #
    ##############

    @property
    def msg(self) -> bytes:
        """
        Full message, formatted to be passed on to RP1210_SendMessage.
        
        Setting this property will affect all other properties except `timestamp`.

        Will be filled with bytes of 0x00 if len isn't long enough to fill a message.
        """
        return self._msg

    @msg.setter
    def msg(self, val : bytes):
        # ensure correctness
        new_val = sanitize_msg_param(val)
        if len(new_val) < 6: # 6 bytes = PGN + SA + DA + PRI
            new_val += b'\x00' * (6 - len(new_val)) # fill with empty bytes to hit 6
        # assign values
        self._msg = new_val
        self._assign_from_msg()

    @property
    def pgn(self) -> int:
        """
        Parameter Group Number (int), consisting of:
        - PDU Format (1 byte)
        - PDU Specific (1 byte)
        - Data Page & Reserved bits (2 bits in 1 byte)

        Setting this property may affect properties `da`, `dp`, and `res`.

        Invalid values for `pgn` may result in garbage.
        """
        return self._pgn

    @pgn.setter
    def pgn(self, val : int):
        if not isinstance(val, int): # we want it to work with e.g. msg.pgn = msg_bytes[4:7]
            val = int.from_bytes(sanitize_msg_param(val, 3), 'little')
        self._pgn = val & 0xFFFFFF
        self._assign_from_pgn()
        self._assign_to_msg()

    @property
    def da(self) -> int:
        """
        Destination Address. Setting this may or may not update PGN.
        
        Invalid values for `da` may result in garbage.
        """
        return self._da

    @da.setter
    def da(self, val : int):
        if not isinstance(val, int):
            val = int.from_bytes(sanitize_msg_param(val, 1), 'big')
        self._da = val & 0xFF
        self._assign_to_pgn()
        self._assign_to_msg()

    @property
    def sa(self) -> int:
        """
        Source Address.

        Invalid values for `sa` may result in garbage.
        """
        return self._sa

    @sa.setter
    def sa(self, val : int):
        if not isinstance(val, int):
            val = int.from_bytes(sanitize_msg_param(val, 1), 'big')
        self._sa = val & 0xFF
        self._assign_to_msg()

    @property
    def pri(self) -> int:
        """
        Message Priority.
        
        In general, 6 = default priority, 3 = high priority.
        """
        return self._pri

    @pri.setter
    def pri(self, val : int):
        if not isinstance(val, int):
            val = int.from_bytes(sanitize_msg_param(val, 1), 'big')
        self._pri = max(min(val, 0b111), 0)
        self._assign_to_msg()

    @property
    def size(self) -> int:
        """
        Returns or modifies `len(data)`. Setting `size` will add or cut bytes from `data`.
        
        Most J1939 messages will be 8 bytes long if not otherwise specified.

        This value has no effect on `MessageSize` param to `RP1210_SendMessage`, which is set
        in its function call.
        """
        return len(self._data)

    @size.setter
    def size(self, val : int):
        if not isinstance(val, int):
            val = int.from_bytes(sanitize_msg_param(val, 1), 'big')
        if len(self._data) > val:
            self._data = self._data[:val]
        elif len(self._data) < val:
            self._data += b'\xFF' * (val - len(self._data))
        self._assign_to_msg()

    @property
    def data(self) -> bytes:
        """
        Message Data.
        """
        return self._data

    @data.setter
    def data(self, val : bytes):
        self._data = sanitize_msg_param(val)
        self._assign_to_msg()

    @property
    def res(self) -> int:
        """Reserved bit (0 or 1)."""
        return self._res
    
    @res.setter
    def res(self, val : int):
        self._res = max(min(int(val), 1), 0)
        self._assign_to_pgn()
        self._assign_to_msg()

    @property
    def dp(self) -> int:
        """Data Page bit (0 or 1)."""
        return self._dp

    @dp.setter
    def dp(self, val : int):
        self._dp = max(min(int(val), 1), 0)
        self._assign_to_pgn()
        self._assign_to_msg()
    
    #################
    # MAGIC METHODS #
    #################

    def __bytes__(self) -> bytes:
        return self._msg

    def __int__(self) -> int:
        return int.from_bytes(self._msg, 'big')

    def __str__(self) -> str:
        return str(self._msg)

    def __len__(self) -> int:
        return len(self._msg)

    def __eq__(self, other) -> bool:
        try:
            return self._msg == sanitize_msg_param(other)
        except Exception:
            return False

    def __bool__(self) -> bool:
        assert len(self._msg) >= 6

    ##################
    # PUBLIC METHODS #
    ##################

    def timestamp_bytes(self) -> bytes:
        """
        Returns 4-byte timestamp code as bytes
        (access `timestamp` property directly if you want an int).
        """
        return sanitize_msg_param(self.timestamp, 4)

    def pf(self) -> int:
        """Returns PDU Format byte as int."""
        return (self._pgn & 0x00FF00) >> 8

    def ps(self) -> int:
        """Returns PDU Specific bytes as int."""
        return self._pgn & 0xFF

    def pdu(self) -> int:
        """
        Returns PDU type (PDU1 or PDU2) as int:
        - 1 = PDU 1 (destination specific)
        - 2 = PDU 2 (broadcast)
        """
        if self.pf() < 0xF0:
            return 1
        else:
            return 2

    def isRequest(self) -> bool:
        return self.pgn & 0x00FF00 == 0x00EA00

    def isEcho(self) -> bool:
        """
        Returns True if this message is an echo of a message you previously sent.

        Requirements for this to detect an echoed message:
        - You used RP1210 command `Set Echo Transmitted Messages` to turn on echo
        - You initialized `J1939Message` with param `echo=True`
        """
        return self._isecho # set in __init__

class DiagnosticMessage():
    """
    A convenience class for parsing Diagnostic Messages DM1, DM2, and DM12.
    
    msg param types:
    - `J1939Message` - copies data directly from message data
    - `bytes` - data taken directly from RP1210_ReadMessage
    - `int` - J1939 message data (w/o PGN, etc)

    It's easy to loop through DTCs within a DiagnosticMessage:
    ```
    for dtc in DiagnosticMessage(msg_data):
        process_dtc(dtc)
    ```
    """
    def __init__(self, msg = None) -> None:
        self._lamps = b'\x00\x00'
        self._codes = [] #type: list[DTC]
        self._data =  b'\x00\x00'
        if msg is None:
            self.data = b'\x00\x00'
        elif isinstance(msg, J1939Message):
            self.data = msg.data
        elif isinstance(msg, bytes):
            self.data = J1939Message(msg).data
        else:
            self.data = sanitize_msg_param(msg)

    ####################
    # PUBLIC FUNCTIONS #
    ####################

    def num_dtcs(self) -> int:
        """Returns the number of DTCs in the message."""
        return len(self._codes)

    def mil(self):
        """MIL (malfunction indicator lamp) status (0-3)."""
        return (self._lamps[0] & 0b11000000) >> 6
    
    def rsl(self):
        """RSL (red stop lamp) status (0-3)."""
        return (self._lamps[0] & 0b00110000) >> 4

    def awl(self):
        """AWL (amber warning lamp) status (0-3)."""
        return (self._lamps[0] & 0b00001100) >> 2

    def pl(self):
        """PL (protection lamp) status (0-3)."""
        return self._lamps[0] &0b00000011

    #######################
    # PROTECTED FUNCTIONS #
    #######################

    def _assign_data(self):
        self._data = b''
        self._data += self._lamps
        for dtc in self._codes:
            self._data += sanitize_msg_param(dtc, 4)

    def _assign_lamps(self):
        if self._data == b'':
            self.lamps = b'\x00\x00' # intentionally assign to property
        elif len(self._data) == 1:
            self.lamps = self._data + b'\x00' # intentionally assign to property
        elif len(self._data) >= 2:
            self._lamps = self._data[0:2]

    def _assign_codes(self):
        self._codes = self.to_dtcs(self._data)

    ##################
    # DUNDER METHODS #
    ##################
    #region dundermethods

    def __getitem__(self, index : int) -> DTC:
        return self._codes[index]
    
    def __setitem__(self, index : int, dtc : DTC):
        if isinstance(dtc, DTC):
            self._codes[index] = dtc
        else:
            self._codes[index] = DTC(dtc)
        self._assign_data()

    def __iadd__(self, dtc : DTC):
        """Add DTCs to DiagnosticMessage."""
        self._data += sanitize_msg_param(dtc, 4)
        if isinstance(dtc, DTC):
            self._codes.append(dtc)
        else:
            self._codes.append(DTC(dtc))
        return self

    def __bytes__(self) -> bytes:
        return self._data

    def __int__(self) -> int:
        return int.from_bytes(self._data, 'big')

    def __str__(self) -> str:
        """Returns string representation of data."""
        return str(self._data)

    def __len__(self) -> int:
        """
        Returns number of DTCs stored in DiagnosticMessage object.
        """
        return self.num_dtcs()

    def __bool__(self) -> bool:
        """Returns True if the DiagnosticMessage contains DTCs."""
        return len(self._codes) > 0

    def __eq__(self, other) -> bool:
        """Returns True if diagnostic message data is exactly equal to some other data."""
        try:
            return sanitize_msg_param(other) == sanitize_msg_param(self._data)
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
        return self._codes
        # return self.to_dtcs(self.data)

    @codes.setter
    def codes(self, new_codes):
        """List of DTC objects parsed from DiagnosticMessage."""
        
        if isinstance(new_codes, bytes):
            self._codes = self.to_dtcs(b'\x00\x00' + new_codes)
        elif isinstance(new_codes, list):
            if new_codes == []:
                self._codes = []
            if isinstance(new_codes[0], DTC):
                self._codes = new_codes
            else:
                self._codes = [] #type: list[DTC]
                self._data = self._data[0:2]
                for element in new_codes:
                    self += element
        else:
            self._codes = self.to_dtcs(b'\x00\x00' + sanitize_msg_param(new_codes))
        self._assign_data()

    @property
    def lamps(self) -> bytes:
        """Byte 0 is lamp codes; Byte 1 is reserved."""
        return self._lamps

    @lamps.setter
    def lamps(self, val : bytes):
        """Byte 0 is lamp codes; Byte 1 is reserved."""
        if isinstance(val, bytes):
            if len(val) == 0:
                self._lamps = b'\x00\x00'
            elif len(val) == 1:
                self._lamps = sanitize_msg_param(val, 2, 'little')
            else:
                self._lamps = sanitize_msg_param(val, 2)
        else:
            self.lamps = sanitize_msg_param(val) # intentionally retrigger setter
        self._assign_data()

    @property
    def data(self) -> bytes:
        """
        The bytes that make up the diagnostic message.
        - Leading 2 bytes are lamp codes.
        - All subsequent bytes are DTCs.
            - Each DTC is 4 bytes.
        """
        return self._data

    @data.setter
    def data(self, val : bytes):
        """
        The bytes that make up the diagnostic message.
        - Leading 2 bytes are lamp codes.
        - All subsequent bytes are DTCs.
            - Each DTC is 4 bytes.
        """
        self._data = sanitize_msg_param(val)
        self._assign_codes()
        self._assign_lamps()

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
                function : int, function_instance : int, ecu_instance : int, mfg_code : int, id_num : int) -> bytes:
    """
    Each J1939-compliant ECU needs its own 64-bit name. This function is meant to help generate such
    a name.
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
    name = add_bits(name, id_num, 21)
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
