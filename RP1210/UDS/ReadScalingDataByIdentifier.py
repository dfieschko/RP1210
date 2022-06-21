from . import UDSMessage


class ReadScalingDataByIdentifierRequest(UDSMessage):
    """
    Read Scaling Data By Identifier (Request)
    - `sid` = 0x24
    - `did` = dataIdentifier
    """

    _sid = 0x24
    _isResponse = False

    def __init__(self, did: int = 0):
        super().__init__()
        self._hasSubfn = False
        self._hasDID = True
        self._hasData = False

        self.did = did


class ReadScalingDataByIdentifierResponse(UDSMessage):
    """
    Read Scaling Data By Identifier (Response)
    - `sid` = 0x64
    - `did` = dataIdentifier
    - `data` = scalingBtye + scalingByteExtension
    """

    _sid = 0x64
    _isResponse = True

    def __init__(self, did: int = 0, data: bytes = b''):
        super().__init__()
        self._hasSubfn = False
        self._hasDID = True
        self._hasData = True
        self._dataSize = len(data)
        self._dataSizeCanChange = True

        self.did = did
        self.data = data
