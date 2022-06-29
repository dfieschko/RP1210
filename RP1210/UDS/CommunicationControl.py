from . import UDSMessage
from .. import sanitize_msg_param


class CommunicationControlRequest(UDSMessage):
    """
    Communication Control (Request)
    - `sid` = 0x28
    - `subfn` = controlType
    - `comtype` = commnucationType (1 byte)
    - `high_node_id` = nodeIdentificationNumber (high byte) (1 byte)
    - `low_node_id` = nodeIdentificationNumber (low byte) (1 byte)
    """
    _sid = 0x28
    _isResponse = False

    # sub-function IDs. for convenience:
    enableRxAndTx = 0x00
    enableRxAndDisableTx = 0x01
    diableRxAndEnableTx = 0x02
    disableRxAndTx = 0x03
    enableRxAndDisableTxWithEnhancedAddressInformation = 0x04
    enableRxAndTxWithEnhancedAddressInformation = 0x05

    def __init__(self, subfn: int = enableRxAndTx, comtype: bytes = b'', high_node_id: bytes = b'', low_node_id: bytes = b''):
        super().__init__()
        self._hasSubfn = True
        self._hasDID = False
        self._hasData = True
        self._dataSizeCanChange = False

        self.subfn = subfn
        if self.subfn in {0x04, 0x05}:
            self._dataSize = len(comtype + high_node_id + low_node_id)
            self.data = comtype + high_node_id + low_node_id
        else:
            self._dataSize = len(comtype)
            self.data = comtype


class CommunicationControlResponse(UDSMessage):
    """
    Communication Control (Response)
    - `sid` = 0x68
    - `subfn` = controlType
    """
    _sid = 0x68
    _isResponse = True

    # sub-function IDs. for convenience:
    enableRxAndTx = 0x00
    enableRxAndDisableTx = 0x01
    diableRxAndEnableTx = 0x02
    disableRxAndTx = 0x03
    enableRxAndDisableTxWithEnhancedAddressInformation = 0x04
    enableRxAndTxWithEnhancedAddressInformation = 0x05

    def __init__(self, subfn: int = enableRxAndTx):
        super().__init__()
        self._hasSubfn = True
        self._hasDID = False
        self._hasData = False

        self.subfn = subfn
