from . import UDSMessage


class ReadDTCInformationRequest(UDSMessage):
    """
    Read DTC information (Request)
    - `sid` = 0x19
    - `subfn` = reportType
    - `data` => depends on subfn
    """

    _sid = 0x19
    _isResponse = False

    # sub-function IDs, for convenience:
    reportNumberOfDTCByStatusMask = 0x01
    reportDTCByStatusMask = 0x02
    reportDTCSnapshotIdentification = 0x03
    reportDTCSnapshotRecordByDTCNumber = 0x04
    reportDTCStoredDataByRecordNumber = 0x05
    reportDTCExtDataRecordByDTCNumber = 0x06
    reportDTCNumberOfDTCBySecerityMaskRecord = 0x07
    reportDTCBySeverityMaskRecord = 0x08
    reportSeverityInformationOfDTC = 0x09
    reportSupportedDTC = 0x0A
    reposrtFirstTestFailedDTC = 0x0B
    reportFirstConfirmedDTC = 0x0C
    reportMostRecentTestFailedDTC = 0x0D
    reportMostRecentConfirmedDTC = 0x0E
    reportDTCFaultDetectionCounter = 0x14
    reportDTCWithPermanentStatus = 0x15
    reportDTCExtDataRecordByRecordNumber = 0x16
    reportUserDefMemoryDTCByStatusMask = 0x17
    reportUserDefMemoryDTCSnapshotRecordByDTCNumber = 0x18
    reportUserDefMemoryDTCExtDataRecordByDTCNumber = 0x19
    reportDTCExtendedDataRecordIdentification = 0x1A
    reportWWHOBDDTCByMaskRecord = 0x42
    reportWWHOBDDTCWithPermanentStatus = 0x55
    reportDTCInformationByDTCReadinessGroupIdentifer = 0x56

    def __init__(self, subfn: int = reportNumberOfDTCByStatusMask, data: bytes = b''):
        super().__init__()
        self._hasSubfn = True
        self._hasDID = False
        self._hasData = True
        self._dataSize = len(data)
        self._dataSizeCanChange = True

        self.subfn = subfn
        self.data = data


class ReadDTCInformationResponse(UDSMessage):
    """
    Read DTC Information (Response)
    - `sid` = 0x59
    - `subfn` = reportType
    - `data` => depends on subfn
    """

    _sid = 0x59
    _isResponse = True

    # sub-function IDs, for convenience:
    reportNumberOfDTCByStatusMask = 0x01
    reportDTCByStatusMask = 0x02
    reportDTCSnapshotIdentification = 0x03
    reportDTCSnapshotRecordByDTCNumber = 0x04
    reportDTCStoredDataByRecordNumber = 0x05
    reportDTCExtDataRecordByDTCNumber = 0x06
    reportDTCNumberOfDTCBySecerityMaskRecord = 0x07
    reportDTCBySeverityMaskRecord = 0x08
    reportSeverityInformationOfDTC = 0x09
    reportSupportedDTC = 0x0A
    reposrtFirstTestFailedDTC = 0x0B
    reportFirstConfirmedDTC = 0x0C
    reportMostRecentTestFailedDTC = 0x0D
    reportMostRecentConfirmedDTC = 0x0E
    reportDTCFaultDetectionCounter = 0x14
    reportDTCWithPermanentStatus = 0x15
    reportDTCExtDataRecordByRecordNumber = 0x16
    reportUserDefMemoryDTCByStatusMask = 0x17
    reportUserDefMemoryDTCSnapshotRecordByDTCNumber = 0x18
    reportUserDefMemoryDTCExtDataRecordByDTCNumber = 0x19
    reportDTCExtendedDataRecordIdentification = 0x1A
    reportWWHOBDDTCByMaskRecord = 0x42
    reportWWHOBDDTCWithPermanentStatus = 0x55
    reportDTCInformationByDTCReadinessGroupIdentifer = 0x56

    def __init__(self, subfn: int = reportNumberOfDTCByStatusMask, data: bytes = b''):
        super().__init__()
        self._hasSubfn = True
        self._hasDID = False
        self._hasData = True
        self._dataSize = len(data)
        self._dataSizeCanChange = True

        self.subfn = subfn
        self.data = data
