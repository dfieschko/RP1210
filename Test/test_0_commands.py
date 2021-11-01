"""
Tests command strings for basic correctness, following the RP1210C standard.

Doesn't test commands on an adapter.
"""

from RP1210C import Commands, sanitize_msg_param

def test_reset():
    assert Commands.resetDevice() == b''

def test_setAllFiltersToPass():
    assert Commands.setAllFiltersToPass() == b''

def test_protectJ1939Address_blocking():
    addr = 0xAC
    name = 0xDEADBEEF
    command = Commands.protectJ1939Address(addr, name)
    assert command == b'\xAC\x00\x00\x00\x00\xDE\xAD\xBE\xEF\x00'
    assert len(command) == 10
    addr = 222
    name = b'Chungus'
    command = Commands.protectJ1939Address(addr, name)
    assert command == b'\xDE' + b'\x00' + b'Chungus' + b'\x00'
    assert len(command) == 10

def test_protectJ1939Address_nonblocking():
    addr = 0xAC
    name = 0xDEADBEEF
    command = Commands.protectJ1939Address(addr, name, False)
    assert command == b'\xAC\x00\x00\x00\x00\xDE\xAD\xBE\xEF\x02'
    assert len(command) == 10
    addr = 222
    name = b'Chungus'
    command = Commands.protectJ1939Address(addr, name, False)
    assert command == b'\xDE' + b'\x00' + b'Chungus' + b'\x02'
    assert len(command) == 10

def test_setJ1939Filters():
    PGN = 1
    SOURCE = 4
    DEST = 8
    assert Commands.setJ1939Filters(0) == b'\x00\x00\x00\x00\x00\x00\x00'
    assert Commands.setJ1939Filters(PGN, pgn=0x0EF123) == b'\x01\x23\xF1\x0E\x00\x00\x00'
    assert Commands.setJ1939Filters(SOURCE, source=0xAB) == b'\x04\x00\x00\x00\x00\xAB\x00'
    assert Commands.setJ1939Filters(DEST, dest=0xCD) == b'\x08\x00\x00\x00\x00\x00\xCD'
    assert Commands.setJ1939Filters(PGN+SOURCE, pgn=0x0EF123, source=0xAB) == b'\x05\x23\xF1\x0E\x00\xAB\x00'

def test_setCANFilters():
    type_std = Commands.CAN_TYPES["STANDARD_CAN"]
    assert type_std == 0x00
    type_ext = Commands.CAN_TYPES["EXTENDED_CAN"]
    assert type_ext == 0x01
    mask = 0b11111111000000001111111100001111 # 0xFF00FF0F
    header = 0b11111111000000001111111100001111 # 0xFF00FF0F
    cmd = Commands.setCANFilters(type_std, mask, header)
    assert cmd == b'\x00\xFF\x00\xFF\x0F\xFF\x00\xFF\x0F'
    cmd = Commands.setCANFilters(type_ext, mask, header)
    assert cmd == b'\x01\xFF\x00\xFF\x0F\xFF\x00\xFF\x0F'

def test_generic_command():
    commands = [0x00FF0F00FF0F, 0xDEADBEEF, b'ajsdhgkjfshgh', "2143251345325"]
    for command in commands:
        assert Commands.generic(command) == sanitize_msg_param(command)

def test_echoTx():
    assert Commands.echoTx(False) == b'\x00'
    assert Commands.echoTx(True) == b'\x01'

def test_setAllFiltersToDiscard():
    assert Commands.setAllFiltersToDiscard() == b''

def test_setMessageReceive():
    assert Commands.setMessageReceive(True) == b'\x01'
    assert Commands.setMessageReceive(False) == b'\x00'

def test_releaseJ1939Address():
    commands = [0x0F, "11", 41, b'\x23']
    for command in commands:
        assert Commands.releaseJ1939Address(command) == sanitize_msg_param(command)
