from . import UDSMessage
from .. import sanitize_msg_param


class TransferDataRequest(UDSMessage):
    """
    Transfer Data (Request)
    - `sid` = 0x36
    - `bsc` = blockSequenceCounter (1 byte)
        The blockSequenceCounter parameter value starts at 0x01 with the first TransferData request that follows the 
        RequestDownload (0x34) or RequestUpload (0x35) or RequestFileTransfer (0x38) service. Its value is incremented 
        by 1 for each subsequent TransferData request. At the value of 0xFF the blockSequenceCounter rolls over and 
        starts at 0x00 with the next TransferData request message.
    - `data` = transferEquestParameterRecord (n bytes)
    """

    _sid = 0x36
    _isResponse = False

    def __init__(self, bsc: int = 1, data: bytes = b''):
        super().__init__()
        self._hasSubfn = False
        self._hasDID = False
        self._hasData = True
        self._dataSize = len(data)
        self._dataSizeCanChange = True

        self.bsc = bsc
        self.data = data

    @property
    def bsc(self) -> int:
        """
        blockSequenceCounter - counts current nth blocks of data
        """
        return self._bsc

    @bsc.setter
    def bsc(self, val: int):
        if not isinstance(val, int):  # handle bytes & str
            val = int.from_bytes(sanitize_msg_param(val, 2), 'big')
        self._bsc = val

    @property
    def raw(self) -> bytes:
        """
        Raw bytes representing the service.

        Does not include protocol-specific data like CANID.

        Byteorder:
        1. Service ID (1 byte)
        2. BSC (2 bytes, blockSequenceCounter)
        3. Data (0 or n bytes)
        """
        return \
            sanitize_msg_param(self._sid, 1) + \
            sanitize_msg_param(self._bsc, 1) + \
            sanitize_msg_param(self._data, self._dataSize)


class TransferDataResponse(UDSMessage):
    """
    Transfer Data (Response)
    - `sid` = 0x76
    - `data` = blockSequenceCounter (1 byte) + transferEquestParameterRecord (n bytes)
    """

    _sid = 0x76
    _isResponse = True

    def __init__(self, data: bytes = b'\x01'):
        super().__init__()
        self._hasSubfn = False
        self._hasDID = False
        self._hasData = True
        self._dataSizeCanChange = True
        if len(data) > 0:
            self._dataSize = len(data) - 1

            self.bsc = data[0]
            self.data = data[1:]
        else:
            raise IndexError("Data length must be at least 1 byte.")

    @property
    def bsc(self) -> int:
        """
        blockSequenceCounter - counts current nth blocks of data
        """
        return self._bsc

    @bsc.setter
    def bsc(self, val: int):
        if not isinstance(val, int):  # handle bytes & str
            val = int.from_bytes(sanitize_msg_param(val, 2), 'big')
        self._bsc = val
