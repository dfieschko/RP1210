from . import UDSMessage


class InputOutputControlByIdentifierRequest(UDSMessage):
    """
    Input Output Control By Identifier (Request)
    - `sid` = 0x2F
    - `did` = dataIdentifier
    - `data` = controlOptionRecord + controlEnableMaskRecord
    """

    _sid = 0x2F
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

class InputOutputControlByIdentifierResponse(UDSMessage):
    """
    Input Output Control By Identifier (Response)
    - `sid` = 0x6F
    - `did` = dataIdentifier
    - `data` = controlStatusRecord
    """

    _sid=0x6F
    _isResponse=True

    def __init__(self, did: int = 0, data: bytes = b''):
        super().__init__()
        self._hasSubfn = False
        self._hasDID = True
        self._hasData = True
        self._dataSize = len(data)
        self._dataSizeCanChange = True

        self.did = did
        self.data = data
        