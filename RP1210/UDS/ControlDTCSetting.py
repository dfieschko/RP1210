from . import UDSMessage


class ControlDTCSettingRequest(UDSMessage):
    """
    Control DTC Setting (Request)
    - `sid` = 0x85
    - `subfn` = DTCSettingType
    - `data` = DTCSettingControlOptionRecord
    """

    _sid = 0x85
    _isResponse = False

    # sub-function IDs, for convenience:
    on = 0x01
    off = 0x02

    def __init__(self, subfn: int = on, data: bytes = b''):
        super().__init__()
        self._hasSubfn = True
        self._hasDID = False
        self._hasData = True
        self._dataSize = len(data)
        self._dataSizeCanChange = True

        self.subfn = subfn
        self.data = data


class ControlDTCSettingResponse(UDSMessage):
    """
    Control DTC Setting (Response)
    - `sid` = 0xC5
    - `subfn` = DTCSettingType
    """

    _sid = 0xC5
    _isResponse = True

    # sub-function IDs, for convenience:
    on = 0x01
    off = 0x02   

    def __init__(self, subfn: int = on):
        super().__init__()
        self._hasSubfn = True
        self._hasDID = False
        self._hasData = False

        self.subfn = subfn
