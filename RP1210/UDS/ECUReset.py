from . import UDSMessage
from .. import sanitize_msg_param

class ECUResetRequest(UDSMessage):
    """
    ECU Reset (Request)
    - `sid` = 0x11
    - `subfn` = resetType
    """

    _sid = 0x11
    _isResponse = False

    # sub-function IDs, for convenience:
    hardReset = 0x01
    keyOffOnReset = 0x02
    softReset = 0x03
    enableRapidPowerShutDown = 0x04
    disableRapidPowerShutDown = 0x05
    
    def __init__(self, subfn : int = hardReset):
        super().__init__()
        self._hasSubfn = True
        self._hasDID = False
        self._hasData = False
        self.subfn = subfn

class ECUResetResponse(UDSMessage):
    """
    ECU Reset (Response)
    - `sid` = 0x51
    - `subfn` = resetType
    - `data` = powerDownTime (0 or 1 bytes)
       1. powerDownTime (only present for subfn = 0x04)
    """

    _sid = 0x51
    _isResponse = True

    # sub-function IDs, for convenience:
    hardReset = 0x01
    keyOffOnReset = 0x02
    softReset = 0x03
    enableRapidPowerShutDown = 0x04
    disableRapidPowerShutDown = 0x05
    
    def __init__(self, subfn : int = hardReset, data = b''):
        super().__init__()
        self._hasSubfn = True
        self._hasDID = False
        self._dataSizeCanChange = False
        self.subfn = subfn

        if self.subfn == self.enableRapidPowerShutDown or data:
            self._hasData = True
            self._dataSize = 1
            self.data = sanitize_msg_param(data, 1)
        else:
            self._hasData = False

    # overload subfn, since changing subfn will change data
    @property
    def subfn(self) -> int:
        return self._subfn

    @subfn.setter
    def subfn(self, val : int):
        if not isinstance(val, int): # handle bytes & str
            val = int.from_bytes(sanitize_msg_param(val, 1), 'big')
        self._subfn = val & 0xFF
        if self._subfn == 0x04: # subfn 0x04 has 1 data byte
            self._hasData = True
            self._dataSize = 1
            self.data = b'\xFF'

    @property
    def powerDownTime(self) -> int:
        """
        `powerDownTime` value in message data. This value should only exist for SID = 0x04.

        Will return None if not available.
        """
        if not self._hasData:
            return None
        return self.data[0]

    @powerDownTime.setter
    def powerDownTime(self, val : int):
        self.data = sanitize_msg_param(val, 1)
