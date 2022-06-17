from . import UDSMessage
from .. import sanitize_msg_param


class RequestDowloadRequest(UDSMessage):
    """
    Request Download (Request)
    - `sid` = 0x34
    - `did` = dfid + alfid
        - `dfid' = dataFormatIdentifier (1 byte)
        - `alfid' = addressAndLengthFormateIdentifier (1 byte)
            - bit 7 - 4: define length (number of bytes) of memoryAddress
            - bit 3 - 0`: define length (number of bytes) of memorySize
    - `data` = maddr + msize
        - `maddr` = memoryAddress (n bytes)
        - `msize` = memorySize (n bytes)
    """

    _sid = 0x34
    _isResponse = False

    def __init__(self, dfid: bytes = b'', alfid: bytes = b'', maddr: bytes = b'', msize: bytes = b''):
        super().__init__()
        self._hasSubfn = False
        self._hasDID = True
        self._hasData = True
        self._dataSize = len(maddr + msize)
        self._dataSizeCanChange = True

        self.did = dfid + alfid
        self.data = maddr + msize


class RequestDowloadResponse(UDSMessage):
    """
    Request Download (Response)
    - `sid` = 0x74
    - `did` = lengthFormatIdentifier (1 byte)
        - bit 7 - 4: maxNumberOfBlockLength
        - bit 3 - 0: reserved; set to be 0
    - `data` = maxNumberOfBlockLength (n bytes)
    """

    _sid = 0x74
    _isResponse = True

    def __init__(self, did: bytes = b'', data: bytes = b''):
        super().__init__()
        self._hasSubfn = False
        self._hasDID = True
        self._hasData = True

        self.did = did
        self.data = data

    @property
    def did(self) -> int:
        return self._did

    @did.setter
    def did(self, val: int):
        """
        DID in RequestDownload Response service is 1 byte instance of 2 bytes
        """
        val = int.from_bytes(sanitize_msg_param(val, 1), 'big')
        self._did = val & 0xFFFF
