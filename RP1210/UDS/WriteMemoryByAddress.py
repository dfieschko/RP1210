from . import UDSMessage
from .. import sanitize_msg_param


class WriteMemoryByAddressRequest(UDSMessage):
    """
    Write Memory By Address (Request)
    - `sid` = 0x3D
    - `did` = addressAndLengthFormatIdentifier (1 byte)
    - `data` = memoryAddress + memorySize + dataRecord
    """

    _sid = 0x3D
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

    @property
    def did(self) -> int:
        return self._did

    @did.setter
    def did(self, val: int):
        """
        DID is 1 byte
        """
        val = int.from_bytes(sanitize_msg_param(val, 1), 'big')
        self._did = val & 0xFF


class WriteMemoryByAddressResponse(UDSMessage):
    """
    Write Memory By Address (Response)
    - `sid` = 0x7D
    - `did` = addressAndLengthFormatIdentifier (1 byte)
    - `data` = memoryAddress + memorySize
    """

    _sid = 0x7D
    _isResponse = True

    def __init__(self, did: int = 0, data: bytes = b''):
        super().__init__()
        self._hasSubfn = False
        self._hasDID = True
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
        DID is 1 byte
        """
        val = int.from_bytes(sanitize_msg_param(val, 1), 'big')
        self._did = val & 0xFF
