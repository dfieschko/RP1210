from . import UDSMessage


class ReadMemoryByAddressRequest(UDSMessage):
    """
    Read Memory By Address (Request)
    - `sid` = 0x23
    - `did` = addressAndLengthFormatIdentifier
    - `data` = memoryAddress + memorySize
    """

    _sid = 0x23
    _isResponse = False

    def __init__(self, did: int = 0, data: bytes = b''):
        super().__init__()
        self._hasSubfn = False
        self._hasDID = True
        self._hasData = True
        self._dataSize = len(data)
        self._dataSizeCanChange = True

        self.did = did
        self.data = data


class ReadMemoryByAddressResponse(UDSMessage):
    """
    Read Memory By Address (Response)
    - `sid` = 0x63
    - `data` = dataRecord
    """

    _sid = 0x63
    _isResponse = True

    def __init__(self, data: bytes = b''):
        super().__init__()
        self._hasSubfn = False
        self._hasDID = False
        self._hasData = True
        self._dataSize = len(data)
        self._dataSizeCanChange = True

        self.data = data
