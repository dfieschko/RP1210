import pytest
from RP1210 import J1939
from RP1210.J1939 import DTC, DiagnosticMessage, J1939Message, toJ1939Message
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
        assert dtc.cm() == 0
        # change properties, check that it changes data
        dtc.spn = 0
        assert dtc.data == toDTC(0, fmi, oc)
        assert dtc.spn == 0
        assert dtc.fmi == fmi
        assert dtc.oc == oc
        assert dtc.cm() == 0
        dtc.fmi = 0
        assert dtc.data == toDTC(0, 0, oc)
        assert dtc.spn == 0
        assert dtc.fmi == 0
        assert dtc.oc == oc
        assert dtc.cm() == 0
        dtc.oc = 0
        assert dtc.data == toDTC(0, 0, 0)
        assert dtc.spn == 0
        assert dtc.fmi == 0
        assert dtc.oc == 0
        assert dtc.cm() == 0
        # data should be 0 now
        assert dtc.data == b'\x00\x00\x00\x00'
        # change data, check that it changes properties
    for i in range(16):
        for j in range(31):
            for k in range(int(126/16)):
                testproperties(i*32767, j, k*15)
    
@pytest.mark.parametrize("spn,fmi", argvalues=[
    (0xBEEF, 22), (0x0000, 0), (0xDEAD, 24)
])
def test_dtc_dunder(spn, fmi):
    oc = 0
    dtc = DTC(None, spn, fmi, oc)
    # += should increment OC
    assert dtc.oc == oc
    for i in range(1, 150):
        dtc += 1
        assert dtc.oc == min(i, 126)
    assert str(dtc) == str(dtc.data)
    assert bytes(dtc) == dtc.data == toDTC(spn, fmi, 126) == sanitize_msg_param(dtc)
    assert len(dtc) == 4
    assert dtc == toDTC(spn, fmi, 126)
    assert dtc == DTC(None, spn, fmi, 126)
    assert dtc != "fasdfkasdlfjadsfk"
    assert dtc != None
    assert dtc != bytes
    assert dtc
    assert not DTC(None, 0, 0, 0)
    assert int(dtc) == int.from_bytes(bytes(dtc), byteorder='big')

def test_dm_init():
    timestamp = b'\x12\x34\x56\x78'
    dm1_data = b'\x72\x00\x31\x04\x5F\xE0'
    msg = toJ1939Message(0xFECA, 6, 0x12, 0xFF, dm1_data)
    assert msg == b'\xCA\xFE\x00\x06\x12\xFF\x72\x00\x31\x04\x5F\xE0'
    j1939 = J1939Message(timestamp + msg)
    assert j1939.data == dm1_data
    assert DiagnosticMessage(timestamp + msg).data == j1939.data
    assert DiagnosticMessage(j1939).data == dm1_data
    assert DiagnosticMessage(int.from_bytes(dm1_data, 'big')) == dm1_data


def test_diagnosticmessage_to_dtcs():
    dtc1 = DTC(spn=0xEED, fmi=4, oc=22)
    dtc2 = DTC(spn=432, fmi=6, oc=1)
    dtc_list = DiagnosticMessage.to_dtcs(b'\x72\x00' + bytes(dtc1) + bytes(dtc2))
    assert dtc1.data == toDTC(dtc1.spn, dtc1.fmi, dtc1.oc) # make sure dtc1 is ok
    assert dtc2.data == toDTC(dtc2.spn, dtc2.fmi, dtc2.oc) # make sure dtc2 is ok
    assert dtc_list[0] == bytes(dtc1)
    assert dtc_list[1] == bytes(dtc2)
    dtc_list = DiagnosticMessage.to_dtcs(b'\x72\x00' + bytes(dtc1) + bytes(dtc2) + b'\x00\x00')
    assert len(dtc_list) == 2 # didn't add the trailing zeros

def test_diagnosticmessage_items():
    lamps = int.to_bytes(0b01110010, 2, 'little')
    dtc1 = DTC(spn=0xEED, fmi=4, oc=22)
    dtc2 = DTC(spn=432, fmi=6, oc=1)
    timestamp = b'\x01\x02\x03\x04'
    data = lamps + bytes(dtc1) + bytes(dtc2)
    pgn = 0xFECA
    pri = 6
    sa = 0x49
    da = 0xFF
    j1939_msg = toJ1939Message(pgn, pri, sa, da, data)
    dm1 = DiagnosticMessage(timestamp + j1939_msg)

    assert dm1[0] == dtc1
    assert dm1[1] == dtc2
    assert dm1[0] != dm1[1]
    dm1[0] = dm1[1]
    assert sanitize_msg_param(dm1[0]) == sanitize_msg_param(dm1[1])
    assert dm1[0] == dm1[1]
    dm1 += dtc1.data
    assert dm1[2] == dtc1

    dm1[0] = b'\x12\x34\x56\x78'
    assert dm1[0] == DTC(b'\x12\x34\x56\x78')

def test_diagnosticmessage_lamps():
    lamps = int.to_bytes(0b01110010, 2, 'little')
    dtc1 = DTC(spn=0xEED, fmi=4, oc=22)
    dtc2 = DTC(spn=432, fmi=6, oc=1)
    timestamp = b'\x01\x02\x03\x04'
    data = lamps + bytes(dtc1) + bytes(dtc2)
    pgn = 0xFECA
    pri = 6
    sa = 0x49
    da = 0xFF
    j1939_msg = toJ1939Message(pgn, pri, sa, da, data)
    dm1 = DiagnosticMessage(timestamp + j1939_msg)

    assert dm1.lamps == b'\x72\x00'
    assert dm1.lamps[0] == 0b01110010
    assert dm1.mil() == 0b01
    assert dm1.rsl() == 0b11
    assert dm1.awl() == 0b00
    assert dm1.pl() == 0b10

    dm1.lamps = 0b00011011
    assert dm1.lamps[0] == 0b00011011
    assert dm1.mil() == 0b00
    assert dm1.rsl() == 0b01
    assert dm1.awl() == 0b10
    assert dm1.pl() == 0b11

    dm1.lamps = b''
    assert dm1.lamps == b'\x00\x00'
    dm1.lamps = b'\x12'
    assert dm1.lamps == b'\x12\x00'
    dm1.lamps = b'\x12\x34'
    assert dm1.lamps == b'\x12\x34'
    dm1.data = b''
    assert dm1.lamps == b'\x00\x00'
    dm1.data = b'\x11'
    assert dm1.lamps == b'\x11\x00'
    dm1.data = b'\x11\x22'
    assert dm1.lamps == b'\x11\x22'

def test_diagnosticmessage_codes():
    lamps = int.to_bytes(0b01110010, 2, 'little')
    dtc1 = DTC(spn=0xEED, fmi=4, oc=22)
    dtc2 = DTC(spn=432, fmi=6, oc=1)
    timestamp = b'\x01\x02\x03\x04'
    data = lamps + bytes(dtc1) + bytes(dtc2)
    pgn = 0xFECA
    pri = 6
    sa = 0x49
    da = 0xFF
    j1939_msg = toJ1939Message(pgn, pri, sa, da, data)
    dm1 = DiagnosticMessage(timestamp + j1939_msg)

    assert dm1.codes[0] == dtc1
    assert dm1.codes[1] == dtc2

    dm1.codes[0] = dtc2
    assert dm1.codes[0] == dtc2

    dm1.codes = [dtc1, dtc2]
    assert dm1.codes[0] == dtc1
    assert dm1.codes[1] == dtc2

    dm1.codes = bytes(dtc1) + bytes(dtc2)
    assert dm1.codes[0] == dtc1
    assert dm1.codes[1] == dtc2

    dm1.codes = []
    assert dm1.codes == []

    with pytest.raises(ValueError):
        dm1.codes = ["dasfasdf"]
    
    dm1.codes = 0x11223344
    assert dm1.codes[0] == b'\x11\x22\x33\x44'

def test_diagnosticmessage_iadd_eq():
    lamps = int.to_bytes(0b01110010, 2, 'little')
    dtc1 = DTC(spn=0xEED, fmi=4, oc=22)
    dtc2 = DTC(spn=432, fmi=6, oc=1)
    timestamp = b'\x01\x02\x03\x04'
    data = lamps + bytes(dtc1) + bytes(dtc2)
    pgn = 0xFECA
    pri = 6
    sa = 0x49
    da = 0xFF
    j1939_msg = toJ1939Message(pgn, pri, sa, da, data)
    dm1 = DiagnosticMessage(timestamp + j1939_msg)
    dm2 = DiagnosticMessage(timestamp + j1939_msg)

    assert dm1[0] == dtc1
    assert dm1[1] == dtc2
    assert sanitize_msg_param(dm1[0]) == sanitize_msg_param(dtc1)
    assert len(sanitize_msg_param(dtc1)) == 4

    assert dm1 == dm2
    dm1 += dtc1
    assert dm1 != dm2

    assert dm1[0] == dtc1
    assert dm1[1] == dtc2
    assert dm1[2] == dtc1

    assert dm1 != ""
    assert dm1 != int
    assert dm1 != 34234234

def test_diagnosticmessage_conversion():
    lamps = int.to_bytes(0b01110010, 2, 'little')
    dtc1 = DTC(spn=0xEED, fmi=4, oc=22)
    dtc2 = DTC(spn=432, fmi=6, oc=1)
    timestamp = b'\x01\x02\x03\x04'
    data = lamps + bytes(dtc1) + bytes(dtc2)
    pgn = 0xFECA
    pri = 6
    sa = 0x49
    da = 0xFF
    j1939_msg = toJ1939Message(pgn, pri, sa, da, data)
    dm1 = DiagnosticMessage(timestamp + j1939_msg)

    assert bytes(dm1) == J1939Message(timestamp + j1939_msg).data
    assert str(dm1) == str(bytes(dm1))

    assert max(int((10 - 2) / 4), 0) == 2
    assert len(dm1) == 2

    assert not DiagnosticMessage()
    assert dm1
    assert int.from_bytes(J1939Message(timestamp + j1939_msg).data, 'big') == int(dm1)

def test_diagnosticmessage_iterate():
    dm1 = DiagnosticMessage()
    for i in range(20):
        spn = i * 23
        fmi = i
        oc = 1 + i*3
        dm1 += DTC(None, spn, fmi, oc)
    count = 0
    for _ in dm1:
        count += 1
    assert count == 20
    for i in range(20):
        assert dm1[i].spn == i * 23
        assert dm1[i].fmi == i
        assert dm1[i].oc == 1 + i*3
    