from . import UDSMessage


class ClearDiagnosticInformationRequest(UDSMessage):
    """
    Clear Diagnostic Information (Request)
    - `sid` = 0x14
    - `data` = groupOfDTC + Memory Selection
    """

    _sid = 0x14
    _isResponse = False

    def __init__(self, data: bytes = b''):
        super().__init__()
        self._hasSubfn = False
        self._hasDID = False
        self._hasData = True
        self._dataSize = len(data)
        self._dataSizeCanChange = True

        self.data = data


class ClearDiagnosticInformationResponse(UDSMessage):
    """
    Clear Diagnostic Information (Response)
    - `sid` = 0x54
    """

    _sid = 0x54
    _isResponse = True

    def __init__(self):
        super().__init__()
        self._hasSubfn = False
        self._hasDID = False
        self._hasData = False
