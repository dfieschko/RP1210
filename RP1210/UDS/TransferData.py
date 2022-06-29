from . import UDSMessage


class TransferDataRequest(UDSMessage):
    """
    Transfer Data (Request)
    - `sid` = 0x36
    - `data` = blockSequenceCounter (1 byte) + transferEquestParameterRecord (n bytes)
    """

    _sid = 0x36
    _isResponse = False

    def __init__(self, data: bytes = b''):
        super().__init__()
        self._hasSubfn = False
        self._hasDID = False
        self._hasData = True
        self._dataSize = len(data)
        self._dataSizeCanChange = True

        self.data = data


class TransferDataResponse(UDSMessage):
    """
    Transfer Data (Response)
    - `sid` = 0x76
    - `data` = blockSequenceCounter (1 byte) + transferEquestParameterRecord (n bytes)
    """

    _sid = 0x76
    _isResponse = True

    def __init__(self, data: bytes = b''):
        super().__init__()
        self._hasSubfn = False
        self._hasDID = False
        self._hasData = True
        self._dataSize = len(data)
        self._dataSizeCanChange = True

        self.data = data
