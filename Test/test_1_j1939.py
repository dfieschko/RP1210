from RP1210 import J1939, Commands, sanitize_msg_param
import binascii
import pytest

def test_getJ1939ProtocolString_default():
    assert J1939.getJ1939ProtocolString() == b"J1939:Baud=Auto"
    assert J1939.getJ1939ProtocolString(protocol=34234324234234) == b"J1939" # default to protocol format 2, default channel

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

@pytest.mark.parametrize("Baud, PROP_SEG, PHASE_SEG1, PHASE_SEG2, SJW, Channel", argvalues=[
    (500, 3, 20, 432, 32421, 234234), (0, 0, 0, 0, 0, 0), (5000, 500, "BAAA", "fadsfasdf", "afdsfasdf", "adsf")
])
def test_getJ1939ProtocolString_format4(Baud, PROP_SEG, PHASE_SEG1, PHASE_SEG2, SJW, Channel):
    chan_arg = f",Channel={str(Channel)}"
    val = bytes(f"J1939:Baud={str(Baud)},PROP_SEG={str(PROP_SEG)},PHASE_SEG1={str(PHASE_SEG1)},PHASE_SEG2={str(PHASE_SEG2)},SJW={str(SJW)},IDSize=29" + chan_arg, 'utf-8')
    assert val == J1939.getJ1939ProtocolString(protocol=4, Baud=Baud, PROP_SEG=PROP_SEG, PHASE_SEG1=PHASE_SEG1, PHASE_SEG2=PHASE_SEG2, SJW=SJW, Channel=Channel)

@pytest.mark.parametrize("Baud, TSEG1, TSEG2, SampleTimes, SJW, Channel", argvalues=[
    (500, 3, 20, 432, 32421, 234234), (0, 0, 0, 0, 0, 0), (5000, 500, "BAAA", "fadsfasdf", "afdsfasdf", "adsf")
])
def test_getJ1939ProtocolString_format5(Baud, TSEG1, TSEG2, SampleTimes, SJW, Channel):
    chan_arg = f",Channel={str(Channel)}"
    val = bytes(f"J1939:Baud={str(Baud)},TSEG1={str(TSEG1)},TSEG2={str(TSEG2)},SampleTimes={str(SampleTimes)},SJW={str(SJW)},IDSize=29" + chan_arg, 'utf-8')
    assert val == J1939.getJ1939ProtocolString(protocol=5, Baud=Baud, Channel=Channel, TSEG1=TSEG1, TSEG2=TSEG2, SampleTimes=SampleTimes, SJW=SJW)

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

@pytest.mark.parametrize("msg_bytes,pgn_ex,da_ex,sa_ex,pri_ex,res_ex,dp_ex,data_ex,size_ex,how_ex", argvalues=[
    # MSG BYTES                             PGN EXP.    DA      SA      PRI RES DP  DATA            SIZE    HOW
    (b'\x00' * 6,                           0x000000,   0x00,   0x00,   0,  0,  0,  b'',            0,      0),
    (b'\xBC\xAA\x00\x03\xBF\x12\xFF',       0x00AA12,   0x12,   0xBF,   3,  0,  0,  b'\xFF',        1,      0), # PDU1 replaces PS w/ DA
    (b'\xBC\xFE\x00\x03\xBF\x12\xFF',       0x00FEBC,   0xFF,   0xBF,   3,  0,  0,  b'\xFF',        1,      0), # PDU2 DA = 0xFF
    (b'\xBC\xFE\x03\x03\xBF\x12\xFF',       0x03FEBC,   0xFF,   0xBF,   3,  1,  1,  b'\xFF',        1,      0), # res & dp
    (b'\xBC\xFE\x00\x83\xBF\x12\xFF',       0x00FEBC,   0xFF,   0xBF,   3,  0,  0,  b'\xFF',        1,      1), # how
    (b'\xBC\xFE\x00\x83\xBF\x12\xFF\xFF',   0x00FEBC,   0xFF,   0xBF,   3,  0,  0,  b'\xFF\xFF',    2,      1), # size 2
])
def test_J1939Message_parsing(msg_bytes, pgn_ex, da_ex, sa_ex, pri_ex, res_ex, dp_ex, data_ex, size_ex, how_ex):
    """
    Runs a parametrized sequence of tests on J1939Message class when instantiated from the output of
    RP1210_ReadMessage.
    """
    msg = J1939.J1939Message(b'\x00\x00\x00\x00' + msg_bytes)
    assert not msg.isEcho()
    assert msg.timestamp_bytes() == b'\x00\x00\x00\x00'
    assert msg.timestamp == 0
    assert msg.isRequest() == (pgn_ex & 0x00FF00 == 0x00EA00)
    assert msg.msg == msg_bytes == bytes(msg) == sanitize_msg_param(msg)
    assert msg.res == res_ex
    assert msg.dp == dp_ex
    assert msg.pgn == pgn_ex
    assert msg.da == da_ex
    assert msg.sa == sa_ex
    assert msg.pri == pri_ex
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
    assert str(msg) == str(msg.msg) == str(msg_bytes)
    assert len(msg) == len(msg.msg) == len(msg_bytes)
    assert msg == msg.msg == bytes(msg) == msg_bytes
    if msg.data:
        assert msg
    else:
        assert not bool(msg)
    for x in range(len(msg_bytes)):
        assert msg[x] == msg_bytes[x] == msg.msg[x]
    
@pytest.mark.parametrize("pgn, da, sa, data", [
    #   PGN     DA      SA      DATA
    (   None,   None,   None,   b''),
    (   None,   None,   1,      None),
    (   None,   1,      None,   None),
    (   1,      None,   None,   None),
    (   None,   None,   None,   None),
    (   None,   None,   None,   b'\xFF\xEF\xDF'),
])
def test_J1939Message_init_params(pgn, da, sa, data):
    """Make sure that no properties are left None when not provided."""
    msg = J1939.J1939Message(pgn=pgn, da=da, sa=sa, data=data)
    assert msg.pgn is not None
    assert msg.da is not None
    assert msg.sa is not None
    assert msg.data is not None
    assert msg.pri is not None
    assert msg.how is not None
    assert msg.size is not None
    assert msg.res is not None
    assert msg.dp is not None
    assert msg.timestamp is not None
    assert msg.pdu() is not None
    assert msg.pf() is not None
    assert msg.ps() is not None
    assert msg.timestamp_bytes() is not None
    assert msg.isEcho() is not None
    assert msg.isRequest() is not None


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
