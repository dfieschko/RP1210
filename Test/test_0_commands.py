"""
Tests command strings for basic correctness, following the RP1210C standard.

Doesn't test commands on an adapter.
"""

from RP1210C import Commands

def test_reset():
    assert Commands.reset() == b''

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
