from . import UDSMessage


class ReadDataByIdentifierRequest(UDSMessage):
    """
    Read Data By Identifier (Request)
    - `sid` = 0x22
    - `did` = dataIdentifier
    """

    _sid = 0x22
    _isResponse = False

    def __init__(self, did: int = 0x00):
        super().__init__()
        self._hasSubfn = False
        self._hasDID = True
        self._hasData = False

        self.did = did


class ReadDataByIdentifierResponse(UDSMessage):
    """
    Read Data By Identifier (Response)
    - `sid` = 0x62
    - `did` = dataIdentifier
    - `data` = dataRecord (n bytes)
    """

    _sid = 0x62
    _isResponse = True

    def __init__(self, did: int = 0x00, data: bytes = b''):
        super().__init__()
        self._hasSubfn = False
        self._hasDID = True
        self._hasData = True
        self._dataSize = len(data)
        self._dataSizeCanChange = True

        self.did = did
        self.data = data
