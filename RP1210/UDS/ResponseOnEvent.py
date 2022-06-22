from . import UDSMessage


class ResponseOnEventRequest(UDSMessage):
    """
    Response On Event (Request)
    - `sid` = 0x86
    - `subfn` = eventType
    - `data` = eventTypeRecord + serviceToRespondToRecord
        - `eventTypeRecord` = eventTypeParameter
        - `serviceToRespondToRecord` = serviceId + serviceParameter
            (serviceId is mandatory to be present if the SubFunction parameter is not equal t0 RepostActivatedEvents, 
            stopResponseOnEvent, startResponseOnEvent, clearResponseOnEvent)
    """

    _sid = 0x86
    _isResponse = False

    # sub-function = storageState (bit 6) + parameter (bit 5 to 0)
    # storageState
    doNotStoreEvent = 0x00
    storeEvent = 0x01

    # parameter
    stopResponseOnEvent = 0x00
    onDTCStatusChange = 0x01
    onChangeOfDataIdentifier = 0x03
    reportActivatedEvents = 0x04
    startResponseOnEvent = 0x05
    clearResponseOnEvent = 0x06
    onComparisonOfValues = 0x07
    reportMostRecentDtcOnStatusChange = 0x08
    reportDTCRecordInformationOnDtcStatusChange = 0x09

    def __init__(self, subfn: int = 0x00, data: bytes = b''):
        super().__init__()
        self._hasSubfn = True
        self._hasDID = False
        self._hasData = True
        self._dataSize = len(data)
        self._dataSizeCanChange = True

        self.subfn = subfn
        self.data = data


class ResponseOnEventResponse(UDSMessage):
    """
    Response On Event (Response)
    - `sid` = 0xC6
    - `did` = eventType + numberOfIdentifiedEvents + eventWindowTime
    - `data` = eventTypeRecord + serviceToRespondToRecord + other data depends on subfn
        - `eventTypeRecord` = eventTypeParameter
        - `serviceToRespondToRecord` = serviceId + serviceParameter
    """

    _sid = 0xC6
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
