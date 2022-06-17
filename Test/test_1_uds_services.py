from tkinter import W
import pytest
from RP1210.UDS import *

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

def test_WriteDataByIdentifierRequest_fromDID():
    did = 8192
    msg = WriteDataByIdentifierRequest(did = did)
    WriteDataByIdentifierRequest_testActions(msg, did = did)

def test_WriteDataByIdentifierRequest_fromMessageData():
    data = b'\xEA\x53\x11\x04'
    msg = WriteDataByIdentifierRequest(data = data)
    WriteDataByIdentifierRequest_testActions(msg, data = data)

def test_WriteDataByIdentifierRequest_fromDIDAndMessageData():
    did = 8376
    data = b'\x32\x02\xA5'
    msg = WriteDataByIdentifierRequest(did = did, data = data)
    WriteDataByIdentifierRequest_testActions(msg, did=did, data=data)

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

def test_WriteDataByIdentifierResponse_fromDID():
    did = 8472
    msg = WriteDataByIdentifierResponse(did = did)
    WriteDataByIdentifierResponse_testActions(msg, did)

#endregion

###########################################################################################
# ReadDataByIdentifier ################################################################
###########################################################################################
#region ReadDataByIdentifier

#endregion

###########################################################################################
# RequestDownload ################################################################
###########################################################################################
#region RequestDownload

#endregion


###########################################################################################
# SecurityAccess ################################################################
###########################################################################################
#region SecurityAccess

#endregion