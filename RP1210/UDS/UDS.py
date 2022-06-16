from .. import sanitize_msg_param

BYTE_STUFFING_VALUE = b'\xAA'

ServiceNames = {
    # Diagnostic and Communications Management
    0x10 : "Diagnostic Session Control",
    0x11 : "ECU Reset",
    0x27 : "Security Access",
    0x28 : "Communication Control",
    0x29 : "Authentication",
    0x3E : "Tester Present",
    0x83 : "Access Timing Parameters",
    0x84 : "Secured Data Transmission",
    0x85 : "Control DTC Settings",
    0x86 : "Response On Event",
    0x87 : "Link Control",
    # Data Transmission
    0x22 : "Read Data By Identifier",
    0x23 : "Read Memory By Address",
    0x24 : "Read Scaling Data By Identifier",
    0x2A : "Read Data By Identifier Periodic",
    0x2C : "Dynamically Define Data Identifier",
    0x2E : "Write Data By Identifier",
    0x3D : "Write Memory By Address",
    # Stored Data Transmission
    0x14 : "Clear Diagnostic Information",
    0x19 : "Read DTC Information",
    # Input / Output Control
    0x2F : "Input Output Control By Identifier",
    # Remote Activation of Routine
    0x31 : "Routine Control",
    # Upload / Download
    0x34 : "Request Download",
    0x35 : "Request Upload",
    0x36 : "Transfer Data",
    0x37 : "Request Transfer Exit",
    0x38 : "Request File Transfer",
    # Negative Response (not a service)
    0x3F : "Negative Response"
}
"""Dict of service names, organized by UDS Request SID."""

ResponseCodes = {
    0x00 : "Positive Response",
    0x10 : "General Reject",
    0x11 : "Service Not Supported",
    0x12 : "Sub-Function Not Supported",
    0x13 : "Incorrect Message Length Or Invalid Format",
    0x14 : "Response Too Long",
    0x21 : "Busy - Repeat Request",
    0x22 : "Conditions Not Correct",
    0x24 : "Request Sequence Error",
    0x25 : "No Response From Subnet Component",
    0x26 : "Failure Prevents Execution Of Requested Action",
    0x31 : "Request Out Of Range",
    0x33 : "Security Access Denied",
    0x34 : "Authentication Required",
    0x35 : "Invalid Key",
    0x36 : "Exceed Number Of Attempts",
    0x37 : "Required Time Delay Not Expired",
    0x38 : "Secure Data Transmission Required",
    0x39 : "Secure Data Transmission Not Allowed",
    0x3A : "Secure Data Verification Failed",
    0x50 : "Certificate verification failed - Invalid Time Period",
    0x51 : "Certificate verification failed - Invalid Signature",
    0x52 : "Certificate verification failed - Invalid Chain of Trust",
    0x53 : "Certificate verification failed - Invalid Type",
    0x54 : "Certificate verification failed - Invalid Format",
    0x55 : "Certificate verification failed - Invalid Content",
    0x56 : "Certificate verification failed - Invalid Scope",
    0x57 : "Certificate verification failed - Invalid Certificate (revoked)",
    0x58 : "Ownership verification failed",
    0x59 : "Challenge calculation failed",
    0x5A : "Setting Access Rights failed",
    0x5B : "Session key creation/derivation failed",
    0x5C : "Configuration data usage failed",
    0x5D : "De-Authentication failed",
    0x70 : "Upload/Download Not Accepted",
    0x71 : "Transfer Data Suspended",
    0x72 : "General Programming Failure",
    0x73 : "Wrong Block Sequence Counter",
    0x78 : "Request Correctly Received - Response Pending",
    0x7E : "Sub-Function Not Supported In Active Session",
    0x7F : "Service Not Supported In Active Session",
    0x81 : "RPM Too High",
    0x82 : "RPM Too Low",
    0x83 : "Engine Is Running",
    0x84 : "Engine Is Not Running",
    0x85 : "Engine Run Time Too Low",
    0x86 : "Temperature Too High",
    0x87 : "Temperature Too Low",
    0x88 : "Vehicle Speed Too High",
    0x89 : "Vehicle Speed Too Low",
    0x8A : "Throttle/Pedal Too High",
    0x8B : "Throttle/Pedal Too Low",
    0x8C : "Transmission Range Not In Neutral",
    0x8D : "Transmission Range Not In Gear",
    0x8F : "Brake Switch(es) Not Closed (Brake Pedal not pressed or not applied)",
    0x90 : "Shifter Lever Not In Park",
    0x91 : "Torque Converter Clutch Locked",
    0x92 : "Voltage Too High",
    0x93 : "Voltage Too Low",
    0x94 : "Resource Temporarily Not Available",
}
"""Dict of response code definitions. Missing values are reserved by ISO/SAE or proprietary."""

def translateRequestSID(sid : int) -> str:
    """Translates a UDS Request SID (service ID) to its service name."""
    return ServiceNames.get(sid, "Proprietary/Reserved")

def translateResponseSID(sid : int) -> str:
    """Translates a UDS Response SID (service ID) to its service name."""
    return ServiceNames.get(sid - 0x40, "Proprietary/Reserved")

def translateResponseCode(code : int) -> str:
    """Returns a description of the specified UDS response code."""
    # cover some specific cases
    if 0x95 <= code <= 0xEF:
        return "Reserved For Specific Conditions Not Correct"
    if 0xF0 <= code <= 0xFE:
        return "Conditions Not Correct: Vehicle Manufacturer Specific"
    return ResponseCodes.get(code, "ISO/SAE Reserved")

class UDSMessage:
    """
    Parent to UDS request & response subclasses.
    
    Each UDS message consists of 1 SID byte, with the existence of other properties
    depending on the service:
    - `sid`   (int - 1 byte)
    - `subfn` (int - 0 or 1 bytes)
    - `did`   (int - 0 or 2 bytes)
    - `data`  (bytes - n bytes)
    """

    _isResponse = False
    _sid    = None #type: int

    def __init__(self):
        self._hasSubfn   = False
        self._hasDID     = False
        self._hasData    = False
        self._dataSizeCanChange = False

        self._subfn  = None #type: int
        self._did    = None #type: int
        self._data   = b'' #type: bytes
        
        self._dataSize   = 0

    def name(self):
        if self._isResponse:
            return translateResponseSID(self._sid)
        else:
            return translateRequestSID(self._sid)

    def hasSubfn(self):
        return self._hasSubfn

    def hasDID(self):
        return self._hasDID

    def hasData(self):
        return self._hasData

    def dataSize(self):
        return self._dataSize

    def dataSizeCanChange(self):
        return self._dataSizeCanChange

    def isResponse(self):
        return self._isResponse

    def isRequest(self):
        return not self._isResponse

    def __str__(self) -> str:
        return self.raw.decode('utf-8', errors='replace')

    def __int__(self) -> int:
        return self.value # I'm torn between returning self.value and self._sid

    def __bytes__(self) -> bytes:
        return self.raw

    def __len__(self) -> int:
        return len(self.raw)

    def __getitem__(self, index : int) -> int:
        return self.raw[index]

    @classmethod
    def fromMessageData(cls, msg_data : bytes):
        """
        Generates a subclass instance of UDSMessage based on the given message data.

        Message data must be in the following format:
        1. Service ID (1 byte)
        2. Sub-Function ID (0 or 1 bytes)
        3. Data ID (0 or 2 bytes)
        4. Data (0 or n bytes)
        """
        msg = cls.fromSID(msg_data[0])
        index = 1
        if msg.hasSubfn():
            msg.subfn = msg_data[index]
            index += 1
        if msg.hasDID():
            msg.did = msg_data[index:index+2]
            index += 2
        if msg.hasData():
            if len(msg_data) > index:
                msg.data = msg_data[index:]
            else:
                msg.data = b''
        return msg

    @classmethod
    def fromSID(cls, sid : int):
        """
        Generates a subclass instance of UDSMessage based on the given message SID.

        Returns generic instance of this class if SID is not found in a subclass.
        """
        for msg in cls.__subclasses__():
            if msg._sid == sid:
                return msg()
        return cls()
            
    @property
    def sid(self) -> int:
        """
        Service ID (8-bit unsigned integer).

        This property is immutable.
        """
        return self._sid

    @property
    def subfn(self) -> int:
        """
        Sub-Function ID (8-bit unsigned integer).
        
        Will be None if the service does not have a sub-function.
        """
        if self._hasSubfn:
            return self._subfn
        else:
            return None

    @subfn.setter
    def subfn(self, val : int):
        if not self._hasSubfn: # attempted to assign subfn when sub-function doesn't exist for this service
            raise AttributeError("Attempted to set subfn of UDS service that doesn't have sub-functions available.")
        if not isinstance(val, int): # handle bytes & str
            val = int.from_bytes(sanitize_msg_param(val, 1), 'big')
        self._subfn = val & 0xFF

    @property
    def did(self) -> int:
        """
        Data ID (16-bit unsigned integer). Acts like a function argument in most cases.

        Will be None if the service does not have a DID.
        """
        if self._hasDID:
            return self._did
        else:
            return None

    @did.setter
    def did(self, val : int):
        if not self._hasDID: # attempted to assign DID when DID doesn't exist for this service
            raise AttributeError("Attempted to set DID of UDS service that doesn't include a DID.")
        if not isinstance(val, int): # handle bytes & str
            val = int.from_bytes(sanitize_msg_param(val, 2), 'big')
        self._did = val & 0xFFFF

    @property
    def data(self) -> bytes:
        """
        Data field (n bytes).

        Will be `b''` if the service does not have a data field.
        """
        if self._hasData:
            return self._data
        else:
            return b''

    @data.setter
    def data(self, val : bytes):
        if not self._hasData: # attempted to assign data when data doesn't exist for this service
            raise AttributeError("Attempted to set data of UDS service that doesn't include a data field.")
        if not isinstance(val, bytes):
            val = sanitize_msg_param(val)
        if len(val) != self._dataSize: # check for length mismatches
            if self._dataSizeCanChange: # update data size if allowed
                self._dataSize = len(val)
            elif len(val) < self._dataSize: # stuff with bytes to fill data size
                val += BYTE_STUFFING_VALUE * (self._dataSize - len(val)) # stuff to fit
            else:
                raise ValueError("Data value for UDS message is too large!")
        self._data = val

    @property
    def raw(self) -> bytes:
        """
        Raw bytes representing the service.
        
        Does not include protocol-specific data like CANID.

        Byteorder:
        1. Service ID (1 byte)
        2. Sub-Function ID (0 or 1 bytes)
        3. Data ID (0 or 2 bytes)
        4. Data (0 or n bytes)
        """
        val = b''
        val += sanitize_msg_param(self._sid, 1)
        if self._hasSubfn:
            val += sanitize_msg_param(self._subfn, 1)
        if self._hasDID:
            val += sanitize_msg_param(self._did, 2)
        if self._hasData:
            val += sanitize_msg_param(self._data, self._dataSize)
        return val

    @property
    def value(self) -> int:
        """
        Integer value of UDS message data field.

        If message doesn't contain a data field, returns 0.
        """
        if not self._data:
            return 0
        return int.from_bytes(self._data, 'big')

    @property
    def suppressPosRspMsgIndicationBit(self) -> bool:
        """
        Bit 7 of `subfn`.
        - True = positive response to this service is suppressed.
        - False = receiving ECU will send positive response.
        """
        if self._hasSubfn:
            return bool(self.subfn & 0b10000000)
        else:
            return False

    @suppressPosRspMsgIndicationBit.setter
    def suppressPosRspMsgIndicationBit(self, val : bool):
        if not self._hasSubfn:
            raise AttributeError("Attempted to set subfn of UDS service that doesn't have sub-functions available.")
        if val:
            self.subfn |= 0b10000000
        else:
            self.subfn &= 0b01111111
