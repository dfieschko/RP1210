import pytest
from RP1210.J1939 import DTC
from RP1210 import sanitize_msg_param

def toDTC(spn : int, fmi : int, oc : int) -> bytes:
    """
    Generates diagnostic trouble code (DTC) for diagnostic messages (DM1, DM2, or DM12).

    To use, generate message data with this function, then use return value for data parameter in
    toJ1939Message().
    - spn = Suspect Parameter Number (19 bits)
    - fmi = Failure Mode Identifier (5 bits)
    - OC = Occurence Count (7 bits)

    Will return 4 bytes containing generated DTC.
    """
    ret_val = b''
    # bytes 0 and 1 are just SPN in little-endian format
    spn_bytes = sanitize_msg_param(spn, 3, 'little')
    ret_val += int.to_bytes(spn_bytes[0], 1, 'big')
    ret_val += int.to_bytes(spn_bytes[1], 1, 'big')
    # byte 2 is mix of SPN (3 bits) and fmi (5 bits)
    # we will handle this by doing bitwise operations on an int, then convert back to bytes
    byte4_int = (int(spn_bytes[2]) << 5) & 0b11100000
    byte4_int |= int(fmi) & 0b00011111
    ret_val += sanitize_msg_param(byte4_int)
    # byte 3 is mix of CM (1 bit) and OC (7 bits) - CM always set to 0
    ret_val += sanitize_msg_param(int(oc) & 0b01111111)
    return ret_val

def test_toDTC():
    """
    Runs tests on the function that we use to test DTC class
    """
    assert toDTC(0,0,0) == b'\x00\x00\x00\x00'

    # test SPN
    data = toDTC(0x5BEEF, 0, 0)
    assert data[0] == 0xEF
    assert data[1] == 0xBE
    assert data[2] == 0b10100000
    # test fmi
    data = toDTC(0, 0b10101, 0)
    assert data[2] == 0b00010101
    # test oc
    data = toDTC(0, 0, 102)
    assert data[3] == 102

    data = toDTC(0x5BEEF, 31, 0)
    assert data[0] == 0xEF
    assert data[1] == 0xBE
    assert data[2] == 0b10111111

def test_dtc_init():
    assert DTC().data == b'\x00\x00\x00\x00'
    assert DTC(b'\x00\x00\x00\x00').data == b'\x00\x00\x00\x00'
    assert DTC(spn=423, fmi=12, oc=80).data == toDTC(423, 12, 80)

def test_dtc_staticmethods():
    def testmethods(spn, fmi, oc):
        dtc = toDTC(spn, fmi, oc)
        assert DTC.to_int(spn, fmi, oc) == int.from_bytes(dtc, 'big')
        assert DTC.to_bytes(spn, fmi, oc) == dtc
        assert DTC.to_bytes(spn, 0, oc) == toDTC(spn, 0, oc)
        assert DTC.get_spn(dtc) == spn
        assert DTC.get_fmi(dtc) == fmi
        assert DTC.get_oc(dtc) == oc
        assert DTC.get_cm(dtc) == 0
    
    testmethods(0, 0, 0)
    testmethods(0x0FFFF, 0, 0)
    testmethods(0, 31, 126)
    testmethods(0x3AE57, 31, 54)
    testmethods(0x3AE57, 15, 1)
    for i in range(16):
        for j in range(31):
            for k in range(int(126/16)):
                testmethods(i*32768, j, k*15)

def test_dtc_properties():
    def testproperties(spn, fmi, oc):
        dtc = DTC(None, spn, fmi, oc)
        assert dtc.data == toDTC(spn, fmi, oc)
        assert dtc.spn == spn
        assert dtc.fmi == fmi
        assert dtc.oc == oc
        # change properties, check that it changes data
        dtc.spn = 0
        assert dtc.data == toDTC(0, fmi, oc)
        assert dtc.spn == 0
        assert dtc.fmi == fmi
        assert dtc.oc == oc
        dtc.fmi = 0
        assert dtc.data == toDTC(0, 0, oc)
        assert dtc.spn == 0
        assert dtc.fmi == 0
        assert dtc.oc == oc
        dtc.oc = 0
        assert dtc.data == toDTC(0, 0, 0)
        assert dtc.spn == 0
        assert dtc.fmi == 0
        assert dtc.oc == 0
        # data should be 0 now
        assert dtc.data == b'\x00\x00\x00\x00'
        # change data, check that it changes properties
    for i in range(16):
        for j in range(31):
            for k in range(int(126/16)):
                testproperties(i*32767, j, k*15)
    
def test_dtc_dunder():
    spn = 0xBEEF
    fmi = 22
    oc = 0
    dtc = DTC(None, spn, fmi, oc)
    # += should increment OC
    assert dtc.oc == 0
    for i in range(1, 150):
        dtc += 1
        assert dtc.oc == min(i, 126)
    assert str(dtc) == str(dtc.data)
    assert bytes(dtc) == dtc.data == toDTC(spn, fmi, 126)
    assert len(dtc) == 4
    assert dtc == toDTC(spn, fmi, 126)
    assert dtc == DTC(None, spn, fmi, 126)
    assert dtc != "fasdfkasdlfjadsfk"
    assert dtc != toDTC(spn - 6, fmi - 1, oc-3)
    assert dtc
    assert not DTC(None, 0, 0, 0)

