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