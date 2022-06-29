from . import UDSMessage


class ReadDataByPeriodicIdentifierRequest(UDSMessage):
    """
    Read Data By Periodic Identifier (Request)
    - `sid` = 0x2A
    - `data` = transmissionMode (1 byte) + periodicDataIdentifier (n bytes)
    """

    _sid = 0x2A
    _isResponse = False

    def __init__(self, data: bytes = b''):
        super().__init__()
        self._hasSubfn = False
        self._hasDID = False
        self._hasData = True
        self._dataSize = len(data)
        self._dataSizeCanChange = True

        self.data = data


class ReadDataByPeriodicIdentifierResponse(UDSMessage):
    """
    Read Data By Periodic Identifier (Response)
    - `sid` = 0x6A
    - `data` = transmissionMode (1 byte) + periodicDataIdentifier (n bytes)
    """

    _sid = 0x6A
    _isResponse = True

    def __init__(self):
        super().__init__()
        self._hasSubfn = False
        self._hasDID = False
        self._hasData = False
