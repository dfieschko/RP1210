"""
Basic tests for UDS.py.
"""

import pytest
from RP1210 import UDS

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
