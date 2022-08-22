from . import UDSMessage
from .. import sanitize_msg_param


class RequestUploadRequest(UDSMessage):
    """
    Request Upload (Request)
    - `sid` = 0x35
    - `did` = dataFormatIdentifier (1 byte) + addressAndLengthFormatIdentifier (1 byte)
    - `data` = memoryAddress + memorySize
    """

    _sid = 0x35
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


class RequestUploadResponse(UDSMessage):
    """
    Request Upload (Response)
    - `sid` = 0x75
    - `data` = lfid + mnrob
        - `lfid` = lengthFormatIdentifier (1 byte)
            - bit 7 - 4: maxNumberOfBlockLength
            - bit 3 - 0: reserved; set to be 0
        - `mnrob` = maxNumberOfBlockLength (n bytes)
    """

    _sid = 0x75
    _isResponse = True

    def __init__(self, data: bytes = b''):
        super().__init__()
        self._hasSubfn = False
        self._hasDID = False
        self._hasData = True
        self._dataSize = len(data)
        self._dataSizeCanChange = True

        self.data = data

    @property
    def lfid(self) -> int:
        """
        Length format identifier. Only bits 7-4 are used.
        """
        return self.data[0]

    @lfid.setter
    def lfid(self, lfid: int | bytes) -> None:
        self.data = sanitize_msg_param(lfid, 1) + self.data[1:]

    @property
    def mnrob(self) -> int:
        """
        Max NumbeR Of Blocks. Length must match the value specified in the LFID.
        """
        return int.from_bytes(self.data[1:], 'big')

    @mnrob.setter
    def mnrob(self, mnrob: int | bytes) -> None:
        self.data = sanitize_msg_param(self.data[0]) + sanitize_msg_param(mnrob)