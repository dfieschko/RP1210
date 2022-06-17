from . import UDSMessage


class SecurityAccessRequest(UDSMessage):
    """`
    Security Access (Request)
    - `sid` = 0x27
    - `subfn` = securityAccesType
    - `data` = securityAccesDataRecord (for requestSeed) 
                or securityKey (for sendKey) (n btyes)
    """

    _sid = 0x27
    _isResponse = False

    # sub-function IDs, for convenience
    # with the level of security defined by the vehicle manufacturer
    requestSeed = 0x01
    sendKey = 0x02
    # with different levels of security defined by the vehicle manufacturer
    # requestSeed = 0x03, 0x05, 0x07 to 0x41
    # sendKey = 0x04, 0x06, 0x08 to 0x42
    def __init__(self, subfn: int=0x01, data: bytes=b''):
        super().__init__()
        self._hasSubfn = True
        self._hasDID = False
        self._hasData = True
        self._dataSize = len(data)
        self._dataSizeCanChange = True

        self.subfn = subfn
        self.data = data


class SecurityAccessResponse(UDSMessage):
    """
    Security Access (Response)
    - `sid` = 0x67

    """
