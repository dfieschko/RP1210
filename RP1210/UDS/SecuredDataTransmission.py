from . import UDSMessage


class SecuredDataTransmissionRequest(UDSMessage):
    """
    Secured Data Transmission (Request)
    - `sid` = 0x84
    - `data` =  Administrative Parameter (2 bytes) +
                Signature/Encryption Calculation (1 byte) +
                Signature Length (2 bytes) +
                Anti-replay Counter (2 bytes) +
                Internal Message Service Request ID (1 byte) +
                Service Specific Parameter (n bytes) +
                Signature/MAC (n bytes)
    """

    _sid = 0x84
    _isResponse = False

    def __init__(self, data: bytes = b''):
        super().__init__()
        self._hasSubfn = False
        self._hasDID = False
        self._hasData = True
        self._dataSize = len(data)
        self._dataSizeCanChange = True

        self.data = data


class SecuredDataTransmissionResponse(UDSMessage):
    """
    Secured Data Transmission (Response)
    - `sid` = 0xC4
    - `data` =  Administrative Parameter (2 bytes) +
                Signature/Encryption Calculation (1 byte) +
                Signature Length (2 bytes) +
                Anti-replay Counter (2 bytes) +
                Internal Message Service Response ID (1 byte) +
                Response Specific Parameter (n bytes) +
                Signature/MAC (n bytes)
    """

    _sid = 0xC4
    _isResponse = True

    def __init__(self, data: bytes = b''):
        super().__init__()
        self._hasSubfn = False
        self._hasDID = False
        self._hasData = True
        self._dataSize = len(data)
        self._dataSizeCanChange = True

        self.data = data
