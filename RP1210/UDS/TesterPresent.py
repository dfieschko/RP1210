from . import UDSMessage


class TesterPresentRequest(UDSMessage):
    """
    TesterPresent (Request)
    - `sid` = 0x3E
    - `subfn` = zeroSubFunction
    """

    _sid = 0x3E
    _isResponse = False

    # sub-function IDs, for convenience:
    zeroSubFunction = 0x00

    def __init__(self, subfn: int = zeroSubFunction):
        super().__init__()
        self._hasSubfn = True
        self._hasDID = False
        self._hasData = False

        self.subfn = subfn


class TesterPresentResponse(UDSMessage):
    """
    Tester Present (Response)
    - `sid` = 0x7E
    - `subfn` = zeroSubFunction
    """

    _sid = 0x7E
    _isResponse = True

    zeroSubFunction = 0x00

    def __init__(self, subfn: int = zeroSubFunction):
        super().__init__()
        self._hasSubfn = True
        self._hasDID = False
        self._hasData = False

        self.subfn = subfn
