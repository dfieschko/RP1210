from . import UDSMessage


class RequestTransferExitRequest(UDSMessage):
    """
    Request Transfer Exit (Request)
    - `sid` = 0x37
    - `data` = transferRequestParameterRecord
    """

    _sid = 0x37
    _isResponse = False

    def __init__(self, data: bytes = b''):
        super().__init__()
        self._hasSubfn = False
        self._hasDID = False
        self._hasData = True
        self._dataSize = len(data)
        self._dataSizeCanChange = True

        self.data = data


class RequestTransferExitResponse(UDSMessage):
    """
    Request Transfer Exit (Response)
    - `sid` = 0x77
    - `data` = transferRequestParameterRecord
    """

    _sid = 0x77
    _isResponse = True

    def __init__(self, data: bytes = b''):
        super().__init__()
        self._hasSubfn = False
        self._hasDID = False
        self._hasData = True
        self._dataSize = len(data)
        self._dataSizeCanChange = True

        self.data = data
