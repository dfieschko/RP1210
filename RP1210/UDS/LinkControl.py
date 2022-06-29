from . import UDSMessage


class LinkControlRequest(UDSMessage):
    """
    Link Control (Request)
    - `sid` = 0x87
    - `subfn` = linkControlType
    - `data` = (1 or 0 btye)
        1. linkControlModelIdentifier (for verifyModeTransitionWithFixedParameter)
        2. linkRecord (for verifyModeTransitionWithSpecificParameter)
        3. None (for transitionMode)
    """

    _sid = 0x87
    _isResponse = False

    # sub-function IDs, for convenience:
    verifyModeTransitionWithFixedParameter = 0x00
    verifyModeTransitionWithSpecificParameter = 0x02
    transitionMode = 0x03

    def __init__(self, subfn: int = verifyModeTransitionWithFixedParameter, data: bytes = b''):
        super().__init__()
        self._hasSubfn = True
        self._hasDID = False

        self.subfn = subfn
        if subfn != self.transitionMode:
            self._hasData = True
            self._dataSize = len(data)
            self._dataSizeCanChange = False
            self.data = data
        else:
            self._hasData = False


class LinkControlResponse(UDSMessage):
    """
    Link Control (Response)
    - `sid` = 0xC7
    - `subfn` = linkControlType
    """

    _sid = 0xC7
    _isResponse = True

    # sub-function IDs, for convenience:
    verifyModeTransitionWithFixedParameter = 0x00
    verifyModeTransitionWithSpecificParameter = 0x02
    transitionMode = 0x03

    def __init__(self, subfn: int = verifyModeTransitionWithFixedParameter):
        super().__init__()
        self._hasSubfn = True
        self._hasDID = False
        self._hasData = False

        self.subfn = subfn
