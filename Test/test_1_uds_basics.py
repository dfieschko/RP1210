"""
Basic tests for UDS.py.
"""

from tabnanny import check
import pytest
from RP1210 import UDS

def checkMagicMethods(msg : UDS.UDSMessage):
    assert str(msg) == msg.raw.decode('utf-8', errors='replace')
    assert int(msg) == msg.value
    assert bytes(msg) == msg.raw
    assert len(msg) == len(msg.raw)
    for i in range(0, len(msg)):
        assert msg[i] == msg.raw[i]

@pytest.mark.parametrize("input,expected", argvalues=[
    (0x10, "Diagnostic Session Control"), (0x11, "ECU Reset"), (0x00, "Proprietary/Reserved"),
    (0x22, "Read Data By Identifier"), (0x23, "Read Memory By Address"), (0x34, "Request Download")
])
def test_translateRequestSID_withExpectedValues(input, expected):
    assert UDS.translateRequestSID(input) == expected

def test_translateRequestSID_withDict():
    for key in range(0x00, 0xFF):
        assert UDS.translateRequestSID(key) == UDS.ServiceNames.get(key, "Proprietary/Reserved")
    
@pytest.mark.parametrize("input,expected", argvalues=[
    (0x50, "Diagnostic Session Control"), (0x51, "ECU Reset"), (0x00, "Proprietary/Reserved"),
    (0x62, "Read Data By Identifier"), (0x63, "Read Memory By Address"), (0x74, "Request Download")
])
def test_translateResponseSID_withExpectedValues(input, expected):
    assert UDS.translateResponseSID(input) == expected

def test_translateResponseSID_withDict():
    for key in range(0x00 + 0x40, 0xFF + 0x40):
        assert UDS.translateResponseSID(key) == UDS.ServiceNames.get(key - 0x40, "Proprietary/Reserved")

def test_translateResponseCode_withDict():
    for key in range(0x00, 0xFF):
        if 0x95 <= key <= 0xEF:
            assert UDS.translateResponseCode(key) == "Reserved For Specific Conditions Not Correct"
        elif 0xF0 <= key <= 0xFE:
            assert UDS.translateResponseCode(key) == "Conditions Not Correct: Vehicle Manufacturer Specific"
        else:
            assert UDS.translateResponseCode(key) == UDS.ResponseCodes.get(key, "ISO/SAE Reserved")

def test_UDSMessage_allEnabled_isRequest():
    """Run a test case with all parameters enabled."""
    class EverythingMessage(UDS.UDSMessage):
        _isResponse = False
        _sid = 0xAA

        def __init__(self):
            super().__init__()
            self._hasSubfn = True
            self._hasDID = True
            self._hasData = True
            self._dataSize = 4
            self._dataSizeCanChange = True

        

    msg = EverythingMessage()
    assert msg.sid == 0xAA
    assert msg.subfn is None
    assert msg.did is None
    assert msg.data == b''
    assert msg.raw == b'\xAA\x00\x00\x00\x00\x00\x00\x00'
    assert msg.value == 0
    checkMagicMethods(msg)
    assert msg.name() == "Proprietary/Reserved"

    msg.subfn = 0x30
    assert msg.subfn == 0x30
    msg.subfn = b'\x31'
    assert msg.subfn == 0x31
    assert msg.raw == b'\xAA\x31\x00\x00\x00\x00\x00\x00'
    checkMagicMethods(msg)

    msg.did = 0xABCD
    assert msg.did == 0xABCD
    msg.did = b'\xDC\xBA'
    assert msg.did == 0xDCBA
    assert msg.raw == b'\xAA\x31\xDC\xBA\x00\x00\x00\x00'
    checkMagicMethods(msg)

    msg.data = b'\xDE\xAD\xBE\xEF'
    assert msg.data == b'\xDE\xAD\xBE\xEF'
    assert msg.raw == b'\xAA\x31\xDC\xBA\xDE\xAD\xBE\xEF'
    assert msg.value == 0xDEADBEEF
    checkMagicMethods(msg)

    msg.data = b'\xC0\xFF\xEE' # dataSizeCanChange is enabled, so this will change data size
    assert len(msg.data) == 3
    assert msg.data == b'\xC0\xFF\xEE'
    assert msg.raw == b'\xAA\x31\xDC\xBA\xC0\xFF\xEE'
    assert msg.value == 0xC0FFEE
    checkMagicMethods(msg)

    msg.data = 0xDEADBEEF
    assert len(msg.data) == 4
    assert msg.data == b'\xDE\xAD\xBE\xEF'
    assert msg.raw == b'\xAA\x31\xDC\xBA\xDE\xAD\xBE\xEF'
    assert msg.value == 0xDEADBEEF
    checkMagicMethods(msg)

    msg._dataSizeCanChange = False
    msg.data = 0xFF
    assert len(msg.data) == 4
    assert msg.data == b'\xFF\xAA\xAA\xAA'
    assert msg.raw == b'\xAA\x31\xDC\xBA\xFF\xAA\xAA\xAA'
    assert msg.value == 0xFFAAAAAA
    checkMagicMethods(msg)

    with pytest.raises(ValueError):
        msg._dataSizeCanChange = False
        msg.data = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
    # data shouldn't change
    assert len(msg.data) == 4
    assert msg.data == b'\xFF\xAA\xAA\xAA'
    assert msg.raw == b'\xAA\x31\xDC\xBA\xFF\xAA\xAA\xAA'
    assert msg.value == 0xFFAAAAAA
    checkMagicMethods(msg)

    msg.subfn = 0x01
    assert msg.subfn == 0x01
    assert msg.suppressPosRspMsgIndicationBit == False
    msg.suppressPosRspMsgIndicationBit = True
    assert msg.suppressPosRspMsgIndicationBit == True
    assert msg.subfn == 0x01 + 0x80
    msg.suppressPosRspMsgIndicationBit = False
    assert msg.suppressPosRspMsgIndicationBit == False
    assert msg.subfn == 0x01
    checkMagicMethods(msg)

def test_UDSMessage_allEnabled_isResponse():
    """
    Run a test case with all parameters enabled. This one sets isResponse to True and uses a
    Response SID.
    """
    class EverythingMessage(UDS.UDSMessage):
        _isResponse = True
        _sid = 0x75

        def __init__(self):
            super().__init__()
            self._hasSubfn = True
            self._hasDID = True
            self._hasData = True
            self._dataSize = 4
            self._dataSizeCanChange = True

    msg = EverythingMessage()
    assert msg.sid == 0x75
    assert msg.subfn is None
    assert msg.did is None
    assert msg.data == b''
    assert msg.raw == b'\x75\x00\x00\x00\x00\x00\x00\x00'
    assert msg.value == 0
    checkMagicMethods(msg)
    assert msg.name() == "Request Upload"

    msg.subfn = 0x30
    assert msg.subfn == 0x30
    msg.subfn = b'\x30'
    assert msg.subfn == 0x30
    assert msg.raw == b'\x75\x30\x00\x00\x00\x00\x00\x00'
    checkMagicMethods(msg)

    msg.did = 0xABCD
    assert msg.did == 0xABCD
    msg.did = b'\xAB\xCD'
    assert msg.did == 0xABCD
    assert msg.raw == b'\x75\x30\xAB\xCD\x00\x00\x00\x00'
    checkMagicMethods(msg)

    msg.data = b'\xDE\xAD\xBE\xEF'
    assert msg.data == b'\xDE\xAD\xBE\xEF'
    assert msg.raw == b'\x75\x30\xAB\xCD\xDE\xAD\xBE\xEF'
    assert msg.value == 0xDEADBEEF
    checkMagicMethods(msg)

def test_UDSMessage_allDisabled():
    """
    Run a test case with all parameters disabled.
    """
    class NothingMessage(UDS.UDSMessage):
        _isResponse = True
        _hasSubfn = False
        _hasDID = False
        _hasData = False

        _sid = 0x75

    msg = NothingMessage()
    checkMagicMethods(msg)
    assert msg.sid == 0x75
    assert msg.subfn is None
    assert msg.did is None
    assert msg.data == b''
    assert msg.raw == b'\x75'
    assert msg.value == 0
    checkMagicMethods(msg)

    with pytest.raises(AttributeError):
        msg.subfn = 0xAA
    assert msg.subfn is None
    checkMagicMethods(msg)

    with pytest.raises(AttributeError):
        msg.did = 0xABCD
    assert msg.did is None
    checkMagicMethods(msg)

    with pytest.raises(AttributeError):
        msg.data = b'\xAA\xAA'
    assert msg.data == b''
    checkMagicMethods(msg)

    with pytest.raises(AttributeError):
        msg.suppressPosRspMsgIndicationBit = True
    assert msg.suppressPosRspMsgIndicationBit == False
