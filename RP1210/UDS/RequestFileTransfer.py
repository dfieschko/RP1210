from . import UDSMessage


class RequestFileTransferRequest(UDSMessage):
    """
    Request File Transfer (Request)
    - `sid` = 0x38
    - `data` =  modeOfOperation (1 byte) +
                filePathAndNameLength (2 bytes) +
                filePathAndName (n bytes) +
                dataFormatIdentifier (0 - 1 byte) +
                fileSizeParameterLength (0 - 1 byte) +
                fileSizeUnCompressed (0 - n bytes) +
                fileSizeCompressed (0 - n bytes)
    """

    _sid = 0x38
    _isResponse = False

    # modeOfOperation:
    AddFile = 0x01
    DeleteFile = 0x02
    ReplaceFile = 0x03
    ReadFile = 0x04
    ReadDir = 0x05
    ResumeFile = 0x06

    def __init__(self, data: bytes = b''):
        super().__init__()
        self._hasSubfn = False
        self._hasDID = False
        self._hasData = True
        self._dataSize = len(data)
        self._dataSizeCanChange = True

        self.data = data


class RequestFileTransferResponse(UDSMessage):
    """
    Request File Transfer (Response)
    - `sid` = 0x78
    - `data` =  modeOfOperation (1 byte) +
                lengthFormatIdentifier (0 - 1 byte) +
                maxNumberOfBlockLength (0 - n bytes) +
                dataFormatIdentifier (0 - 1 byte) +
                fileSizeOrDirInfoParameterLength (0 or 2 bytes) +
                fileSizeUpcompressedOrDirInfoLength (0 - n bytes) +
                fileSizeCompressed (0 - n bytes) +
                filePosition (0 - 8 bytes)
    """

    _sid = 0x78
    _isResponse = True

    # modeOfOperation:
    AddFile = 0x01
    DeleteFile = 0x02
    ReplaceFile = 0x03
    ReadFile = 0x04
    ReadDir = 0x05
    ResumeFile = 0x06

    def __init__(self, data: bytes = b''):
        super().__init__()
        self._hasSubfn = False
        self._hasDID = False
        self._hasData = True
        self._dataSize = len(data)
        self._dataSizeCanChange = True

        self.data = data
