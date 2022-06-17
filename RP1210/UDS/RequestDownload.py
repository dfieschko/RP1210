from . import UDSMessage


class RequestDowloadRequest(UDSMessage):
    """
    Request Download (Request)
    - `sid` = 0x34
    - `dfid' = dataFormatIdentifier (1 byte)
    - `alfid' = addressAndLengthFormateIdentifier (1 byte)
        - `maddr` = memoryAddress (bit 7 - 4)
        - `msize` = memorySize (bit 3 - 0)
    """

    _sid = 0x34
    _isResponse = False

    def __init__(self, dfid: bytes, alfid: bytes, maddr: bytes, msize: bytes):
        super().__init__()
        self._hasSubfn = False
        self._hasDID = True
        self._hasData = False

        self.dfid = dfid
        self.alfid = alfid
        self.maddr = maddr
        self.msize = msize


class RequestDowloadResponse(UDSMessage):
    """
    Request Download (Response)
    - `sid` = 0x74
    - `lfid` = lengthFormatIdentifier (1 byte)
        - `mnobl` = maxNumberOfBlockLength (bit 7 - 4)
        - reserved; set to be 0 (bit 3 - 0)
    """

    _sid = 0x74
    _isResponse = True

    def __init__(self, lfid: bytes, mnobl: bytes):
        super().__init__()
        self._hasSubfn = False
        self._hasDID = False
        self._hasData = False

        self.lfid = lfid
        self.mnobl = mnobl
