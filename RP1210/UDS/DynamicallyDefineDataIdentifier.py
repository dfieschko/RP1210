from . import UDSMessage


class DynamicallyDefineDataIdentifierRequest(UDSMessage):
    """
    Dynamically Define Data Identifier (Request)
    - `sid` = 0x2C
    - `subfn` = definitionType
    - `did` = dynamicallyDefinedDataIdentifier = byte #1 (MSB F2/F3) + byte #2 (LSB 00 - FF)
    - `data` => depends on subfn
    """

    _sid = 0x2C
    _isResponse = False

    # sub-function IDs, for convenience:
    defineByIdentifier = 0x01
    defineByMemoryAddress = 0x02
    clearDynamicallyDefineddataIdentifier = 0x03

    def __init__(self, subfn: int = defineByIdentifier, did: int = 0, data: bytes = b''):
        super().__init__()
        self._hasSubfn = True
        self._hasDID = True

        if subfn != self.clearDynamicallyDefineddataIdentifier:
            self._hasData = True
            self._dataSize = len(data)
            self._dataSizeCanChange = True
            self.data = data
        else:
            self._hasData = False

        self.subfn = subfn
        self.did = did


class DynamicallyDefineDataIdentifierResponse(UDSMessage):
    """
    Dynamically Define Data Identifier (Response)
    - `sid` = 0x6C
    - `subfn` = definitionType
    - `did` = dynamicallyDefinedDataIdentifier = byte #1 (MSB F2/F3) + byte #2 (LSB 00 - FF)
    """

    _sid = 0x6C
    _isResponse = True

    # sub-function IDs, for convenience:
    defineByIdentifier = 0x01
    defineByMemoryAddress = 0x02
    clearDynamicallyDefineddataIdentifier = 0x03

    def __init__(self, subfn: int = defineByIdentifier, did: int = 0):
        super().__init__()
        self._hasSubfn = True
        self._hasDID = True
        self._hasData = False

        self.subfn = subfn
        self.did = did
