from RP1210 import J1939, Commands, sanitize_msg_param
import binascii
import pytest

def test_getJ1939ProtocolString_default():
    assert J1939.getJ1939ProtocolString() == b"J1939:Baud=Auto"

def test_getJ1939ProtocolString_format1():
    assert J1939.getJ1939ProtocolString(protocol=1, Baud=250) == b"J1939:Baud=250"
    assert J1939.getJ1939ProtocolString(protocol=1, Baud="Auto") == b"J1939:Baud=Auto"
    assert J1939.getJ1939ProtocolString(protocol=1, Baud=666, Channel=3) == b"J1939:Baud=666,Channel=3"
    assert J1939.getJ1939ProtocolString(protocol=1, Baud="Auto", Channel=3) == b"J1939:Baud=Auto,Channel=3"
    assert J1939.getJ1939ProtocolString(protocol=1) == b"J1939:Baud=Auto"
    assert J1939.getJ1939ProtocolString(protocol=1, Channel=2) == b"J1939:Baud=Auto,Channel=2"
    assert J1939.getJ1939ProtocolString(protocol=1, Baud=250, SampleLocation=23, SJW=1, 
                                    PROP_SEG=4, PHASE_SEG1=4, PHASE_SEG2=3, TSEG1=53, 
                                    TSEG2=43, SampleTimes=5) == b"J1939:Baud=250"

def test_getJ1939ProtocolString_format2():
    assert J1939.getJ1939ProtocolString(protocol=2) == b"J1939"
    assert J1939.getJ1939ProtocolString(protocol=2, Channel=4) == b"J1939,Channel=4"
    assert J1939.getJ1939ProtocolString(protocol=2, Baud=500) == b"J1939"

@pytest.mark.parametrize("Baud,SampleLocation,SJW,Channel", [
    (500, 3, 20, 432), (0, 0, 0, 0), (5000, 500, "BAAA", "fadsfasdf")
])
def test_getJ1939ProtocolString_format3(Baud, SampleLocation, SJW, Channel):
    protocol_string = J1939.getJ1939ProtocolString(protocol=3, Baud=Baud, SampleLocation=SampleLocation, SJW=SJW, Channel=Channel)
    assert protocol_string == bytes(f"J1939:Baud={str(Baud)},SampleLocation={str(SampleLocation)},SJW={str(SJW)},IDSize=29" + f",Channel={str(Channel)}", 'utf-8')

# I don't really care about protocol IDs 3 through 5 at the moment

def test_getJ1939ProtocolDescription():
    assert J1939.getJ1939ProtocolDescription(1) == "Variable J1939 baud rate. Select 125, 250, 500, 1000, or Auto."
    assert J1939.getJ1939ProtocolDescription(2) == "General default for J1939 baud rate (250k baud)."
    assert J1939.getJ1939ProtocolDescription(3) == "Driver uses SampleLocation to calculate parameters."
    assert J1939.getJ1939ProtocolDescription(4) == "Baud formula derived from BOSCH CAN specification."
    assert J1939.getJ1939ProtocolDescription(5) == "Baud formula derived from Intel implementations."
    assert J1939.getJ1939ProtocolDescription(-1) == "Invalid J1939 protocol format selected."
    assert J1939.getJ1939ProtocolDescription(0) == "Invalid J1939 protocol format selected."
    assert J1939.getJ1939ProtocolDescription(6) == "Invalid J1939 protocol format selected."

def test_toJ1939Message_empty():
    """test toJ1939Message() with empty/null arguments"""
    assert J1939.toJ1939Message(0, 0, 0, 0, bytes(0)) == bytes(6)
    assert J1939.toJ1939Message(0, 0, 0, 0, b'') == bytes(6)
    assert J1939.toJ1939Message(b'', b'', b'', b'', b'') == bytes(6)
    assert J1939.toJ1939Message('', '', '', '', b'') == bytes(6)

def test_toJ1939Message():
    """test toJ1939Message()"""
    pgn = 0x00FEEE
    pri = 3
    sa = 2
    da = 0x0E
    data = 0xDEADBEEF
    message = J1939.toJ1939Message(pgn, pri, sa, da, data)
    assert message == b'\xEE\xFE\x00\x03\x02\x0E\xDE\xAD\xBE\xEF'
    data = b'\xDE\xAD\xBE\xEF'
    message = J1939.toJ1939Message(pgn, pri, sa, da, data)
    assert message == b'\xEE\xFE\x00\x03\x02\x0E\xDE\xAD\xBE\xEF'
    dm1_data = b'\x72\x00\x31\x04\x5F\xE0'
    msg = J1939.toJ1939Message(0xFECA, 6, 0x12, 0xFF, dm1_data)
    assert msg ==b'\xCA\xFE\x00\x06\x12\xFF\x72\x00\x31\x04\x5F\xE0'
    pgn = 0x0AACCC
    pri = 0
    sa = 22
    da = 0x1E
    data = 0xDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEF0000
    message = J1939.toJ1939Message(pgn, pri, sa, da, data)
    assert message == b'\xCC\xAC\x0A\x00\x16\x1E\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\x00\x00'

# def test_J1939MessageParser_pdu2_specificexample():
#     """Test J1939MessageParser class"""
#     timestamp = sanitize_msg_param(0x01020304)
#     assert timestamp == b'\x01\x02\x03\x04'
#     pgn = 0x00FEEE
#     pri = 3
#     sa = 2
#     da = 0x0E # this should be ignored by RP1210 since it's broadcast to 0xFF, but will still set da
#     data = 0xDEADBEEF
#     message = timestamp + J1939.toJ1939Message(pgn, pri, sa, da, data)
#     assert message == b'\x01\x02\x03\x04\xEE\xFE\x00\x03\x02\x0E\xDE\xAD\xBE\xEF'
#     msg = J1939.J1939Message(message)
#     assert msg.timestamp == 0x01020304
#     assert msg.pgn == pgn
#     assert msg.sa == sa
#     assert msg.da == da
#     assert msg.pri == pri
#     assert msg.res == 0
#     assert msg.dp == 0
#     assert msg.pdu() == 2
#     assert msg.pf() == 0xFE
#     assert msg.ps() == 0xEE
#     assert msg.data == sanitize_msg_param(data)

# def test_J1939Message_2():
#     timestamp = b'\x12\34\x56\x78'
#     pgn = 0x00FEEE
#     pri = 3
#     sa = 2
#     da = 0x0E
#     data = 0xDEADBEEF
#     message = J1939.toJ1939Message(pgn, pri, sa, da, data)
#     assert message == b'\xEE\xFE\x00\x03\x02\x0E\xDE\xAD\xBE\xEF'
#     j1939 = J1939.J1939Message(timestamp + message)
#     assert j1939.timestamp == int.from_bytes(timestamp, 'big')
#     assert j1939.pgn == pgn
#     assert j1939.pri == pri
#     assert j1939.sa == sa
#     assert j1939.da == da
#     assert j1939.data == sanitize_msg_param(data)
#     data = b'\xDE\xAD\xBE\xEF'
#     message = J1939.toJ1939Message(pgn, pri, sa, da, data)
#     assert message == b'\xEE\xFE\x00\x03\x02\x0E\xDE\xAD\xBE\xEF'
#     j1939 = J1939.J1939Message(timestamp + message)
#     assert j1939.timestamp == int.from_bytes(timestamp, 'big')
#     assert j1939.pgn == pgn
#     assert j1939.pri == pri
#     assert j1939.sa == sa
#     assert j1939.da == da
#     assert j1939.data == sanitize_msg_param(data)
#     dm1_data = b'\x72\x00\x31\x04\x5F\xE0'
#     msg = J1939.toJ1939Message(0xFECA, 6, 0x12, 0xFF, dm1_data)
#     assert msg ==b'\xCA\xFE\x00\x06\x12\xFF\x72\x00\x31\x04\x5F\xE0'
#     j1939 = J1939.J1939Message(timestamp + msg)
#     assert j1939.timestamp == int.from_bytes(timestamp, 'big')
#     assert j1939.pgn == 0xFECA
#     assert j1939.pri == 6
#     assert j1939.sa == 0x12
#     assert j1939.da == 0xFF
#     assert j1939.data == sanitize_msg_param(dm1_data)

# @pytest.mark.parametrize("pgn,res,dp,pf,ps,da", argvalues=[
#     (0x00F004, 3, 0, 0, 0xF0, 0x04, 0xFF)
# ])
# def test_J1939Message_from_pgn(pgn, res, dp, pf, ps, da):
#     """
#     Test that values are correctly populated from PGN.
    
#     PGN is the variable being tested; res, dp, pf, ps, and da are expected values.
#     """
#     msg = J1939.J1939Message(pgn=pgn)
#     assert msg.pgn == pgn

# def test_J1939Message_3():
#     timestamp = b'\x01\x23\x45\x67'
#     data = b'\x72\x00\x31\x04\x5F\xE0'
#     msg = J1939.toJ1939Message(0xFECA, 6, 0x12, 0xFF, data)
#     assert msg == b'\xCA\xFE\x00\x06\x12\xFF\x72\x00\x31\x04\x5F\xE0'
#     j1939 = J1939.J1939Message(timestamp + msg)
#     assert j1939.msg == timestamp + msg
#     assert j1939.getPriority() == 6
#     assert j1939.getPGN() == 0xFECA
#     assert j1939.getDestination() == 0xFF
#     assert j1939.getSource() == 0x12
#     assert j1939.getData() == data

# def test_J1939Message_long():
#     timestamp = b'\x12\34\x56\x78'
#     pgn = 0x01ACCC
#     pri = 0
#     sa = 22
#     da = 0x1E
#     data = 0xDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEF0000
#     message = J1939.toJ1939Message(pgn, pri, sa, da, data)
#     assert message == b'\xCC\xAC\x0A\x00\x16\x1E\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\x00\x00'
#     j1939 = J1939.J1939Message(timestamp + message)
#     assert j1939.timestamp == int.from_bytes(timestamp, 'big')
#     assert hex(j1939.pgn) == hex(pgn)
#     assert j1939.pri == pri
#     assert j1939.sa == sa
#     assert j1939.da == da
#     assert j1939.data == sanitize_msg_param(data)
@pytest.mark.parametrize("pgn,da", argvalues=[
    (0xB100, 24), (0x0000, 0xFF), (0x1111, 0x00), (0x0000, 0x00), (0xFFFF, 0xFF)
])
def test_J1939Message_Request(pgn, da):
    """Test J1939Message class w/ a J1939 Request message."""
    timestamp = b'\x00\x00\x00\x00'
    msg_request = J1939.toJ1939Request(pgn, sa=2, da=da, size=8)
    msg = J1939.J1939Message(timestamp + msg_request)
    assert msg.isRequest()
    assert not msg.isEcho()
    assert msg.timestamp == int.from_bytes(timestamp, 'big')
    assert msg.pgn == 0x00EA00 + da
    assert msg.pri == 6
    assert msg.sa == 2
    assert msg.da == da
    assert msg.pf() == 0xEA
    assert msg.ps() == da
    assert msg.pdu() == 1
    assert msg.timestamp_bytes() == timestamp
    assert msg.data == sanitize_msg_param(pgn, 3, 'little') + b'\xFF\xFF\xFF\xFF\xFF'

def test_command_claimAddress():
    address = 0x0F
    name = 0xDEADBEEF
    blocking = True
    command = Commands.protectJ1939Address(address, name, blocking)
    assert command == b"\x0F\x00\x00\x00\x00\xDE\xAD\xBE\xEF\x00"
    address = 1
    name = 2355321 # 0x23F079
    blocking = False
    command = Commands.protectJ1939Address(address, name, blocking)
    assert command == b"\x01\x00\x00\x00\x00\x00\x23\xF0\x79\x02"

def test_setJ1939Filters():
    PGN = 1
    SOURCE = 4
    DEST = 8
    assert Commands.setJ1939Filters(0) == b'\x00\x00\x00\x00\x00\x00\x00'
    assert Commands.setJ1939Filters(PGN, pgn=0x0EF123) == b'\x01\x23\xF1\x0E\x00\x00\x00'
    assert Commands.setJ1939Filters(SOURCE, source=0xAB) == b'\x04\x00\x00\x00\x00\xAB\x00'
    assert Commands.setJ1939Filters(DEST, dest=0xCD) == b'\x08\x00\x00\x00\x00\x00\xCD'
    assert Commands.setJ1939Filters(PGN+SOURCE, pgn=0x0EF123, source=0xAB) == b'\x05\x23\xF1\x0E\x00\xAB\x00'

    filter_type = PGN # filter by PGN
    filter_list_int = [0xB100,
                    0xB200,
                    0xB300,
                    0xB400,
                    0xE000,
                    0xE04E,
                    0xE099,
                    0xE0FF,
                    0xF003,
                    0xF004,
                    0xFEDA,
                    0xFEEE,
                    0xFEF1,
                    0xFEF6,
                    0xFEF7,
                    0xFEF8,
                    0xFFCC,
                    0xFECA,
                    0x7500,
                    0x7800]
    filter_list_str = ["B100",
                       "B200",
                       "B300",
                       "B400",
                       "E000",
                       "E04E",
                       "E099",
                       "E0FF",
                       "F003",
                       "F004",
                       "FEDA",
                       "FEEE",
                       "FEF1",
                       "FEF6",
                       "FEF7",
                       "FEF8",
                       "FFCC",
                       "FECA",
                       "7500",
                       "7800"
                       ]
    for i in range(len(filter_list_int)):
        messageString = binascii.a2b_hex("01" + filter_list_str[i][2:4] + filter_list_str[i][0:2] + "00" + "000000")
        cmd_string = Commands.setJ1939Filters(filter_type, pgn=filter_list_int[i])
        assert messageString == cmd_string

@pytest.mark.skip("This test hasn't been implemented yet.")
def test_toJ1939Name():
    # arbitrary address (1 bit)
    # industry group (3 bits)
    # vehicle system instance (4 bits)
    # vehicle system (7 bits)
    # reserved bit (1 bit)
    # function (8 bits)
    # function instance (5 bits)
    # ecu instance (3 bits)
    # manufacturer code (11 bits)
    # identity number (21 bits)
    """TODO"""

@pytest.mark.parametrize("pgn,sa,da,pri", argvalues=[
    (0,0,0,0), (0xBEEF,0xF9,0xFF, 3), (0xFFFFFF, 0xFF, 0xFF, 6)
])
def test_toJ1939Request(pgn, sa, da, pri):
    """Tests J1939.toJ1939Request() function."""
    for x in range(3, 8): # check len
        assert len(J1939.toJ1939Request(pgn, sa, da, pri, size=x)) - 6 == x
    msg_data = J1939.toJ1939Request(pgn, sa, da, pri)
    pgn_bytes = sanitize_msg_param(pgn, 3, 'little')
    assert msg_data == J1939.toJ1939Message(0xEA00, pri, sa, da, pgn_bytes)

@pytest.mark.parametrize("byte5,echo,expected", argvalues=[
    (b'\x00', True, False), (b'\x01', True, True), # echo = on
    (b'\x00', False, False), (b'\x01', False, False)  # echo = off
])
def test_J1939Message_echo(byte5, echo, expected):
    """Tests echo parameter with isEcho()."""
    msg = b'\x00\x00\x00\x00' + byte5 + b'\x00\x00\x00\x00\x00\x00'
    assert J1939.J1939Message(msg, echo=echo).isEcho() == expected
    # message with echo

@pytest.mark.parametrize("msg_bytes,msg_ex,pgn_ex,da_ex,sa_ex,pri_ex,res_ex,dp_ex,data_ex,size_ex,how_ex", argvalues=[
    (b'\x00' * 6, b'\x00' * 6, 0x000000, 0x00, 0x00, 0, 0, 0, b'', 0, 0)
])
def test_J1939Message_parsing(msg_bytes, msg_ex, pgn_ex, da_ex, sa_ex, pri_ex, res_ex, dp_ex, data_ex, size_ex, how_ex):
    """
    Runs a parametrized sequence of tests on J1939Message class when instantiated from the output of
    RP1210_ReadMessage.
    """
    msg = J1939.J1939Message(b'\x00\x00\x00\x00' + msg_bytes)
    assert not msg.isEcho()
    assert msg.timestamp_bytes() == b'\x00\x00\x00\x00'
    assert msg.timestamp == 0
    assert msg.isRequest() == (pgn_ex & 0x00FF00 == 0x00EA00)
    assert msg.msg == msg_ex == bytes(msg) == sanitize_msg_param(msg)
    assert msg.pgn == pgn_ex
    assert msg.da == da_ex
    assert msg.sa == sa_ex
    assert msg.pri == pri_ex
    assert msg.res == res_ex
    assert msg.dp == dp_ex
    assert msg.data == data_ex
    assert msg.size == size_ex
    assert msg.how == how_ex
    assert msg.pf() == (pgn_ex & 0x00FF00) >> 8
    assert msg.ps() == pgn_ex & 0x0000FF
    if msg.pf() < 0xF0: # pdu1
        assert msg.pdu() == 1
        assert msg.ps() == da_ex
    else: # pdu2
        assert msg.pdu() == 2
    assert int(msg) == int.from_bytes(bytes(msg), 'big')
    assert str(msg) == str(msg.msg) == str(msg_ex)
    assert len(msg) == len(msg.msg) == len(msg_ex)
    assert msg == msg.msg == bytes(msg) == msg_ex
    if msg.data:
        assert msg
    else:
        assert not bool(msg)
    for x in range(len(msg_ex)):
        assert msg[x] == msg_ex[x] == msg.msg[x]
    

def test_j1939message_parsing_invalid_length():
    """Test J1939Message with invalid length. J1939Message should fill missing bytes with 0x00."""
    for x in range(1, 10):
        msg_bytes = sanitize_msg_param(0xff, x) # generate bytes w/ length of x
        msg_bytes_ext = msg_bytes + b'\x00' * (10-x)
        msg = J1939.J1939Message(RP1210_ReadMessage_bytes=msg_bytes)
        assert msg.msg == msg_bytes_ext[4:]
        assert msg.timestamp == int.from_bytes(msg_bytes_ext[:4], 'big')
        assert msg.timestamp_bytes() == msg_bytes_ext[:4]

def test_j1939message_generation():
    """
    Runs a parametrized sequence of tests on J1939Message class when instantiated from the output of
    RP1210_ReadMessage.
    """
