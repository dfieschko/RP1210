from . import UDSMessage


class SecurityAccessRequest(UDSMessage):
    """`
    Security Access (Request)
    - `sid` = 0x27
    - `subfn` = securityAccesType
    - `data` = securityAccesDataRecord
    """

    _sid = 0x27
    _isResponse = False

    # sub-function IDs, for convenience
    requestSeed = 0x01
    sendKey = 0x02
    requestSeed = 0x03

    def __init__(self, subfn: int, data: bytes):
        super().__init__()
        self._hasSubfn = True
        self._hasDID = False
        self._hasData = True

        self.subfn = subfn


class SecurityAccessResponse(UDSMessage):
    """
    Security Access (Response)
    - `sid` = 0x67

    """
