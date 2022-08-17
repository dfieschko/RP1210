from . import UDSMessage
from .. import sanitize_msg_param

from RP1210 import sanitize_msg_param
from RP1210.UDS import UDSMessage

class RequestDownloadRequest(UDSMessage):
    """
    Request Download (Request)
    - `sid` = 0x34
    - `data` = dfid + alfid + maddr + msize
        - `dfid' = dataFormatIdentifier (1 byte)
        - `alfid' = addressAndLengthFormateIdentifier (1 byte)
            - bit 7 - 4: define length (number of bytes) of memoryAddress
            - bit 3 - 0`: define length (number of bytes) of memorySize
        - `maddr` = memoryAddress (n bytes)
        - `msize` = memorySize (n bytes)
    """

    _DFID_IDX = 0

    _sid = 0x34
    _isResponse = False

    def __init__(self, dfid: bytes = b'', alfid: bytes = b'', maddr: bytes = b'', msize: bytes = b''):
        super().__init__()
        self._hasSubfn = False
        self._hasDID = False
        self._hasData = True
        self._dataSize = len(maddr + msize)
        self._dataSizeCanChange = True

        self.dfid = dfid
        self.alfid = alfid
        self.maddr = maddr
        self.msize = msize

        # self.did = int.from_bytes(sanitize_msg_param(dfid + alfid, 2), 'big') # remove later
        # self.data = dfid + alfid + maddr + msize

    @property
    def dfid(self) -> int:
        return int.from_bytes(self._dfid, 'big')

    @dfid.setter
    def dfid(self, dfid: int | bytes):
        dfid = sanitize_msg_param(dfid)
        if(dfid.__len__() != 1):
            raise ValueError(F"DFID length must be 1 byte, got {dfid.__len__()} bytes: {dfid}")
        self._dfid = dfid
    
    @property
    def alfid(self) -> int:
        return int.from_bytes(self._alfid, 'big')

    @alfid.setter
    def alfid(self, alfid: int | bytes):
        alfid = sanitize_msg_param(alfid)
        if(alfid.__len__() != 1):
            raise ValueError(F"ALFID length must be 1 byte, got {alfid.__len__()} bytes: {alfid}")
        self._alfid = alfid

    @property
    def maddr(self) -> int:
        return int.from_bytes(self._maddr, 'big')

    @maddr.setter
    def maddr(self, maddr: int | bytes):
        maddr = sanitize_msg_param(maddr)
        if(maddr.__len__() != 1):
            raise ValueError(F"maddr length must be 1 byte, got {maddr.__len__()} bytes: {maddr}")
        self._maddr = maddr
    
    @property
    def msize(self) -> int:
        return int.from_bytes(self._msize, 'big')

    @msize.setter
    def msize(self, msize: int | bytes):
        msize = sanitize_msg_param(msize)
        if(msize.__len__() != 1):
            raise ValueError(F"msize length must be 1 byte, got {msize.__len__()} bytes: {msize}")
        self._msize = msize
    
    def _refresh_data(self) -> None:
        self.data = sanitize_msg_param(self._dfid) + sanitize_msg_param(self._alfid)


class RequestDownloadResponse(UDSMessage):
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

    def __init__(self, did: int = 0, data: bytes = b''):
        super().__init__()
        self._hasSubfn = False
        self._hasDID = False
        self._hasData = True
        self._dataSize = len(data)
        self._dataSizeCanChange = True

        self.did = did
        self.data = data

    @property
    def did(self) -> int:
        return self._did

    @did.setter
    def did(self, val: int):
        """
        DID in RequestDownload Response service is 1 byte
        """
        val = int.from_bytes(sanitize_msg_param(val, 1), 'big')
        self._did = val & 0xFF
