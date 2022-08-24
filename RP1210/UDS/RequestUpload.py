from typing import Union
from . import UDSMessage
from .. import sanitize_msg_param

class RequestUploadRequest(UDSMessage):
    """
    Request Upload (Request)
    - `sid` = 0x35
    - `data` = dfid + alfid + maddr + msize
        - `dfid' = dataFormatIdentifier (1 byte)
        - `alfid' = addressAndLengthFormatIdentifier (1 byte)
            - bits 7-4: define length (number of bytes) of memorySize
            - bits 3-0`: define length (number of bytes) of memoryAddress
        - `maddr` = memoryAddress (n bytes)
        - `msize` = memorySize (n bytes)
    """

    _sid = 0x35
    _isResponse = False

    def __init__(self, dfid: bytes = b'\x00', alfid: bytes = b'\x00', maddr: bytes = b'', msize: bytes = b'', autoALFID: bool = True):
        """
        - `dfid`: Data Format Identifier (1 byte). Default is `0x00` (no encryption or compression), other values are manufacturer-specific.
        - `alfid`: Address and Length Format Identifer (1 byte). Can be left default if `autoALFID` is `True`.
            - bits 7-4: define length (number of bytes) of msize
            - bits 3-0: define length (number of bytes) of maddr
        - `maddr`: memoryAddress (0-15 bytes)
        - `msize`: memorySize (0-15 bytes)
        - `autoALFID`: If `True`, `alfid` is automatically calculated based on the values of `maddr` and `msize`. If `False`, `alfid` must
        be specified manually to produce a valid request.
        """
        super().__init__()
        self._hasSubfn:          bool = False
        self._hasDID:            bool = False
        self._hasData:           bool = True
        self._dataSizeCanChange: bool = True

        self._autoALFID: bool = autoALFID
        self.dfid             = dfid
        self.alfid            = alfid
        self.maddr            = maddr
        self.msize            = msize

        self._dataSize: int = len(self.data)

    @property
    def dfid(self) -> int:
        return int.from_bytes(self._dfid, 'big')

    @dfid.setter
    def dfid(self, dfid: Union[int, bytes]) -> None:
        self._dfid = sanitize_msg_param(dfid, 1)
    
    @property
    def alfid(self) -> int:
        return int.from_bytes(self._alfid, 'big')

    @alfid.setter
    def alfid(self, alfid: Union[int, bytes]) -> None:
        self._alfid = sanitize_msg_param(alfid, 1)

    @property
    def maddr(self) -> int:
        return int.from_bytes(self._maddr, 'big')

    @maddr.setter
    def maddr(self, maddr: Union[int, bytes]) -> None:
        maddr = sanitize_msg_param(maddr)
        if self._autoALFID: # Auto-calculating alfid
            if len(maddr) > 0x0f:
                raise ValueError(F"maddr length must be less than 16 bytes, got {len(maddr)} bytes: {maddr}")
            self.alfid = (self.alfid & 0xf0) | (len(maddr) & 0x0f)
        self._maddr = maddr

    @property
    def msize(self) -> int:
        return int.from_bytes(self._msize, 'big')

    @msize.setter
    def msize(self, msize: Union[int, bytes]) -> None:
        msize = sanitize_msg_param(msize)
        if self._autoALFID: # Auto-calculating alfid
            if len(msize) > 0x0f:
                raise ValueError(F"msize length must be less than 16 bytes, got {len(msize)} bytes: {msize}")
            self.alfid = (self.alfid & 0x0f) | ((len(msize) & 0x0f) << 4)
        self._msize = msize

    @property
    def data(self) -> bytes:
        """
        Concatenates the request's properties to form the data field.
        """
        return sanitize_msg_param(self._dfid) + sanitize_msg_param(self._alfid) + sanitize_msg_param(self._maddr) + sanitize_msg_param(self._msize)


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
    def lfid(self, lfid: Union[int, bytes]) -> None:
        self.data = sanitize_msg_param(lfid, 1) + self.data[1:]

    @property
    def mnrob(self) -> int:
        """
        Max NumbeR Of Blocks. Length must match the value specified in the LFID.
        """
        return int.from_bytes(self.data[1:], 'big')

    @mnrob.setter
    def mnrob(self, mnrob: Union[int, bytes]) -> None:
        self.data = sanitize_msg_param(self.data[0]) + sanitize_msg_param(mnrob)
