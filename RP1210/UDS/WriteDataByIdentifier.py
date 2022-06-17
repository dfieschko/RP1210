from . import UDSMessage

class WriteDataByIdentifierRequest(UDSMessage):
    """
    Write Data By Identifier (Request)
    - `sid` = 0x2E
    - `did` = dataIdentifier
    - `data` = dataRecord (n bytes)
    """

    _sid = 0x2E
    _isResponse = False

    def __init__(self, did : int = 0, data : bytes = b''):
        super().__init__()
        self._hasSubfn = False
        self._hasDID = True
        self._hasData = True
        self._dataSize = len(data)
        self._dataSizeCanChange = True

        self.did = did
        self.data = data

class WriteDataByIdentifierResponse(UDSMessage):
    """
    Write Data By Identifier (Response)
    - `sid` = 0x6E
    - `did` = dataIdentifier
    """

    _sid = 0x6E
    _isResponse = True

    def __init__(self, did : int = 0):
        super().__init__()
        self._hasSubfn = False
        self._hasDID = True
        self._hasData = False

        self.did = did