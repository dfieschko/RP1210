"""
Basic tests for UDS.py.
"""

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
        _hasSubfn = True
        _hasDID = True
        _hasData = True
        _dataSize = 4
        _dataSizeCanChange = True

        _sid = 0xAA

    msg = EverythingMessage()
    assert msg.sid == 0xAA
    assert msg.subfn is None
    assert msg.did is None
    assert msg.data is None
    assert msg.raw == b'\xAA\x00\x00\x00\x00\x00\x00\x00'
    assert msg.value == 0
    checkMagicMethods(msg)
    assert msg.name() == "Proprietary/Reserved"

    msg.subfn = 0x30
    assert msg.subfn == 0x30
    msg.subfn = b'\x30'
    assert msg.subfn == 0x30
    assert msg.raw == b'\xAA\x30\x00\x00\x00\x00\x00\x00'

    msg.did = 0xABCD
    assert msg.did == 0xABCD
    msg.did = b'\xAB\xCD'
    assert msg.did == 0xABCD
    assert msg.raw == b'\xAA\x30\xAB\xCD\x00\x00\x00\x00'

    msg.data = b'\xDE\xAD\xBE\xEF'
    assert msg.data == b'\xDE\xAD\xBE\xEF'
    assert msg.raw == b'\xAA\x30\xAB\xCD\xDE\xAD\xBE\xEF'
    assert msg.value == 0xDEADBEEF

    checkMagicMethods(msg)
