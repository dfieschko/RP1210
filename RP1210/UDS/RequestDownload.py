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

    _sid = 0x34
    _isResponse = False

    def __init__(self, dfid: bytes = b'\x00', alfid: bytes = b'\x00', maddr: bytes = b'', msize: bytes = b'', autoALFID: bool = True):
        super().__init__()
        self._hasSubfn = False
        self._hasDID = False
        self._hasData = True
        self._dataSizeCanChange = True
        self._autoALFID: bool = autoALFID

        self.dfid = dfid
        self.alfid = alfid
        self.maddr = maddr
        self.msize = msize
        self._dataSize = len(self.data)

        # self.did = int.from_bytes(sanitize_msg_param(dfid + alfid, 2), 'big') # remove later
        # self.data = dfid + alfid + maddr + msize

    @property
    def dfid(self) -> int:
        return int.from_bytes(self._dfid, 'big')

    @dfid.setter
    def dfid(self, dfid: int | bytes):
        dfid = sanitize_msg_param(dfid, 1)
        # if(dfid.__len__() != 1):
        #     raise ValueError(F"DFID length must be 1 byte, got {dfid.__len__()} bytes: {dfid}")
        self._dfid = dfid
    
    @property
    def alfid(self) -> int:
        return int.from_bytes(self._alfid, 'big')

    @alfid.setter
    def alfid(self, alfid: int | bytes):
        alfid = sanitize_msg_param(alfid, 1)
        # if(alfid.__len__() != 1):
        #     raise ValueError(F"ALFID length must be 1 byte, got {alfid.__len__()} bytes: {alfid}")
        self._alfid = alfid

    @property
    def maddr(self) -> int:
        return int.from_bytes(self._maddr, 'big')

    @maddr.setter
    def maddr(self, maddr: int | bytes):
        maddr = sanitize_msg_param(maddr)
        if(self._autoALFID == True):
            if(maddr.__len__() > 0x0f):
                raise ValueError(F"maddr length must be less than 16 bytes, got {maddr.__len__()} bytes: {maddr}")
            self.alfid = (self.alfid & 0xf0) | (maddr.__len__() & 0x0f)
        self._maddr = maddr
    
    @property
    def msize(self) -> int:
        return int.from_bytes(self._msize, 'big')

    @msize.setter
    def msize(self, msize: int | bytes):
        msize = sanitize_msg_param(msize)
        if(self._autoALFID == True):
            if(msize.__len__() > 0x0f):
                raise ValueError(F"msize length must be less than 16 bytes, got {msize.__len__()} bytes: {msize}")
            self.alfid = (self.alfid & 0x0f) | ((msize.__len__() & 0x0f) << 4)
        self._msize = msize
    
    @property
    def data(self) -> bytes:
        return sanitize_msg_param(self._dfid) + sanitize_msg_param(self._alfid) + sanitize_msg_param(self._maddr) + sanitize_msg_param(self._msize)

    # @property
    # def _dataSize(self) -> int:
    #     return self.data.__len__()


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
