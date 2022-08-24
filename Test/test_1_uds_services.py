from calendar import c
from re import A, I, sub
from statistics import mode
from tkinter import W
from unittest.case import _AssertRaisesContext

import pytest
from RP1210.UDS import *

from RP1210 import sanitize_msg_param

###########################################################################################
# DiagnosticSessionControl ################################################################
###########################################################################################
#region DiagnosticSessionControl

def DiagnosticSessionControlRequest_testActions(msg : DiagnosticSessionControlRequest, subfn = 0x01):
    """
    Runs default test actions for subclass.
    
    msg properties must match those tested:
    - sid = 0x10
    - subfn = default or 0x01
    """
    assert isinstance(msg, DiagnosticSessionControlRequest)
    assert msg.sid == 0x10
    assert not msg.isResponse()
    assert msg.isRequest()
    assert msg.hasSubfn()
    assert not msg.hasDID()
    assert not msg.hasData()
    assert msg.subfn == subfn
    assert msg.value == 0
    msg.subfn = 0x02
    assert msg.subfn == DiagnosticSessionControlRequest.programmingSession

def test_DiagnosticSessionControlRequest_fromSID():
    msg = UDSMessage.fromSID(0x10)
    DiagnosticSessionControlRequest_testActions(msg)

def test_DiagnosticSessionControlRequest_fromSID_subclass():
    msg = DiagnosticSessionControlRequest.fromSID(0x10)
    DiagnosticSessionControlRequest_testActions(msg)

def test_DiagnosticSessionControlRequest_fromMessageData():
    data = b'\x10\x01'
    msg = UDSMessage.fromMessageData(data)
    DiagnosticSessionControlRequest_testActions(msg)

def test_DiagnosticSessionControlRequest_fromMessageData_subclass():
    data = b'\x10\x03'
    msg = DiagnosticSessionControlRequest.fromMessageData(data)
    DiagnosticSessionControlRequest_testActions(msg, subfn=0x03)

def test_DiagnosticSessionControlRequest():
    msg = DiagnosticSessionControlRequest()
    DiagnosticSessionControlRequest_testActions(msg)

def DiagnosticSessionControlResponse_testActions(msg : DiagnosticSessionControlResponse, subfn = 0x01,
        data = None):
    if data is None:
        data = BYTE_STUFFING_VALUE * msg.dataSize()
    assert isinstance(msg, DiagnosticSessionControlResponse)
    assert msg.sid == 0x50
    assert msg.isResponse()
    assert not msg.isRequest()
    assert msg.hasSubfn()
    assert not msg.hasDID()
    assert msg.hasData()
    assert msg.dataSize() == 4
    assert not msg.dataSizeCanChange()
    assert msg.subfn == subfn
    msg.subfn = 0x02
    assert msg.subfn == DiagnosticSessionControlResponse.programmingSession
    assert msg.data == data
    msg.data = b'\xFF'
    assert msg.data == b'\xFF' + BYTE_STUFFING_VALUE * (msg.dataSize() - 1)

def test_DiagnosticSessionControlResponse_fromSID():
    msg = UDSMessage.fromSID(0x50)
    DiagnosticSessionControlResponse_testActions(msg)

def test_DiagnosticSessionControlResponse_fromSID_subclass():
    msg = DiagnosticSessionControlResponse.fromSID(0x50)
    DiagnosticSessionControlResponse_testActions(msg)

def test_DiagnosticSessionControlResponse_fromMessageData():
    data = b'\x50\x02\x11\x22\x33\x44'
    msg = UDSMessage.fromMessageData(data)
    DiagnosticSessionControlResponse_testActions(msg, subfn=0x02, data=b'\x11\x22\x33\x44')

def test_DiagnosticSessionControlResponse_fromMessageData_noData():
    data = b'\x50\x02'
    msg = UDSMessage.fromMessageData(data)
    DiagnosticSessionControlResponse_testActions(msg, subfn=0x02)

def test_DiagnosticSessionControlResponse():
    msg = DiagnosticSessionControlResponse()
    DiagnosticSessionControlResponse_testActions(msg)

#endregion

###########################################################################################
# ECUReset ################################################################################
###########################################################################################
#region ECUReset
def ECUResetRequest_testActions(msg : ECUResetRequest, subfn=0x01):
    assert msg.sid == 0x11
    assert msg.hasSubfn()
    assert not msg.hasDID()
    assert not msg.hasData()
    assert msg.subfn == subfn
    assert msg.raw == b'\x11' + sanitize_msg_param(subfn)

def test_ECUResetRequest():
    subfn = 0x02
    msg = ECUResetRequest(subfn=subfn)
    ECUResetRequest_testActions(msg, subfn)

def test_ECUResetRequest_fromSID():
    msg = UDSMessage.fromSID(0x11)
    ECUResetRequest_testActions(msg)

def test_ECUResetRequest_fromMessageData():
    data = b'\x11\x02'
    msg = UDSMessage.fromMessageData(data)
    ECUResetRequest_testActions(msg, 0x02)

def ECUResetResponse_testActions(msg : ECUResetResponse, subfn = 0x01, data = b''):
    assert msg.sid == 0x51
    assert msg.hasSubfn()
    assert not msg.hasDID()
    assert msg.data == data
    if subfn == 0x04:
        assert msg.hasData()
        assert msg.dataSize() == 1
        assert msg.powerDownTime == int.from_bytes(data, 'big')
        msg.powerDownTime = 0xFE
        assert msg.powerDownTime == 0xFE
        assert msg.data == b'\xFE'
    else:
        assert not msg.hasData()
        assert msg.powerDownTime is None
    assert not msg.dataSizeCanChange()
    assert msg.subfn == subfn
    assert msg.raw == b'\x51' + sanitize_msg_param(subfn, 1) + msg.data
    msg.subfn = b'\x05'
    assert msg.subfn == 0x05

def test_ECUResetResponse():
    msg = ECUResetResponse()
    ECUResetResponse_testActions(msg)

def test_ECUResetResponse_0x04():
    msg = ECUResetResponse(0x04, data=b'\x02')
    ECUResetResponse_testActions(msg, 0x04, b'\x02')

def test_ECUResetResponse_fromSID():
    msg = UDSMessage.fromSID(0x51)
    ECUResetResponse_testActions(msg)

def test_ECUResetResponse_0x04_fromMessageData():
    data = b'\x51\x04\x11'
    msg = UDSMessage.fromMessageData(data)
    ECUResetResponse_testActions(msg, 0x04, b'\x11')

#endregion

###########################################################################################
# WriteDataByIdentifier ################################################################
###########################################################################################
#region WriteDataByIdentifier
def WriteDataByIdentifierRequest_testActions(msg: WriteDataByIdentifierRequest, did: int = 0, data: bytes = b''):
    assert isinstance(msg, WriteDataByIdentifierRequest)
    assert msg.sid == 0x2E
    assert not msg.hasSubfn()
    assert msg.hasDID()
    assert msg.hasData()
    assert msg.dataSize() == len(data)
    assert msg.dataSizeCanChange()
    assert msg.did == did
    assert msg.data == data

def test_WriteDataByIdentifierRequest():
    msg = WriteDataByIdentifierRequest()
    WriteDataByIdentifierRequest_testActions(msg)

def test_WriteDataByIdentifierRequest_fromSID():
    msg = UDSMessage.fromSID(0x2E)
    WriteDataByIdentifierRequest_testActions(msg)

def test_WriteDataByIdentifierRequest_DID():
    did = 8192
    msg = WriteDataByIdentifierRequest(did = did)
    WriteDataByIdentifierRequest_testActions(msg, did = did)

def test_WriteDataByIdentifierRequest_Data():
    data = b'\xEA\x53\x11\x04'
    msg = WriteDataByIdentifierRequest(data = data)
    WriteDataByIdentifierRequest_testActions(msg, data = data)

def test_WriteDataByIdentifierRequest_DIDAndData():
    did = 8376
    data = b'\x32\x02\xA5'
    msg = WriteDataByIdentifierRequest(did = did, data = data)
    WriteDataByIdentifierRequest_testActions(msg, did=did, data=data)

def test_WriteDataByIdentifierRequest_dataIdentifierAndDataRecord():
    did = 8470
    data = b'x11'
    msg1 = WriteDataByIdentifierRequest()
    msg2 = WriteDataByIdentifierRequest(did, data)
    msg1.dataIdentifier = did
    msg1.dataRecord = data
    assert msg1.did == msg1.dataIdentifier == msg2.did == msg2.dataIdentifier == did
    assert msg1.data == msg1.dataRecord == msg2.data == msg2.dataRecord == data

def WriteDataByIdentifierResponse_testActions(msg: WriteDataByIdentifierRequest, did: int = 0):
    assert isinstance(msg, WriteDataByIdentifierResponse)
    assert msg.sid == 0x6E
    assert not msg.hasSubfn()
    assert msg.hasDID()
    assert not msg.hasData()
    assert msg.did == did

def test_WriteDataByIdentifierResponse():
    msg = WriteDataByIdentifierResponse()
    WriteDataByIdentifierResponse_testActions(msg)

def test_WriteDataByIdentifierResponse_fromSID():
    msg = UDSMessage.fromSID(0x6E)
    WriteDataByIdentifierResponse_testActions(msg)

def test_WriteDataByIdentifierResponse_fromMessageData():
    did = 8472
    msg = UDSMessage.fromMessageData(b'n!\x18')
    WriteDataByIdentifierResponse_testActions(msg, did)

def test_WriteDataByIdentifierResponse_dataIdentifierAndDataRecord():
    did = 8470
    data = b'x11'
    msg1 = WriteDataByIdentifierResponse()
    msg1.dataIdentifier = did
    msg1.dataRecord = data
    assert msg1.did == msg1.dataIdentifier == did
#endregion

###########################################################################################
# ReadDataByIdentifier ################################################################
###########################################################################################
#region ReadDataByIdentifier
def ReadDataByIdentifierRequest_testActions(msg: ReadDataByIdentifierRequest, did: int = 0):
    assert isinstance(msg, ReadDataByIdentifierRequest)
    assert msg.sid == 0x22
    assert not msg.hasSubfn()
    assert msg.hasDID()
    assert not msg.hasData()
    assert msg.did == did

def test_ReadDataByIdentifierRequest():
    msg = ReadDataByIdentifierRequest()
    ReadDataByIdentifierRequest_testActions(msg)

def test_ReadDataByIdentifierRequest_fromSID():
    msg = UDSMessage.fromSID(0x22)
    ReadDataByIdentifierRequest_testActions(msg)

def test_ReadDataByIdentifierRequest_DID():
    did = 8427
    msg = ReadDataByIdentifierRequest(did)
    ReadDataByIdentifierRequest_testActions(msg, did)

def ReadDataByIdentifierResponse_testActions(msg: ReadDataByIdentifierResponse, did: int = 0, data : bytes = b''):
    assert isinstance(msg, ReadDataByIdentifierResponse)
    assert msg.sid == 0x62
    assert not msg.hasSubfn()
    assert msg.hasDID()
    assert msg.hasData()
    assert msg.dataSize() == len(data)
    assert msg.dataSizeCanChange()
    assert msg.did == did
    assert msg.data == data

def test_ReadDataByIdentifierResponse():
    msg = ReadDataByIdentifierResponse()
    ReadDataByIdentifierResponse_testActions(msg)

def test_ReadDataByIdentifierResponse_fromSID():
    msg = UDSMessage.fromSID(0x62)
    ReadDataByIdentifierResponse_testActions(msg)

def test_ReadDataByIdentifierResponse_DIDAndData():
    did = 8384
    data = b'\x33\x42\x76'
    msg = ReadDataByIdentifierResponse(did, data)
    ReadDataByIdentifierResponse_testActions(msg, did, data)

def test_ReadDataByIdentifierResponse_Raw():
    did = 8220
    data = b'\x11'
    msg = ReadDataByIdentifierResponse(did, data)
    raw = msg.raw
    assert b'b \x1c\x11' == raw
#endregion

###########################################################################################
# SecurityAccess ################################################################
###########################################################################################
#region SecurityAccess
def SecurityAccessRequest_testActions(msg: SecurityAccessRequest, subfn = 0x01, data:bytes = b''):
    assert isinstance(msg, SecurityAccessRequest)
    assert msg.sid == 0x27
    assert msg.hasSubfn()
    assert not msg.hasDID()
    assert msg.hasData()
    assert msg.dataSize() == len(data)
    assert msg.dataSizeCanChange()
    assert msg.subfn == subfn
    assert msg.data == data

def test_SecurityAccessRequest():
    msg = SecurityAccessRequest()
    SecurityAccessRequest_testActions(msg)

def test_SecurityAccessRequest_fromSID():
    msg = UDSMessage.fromSID(0x27)
    SecurityAccessRequest_testActions(msg)

def test_SecurityAccessRequest_SubfnAndData():
    subfn = 0x02
    data = b'\xAB\xCD'
    msg = SecurityAccessRequest(subfn, data)
    SecurityAccessRequest_testActions(msg, subfn, data)

def SecurityAccessResponse_testActions(msg: SecurityAccessResponse, subfn = 0x01, data: bytes = b''):
    assert isinstance(msg, SecurityAccessResponse)
    assert msg.sid == 0x67
    assert msg.hasSubfn()
    assert not msg.hasDID()
    assert msg.hasData()
    assert msg.dataSize() == len(data)
    assert msg.dataSizeCanChange()
    assert msg.subfn == subfn
    assert msg.data == data

def test_SecurityAccessResponse():
    msg = SecurityAccessResponse()
    SecurityAccessResponse_testActions(msg)

def test_SecurityAccessResponse_fromSID():
    msg = UDSMessage.fromSID(0x67)
    SecurityAccessResponse_testActions(msg)

def test_SecurityAccessResponse_SubfnAndData():
    subfn = 0x03
    data = b'\xAB\xCD'
    msg = SecurityAccessResponse(subfn, data)
    SecurityAccessResponse_testActions(msg, subfn, data)
#endregion

###########################################################################################
# RequestDownload ################################################################
###########################################################################################
#region RequestDownload
def RequestDownloadRequest_testActions(msg: RequestDownloadRequest, dfid: bytes = b'\x00', alfid: bytes = b'\x00', maddr: bytes = b'', msize: bytes = b'', autoALFID: bool = True):
    assert isinstance(msg, RequestDownloadRequest)
    assert msg.sid == 0x34
    assert not msg.hasSubfn()
    assert not msg.hasDID()
    assert msg.hasData()
    assert msg.dataSize() == len(dfid + alfid + maddr + msize)
    assert msg.dataSizeCanChange()
    assert msg.dfid == int.from_bytes(dfid, 'big')
    if autoALFID is False:
        assert msg.alfid == int.from_bytes(alfid, 'big')
    assert msg.maddr == int.from_bytes(maddr, 'big')
    assert msg.msize == int.from_bytes(msize, 'big')
    assert msg.data == dfid + alfid + maddr + msize

def test_RequestDownloadRequest():
    msg = RequestDownloadRequest()
    RequestDownloadRequest_testActions(msg)

def test_RequestDownloadRequest_fromSID():
    msg = UDSMessage.fromSID(0x34)
    RequestDownloadRequest_testActions(msg)

def test_RequestDownloadRequest_Data():
    dfid = b'\x33'
    alfid = b'\x34'
    maddr = b'\xBB\xCC'
    msize = b'\xDD\xEE'
    autoALFID = False
    msg = RequestDownloadRequest(dfid=dfid, alfid=alfid, maddr=maddr, msize=msize, autoALFID=autoALFID)
    RequestDownloadRequest_testActions(msg=msg, dfid=dfid, alfid=alfid, maddr=maddr, msize=msize, autoALFID=autoALFID)

    # Testinng with autoALFID
    dfid = b'\x00'
    alfid = b'\x22'
    maddr = b'\xBB\xCC'
    msize = b'\xDD\xEE'
    autoALFID = True
    msg = RequestDownloadRequest(dfid=dfid, alfid=alfid, maddr=maddr, msize=msize, autoALFID=autoALFID)
    RequestDownloadRequest_testActions(msg=msg, dfid=dfid, alfid=alfid, maddr=maddr, msize=msize, autoALFID=autoALFID)

def test_RequestDownloadRequest_Errors():
    dfid = b'\x00'
    alfid = b'\x22'
    maddr = b'\xBB\xCC\xBB\xCC\xBB\xCC\xBB\xCC\xBB\xCC\xBB\xCC\xBB\xCC\xBB\xCC'
    msize = b'\xDD\xEE'
    autoALFID = True
    with pytest.raises(ValueError):
        msg = RequestDownloadRequest(dfid=dfid, alfid=alfid, maddr=maddr, msize=msize, autoALFID=autoALFID)
        RequestDownloadRequest_testActions(msg=msg, dfid=dfid, alfid=alfid, maddr=maddr, msize=msize, autoALFID=autoALFID)

    dfid = b'\x00'
    alfid = b'\x22'
    maddr = b'\xDD\xEE'
    msize = b'\xBB\xCC\xBB\xCC\xBB\xCC\xBB\xCC\xBB\xCC\xBB\xCC\xBB\xCC\xBB\xCC'
    autoALFID = True
    with pytest.raises(ValueError):
        msg = RequestDownloadRequest(dfid=dfid, alfid=alfid, maddr=maddr, msize=msize, autoALFID=autoALFID)
        RequestDownloadRequest_testActions(msg=msg, dfid=dfid, alfid=alfid, maddr=maddr, msize=msize, autoALFID=autoALFID)

def RequestDownloadResponse_testActions(msg: RequestDownloadResponse, data: bytes = b''):
    assert isinstance(msg, RequestDownloadResponse)
    assert msg.sid == 0x74
    assert not msg.hasSubfn()
    assert not msg.hasDID()
    assert msg.hasData()
    assert msg.dataSize() == len(data)
    assert msg.dataSizeCanChange()
    assert msg.data == data
    if len(data) >= 2:
        assert msg.lfid == data[0]
        assert msg.mnrob == int.from_bytes(data[1:], 'big')
        msg.lfid = 32
        msg.mnrob = 128
        assert msg.lfid == 32
        assert msg.mnrob == 128


def test_RequestDownloadResponse():
    msg = RequestDownloadResponse()
    RequestDownloadResponse_testActions(msg=msg)

    msg = RequestDownloadResponse(data=b'\x30\x12\x34\x56')
    RequestDownloadResponse_testActions(msg=msg, data=b'\x30\x12\x34\x56')

def test_RequestDownloadResponse_fromSID():
    msg = UDSMessage.fromSID(0x74)
    RequestDownloadResponse_testActions(msg=msg)

#endregion

###########################################################################################
# LinkControl ################################################################
###########################################################################################
#region LinkControl
def LinkControlRequest_testActions(msg: LinkControlRequest, subfn: int = 0x00, data: bytes = b''):
    assert isinstance(msg, LinkControlRequest)
    assert msg.sid == 0x87
    assert msg.hasSubfn()
    assert not msg.hasDID()
    if subfn != 0x03:
        assert msg.hasData()
        assert msg.dataSize() == len(data)
        assert not msg.dataSizeCanChange()
        assert msg.data == data
    else:
        assert not msg.hasData()
    assert msg.subfn == subfn

def test_LinkControlRequest():
    msg = LinkControlRequest()
    LinkControlRequest_testActions(msg)

def test_LinkControlRequest_fromSID():
    msg = UDSMessage.fromSID(0x87)
    LinkControlRequest_testActions(msg)

def test_LinkControlRequest_transitionMode():
    subfn = 0x03
    data = b'\x01'
    msg = LinkControlRequest(subfn, data)
    LinkControlRequest_testActions(msg, subfn, data)

def LinkControlResponse_testActions(msg: LinkControlResponse, subfn: int = 0x00):
    assert isinstance(msg, LinkControlResponse)
    assert msg.sid == 0xC7
    assert msg.hasSubfn()
    assert not msg.hasDID()
    assert not msg.hasData()
    assert msg.subfn == subfn

def test_LinkControlResponse():
    msg = LinkControlResponse()
    LinkControlResponse_testActions(msg)

def test_LinkControlResponse_fromSID():
    msg = UDSMessage.fromSID(0xC7)
    LinkControlResponse_testActions(msg)

def test_LinkControlResponse_transitionMode():
    subfn = 0x03
    msg = LinkControlResponse(subfn)
    LinkControlResponse_testActions(msg, subfn)

#endregion

###########################################################################################
# CommunicationControl ################################################################
###########################################################################################
#region CommunicationControl
def CommunicationControlRequest_testActions(msg: CommunicationControlRequest, subfn: int = 0, comtype: bytes = b'', high_node_id: bytes = b'', low_node_id: bytes = b''):
    assert isinstance(msg, CommunicationControlRequest)
    assert msg.sid == 0x28
    assert msg.hasSubfn()
    assert not msg.hasDID()
    assert msg.hasData()
    if subfn in {0x04, 0x05}:
        assert msg.dataSize() == len(comtype + high_node_id + low_node_id)
        assert msg.data == comtype + high_node_id + low_node_id
    else:
        assert msg.dataSize() == len(comtype)
        assert msg.data == comtype
    assert not msg.dataSizeCanChange()
    assert msg.subfn == subfn

def test_CommunicationControlRequest():
    msg = CommunicationControlRequest()
    CommunicationControlRequest_testActions(msg)

def test_CommunicationControlRequest_fromSID():
    msg = UDSMessage.fromSID(0x28)
    CommunicationControlRequest_testActions(msg)

def test_CommunicationControlRequest_0x01():
    subfn = 0x01
    comtype = b'\x11'
    msg = CommunicationControlRequest(subfn, comtype)
    CommunicationControlRequest_testActions(msg, subfn, comtype)

def test_CommunicationControlRequest_0x04():
    subfn = 0x04
    comtype = b'\x33'
    high_node_id = b'\x88'
    low_node_id = b'\x66'
    msg = CommunicationControlRequest(subfn, comtype, high_node_id, low_node_id)
    CommunicationControlRequest_testActions(msg, subfn, comtype, high_node_id, low_node_id)

def CommunicationControlResponse_testActions(msg: CommunicationControlResponse, subfn: int = 0):
    assert isinstance(msg, CommunicationControlResponse)
    assert msg.sid == 0x68
    assert msg.hasSubfn()
    assert not msg.hasDID()
    assert not msg.hasData()
    assert msg.subfn == subfn
    
def test_CommunicationControlResponse():
    msg = CommunicationControlResponse()
    CommunicationControlResponse_testActions(msg)

def test_CommunicationControlResponse_fromSID():
    msg = UDSMessage.fromSID(0x68)
    CommunicationControlResponse_testActions(msg)

def test_CommunicationControlResponse_0x01():
    subfn = 0x01
    msg = CommunicationControlResponse(subfn)
    CommunicationControlResponse_testActions(msg, subfn)

def test_CommunicationControlResponse_0x04():
    subfn = 0x04
    msg = CommunicationControlResponse(subfn)
    CommunicationControlResponse_testActions(msg, subfn)

#endregion

###########################################################################################
# ClearDiagnosticInformation ################################################################
###########################################################################################
#region ClearDiagnosticInformation
def ClearDiagnosticInformationRequest_testActions(msg: ClearDiagnosticInformationRequest, data: bytes = b''):
    assert isinstance(msg, ClearDiagnosticInformationRequest)
    assert msg.sid == 0x14
    assert not msg.hasSubfn()
    assert not msg.hasDID()
    assert msg.hasData()
    assert msg.dataSize() == len(data)
    assert msg.dataSizeCanChange()
    assert msg.data == data

def test_ClearDiagnosticInformationRequest():
    msg = ClearDiagnosticInformationRequest()
    ClearDiagnosticInformationRequest_testActions(msg)

def test_ClearDiagnosticInformationRequest_fromSID():
    msg = UDSMessage.fromSID(0x14)
    ClearDiagnosticInformationRequest_testActions(msg)

def test_ClearDiagnosticInformationRequest_data():
    data = b'\xA3\xA2'
    msg = ClearDiagnosticInformationRequest(data)
    ClearDiagnosticInformationRequest_testActions(msg, data)

def ClearDiagnosticInformationResponse_testActions(msg: ClearDiagnosticInformationResponse):
    assert isinstance(msg, ClearDiagnosticInformationResponse)
    assert msg.sid == 0x54
    assert not msg.hasSubfn()
    assert not msg.hasDID()
    assert not msg.hasData()

def test_ClearDiagnosticInformationResponse():
    msg = ClearDiagnosticInformationResponse()
    ClearDiagnosticInformationResponse_testActions(msg)

def test_ClearDiagnosticInformationResponse_fromSID():
    msg = UDSMessage.fromSID(0x54)
    ClearDiagnosticInformationResponse_testActions(msg)

#endregion

###########################################################################################
# InputOutputControlByIdentifier ################################################################
###########################################################################################
#region InputOutputControlByIdentifier
def InputOutputControlByIdentifierRequest_testActions(msg: InputOutputControlByIdentifierRequest, did: int = 0, data: bytes = b''):
    assert isinstance(msg , InputOutputControlByIdentifierRequest)
    assert msg.sid == 0x2F
    assert not msg.hasSubfn()
    assert msg.hasDID()
    assert msg.hasData()
    assert msg.dataSize() == len(data)
    assert msg.dataSizeCanChange()
    assert msg.did == did
    assert msg.data == data

def test_InputOutputControlByIdentifierRequest():
    msg = InputOutputControlByIdentifierRequest()
    InputOutputControlByIdentifierRequest_testActions(msg)

def test_InputOutputControlByIdentifierRequest_fromSID():
    msg = UDSMessage.fromSID(0x2F)
    InputOutputControlByIdentifierRequest_testActions(msg)

def test_InputOutputControlByIdentifierRequest_didAndData():
    did = 8400
    data = b'\xCC'
    msg = InputOutputControlByIdentifierRequest(did, data)
    InputOutputControlByIdentifierRequest_testActions(msg, did, data)

def InputOutputControlByIdentifierResponse_testActions(msg: InputOutputControlByIdentifierResponse, did: int = 0, data: bytes = b''):
    assert isinstance(msg , InputOutputControlByIdentifierResponse)
    assert msg.sid == 0x6F
    assert not msg.hasSubfn()
    assert msg.hasDID()
    assert msg.hasData()
    assert msg.dataSize() == len(data)
    assert msg.dataSizeCanChange()
    assert msg.did == did
    assert msg.data == data

def test_InputOutputControlByIdentifierResponse():
    msg = InputOutputControlByIdentifierResponse()
    InputOutputControlByIdentifierResponse_testActions(msg)

def test_InputOutputControlByIdentifierResponse_fromSID():
    msg = UDSMessage.fromSID(0x6F)
    InputOutputControlByIdentifierResponse_testActions(msg)

def test_InputOutputControlByIdentifierResponse_didAndData():
    did = 8400
    data = b'\xCC'
    msg = InputOutputControlByIdentifierResponse(did, data)
    InputOutputControlByIdentifierResponse_testActions(msg, did, data)
#endregion

###########################################################################################
# ReadDTCInformation ################################################################
###########################################################################################
#region ReadDTCInformation
def ReadDTCInformationRequest_testActions(msg: ReadDTCInformationRequest, subfn: int = 0x01, data: bytes = b''):
    assert isinstance(msg , ReadDTCInformationRequest)
    assert msg.sid == 0x19
    assert msg.hasSubfn()
    assert not msg.hasDID()
    assert msg.hasData()
    assert msg.dataSize() == len(data)
    assert msg.dataSizeCanChange()
    assert msg.subfn == subfn
    assert msg.data == data

def test_ReadDTCInformationRequest():
    msg = ReadDTCInformationRequest()
    ReadDTCInformationRequest_testActions(msg)

def test_ReadDTCInformationRequest_fromSID():
    msg = UDSMessage.fromSID(0x19)
    ReadDTCInformationRequest_testActions(msg)

def test_ReadDTCInformationRequest_reportNumberOfDTCByStatusMask():
    subfn = 0x01
    data = b'\x25'
    msg = ReadDTCInformationRequest(subfn, data)
    ReadDTCInformationRequest_testActions(msg, subfn, data)

def test_ReadDTCInformationRequest_reportDTCSnapshotIdentification():
    subfn = 0x03
    data= b'\xA1\xA2\xA3\xA4'
    msg = ReadDTCInformationRequest(subfn, data)
    ReadDTCInformationRequest_testActions(msg, subfn, data)

def ReadDTCInformationResponse_testActions(msg: ReadDTCInformationResponse, subfn: int = 0x01, data: bytes = b''):
    assert isinstance(msg , ReadDTCInformationResponse)
    assert msg.sid == 0x59
    assert msg.hasSubfn()
    assert not msg.hasDID()
    assert msg.hasData()
    assert msg.dataSize() == len(data)
    assert msg.dataSizeCanChange()
    assert msg.subfn == subfn
    assert msg.data == data

def test_ReadDTCInformationResponse():
    msg = ReadDTCInformationResponse()
    ReadDTCInformationResponse_testActions(msg)

def test_ReadDTCInformationResponse_fromSID():
    msg = UDSMessage.fromSID(0x59)
    ReadDTCInformationResponse_testActions(msg)

def test_ReadDTCInformationResponse_reportNumberOfDTCBySeverityMaskRecord():
    subfn = 0x07
    data = b'\xB5\x00\x01\x02\x03\x04\xF1\x01'
    msg = ReadDTCInformationResponse(subfn, data)
    ReadDTCInformationResponse_testActions(msg, subfn, data)

def test_ReadDTCInformationResponse_reportFirstTestFailedDTC():
    subfn = 0x08
    data = b'\xE3\x04\xF3\x25\x83\x77\x57'
    msg = ReadDTCInformationResponse(subfn, data)
    ReadDTCInformationResponse_testActions(msg, subfn, data)

#endregion

###########################################################################################
# RequestFileTransfer ################################################################
###########################################################################################
#region RequestFileTransfer
def RequestFileTransferRequest_testActions(msg: RequestFileTransferRequest, data: bytes = b''):
    assert isinstance(msg, RequestFileTransferRequest)
    assert msg.sid == 0x38
    assert not msg.hasSubfn()
    assert not msg.hasDID()
    assert msg.hasData()
    assert msg.dataSize() == len(data)
    assert msg.dataSizeCanChange()
    assert msg.data == data

def test_RequestFileTransferRequest():
    msg = RequestFileTransferRequest()
    RequestFileTransferRequest_testActions(msg)

def test_RequestFileTransferRequest_fromSID():
    msg = UDSMessage.fromSID(0x38)
    RequestFileTransferRequest_testActions(msg)

def test_RequestFileTransferRequest_AddFile():
    modeOfOperation = b'\x01'
    filePathAndNameLength = b'\x00\x01'
    filePathAndName = b'\xF6'
    dataFormatIdentifier = b'\x43'
    fileSizeParameterLength = b'\x02'
    fileSizeUncompressed = b'\x34\x21'
    fileSizeUncompressed = b'\xE7\xC4'

    data = modeOfOperation + filePathAndNameLength + filePathAndName + dataFormatIdentifier \
        + fileSizeParameterLength + fileSizeUncompressed + fileSizeUncompressed
    msg = RequestFileTransferRequest(data)
    RequestFileTransferRequest_testActions(msg, data)

def test_RequestFileTransferRequest_DeleteFile():
    modeOfOperation = b'\x01'
    filePathAndNameLength = b'\x00\x01'
    filePathAndName = b'\xF6'

    data = modeOfOperation + filePathAndNameLength + filePathAndName
    msg = RequestFileTransferRequest(data)
    RequestFileTransferRequest_testActions(msg, data)

def RequestFileTransferResponse_testActions(msg: RequestFileTransferResponse, data: bytes = b''):
    assert isinstance(msg, RequestFileTransferResponse)
    assert msg.sid == 0x78
    assert not msg.hasSubfn()
    assert not msg.hasDID()
    assert msg.hasData()
    assert msg.dataSize() == len(data)
    assert msg.dataSizeCanChange()
    assert msg.data == data

def test_RequestFileTransferResponse():
    msg = RequestFileTransferResponse()
    RequestFileTransferResponse_testActions(msg)

def test_RequestFileTransferResponse_fromSID():
    msg = UDSMessage.fromSID(0x78)
    RequestFileTransferResponse_testActions(msg)

def test_RequestFileTransferResponse_ReplaceFile():
    modeOfOperation = b'\x03'
    lengthFormatIdentifier = b'\x02'
    maxNumberOfBlockLength = b'\xD3\x83'
    dataFormatIdentifier = b'\x33\x55'

    data = modeOfOperation + lengthFormatIdentifier + maxNumberOfBlockLength + dataFormatIdentifier
    msg = RequestFileTransferResponse(data)
    RequestFileTransferResponse_testActions(msg, data)

def test_RequestFileTransferResponse_ReadDir():
    modeOfOperation = b'\x05'
    lengthFormatIdentifier = b'\x02'
    maxNumberOfBlockLength = b'\xD3\x83'
    dataFormatIdentifier = b'\x00' # has to be 0x00 if ReadDir
    fileSizeOrDirInfoParameterLength = b'\x01'
    fileSizeUncompressedOrDirInfoLength = b'\x02'

    data = modeOfOperation + lengthFormatIdentifier + maxNumberOfBlockLength + dataFormatIdentifier + \
            fileSizeOrDirInfoParameterLength + fileSizeUncompressedOrDirInfoLength
    msg = RequestFileTransferResponse(data)
    RequestFileTransferResponse_testActions(msg, data)

#endregion

###########################################################################################
# RequestTransferExit ################################################################
###########################################################################################
#region RequestTransferExit
def RequestTransferExitRequest_testActions(msg: RequestTransferExitRequest, data: bytes = b''):
    assert isinstance(msg, RequestTransferExitRequest)
    assert msg.sid == 0x37
    assert not msg.hasSubfn()
    assert not msg.hasDID()
    assert msg.hasData()
    assert msg.dataSize() == len(data)
    assert msg.dataSizeCanChange()
    assert msg.data == data

def test_RequestTransferExitRequest():
    msg = RequestTransferExitRequest()
    RequestTransferExitRequest_testActions(msg)

def test_RequestTransferExitRequest_fromSID():
    msg = UDSMessage.fromSID(0x37)
    RequestTransferExitRequest_testActions(msg)

def test_RequestTransferExitRequest_data():
    data = b'\xE3\xD6\x65'
    msg = RequestTransferExitRequest(data)
    RequestTransferExitRequest_testActions(msg, data)

def RequestTransferExitResponse_testActions(msg: RequestTransferExitResponse, data: bytes = b''):
    assert isinstance(msg, RequestTransferExitResponse)
    assert msg.sid == 0x77
    assert not msg.hasSubfn()
    assert not msg.hasDID()
    assert msg.hasData()
    assert msg.dataSize() == len(data)
    assert msg.dataSizeCanChange()
    assert msg.data == data

def test_RequestTransferExitResponse():
    msg = RequestTransferExitResponse()
    RequestTransferExitResponse_testActions(msg)

def test_RequestTransferExitResponse_fromSID():
    msg = UDSMessage.fromSID(0x77)
    RequestTransferExitResponse_testActions(msg)

def test_RequestTransferExitResponse_data():
    data = b'\xE3\xD6\x65'
    msg = RequestTransferExitResponse(data)
    RequestTransferExitResponse_testActions(msg, data)
#endregion

###########################################################################################
# RequestUpload ################################################################
###########################################################################################
#region RequestUpload
def RequestUploadRequest_testActions(msg: RequestUploadRequest, dfid: bytes = b'\x00', alfid: bytes = b'\x00', maddr: bytes = b'', msize: bytes = b'', autoALFID: bool = True):
    assert isinstance(msg, RequestUploadRequest)
    assert msg.sid == 0x35
    assert not msg.hasSubfn()
    assert not msg.hasDID()
    assert msg.hasData()
    assert msg.dataSize() == len(dfid + alfid + maddr + msize)
    assert msg.dataSizeCanChange()
    assert msg.dfid == int.from_bytes(dfid, 'big')
    if autoALFID is False:
        assert msg.alfid == int.from_bytes(alfid, 'big')
    assert msg.maddr == int.from_bytes(maddr, 'big')
    assert msg.msize == int.from_bytes(msize, 'big')
    assert msg.data == dfid + alfid + maddr + msize

def test_RequestUploadRequest():
    msg = RequestUploadRequest()
    RequestUploadRequest_testActions(msg)

def test_RequestUploadRequest_fromSID():
    msg = UDSMessage.fromSID(0x35)
    RequestUploadRequest_testActions(msg)

def test_RequestUploadRequest_Data():
    dfid = b'\x33'
    alfid = b'\x34'
    maddr = b'\xBB\xCC'
    msize = b'\xDD\xEE'
    autoALFID = False
    msg = RequestUploadRequest(dfid=dfid, alfid=alfid, maddr=maddr, msize=msize, autoALFID=autoALFID)
    RequestUploadRequest_testActions(msg=msg, dfid=dfid, alfid=alfid, maddr=maddr, msize=msize, autoALFID=autoALFID)

    # Testinng with autoALFID
    dfid = b'\x00'
    alfid = b'\x22'
    maddr = b'\xBB\xCC'
    msize = b'\xDD\xEE'
    autoALFID = True
    msg = RequestUploadRequest(dfid=dfid, alfid=alfid, maddr=maddr, msize=msize, autoALFID=autoALFID)
    RequestUploadRequest_testActions(msg=msg, dfid=dfid, alfid=alfid, maddr=maddr, msize=msize, autoALFID=autoALFID)

def test_RequestUploadRequest_Errors():
    dfid = b'\x00'
    alfid = b'\x22'
    maddr = b'\xBB\xCC\xBB\xCC\xBB\xCC\xBB\xCC\xBB\xCC\xBB\xCC\xBB\xCC\xBB\xCC'
    msize = b'\xDD\xEE'
    autoALFID = True
    with pytest.raises(ValueError):
        msg = RequestUploadRequest(dfid=dfid, alfid=alfid, maddr=maddr, msize=msize, autoALFID=autoALFID)
        RequestUploadRequest_testActions(msg=msg, dfid=dfid, alfid=alfid, maddr=maddr, msize=msize, autoALFID=autoALFID)

    dfid = b'\x00'
    alfid = b'\x22'
    maddr = b'\xDD\xEE'
    msize = b'\xBB\xCC\xBB\xCC\xBB\xCC\xBB\xCC\xBB\xCC\xBB\xCC\xBB\xCC\xBB\xCC'
    autoALFID = True
    with pytest.raises(ValueError):
        msg = RequestUploadRequest(dfid=dfid, alfid=alfid, maddr=maddr, msize=msize, autoALFID=autoALFID)
        RequestUploadRequest_testActions(msg=msg, dfid=dfid, alfid=alfid, maddr=maddr, msize=msize, autoALFID=autoALFID)

def RequestUploadResponse_testActions(msg: RequestUploadResponse, data: bytes = b''):
    assert isinstance(msg, RequestUploadResponse)
    assert msg.sid == 0x75
    assert not msg.hasSubfn()
    assert not msg.hasDID()
    assert msg.hasData()
    assert msg.dataSize() == len(data)
    assert msg.dataSizeCanChange()
    assert msg.data == data
    if len(data) >= 2:
        assert msg.lfid == data[0]
        assert msg.mnrob == int.from_bytes(data[1:], 'big')
        msg.lfid = 32
        msg.mnrob = 128
        assert msg.lfid == 32
        assert msg.mnrob == 128

def test_RequestUploadResponse():
    msg = RequestUploadResponse()
    RequestUploadResponse_testActions(msg=msg)

    msg = RequestUploadResponse(data=b'\x30\x12\x34\x56')
    RequestUploadResponse_testActions(msg=msg, data=b'\x30\x12\x34\x56')

def test_RequestUploadResponse_fromSID():
    msg = UDSMessage.fromSID(0x75)
    RequestUploadResponse_testActions(msg=msg)


#endregion

###########################################################################################
# RoutineControl ################################################################
###########################################################################################
#region RoutineControl
def RoutineControlRequest_testActions(msg: RoutineControlRequest, subfn: int = 0x01, did: int = 0, data: bytes = b''):
    assert isinstance(msg, RoutineControlRequest)
    assert msg.sid == 0x31
    assert msg.hasSubfn()
    assert msg.hasDID()
    assert msg.hasData()
    assert msg.dataSize() == len(data)
    assert msg.dataSizeCanChange()
    assert msg.subfn == subfn
    assert msg.did == did
    assert msg.data == data

def test_RoutineControlRequest():
    msg = RoutineControlRequest()
    RoutineControlRequest_testActions(msg)

def test_RoutineControlRequest_fromSID():
    msg = UDSMessage.fromSID(0x31)
    RoutineControlRequest_testActions(msg)

def test_RoutineControlRequest_startRoutine():
    subfn = 0x01
    did = 8411
    data = b'\x31'
    msg = RoutineControlRequest(subfn, did, data)
    RoutineControlRequest_testActions(msg, subfn, did, data)

def RoutineControlResponse_testActions(msg: RoutineControlResponse, subfn: int = 0x01, did: int = 0, data: bytes = b''):
    assert isinstance(msg, RoutineControlResponse)
    assert msg.sid == 0x71
    assert msg.hasSubfn()
    assert msg.hasDID()
    assert msg.hasData()
    assert msg.dataSize() == len(data)
    assert msg.dataSizeCanChange()
    assert msg.subfn == subfn
    assert msg.did == did
    assert msg.data == data

def test_RoutineControlResponse():
    msg = RoutineControlResponse()
    RoutineControlResponse_testActions(msg)

def test_RoutineControlResponse_fromSID():
    msg = UDSMessage.fromSID(0x71)
    RoutineControlResponse_testActions(msg)

def test_RoutineControlResponse_startRoutine():
    subfn = 0x01
    did = 8411
    data = b'\x31'
    msg = RoutineControlResponse(subfn, did, data)
    RoutineControlResponse_testActions(msg, subfn, did, data)
#endregion

###########################################################################################
# TransferData ################################################################
###########################################################################################
#region TransferData
def TransferDataRequest_testActions(msg: TransferDataRequest, data: bytes = b''):
    assert isinstance(msg, TransferDataRequest)
    assert msg.sid == 0x36
    assert not msg.hasSubfn()
    assert not msg.hasDID()
    assert msg.hasData()
    assert msg.dataSize() == len(data)
    assert msg.dataSizeCanChange()
    assert msg.data == data

def test_TransferDataRequest():
    msg = TransferDataRequest()
    TransferDataRequest_testActions(msg)

def test_TransferDataRequest_fromSID():
    msg = UDSMessage.fromSID(0x36)
    TransferDataRequest_testActions(msg)

def test_TransferDataRequest_data():
    data = b'\x46'
    msg = TransferDataRequest(data)
    TransferDataRequest_testActions(msg, data)

def TransferDataResponse_testActions(msg: TransferDataResponse, data: bytes = b''):
    assert isinstance(msg, TransferDataResponse)
    assert msg.sid == 0x76
    assert not msg.hasSubfn()
    assert not msg.hasDID()
    assert msg.hasData()
    assert msg.dataSize() == len(data)
    assert msg.dataSizeCanChange()
    assert msg.data == data

def test_TransferDataResponse():
    msg = TransferDataResponse()
    TransferDataResponse_testActions(msg)

def test_TransferDataResponse_fromSID():
    msg = UDSMessage.fromSID(0x76)
    TransferDataResponse_testActions(msg)

def test_TransferDataResponse_data():
    data = b'\x46'
    msg = TransferDataResponse(data)
    TransferDataResponse_testActions(msg, data)
#endregion

###########################################################################################
# WriteMemoryByAddress ################################################################
###########################################################################################
#region WriteMemoryByAddress
def WriteMemoryByAddressRequest_testActions(msg: WriteMemoryByAddressRequest, did: int = 0, data: bytes = b''):
    assert isinstance(msg, WriteMemoryByAddressRequest)
    assert msg.sid == 0x3D
    assert not msg.hasSubfn()
    assert msg.hasDID()
    assert msg.hasData()
    assert msg.dataSize() == len(data)
    assert msg.dataSizeCanChange()
    assert msg.did == did
    assert msg.data == data

def test_WriteMemoryByAddressRequest():
    msg = WriteMemoryByAddressRequest()
    WriteMemoryByAddressRequest_testActions(msg)

def test_WriteMemoryByAddressRequest_fromSID():
    msg = UDSMessage.fromSID(0x3D)
    WriteMemoryByAddressRequest_testActions(msg)

def test_WriteMemoryByAddressRequest_didAndData():
    did = 20
    data = b'\xFE\x33'
    msg = WriteMemoryByAddressRequest(did, data)
    WriteMemoryByAddressRequest_testActions(msg, did, data)

def WriteMemoryByAddressResponse_testActions(msg: WriteMemoryByAddressResponse, did: int = 0, data: bytes = b''):
    assert isinstance(msg, WriteMemoryByAddressResponse)
    assert msg.sid == 0x7D
    assert not msg.hasSubfn()
    assert msg.hasDID()
    assert msg.hasData()
    assert msg.dataSize() == len(data)
    assert msg.dataSizeCanChange()
    assert msg.did == did
    assert msg.data == data

def test_WriteMemoryByAddressResponse():
    msg = WriteMemoryByAddressResponse()
    WriteMemoryByAddressResponse_testActions(msg)

def test_WriteMemoryByAddressResponse_fromSID():
    msg = UDSMessage.fromSID(0x7D)
    WriteMemoryByAddressResponse_testActions(msg)

def test_WriteMemoryByAddressResponse_didAndData():
    did = 20
    data = b'\x55\x33'
    msg = WriteMemoryByAddressResponse(did, data)
    WriteMemoryByAddressResponse_testActions(msg, did, data)

#endregion

###########################################################################################
# SecuredDataTransmission ################################################################
###########################################################################################
#region SecuredDataTransmission
def SecuredDataTransmissionRequest_testActions(msg: SecuredDataTransmissionRequest, data: bytes = b''):
    assert isinstance(msg, SecuredDataTransmissionRequest)
    assert msg.sid == 0x84
    assert not msg.hasSubfn()
    assert not msg.hasDID()
    assert msg.hasData()
    assert msg.dataSize() == len(data)
    assert msg.dataSizeCanChange()
    assert msg.data == data

def test_SecuredDataTransmissionRequest():
    msg = SecuredDataTransmissionRequest()
    SecuredDataTransmissionRequest_testActions(msg)

def test_SecuredDataTransmissionRequest_fromSID():
    msg = UDSMessage.fromSID(0x84)
    SecuredDataTransmissionRequest_testActions(msg)

def test_SecuredDataTransmissionRequest_data():
    data = b'\x00\x01\x44\xA4\xB2\xD4\xC6\x12\x42\x12\x42'
    msg = SecuredDataTransmissionRequest(data)
    SecuredDataTransmissionRequest_testActions(msg, data)

def SecuredDataTransmissionResponse_testActions(msg: SecuredDataTransmissionResponse, data: bytes = b''):
    assert isinstance(msg, SecuredDataTransmissionResponse)
    assert msg.sid == 0xC4
    assert not msg.hasSubfn()
    assert not msg.hasDID()
    assert msg.hasData()
    assert msg.dataSize() == len(data)
    assert msg.dataSizeCanChange()
    assert msg.data == data

def test_SecuredDataTransmissionResponse():
    msg = SecuredDataTransmissionResponse()
    SecuredDataTransmissionResponse_testActions(msg)

def test_SecuredDataTransmissionResponse_fromSID():
    msg = UDSMessage.fromSID(0xC4)
    SecuredDataTransmissionResponse_testActions(msg)

def test_SecuredDataTransmissionResponse_data():
    data = b'\x00\x02\x73\xE2\xB2\xD4\xC6\x12\x42\xC2\x53'
    msg = SecuredDataTransmissionResponse(data)
    SecuredDataTransmissionResponse_testActions(msg, data)

#endregion

###########################################################################################
# ReadDataByPeriodicIdentifier ################################################################
###########################################################################################
#region ReadDataByPeriodicIdentifier
def ReadDataByPeriodicIdentifierRequest_testActions(msg: ReadDataByPeriodicIdentifierRequest, data: bytes = b''):
    assert isinstance(msg, ReadDataByPeriodicIdentifierRequest)
    assert msg.sid == 0x2A
    assert not msg.hasSubfn()
    assert not msg.hasDID()
    assert msg.hasData()
    assert msg.dataSize() == len(data)
    assert msg.dataSizeCanChange()
    assert msg.data == data

def test_ReadDataByPeriodicIdentifierRequest():
    msg = ReadDataByPeriodicIdentifierRequest()
    ReadDataByPeriodicIdentifierRequest_testActions(msg)

def test_ReadDataByPeriodicIdentifierRequest_fromSID():
    msg = UDSMessage.fromSID(0x2A)
    ReadDataByPeriodicIdentifierRequest_testActions(msg)

def test_ReadDataByPeriodicIdentifierRequest_data():
    data = b'\xFE\x33'
    msg = ReadDataByPeriodicIdentifierRequest(data)
    ReadDataByPeriodicIdentifierRequest_testActions(msg, data)

def ReadDataByPeriodicIdentifierResponse_testActions(msg: ReadDataByPeriodicIdentifierResponse):
    assert isinstance(msg, ReadDataByPeriodicIdentifierResponse)
    assert msg.sid == 0x6A
    assert not msg.hasSubfn()
    assert not msg.hasDID()
    assert not msg.hasData()

def test_ReadDataByPeriodicIdentifierResponse():
    msg = ReadDataByPeriodicIdentifierResponse()
    ReadDataByPeriodicIdentifierResponse_testActions(msg)

def test_ReadDataByPeriodicIdentifierResponse_fromSID():
    msg = UDSMessage.fromSID(0x6A)
    ReadDataByPeriodicIdentifierResponse_testActions(msg)

#endregion

###########################################################################################
# DynamicallyDefineDataIdentifier ################################################################
###########################################################################################
#region DynamicallyDefineDataIdentifier
def DynamicallyDefineDataIdentifierRequest_testActions(msg: DynamicallyDefineDataIdentifierRequest, subfn: int = 1, did: int = 0, data: bytes = b''):
    assert isinstance(msg, DynamicallyDefineDataIdentifierRequest)
    assert msg.sid == 0x2C
    assert msg.hasSubfn()
    assert msg.hasDID()
    if subfn != 0x03:
        assert msg.hasData()
        assert msg.dataSize() == len(data)
        assert msg.dataSizeCanChange()
        assert msg.data == data
    else:
        assert not msg.hasData()
    assert msg.subfn == subfn
    assert msg.did == did

def test_DynamicallyDefineDataIdentifierRequest():
    msg = DynamicallyDefineDataIdentifierRequest()
    DynamicallyDefineDataIdentifierRequest_testActions(msg)

def test_DynamicallyDefineDataIdentifierRequest_fromSID():
    msg = UDSMessage.fromSID(0x2C)
    DynamicallyDefineDataIdentifierRequest_testActions(msg)

def test_DynamicallyDefineDataIdentifierRequest_defineByIdentifier():
    subfn = 0x01
    did = 0xF352
    data = b'\xFE\x33\x43\x24\x53\xD5\x35\xF4'
    msg = DynamicallyDefineDataIdentifierRequest(subfn, did, data)
    DynamicallyDefineDataIdentifierRequest_testActions(msg, subfn, did, data)

def test_DynamicallyDefineDataIdentifierRequest_clearDynamicallyDefineddataIdentifier():
    subfn = 0x03
    did = 0xF301
    msg = DynamicallyDefineDataIdentifierRequest(subfn, did)
    DynamicallyDefineDataIdentifierRequest_testActions(msg, subfn, did,)

def DynamicallyDefineDataIdentifierResponse_testActions(msg: DynamicallyDefineDataIdentifierResponse, subfn: int = 1, did: int = 0):
    assert isinstance(msg, DynamicallyDefineDataIdentifierResponse)
    assert msg.sid == 0x6C
    assert msg.hasSubfn()
    assert msg.hasDID()
    assert not msg.hasData()
    assert msg.subfn == subfn
    assert msg.did == did

def test_DynamicallyDefineDataIdentifierResponse():
    msg = DynamicallyDefineDataIdentifierResponse()
    DynamicallyDefineDataIdentifierResponse_testActions(msg)

def test_DynamicallyDefineDataIdentifierResponse_fromSID():
    msg = UDSMessage.fromSID(0x6C)
    DynamicallyDefineDataIdentifierResponse_testActions(msg)

def test_DynamicallyDefineDataIdentifierResponse_defineByMemoryAddress():
    subfn = 0x02
    did = 0xF244
    msg = DynamicallyDefineDataIdentifierResponse(subfn, did)
    DynamicallyDefineDataIdentifierResponse_testActions(msg, subfn, did)

#endregion