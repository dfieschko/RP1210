"""
Tests command strings for basic correctness, following the RP1210C standard.

Doesn't test commands on an adapter.
"""

from RP1210 import Commands, sanitize_msg_param

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
    assert Commands.setEcho(False) == b'\x00'
    assert Commands.setEcho(True) == b'\x01'

def test_setAllFiltersToDiscard():
    assert Commands.setAllFiltersToDiscard() == b''

def test_setMessageReceive():
    assert Commands.setMessageReceive(True) == b'\x01'
    assert Commands.setMessageReceive(False) == b'\x00'

def test_releaseJ1939Address():
    commands = [0x0F, 11, 41, b'\x23']
    for command in commands:
        assert Commands.releaseJ1939Address(command) == sanitize_msg_param(command)

def test_setBroadcastList():
    assert Commands.setBroadcastList(1, b'test') == b'\x01' + b'test'
    assert Commands.setBroadcastList(2, 0xDEADBEEF) == b'\x02' + b'\xDE\xAD\xBE\xEF'
    assert Commands.setBroadcastList(3, b'Bingus') == b'\x03' + b'Bingus'

def test_setFilterType():
    assert Commands.setFilterType(0) == b'\x00'
    assert Commands.setFilterType(1) == b'\x01'

def test_setJ1939InterpacketTime():
    time = 200
    assert Commands.setJ1939InterpacketTime(time) == b'\xC8\x00\x00\x00'
    time = 2000
    assert Commands.setJ1939InterpacketTime(time) == b'\xD0\x07\x00\x00'
    time = 500000 # 0x07 A1 20
    assert Commands.setJ1939InterpacketTime(time) == b'\x20\xA1\x07\x00'

def test_setMaxErrorMsgSize():
    assert Commands.setMaxErrorMsgSize(81) == b'\x51\x00'
    assert Commands.setMaxErrorMsgSize(65535) == b'\xFF\xFF'
    assert Commands.setMaxErrorMsgSize(2122) == b'\x4A\x08'

def test_disallowConnections():
    assert Commands.disallowConnections() == b''

def test_flushBuffers():
    assert Commands.flushBuffers() == b''

def test_getConnectionSpeed():
    assert Commands.getConnectionSpeed() == b''

def test_setCANBaud():
    for baud_code in [0, b'\x00', 9600, 9.6, '9600', '9.6k']:
        assert Commands.setCANBaud(baud_code, False) == b'\x00\x00'
        assert Commands.setCANBaud(baud_code, True) == b'\x01\x00'
    for baud_code in [1, b'\x01', 19200, 19.2, '19200', '19.2k']:
        assert Commands.setCANBaud(baud_code, False) == b'\x00\x01'
        assert Commands.setCANBaud(baud_code, True) == b'\x01\x01'
    for baud_code in [2, b'\x02', 38400, 38.4, '38400', '38.4k']:
        assert Commands.setCANBaud(baud_code, False) == b'\x00\x02'
        assert Commands.setCANBaud(baud_code, True) == b'\x01\x02'
    for baud_code in [3, b'\x03', 57600, 57.6, '57600', '57.6k']:
        assert Commands.setCANBaud(baud_code, False) == b'\x00\x03'
        assert Commands.setCANBaud(baud_code, True) == b'\x01\x03'
    for baud_code in [4, b'\x04', 125000, 125, '125', '125k', '125000']:
        assert Commands.setCANBaud(baud_code, False) == b'\x00\x04'
        assert Commands.setCANBaud(baud_code, True) == b'\x01\x04'
    for baud_code in [5, b'\x05', 250000, 250, '250', '250k', '250000']:
        assert Commands.setCANBaud(baud_code, False) == b'\x00\x05'
        assert Commands.setCANBaud(baud_code, True) == b'\x01\x05'
    for baud_code in [6, b'\x06', 500000, 500, '500', '500k', '500000']:
        assert Commands.setCANBaud(baud_code, False) == b'\x00\x06'
        assert Commands.setCANBaud(baud_code, True) == b'\x01\x06'
    for baud_code in [7, b'\x07', 1000000, 1000, '1000', '1000000', '1000k']:
        assert Commands.setCANBaud(baud_code, False) == b'\x00\x07'
        assert Commands.setCANBaud(baud_code, True) == b'\x01\x07'

def test_setJ1939Baud():
    for baud_code in [4, b'\x04', 125000, 125, '125', '125k', '125000']:
        assert Commands.setJ1939Baud(baud_code, False) == b'\x00\x04'
        assert Commands.setJ1939Baud(baud_code, True) == b'\x01\x04'
    for baud_code in [5, b'\x05', 250000, 250, '250', '250k', '250000']:
        assert Commands.setJ1939Baud(baud_code, False) == b'\x00\x05'
        assert Commands.setJ1939Baud(baud_code, True) == b'\x01\x05'
    for baud_code in [6, b'\x06', 500000, 500, '500', '500k', '500000']:
        assert Commands.setJ1939Baud(baud_code, False) == b'\x00\x06'
        assert Commands.setJ1939Baud(baud_code, True) == b'\x01\x06'
    for baud_code in [7, b'\x07', 1000000, 1000, '1000', '1000000', '1000k']:
        assert Commands.setJ1939Baud(baud_code, False) == b'\x00\x07'
        assert Commands.setJ1939Baud(baud_code, True) == b'\x01\x07'

def test_setBlockingTimeout():
    for x in range(255):
        for y in range(255):
            assert Commands.setBlockingTimeout(x, y) == sanitize_msg_param(x, 1) + sanitize_msg_param(y, 1)
